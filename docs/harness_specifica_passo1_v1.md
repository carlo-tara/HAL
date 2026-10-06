# Harness Engineering — Specifica Passo 1: Gateway (v1.0, 2026-10-03)

## 1. Obiettivo

Gateway FastAPI che espone a Zed un endpoint OpenAI-compatible (chat completions con SSE +
images) instradato verso OrcaRouter, con modelli virtuali per caso d'uso, autenticazione Bearer
e logging eventi v0. Solo container; nessun orchestratore ancora (arriva al passo 2).

Alla fine del passo 1: si scrive codice dentro Zed attraverso il proprio harness, con eventi reali
nel log.

## 2. Integrazione OrcaRouter

- Endpoint: https://api.orcarouter.ai/v1 — OpenAI-compatible (Chat Completions, Responses,
  Embeddings, Images, Audio, streaming).
- model="orcarouter/auto": grading del prompt (<1ms) e routing interno frontier/OSS con failover.
- Overhead totale <50ms. Zero markup sul token.
- Prompt NON loggati lato OrcaRouter (ZDR): l'unica copia completa del traffico è il log locale.
- Il campo modello effettivamente servito va catturato dalla risposta (per-prompt receipt) e loggato.

## 3. Struttura progetto

gateway/
├── Dockerfile
├── app/
│   ├── main.py                # FastAPI, lifespan, caricamento config a startup
│   ├── config.py              # providers.yaml + use-cases/*.yaml
│   ├── auth.py                # Bearer (env GATEWAY_API_KEY)
│   ├── models_catalog.py      # GET /v1/models generato dagli use-case
│   ├── chat.py                # POST /v1/chat/completions (SSE)
│   ├── images.py              # POST /v1/images/generations
│   ├── providers/
│   │   ├── base.py            # ModelBackend protocol + Capabilities
│   │   ├── registry.py        # load da providers.yaml
│   │   └── openai_compatible.py
│   ├── events.py              # append JSONL diretto sul volume (al passo 1; event-writer al passo 3)
│   └── session.py             # session_id deterministico da (api_key, conversation)
├── config/
│   ├── providers.yaml
│   └── use-cases/             # 5 file YAML (sezione 5)
└── docker-compose.yml

## 4. config/providers.yaml

```yaml
providers:
  orcarouter:
    type: openai_compatible
    base_url: "https://api.orcarouter.ai/v1"
    auth: env:ORCAROUTER_API_KEY
    capabilities: {chat: true, images: true, streaming: true, audio: true}
    default_model: "orcarouter/auto"
    priority: 10
  # ollama:          # dopo upgrade hardware
  #   type: ollama
  #   base_url: "http://ollama:11434"
  #   capabilities: {chat: true, streaming: true}
  #   priority: 5
  # specialist-xyz:  # servizio esterno per modelli proprietari non coperti:
  #   type: openai_compatible   # se parla OpenAI: zero codice
  #   base_url: "https://api.specialist.example/v1"
  #   auth: env:SPECIALIST_KEY
  #   capabilities: {chat: true, streaming: true, max_context: 500000}
  #   models: [modello-proprietario]
  #   priority: 20
```

Risoluzione (già strutturata per il futuro): capability match → catena preferred → health →
fallback globale. Se il profilo dichiara model esplicito ("provider/modello"), quello vince.

## 5. config/use-cases/*.yaml (uno per file, scoperti a runtime)

Esempio code-tdd.yaml — tutti seguono la stessa forma:

```yaml
id: harness-code-tdd
label: "Coding TDD"
routing:
  preferred: [orcarouter]        # domani: [ollama, orcarouter]
  model: null                    # null = delega a orcarouter/auto
  params: { temperature: 0.2 }
  latency_budget_ms: 8000
tools: [shell-runner]            # whitelist (informativa al passo 1)
laya:
  intake_class: coding_tdd
  min_confidence: 0.7
limits:
  max_context_tokens: 64000
```

File: code-tdd.yaml, analyze-docs.yaml, write-article.yaml, image-gen.yaml, web-agent.yaml.
Aggiungere un caso d'uso = nuovo file (richiede anche entry in intake.yaml di Laya al passo 2).

## 6. Endpoint

- GET /v1/models → array da use-cases/ (id harness-*, max_tokens dai limits, images:true solo su harness-image)
- POST /v1/chat/completions → valida → risolve provider da model → inoltra con stream=true forzato
  → re-stream SSE a Zed. Il campo tools, se presente, passa così com'è (Zed Agent chiude il loop tool).
- POST /v1/images/generations → stessa risoluzione, risposta singola.
- 401 senza Bearer valido. session_id deterministico da (api_key, messages).

## 7. settings.json di Zed

```json
{
  "language_models": {
    "harness": {
      "type": "openai_compatible",
      "name": "Harness",
      "api_url": "http://localhost:8900/v1",
      "available_models": [
        {"name": "harness-code-tdd", "display_name": "Harness · Coding TDD", "max_tokens": 64000},
        {"name": "harness-analyze",  "display_name": "Harness · Analisi",    "max_tokens": 200000},
        {"name": "harness-write",    "display_name": "Harness · Scrittura",  "max_tokens": 128000},
        {"name": "harness-image",    "display_name": "Harness · Immagini",   "max_tokens": 0, "images": true}
      ]
    }
  }
}
```

Chiave: keychain di Zed o env HARNESS_API_KEY.

## 8. Schema eventi v0 (JSONL, una riga per evento)

{"kind":"request","ts":"...","session_id":"...","use_case":"harness-code-tdd",
 "model_requested":"harness-code-tdd","n_messages":12,"n_tokens_est":4500,
 "has_tools":true,"client":"zed"}

{"kind":"llm_call","ts":"...","session_id":"...","provider":"orcarouter",
 "model_served":"claude-...","latency_ms":3200,"tokens_in":4500,"tokens_out":612,
 "cost_usd":0.014,"finish_reason":"stop"}

{"kind":"error","ts":"...","session_id":"...","provider":"orcarouter",
 "error_type":"timeout|rate_limit|server|client","status":429}

Colonne chiave per il routing futuro: use_case vs model_served vs outcome.
Se model_served manca nella risposta: loggare null + flag, mai omettere la riga.

## 9. docker-compose.yml

```yaml
services:
  gateway:
    build: ./gateway
    ports: ["8900:8900"]
    environment:
      GATEWAY_API_KEY: ${GATEWAY_API_KEY}
      ORCAROUTER_API_KEY: ${ORCAROUTER_API_KEY}
    volumes:
      - ./config:/app/config:ro
      - events:/data/events
volumes:
  events:
```

## 10. Regole operative

1. Body logging fin dal giorno 1 (OrcaRouter ZDR: la copia locale è l'unica). Rotazione JSONL
   giornaliera, backup del volume.
2. model_served sempre loggato (null se assente).
3. Config montata read-only; mai editare la config live, si promuove una versione nuova.
4. Ogni passo deve lasciare il sistema utilizzabile da Zed.

## 11. Criterio di completamento del passo 1

- Zed connesso: chat streaming funzionante su almeno due profili
- Generazione immagini funzionante via profilo harness-image
- Eventi v0 presenti nel volume per ogni request
- Verifica manuale: request → llm_call con model_served popolato, latency e token

## 12. Passo 2 (prossimo)

Estrarre system2 dal gateway (che torna puro protocol adapter): policy di routing, collegamento
Laya (laya-serve in container: preset intake con tassonomia a 5 classi + guardrail), health check
provider, prime soglie di astensione → classificazione di riserva. Il log del passo 1 alimenterà
le prime regole del futuro sistema esperto.

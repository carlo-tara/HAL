# Harness Engineering — Visione d'insieme (v1.0, 2026-10-03)

## 1. Scopo

Sistema personale di harness per LLM, ispirato alla dicotomia System 1 / System 2 di Kahneman:
- **System 1 (Laya)** — classificatore decisionale non-autoregressivo (choice / score / noul), ~33ms per
  forward pass. Non genera testo: decide. Viene invocato continuamente, da orchestratore e modelli,
  ogni volta che serve una decisione. È il sistema nervoso del harness.
- **System 2 (Orchestratore)** — livello deliberato: classifica la richiesta, sceglie il modello,
  gestisce fallback, handoff ed escalation. Esercita il controllo solo dove serve.

Il client è **Zed** (IDE), che parla OpenAI-compatible (chat + streaming SSE) e MCP (tools).

## 2. Principi architetturali

1. **Separazione control plane / data plane.** Il runtime non dipende mai dall'analisi;
   l'analisi è read-only sui dati del runtime.
2. **Config as code.** Policy di routing, question set Laya, profili d'uso: tutto in YAML
   versionato. Il sistema esperto propone diff, non tocca codice.
3. **Event sourcing completo.** Ogni decisione, chiamata, handoff, output e feedback è un evento
   immutabile e append-only. È il dataset per analisi, replay e fine-tuning.
4. **Confini = API.** Nessun container importa il codice di un altro.
5. **Modularità per casi d'uso e provider.** Casi d'uso = file YAML scoperti a runtime;
   provider = adapter dietro un contratto uniforme. Aggiungere uno dei due non tocca l'altro.

## 3. Topologia dei container

| Container | Ruolo | Stato |
|---|---|---|
| gateway | Ingresso unico verso Zed: auth Bearer, validazione, protocollo OpenAI-compatible, SSE, catalogo modelli virtuali | stateless |
| system2 | Orchestratore/router: pre-flight Laya, policy di routing, risoluzione provider, handoff, fallback | stateless (stato in Redis) |
| system1 | Laya (laya-serve): decisioni tipizzate via POST /v1/systemone, preload checkpoints | stateless (modelli in memoria) |
| prompt-opt | Ottimizzazione/rewriting prompt | da costruire |
| context-opt | Assemblaggio contesto: memoria, storico, compattazione, injection fatti Laya | da costruire |
| guardrail | Validazione input/output, PII, injection — incluso su contenuto web recuperato | da costruire (retained) |
| tool-svc | Esecuzione tool centralizzata; espone transport MCP verso Zed Agent (shell-runner MVP, poi playwright) | da costruire |
| ollama | LLM locali | da attivare dopo upgrade hardware |
| providers esterni | OrcaRouter (OpenAI-compatible, orcarouter/auto); in futuro servizi specialistici | — |
| memory | Store memoria persistente tra sessioni | da costruire |
| redis | Cache risposte, stato sessioni, code, lavagna dei fatti decisionali | adottato |
| event-writer | Riceve eventi via HTTP, append JSONL atomico su volume | da costruire |
| log-compactor | Compatta JSONL → Parquet periodico | da costruire |
| expert | DuckDB su Parquet (read-only) + regole: analisi, proposte diff, replay | da costruire |
| evals | Gate di qualità: valutazione offline delle config candidate prima della promozione | da costruire |
| config-svc | Versionamento e distribuzione config ai container | da costruire |

## 4. Flusso di una richiesta

1. Zed → gateway: POST /v1/chat/completions (o /v1/images/generations), Bearer auth.
2. gateway risolve il profilo d'uso dal campo model (modelli virtuali harness-*).
3. system2 chiama system1 con i preset intake + guardrail (un solo forward pass):
   task_type, complessità, needs_tools, safety. Astensione → classificazione di riserva o
   policy prudente (System 1 incerto → palla a System 2 deliberato).
4. context-opt assembla contesto (memoria + storico Zed + fatti Laya dalla lavagna);
   prompt-opt compone il prompt finale.
5. system2 risolve il provider: catena preferred filtrata per capability, health, budget;
   in assenza, fallback orcarouter/auto.
6. Esecuzione: LLM via provider; tool passano per tool-svc (MCP verso Zed Agent, che chiude
   il loop); stream SSE verso Zed.
7. Post-flight: guardrail valida output; system1 (preset output) lo scora; handoff riavvia
   dal punto 5 con modello promosso.
8. Ogni passo emette eventi (request, laya_decision, llm_call, tool_call, handoff, output,
   user_feedback).

## 5. Il vocabolario decisionale condiviso

Registry centralizzato di question set Laya versionati (YAML): intake, routing, guardrail,
execution, output, budget, memory. I componenti referenziano preset per nome+versione, mai
domande inline. Le decisioni di Laya vengono scritte in Redis come fatti tipizzati con
provenance (source, versione, timestamp) — la "lavagna" condivisa tra System 1 e System 2.

Tassonomia intake = i cinque casi d'uso: coding_tdd, document_analysis, writing,
image_gen, data_retrieval (+ casual/other). Il profilo scelto in Zed e la classe Laya devono
concordare: la discordanza è un segnale di misclassificazione gratuito e misurabile sul log.

## 6. Provider layer

Contratto ModelBackend: capabilities(), chat(), images(). Adapter openai_compatible riusabile
per qualunque servizio che parli quel protocollo (OrcaRouter oggi, servizi specialistici domani,
zero codice); adapter dedicati solo per protocolli diversi (Ollama). Risoluzione capability-based:
il profilo dichiara capability richieste e catena preferred; i provider dichiarano cosa offrono.

Divisione dei ruoli col routing interno di OrcaRouter: System 2 decide la CLASSE d'uso (semantica);
orcarouter/auto decide il MODELLO concreto (operativo) finché il log non giustifica fissarlo.

## 7. Control plane: miglioramento continuo

eventi (Parquet, append-only) → expert (DuckDB + regole) → proposta diff (es. routing.yaml v14→v15)
→ evals: replay offline degli eventi con la config candidata + benchmark → PASS: promozione via
config-svc; FAIL: scartata con report → misurazione dell'impatto post-deploy.

Livelli del sistema esperto:
1. Regole deterministiche sul log (IF condizioni THEN proposta di config) — da subito
2. Ricalibrazione Laya (temperature, abstention thresholds) con gate laya-evals
3. Fine-tuning Laya sulle decisioni loggate con outcome (0.362 → 0.766 sul benchmark del progetto)

Regola di sicurezza: il sistema esperto non scrive mai direttamente in produzione.
Ciclo: log → analisi → proposta → valutazione replay → promozione → monitoraggio.

## 8. Persistenza e dati

- Eventi grezzi: JSONL append-only (rotazione giornaliera, volume Docker, backup fin dal giorno 1:
  OrcaRouter non conserva i prompt — ZDR — quindi la copia locale è l'unica).
- Compattazione periodica in Parquet (formato standard per DuckDB, pandas, dataset di fine-tuning).
- DuckDB (libreria, dentro expert) per l'analisi: separazione naturale scrittura/analisi,
  nessuna contesa.
- Scelta quasi reversibile: il lock-in è il formato (Parquet), non il motore.

## 9. Risorse e note operative (laptop)

- GPU → ollama (quando attivo); Laya gira su CPU con core pin (LAYA_THREADS) — mai contesa.
- Redis ed event-writer leggeri; system2 stateless (scalabile).
- Config montata read-only come artefatto immutabile per versione.
- Profili Zed via feature-specific models possibili (inline assistant, commit, ecc.).

## 10. Casi d'uso (moduli use-cases/*.yaml)

| Profilo | Default | Vincolo | Tools |
|---|---|---|---|
| harness-code-tdd | modello piccolo/furbo | latenza (loop iterativo) | shell-runner (pytest, cargo test...) |
| harness-analyze | grande contesto | contesto documenti, ragionamento | retrieval |
| harness-write | medio-grande | qualità stilistica, output lunghi | — |
| harness-image | endpoint images | pipeline dedicata | — |
| harness-agent | medio tool-calling | affidabilità loop | playwright + guardrail su contenuti web |

Aggiungere un caso d'uso = file YAML + entry in intake.yaml + eventuale criterio routing.
Il caso playwright richiede guardrail su contenuto non fidato (injection via pagine web).

## 11. Ordine di costruzione (walking skeleton)

1. **Gateway passthrough** → OrcaRouter, modelli virtuali, SSE, eventi v0. Zed collegato.
2. **system2** nel mezzo: policy YAML, Laya intake+guardrail, health check.
3. **Eventi**: event-writer + compactor Parquet (parallelo al 2).
4. MCP shell-runner (TDD end-to-end), poi playwright con guardrail.
5. context-opt, prompt-opt, memoria.
6. expert + evals (il log ci sarà già).
7. Ollama dopo upgrade hardware: entry providers.yaml + fallback chain.

Regola dello skeleton: ogni passo lascia il sistema utilizzabile da Zed.

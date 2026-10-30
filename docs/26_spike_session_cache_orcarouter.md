# 26 — Spike: session-cache e marker explicit via OrcaRouter (N28, 2026-10-30)

Domanda (ToDo P2, doc QwenCloud «Context cache» §session): OrcaRouter inoltra
l'header `x-dashscope-session-cache: enable` e i marker `cache_control`
(explicit, due strati)? Quale ingresso di caching conviene a HAL?

## Protocollo di misura

- Endpoint: `{ORCAROUTER_API_URI}/chat/completions`, modello `orcarouter/free`.
- Prefisso statico ~1092 token (sopra la soglia di 1024), stessa richiesta
  ripetuta a caldo (distanza 2 s, entro il TTL session di 5 min):
  - R1 plain, R2 plain-hot, R3 `x-dashscope-session-cache: enable`,
    R4 content-block con `cache_control: {"type":"ephemeral"}`.
- Pre-probe con 4 chiamate su `qwen/qwen3-vl-8b-instruct`: upstream 503 (provider
  non disponibile al momento del test, non un risultato del forwarding).

## Esiti

| Variante            | HTTP | prompt_tokens | cached_tokens |
| ------------------- | ---- | ------------- | ------------- |
| R1 plain            | 200  | 1092          | 0             |
| R2 plain hot        | 200  | 1092          | 0             |
| R3 session-header   | 200  | 1092          | 0             |
| R4 marker ephemeral | 200  | 1092          | 0             |

- Il marker viene **accettato** (payload valido, niente 400) ma è **inerente**:
  nessun campo di cache esplicita (né `cache_creation_input_tokens` né hit).
- L'header di sessione non produce alcun effetto osservabile sul billing.
- Anche l'implicit non mostra hit a caldo su questa rotta (cached_tokens resta 0).

## Decisione

1. **Explicit `cache_control` (voce N29): non adottato ora.** Il contratto dei
   backend già tollera i marker e il flag `context_cache` esiste nei profili
   (N14), ma senza hit misurabile il builder di guardrail sarebbe non verificabile
   → skip documentato, riaprire solo con backend che esponga cache esplicita.
2. **Session-cache Qwen: rifiutato.** OrcaRouter come aggregatore non inoltra
   la semantica; HAL non può contarci.
3. **Ingresso scelto: implicit + ordering static-first (già atterrato) + Cache
   L1 a due livelli lato gateway** (consegnata N1–N2): il risparmio reale su
   OrcaRouter oggi viene dalla cache di risposta del gateway, non dal provider.

## Riprodurre

`env PYTHONPATH=. python3 scripts/spike_orcarouter_cache.py` (script dello
spike, chiamate minime su modello free; sorgente dei dati della tabella sopra).

System 1 (Laya) conferma la decisione con `choice` → `rifiuta` (status ok).

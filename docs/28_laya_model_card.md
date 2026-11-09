# Laya Model Card — System 1 del gateway

Carta del modello per `laya_service.py` (consumer HTTP) — fonte: `/var/www/hal_system1`
(README + `laya_gate.py` canonico), sonda `laya_health` 2026-11-09. Scopo: rendere il
black-box ricostruibile senza aprire il repo sorgente a ogni domanda (finding
`/impersonate karpathy` 2026-11-09 → voce ToDo `HT-006`).

## Identità

- **Modello**: Laya (`convaiinnovations/laya`, HuggingFace), classe multilingue; il
  deployment HAL risponde `model: "multilingual"` all'endpoint `/health`.
- **Servizio**: HTTP locale `http://laya.local:8091` (→ `127.0.0.1:8091`, solo HTTP),
  una istanza host condivisa da tutti i progetti HAL. Consumer: CLI `router.py`,
  MCP `mcp_laya.py`, gateway `laya_service.py` — tre binding, soglie uniche da
  `laya_gate.py` (mirror tracciato, guardia `tests/test_laya_gate_mirror.py`).
- **Hardware**: Quadro M2200 4 GB (capability 5.2); VRAM allocata ~1,23 GB (2026-09-09: sonda).

## Cosa è (funzione)

Input: `{task, text, options|routes|criteria}` su `POST /v1/systemone` (convenzione
HAL) o `/predict` passthrough nativo `{state, questions}`. Uscita: scelta + `probabilities`
per opzione; il gate ricava `margin = top1 − top2` e `recommendation`
(`system1_direct` / `accept_with_caution` / `escalate_system2`). Famiglie task:
`choice`, `routing`, `score`, `noul` (+ `confidence`, `context` sul binding nativo).

## Limiti misurati (non opinioni)

- **`confidence` deprecata come soglia**: è `1 − entropia normalizzata` e dipende da k;
  a k=2 solo il 6–8% dei verdetti supera 0,8 benché il 54% abbia top1>0,8. Il segnale
  corretto è il margine top1-top2.
- **Decision-family (choice/routing) non è `noul`**: run rv7 2026-11-05, n=94 voti
  outcome — accuracy ~37% **anche a margin ≥ 0,5/0,6** (29/56 errori dentro la zona
  direct). L'eccezione `top1 ≥ 0,8` per k ≥ 4 (2026-10-31) è **revocata**: a k ≥ cap
  (`DIRECT_CAP_OPTIONS=4`) il verdetto non è mai diretto. `noul` mantiene 96,5% a
  margin ≥ 0,5.
- **Over-confidence a k grande**: margini alti convivono con masse disperse e refactor
  a conf 0,99 votati incorrect.
- **Latenza**: base ~0,3 s (range doc-consented 0,2–0,5); picchi `noul` 3–30 s sotto
  contesa GPU (eccezione, non media).
- **Input lunghi**: il server collassa righe identiche consecutive e poi testa+coda;
  segnalato in `usage.input_collapsed` / `input_compacted`.

## Ciclo di calibrazione

`request_hash` in ogni risposta → `POST /outcome` (voto esplicito o cieco `expected`)
→ `make telemetry` (accuracy per fascia di margine, separata `noul` vs decision-family).
Escalation L1→L2 registra **voti impliciti** (`LAYA_IMPLICIT_VOTES`, disattivabile).

## Riesame ROI del layer (lezione amara)

Il mid-layer System 1 vale finché batte in costo la chiamata diretta a un modello
System 2 economico; **se i modelli di scala scendono di prezzo il layer si assottiglia**.
Riesame obbligato a ogni run benchmark che tocca la §Telemetria; esito agganciato alla
voce ToDo `HT-003` (A/B gated vs baseline `20261017_all` con kill criterion).

## N/A documentati

- Training data / famiglia architetturale interna: fuori perimetro HAL (repo sorgente
  privato `carlo-tara/laya`); la carta registra ciò che è **misurato in produzione**,
  non ciò che è dichiarato dal paper.
- Eval raw con gold set etichettato: assente — è la voce ToDo `HT-005` (l'accuracy
  citata viene da voti outcome di produzione, n=94, non da dati con risposta nota).
  L'infrastruttura di misura è pronta da HT-008: schema
  `benchmark/config/gold_set.schema.json` + CLI `scripts/gold_set_scoring.py`
  (hit-rate e accuracy per fascia di margine, soglie da `laya_gate`); mancano
  solo le etichette umane.

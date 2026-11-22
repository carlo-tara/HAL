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

- **Primo eval raw su oro etichettato (HT-010, run 2026-11-18, n=123 casi confermati**
  da umano — `benchmark/gold_set/gold_set.jsonl` + `pred.jsonl`, rigenerabili con
  `python3 benchmark/scripts/gold_set_pred_runner.py` e misurabili con
  `python3 scripts/gold_set_scoring.py benchmark/gold_set/gold_set.jsonl benchmark/gold_set/pred.jsonl`):
  hit_rate complessivo **0.276**; decision-family 34/63 ≈ .540 (choice .484,
  routing .594); by_band **direct .523 (n=44)**, caution .643 (n=14),
  escalate .031 (n=65 — include le astensioni). Curva margin→accuracy debole e
  non monotona: .548 a ≥0.8, .667 a ≥0.9, .812 solo a ≥0.95 (n=16) — al draft
  attuale **nessuna soglia giustifica di toccare `laya_gate`**; l'adozione è
  gated su copertura piena (`HT-011`). Due caveat sull'instrumento, non sul
  modello: `score` è by-pass onesto del servizio (30/30 `score_not_discriminative`,
  by design) e `noul` risponde nel suo vocabolario {uncertain, refuse,…} mentre
  l'oro usa {routing, choice, score, astensione} → 0/30 sistematico; il
  allineamento del vocabolario è nel residuo di `HT-005`.

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
- **Prefissi conventional-commit (decision-family `choice`, sessioni hal_gateway 2026-11-20/22)**: **1/5** correct nei voti `laya_outcome` (hash `09868699…`, `91c419b0…`, `ee11e6f2…`, `130db61c…`, `01c15afe…`): `feat` scelto 3 volte su 5 e corretto solo sulla transazione infra reale (HT-014 apply); gli errori sono tutti su diff di soli registri/docs (scritti `docs`/`fix` contro scelte feat/fix/refactor; margin 0,041–0,522 → `escalate_system2` a k≥4 come da T-73140). Corrobora la confusion matrix nota (feat↔docs/refactor) sui diff non-codice. Regola operativa: su commit di soli registri/markdown l'escalation S2 è la norma e la risposta quasi a priori è `docs`; la consultazione S1 resta obbligatoria da protocollo, la delibera è di S2.

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
- Eval raw con gold set etichettato: prima misura **eseguita il 2026-11-18** su
  123 casi confermati (vedi §Limiti misurati) — il gold set **completo**
  (~200/famiglia) e il vocabolario noul allineato restano voce ToDo `HT-005`;
  l'accuratezza storica citata altrove viene da voti outcome di produzione
  (n=94), non dall'oro. Infrastruttura di misura da HT-008/HT-010: schema
  `benchmark/config/gold_set.schema.json` + `scripts/gold_set_scoring.py` +
  runner `benchmark/scripts/gold_set_pred_runner.py`.

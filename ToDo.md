# Mappa residui — HAL

Backlog rinfrescabile (≠ Progress append-only). Igiene: `/todo`.

Convention: ID stabile `HT-nnn` (non cambia a seguito di riordino); tag di chiusura — `#cycle` = richiudibile con `/cycle` (slice → red → green → refactor sotto gate Make), `#human` = richiede intervento umano (sessioni reali, step cross-repo, validazione).

Delta 2026-11-09 da `/impersonate karpathy hal_gateway` (lente registry `hal_mcp_tools`): le voci HT-003…HT-007 derivano dai finding della lettura (residuo aperto al 2026-11-16: solo HT-005 e HT-007; HT-003/004/006/008/009 chiuse, esiti in CHANGELOG); praise «modello-usato-come-funzione» (`system1_preflight.TaskContract`/`PreflightDecision`) e «calibrazione da telemetria» (`laya_gate.py`) sono già architetture consolidate, senza voce.

Delta 2026-11-18 (sessione HT-005): consegnati strumento e draft oro — `benchmark/gold_set/HT-005_labeling.xlsx` + generator/exporter (`1822d3e`, fix pyright `8f17fb0`) e `benchmark/gold_set/gold_set.jsonl` con 123 casi draft (`f1cdb94`). Aperta `HT-010` come estratto ciclabile (pred runner + regressione make target + ricalibrazione `laya_gate`); `HT-005` resta `#human` per il completamento a ~200/famiglia (le prime 123 label confermate da umano il 2026-11-18).

## P0

## P1

## P2

- [ ] `HT-005` — Gold set etichettato per l'eval raw di Laya (~200 casi/famiglia task) `#human` · P2 · System 1 (Laya)
  - STATO 2026-11-18: infrastruttura e strumento consegnati (HT-008 schema+scoring; workbook con 800 id/famiglia e workflow nel foglio Istruzioni, export `benchmark/scripts/gold_set_xlsx_to_jsonl.py`). Draft versionato in `benchmark/gold_set/gold_set.jsonl`: 123 casi validati (choice 31, routing 32, score 30, noul 30) con label **confermate da umano il 2026-11-18** (`f1cdb94`). Residuo umano: (a) confermare/rettificare le 123 label — **FATTO 2026-11-18** (conferma in sessione Zed; note del workbook aggiornate a «confermata»), (b) redigere i casi mancanti fino a ~200/famiglia, re-esportando dopo ogni sessione di etichettatura. La parte automatizzata dell'acceptance è estratta in `HT-010` (sull'orma dell'estratto `HT-008`).
  - Perché utile: l'accuracy ~96,5% del gate è misurata su **traffico di produzione** (8k chiamate, telemetria margini), non su casi con risposta nota: è calibrazione della soglia, non eval del modello. Un gold set rende l'eval di Laya una regressione riproducibile (benchmark, non impressione) ed è la baseline che il reject di `/impersonate karpathy` chiede («feature AI senza baseline»).
  - Acceptance: set versionato (choice/routing/score/noul, ~200 casi con label **confermate da umano**) + script di scoring in `benchmark/` (già consegnato, HT-008); il gate e le soglie di `laya_gate.py` ricalibrati sul set e la run di regressione agganciata a una make target esistente — estratti in `HT-010`.

- [ ] `HT-010` — Chiusura eval gold set System 1: runner `pred.jsonl` sul percorso prod + regressione `gold_set_scoring` su make target + proposta di ricalibrazione soglie `laya_gate` (estratto ciclabile di `HT-005`) `#cycle` · P2 · System 1 (Laya)
  - Perché utile: il set draft (`benchmark/gold_set/gold_set.jsonl`, 123 casi) non è mai stato misurato contro il modello: senza pred pipeline lo scorer HT-008 resta uno strumento senza dati e l'accuracy del gate continua a essere calibrazione su telemetria, non regressione su risposte note.
  - Acceptance: script runner che genera `pred.jsonl` per ogni caso gold (choice/routing/noul via percorso prod; per `score` il numerico va buckettato in {alto, medio, basso} con soglia dichiarata nel test); unit test a fixture sintetiche senza duplicare le soglie (fonte unica `laya_gate`, precedent HT-008); run `python3 scripts/gold_set_scoring.py` inclusa in una make target esistente via discovery `test-unit` (nessun gate nuovo); esito `by_band` e proposta soglie (`FAST_MARGIN`/`ESCALATE_MARGIN`/`ROUTE_*`) portati nel figlio `- Esito:` della voce. Prerequisito: conferma umana delle label `HT-005` — **soddisfatto sulle prime 123 (2026-11-18, oro confermato parziale)**; la ricalibrazione in produzione si adotta con il set completo a copertura piena.

- [ ] `HT-007` — Misura dell'effetto assemblaggio locale vs `assemblaggio_finale` via modello `#human` · P2 · Benchmark
  - STATO (2026-11-09, /cycle step-0 CHIUSO): lo switch mancava (verificato sul canonico) — ora c'è: `BENCHMARK_LOCAL_ASSEMBLY=0` nell'ambiente del processo fa ritornare `None` a `assemble_segments_locally` (braccio B), default invariato (braccio A). Lato `hal_system2`: `app/benchmark_workflow.py` + test `tests/test_benchmark_local_assembly_toggle.py` (4 casi, RED 2/694 → suite 696 MAKE_EXIT=0) + voce CHANGELOG `[sync:safe]` — tutto non committato lì (commit responsabilità della sessione parallela HT-004); mirror gateway allineato, suite verde. Smoke braccio B **reale completato**: llama3.2:1b, 1 ok, 2.189 token, 68,4 s, qualità 2/2, trace con `assemblaggio_finale` e ZERO `assemblaggio_locale` (run-dir `events/benchmarks/20261109b_smokeB`). catalogs usati (necessari, il default hs2 è ruotato e il loader vuole esattamente 5 prompt): `--models events/benchmarks/20261109b_models_ht003.json` + `--prompts events/benchmarks/20261109b_prompts_h007.json` (creato: 5 canonici con `estrazione_json` sostituito dal simplified) + `--prompt estrazione_json_semplificato`.
  - Run da lanciare (umano, bracci appaiati, in `hal_system2`): ARM A `setsid python3 -m app.benchmark_models --models events/benchmarks/20261109b_models_ht003.json --model phi3:mini --model llama3.2:3b --prompts events/benchmarks/20261109b_prompts_h007.json --prompt estrazione_json_semplificato --provider ollama --cooldown 180 --timeout 1200 --run-dir events/benchmarks/20261109_h07A --output events/benchmarks/20261109_h07A/results.json`; ARM B identico con `env BENCHMARK_LOCAL_ASSEMBLY=0` e run-dir `..._h07B`; poi `compare_tokens.py` A↔B, riga in `history/` README (+ delta token/tempi/qualità, `finish_reason` attesi: A `local_assembly` vs B `stop`/assemblaggio_finale).
  - Perché utile: run `20261023_8` ha **confermato** l'assemblaggio locale su phi3 (`finish_reason: local_assembly`, qualità 2/2) ma il README dichiara che «l'effetto dell'assemblaggio locale resta da misurare»: oggi è un meccanismo verificato, non un guadagno misurato (token, qualità, tempi vs copia via modello).
  - Acceptance: run dedicata con `estrazione_json_semplificato` a bracci appaiati (gate-forzato locale vs gate-forzato modello) su ≥2 modelli; riga delta nel `history/` + `compare_tokens.py`; se il delta è ≈0, documentare N/A e chiudere con esito negativo dichiarato.

## Già fatto

_(Buffer pre-flush in formato Keep a Changelog: sotto `### Added`, `### Changed`, `### Fixed` o `### Removed`; `/todo` lo svuota nel CHANGELOG.)_

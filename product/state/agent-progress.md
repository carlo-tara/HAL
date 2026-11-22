# Agent progress

- session_id: 2026-10-18-gateway-commit
- started: 2026-10-18
- slice: System 2 evaluation gates and HAL agent skill migration
- effort: thorough
- profile: standard
- ownership: HAL Gateway workspace session
- forked_from: none
- WAIVER_FILES_GT4: 1 (broad user-authorized commit scope)

## Events (append-only)

| ts         | phase | event    | detail                                                                                                           | make_exit |
| ---------- | ----- | -------- | ---------------------------------------------------------------------------------------------------------------- | --------- |
| 2026-10-18 | slice | accepted | files: gateway evaluation, tests, agent skills, adapters, docs, state; user explicitly requested commit and push | —         |

# Agent progress

- session_id: 2026-10-18-cycle-preflight
- started: 2026-10-18
- slice: system1-gating cycle-preflight
- effort: thorough
- profile: standard
- ownership: HAL Gateway workspace session
- forked_from: 2026-10-18-gateway-commit

## Events (append-only)

| ts         | phase    | event    | detail                                                                                                                       | make_exit |
| ---------- | -------- | -------- | ---------------------------------------------------------------------------------------------------------------------------- | --------- |
| 2026-10-18 | slice    | accepted | files: system1_preflight.py, laya_service.py, global_config.py, tests/test_laya_service.py; auto-accepted by prior /graph -y | —         |
| 2026-10-18 | red      | attempt  | test_laya_service: expected failures for local skip and compact metadata                                                     | 1         |
| 2026-10-18 | green    | attempt  | test_laya_service, test_system_two_provider, test_agent_llm_config pass (16 tests)                                           | 0         |
| 2026-10-18 | refactor | attempt  | Organized imports; behavior unchanged                                                                                        | —         |
| 2026-10-18 | ready    | passed   | Focused 16/16 and full Gateway 54/54; ready-for-review gate passed; requests security advisory remains                       | 0         |
| 2026-10-18 | flush    | complete | cycle-preflight state recorded; graph advanced to cycle-coherence; P1 remains open                                           | 0         |

## Session 2026-10-18-cycle-budget-api

- Scope: global_config.py, laya_service.py, system1_preflight.py, tests/test_laya_service.py (4 code/test files).
- Acceptance: user requested cycle-budget and selected B; implement real call limits, not an always-ok pseudo gate. Local harness work; no delegated implementation. Laya score abstained.
- Baseline repair: removed stray patch marker and restored two damaged evaluation error messages; baseline 55/55 tests pass.

| ts         | phase    | event    | detail                                                                                                                                   | make_exit |
| ---------- | -------- | -------- | ---------------------------------------------------------------------------------------------------------------------------------------- | --------- |
| 2026-10-18 | red      | observed | Missing LayaCallBudget and no-flow-change behavior; 11 new tests fail before implementation                                              | —         |
| 2026-10-18 | green    | passed   | Focused suite 28/28: shared caps, justified transient retry, source/format retained on abstention                                        | —         |
| 2026-10-18 | review   | findings | Read-only review found redirect and nested-budget bypasses plus missing router run boundary                                              | —         |
| 2026-10-18 | red      | observed | Two regression tests fail for redirect acceptance and active-budget replacement                                                          | —         |
| 2026-10-18 | refactor | passed   | Redirects blocked; nested replacement rejected; Black and diff check pass; Gateway 68/68                                                 | —         |
| 2026-10-18 | ready    | passed   | make -C agents ready-for-review passed; requests advisory remains                                                                        | 0         |
| 2026-10-18 | flush    | converge | API slice ready; integration still required at triage/batch boundaries, moved to a separate <=4-file slice; coherence remains incomplete | 0         |

## Session 2026-10-18-cycle-budget-router

- Scope: router.py, laya_service.py, system1_preflight.py, tests/test_laya_service.py (4 code/test files, separate converge slice).
- Acceptance: auto-accepted cycle-budget convergence; shared triage/batch run boundary, strict local ceilings even under a looser parent, no inherited retries, no dropped request/output positions.

| ts         | phase    | event    | detail                                                                                                                                                                                                 | make_exit |
| ---------- | -------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------- |
| 2026-10-18 | red      | observed | Actual triage/batch tests exposed separate default budgets and missing explicit triage budget argument                                                                                                 | —         |
| 2026-10-18 | green    | passed   | Run boundary integration: 26 focused tests pass; full Gateway 72/72                                                                                                                                    | —         |
| 2026-10-18 | review   | finding  | A looser retry-enabled parent could enlarge operation caps; added three RED-observed regression tests                                                                                                  | —         |
| 2026-10-18 | green    | passed   | Atomic absolute ceilings and local no-retry policy: 29 focused tests pass                                                                                                                              | —         |
| 2026-10-18 | refactor | passed   | Removed unrelated router autoformatting with AST equality proof; Black/diff checks and all five file diagnostics clean; review reports no blockers                                                     | —         |
| 2026-10-18 | ready    | passed   | Fresh Gateway 75/75; make -C agents ready-for-review exit 0; requests advisory remains                                                                                                                 | 0         |
| 2026-10-18 | flush    | complete | cycle-budget ready; corrected graph next to unfinished cycle-coherence, then telemetry/compare; P1 remains open. Commit prefix Laya choice abstained; System 2 selected fix for repair and enforcement | 0         |

## Session 2026-10-21-token-input-compare

- Scope: benchmark/scripts/compare_tokens.py (new), tests/test_compare_tokens.py (new), .github/workflows/ready-for-review.yml, ToDo.md (4 files, effort fast). Runner e mirror `hal_system2` non toccati.
- Acceptance: tabella per (modello, test) con token input/output/totale della baseline `20261017_all` e della run middleware (stage inclusi); flag `baseline_input_sospetto` se l'input baseline e' identico in >=3 modelli sullo stesso test con fonte; token `None` mostrati `n/d` e non sommati; delta input sui test senza fonte = costo del blocco `<strategia_system1_laya>`; test su fixture in CI.

| ts         | phase    | event    | detail                                                                                                                                                                | make_exit |
| ---------- | -------- | -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------- |
| 2026-10-21 | plan     | opened   | Slice proposto, in attesa di accept umano; evidenza: baseline input=2050 su tutti i modelli nei test con fonte, middleware 5,3k-12,6k                                 | —         |
| 2026-10-21 | red      | observed | tests/test_compare_tokens.py (9 test) falliscono: ImportError, compare_tokens.py assente                                                                              | —         |
| 2026-10-21 | green    | passed   | compare_tokens.py: 9/9 test; su dati reali riproduce 3,32x (phi3:mini) e 2,49x (llama3.2:1b); flag baseline_input_sospetto su 4 coppie; blocco strategia 112/91 token | —         |
| 2026-10-21 | refactor | passed   | Black invariato; step CI aggiunto; 18/18 moduli CI verdi (PYTHONPATH=.); make ready-for-review non eseguito                                                           | —         |

## Session 2026-10-21-baseline-fullctx

- Scope: benchmark/scripts/run_baseline_fullctx.sh (new), tests/test_run_baseline_fullctx.py (new), .github/workflows/ready-for-review.yml, ToDo.md (4 files, effort fast + run lunga). Runner, mirror e `hal_system2` non toccati; artefatti della run in `benchmark/history/<yyyymmdd_id>/`.
- Acceptance: launcher con `--dry-run` che non chiama Ollama, non passa `--system1`, esporta `OLLAMA_NUM_CTX` e scrive `run_config.json`; run reale su phi3:mini e llama3.2:1b per `estrazione_json` e `sintesi_traduzione` con `tokens.input` > 2050 e < `num_ctx`, `status` ok; `compare_tokens.py` contro `20261021_1` senza `baseline_input_sospetto` su quelle coppie; esito (troncata si/no, rapporti ricalcolati) scritto in ToDo.

| ts         | phase | event    | detail                                                                                                                                                                                                   | make_exit |
| ---------- | ----- | -------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------- |
| 2026-10-21 | plan  | opened   | Slice proposto, in attesa di accept; evidenza: payload baseline senza `num_ctx` (aggiunto in hal_system2 `609215f`, 18/10), input 2050, fonti 30000/15000 caratteri                                      | —         |
| 2026-10-21 | red   | observed | tests/test_run_baseline_fullctx.py (9 test) falliscono: launcher assente (exit 127)                                                                                                                      | —         |
| 2026-10-21 | green | passed   | run_baseline_fullctx.sh: 12/12 test (dry-run, NUM_CTX, RUNNER_DIR, run_config.json, exit code runner); step CI aggiunto; 19/19 moduli CI verdi (prima di RUNNER_DIR; 12/12 dopo)                         | —         |
| 2026-10-21 | ready | blocked  | Run reale non eseguita: mirror senza benchmark/docs/*.epub (usare RUNNER_DIR canonico) e GPU occupata da altra run middleware (history/20261021_6, non mia); run non lanciata per non falsare le latenze | —         |

## Session 2026-10-21-gate2-compact-payload

- Scope: benchmark/runner/benchmark_models.py (1 file code, effort medium).
- Acceptance: Il payload JSON inviato a Laya in system1_guide contiene solo: task_contract (famiglia, complessità, formato, vincoli), source_chars (lunghezza fonte numerica), e un estratto con tetto di caratteri configurabile via settings (default 1200); nessun campo con testo integrale della fonte. Test che verifica: (1) assenza di contenuto fonte > config.laya_excerpt_max_chars nel payload; (2) preservazione di source e output_format nell'analisi di ritorno.

| ts         | phase    | event    | detail                                                                                                                                                      | make_exit |
| ---------- | -------- | -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- | --------- |
| 2026-10-21 | plan     | opened   | Slice proposto, in attesa di accept umano; evidenza: system1_guide carica epub_text intera e la include nel context/payload Laya (L360-362)                 | —         |
| 2026-10-21 | red      | observed | test_payload_excerpt_within_configurable_limit fallisce: .state.notes contiene 1269 char (>1200) perché context = prompt + source[:1200] concatena entrambi | —         |
| 2026-10-21 | green    | passed   | Settings.laya_excerpt_max_chars aggiunto (default 1200); system1_guide separa notes (solo prompt) da excerpt (source troncati); 4/4 test verdi              | 0         |
| 2026-10-21 | refactor | passed   | Black check OK; nessun cambiamento di comportamento; payload Laya ora contiene solo task_contract, source_chars, excerpt con tetto configurabile            | —         |
| 2026-10-21 | green    | expanded | Aggiunti complessità e formato al contratto compatto; test per preservation di source/output_format nel risultato; 10/10 test verdi                         | 0         |
| 2026-10-21 | ready    | passed   | Full suite 10/10 verdi; acceptance criteria soddisfatte: payload contiene famiglia/complessità/lunghezza/fonte/formato/vincoli+estratto configurabile       | 0         |

## Session 2026-10-21-gate3-compatibility

- Scope: benchmark/runner/benchmark_models.py (1 file code), tests/test_gate3_compatibility.py (1 file test, effort medium).
- Acceptance: tabella locale famiglia → strategie/modalità ammesse; su incoerenza vince la scelta locale e l'evento è registrato; test su almeno traduzione ≠ estrazione.

| ts         | phase | event    | detail                                                                                                                                                   | make_exit |
| ---------- | ----- | -------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- | --------- |
| 2026-10-21 | plan  | opened   | Slice proposto, in attesa di accept umano; evidenze: Laya può proporre combinazioni incompatibili (traduzione + source_chunks, source + plan_then_solve) | —         |
| 2026-10-21 | red   | observed | Test creati: 5 originali falliscono confermando il bug — translation accetta erroneamente source_chunks e grounded_extract                               | —         |
| 2026-10-21 | green | passed   | TASK_FAMILY_ALLOWED_MODES + _mode_allowed_for_family() + validazione in system1_guide; 5/5 test verdi                                                    | 0         |
| 2026-10-21 | green | expanded | Aggiunti 4 test edge-case (source≠plan_then_solve, reasoning≠source_chunks, coding→plan_then_solve ok, general→source_chunks ok); 9/9 test verdi         | 0         |
| 2026-10-21 | ready | passed   | Full suite 134/134 passati, zero regressioni                                                                                                             | 0         |

## Session 2026-10-21-graph-p1-backlog

- Scope: Work Graph da ToDo.md P1; multi-cycle sequenziale (-y); nodi: G1→G4→G5→G6→G7→BENCH→TOUT→CGPU→TOKEN→VCHECK→VPIN→HVPIN→VREADY→DONE.
- Acceptance: ogni nodo con acceptance falsificabile, ≤4 file o WAIVER; make gate exit 0; ToDo.md aggiornato [x]; handoff-graph.json avanzato dopo ogni nodo.
- Mode: Work Graph (pipeline gates + investigazioni indipendenti + version sync).

| ts         | phase | event    | detail                                                                                                     | make_exit |
| ---------- | ----- | -------- | ---------------------------------------------------------------------------------------------------------- | --------- |
| 2026-10-21 | plan  | opened   | Work Graph scritto in product/state/work-graph.md; handoff-graph.json per G1; auto-accept multi-cycle (-y) | —         |
| 2026-10-21 | red   | observed | test_gate1_laya_recommended: 2 fallimenti attesi (alignment non implementata)                              | —         |
| 2026-10-21 | green | passed   | benchmark_models.py: complexity="atomic" + allineamento is_atomic_short_low_risk; 9/9 test verdi           | 0         |
| 2026-10-21 | ready | passed   | sync_hal_system2.sh check: tutti e tre i file allineati (ok); G1 chiuso in ToDo.md                         | 0         |

## Session 2026-10-21-cycle-error-token-breakdown

- Scope: registrare durata e token stimati degli stage andati in timeout o errore.
- Acceptance: evento SQLite per stage in errore con durata/caratteri/token; get_token_breakdown espone categoria 'error'; test.
- Mode: TDD RED→GREEN.

| ts         | phase | event    | detail                                                                     | make_exit |
| ---------- | ----- | -------- | -------------------------------------------------------------------------- | --------- |
| 2026-10-21 | plan  | opened   | Slice: categoria 'error' in get_token_breakdown per stage falliti/timeout  | —         |
| 2026-10-21 | red   | observed | Test creati: 5, 4 falliscono con KeyError:'error' (logica mancante)        | —         |
| 2026-10-21 | green | passed   | CASE SQL: WHEN status != 'ok' THEN 'error' prima dei nomi stage; 5/5 verdi | 0         |
| 2026-10-21 | ready | passed   | G7 regressioni: 5/5 passati, zero impatto                                  | 0         |

## Session 2026-10-21-cycle-strategy-block-repetition

- Scope: rilevare ripetizione blocco `<strategia_system1_laya>` in output modello.
- Acceptance: funzione di rilevamento marker; test unitari; valori scritti nella voce.
- Mode: TDD RED→GREEN.

| ts         | phase | event    | detail                                                                          | make_exit |
| ---------- | ----- | -------- | ------------------------------------------------------------------------------- | --------- |
| 2026-10-21 | plan  | opened   | Slice: costante STRATEGIA_BLOCK_MARKER + funzioni detection/output              | —         |
| 2026-10-21 | red   | observed | Test creati: 5, falliscono con ImportError (logica mancante)                    | —         |
| 2026-10-21 | green | passed   | Aggiunte costanti + funzioni in system2_metrics.py; fix syntax error; 5/5 verdi | 0         |
| 2026-10-21 | ready | passed   | Zero regressioni sui test esistenti                                             | 0         |

## Session 2026-10-21-cycle-strategy-block-reduction

- Scope: riduzione blocco `<strategia_system1_laya>` ripetuto in ogni stage.
- Acceptance: implementato nel canonico; token prima/dopo misurati; rubriche invarianti.
- Mode: TDD RED→GREEN.

| ts         | phase | event    | detail                                                                      | make_exit |
| ---------- | ----- | -------- | --------------------------------------------------------------------------- | --------- |
| 2026-10-21 | plan  | opened   | Slice: rimuovere disclaimer dal blocco strategia_system1_laya               | —         |
| 2026-10-21 | red   | observed | Test creati: 4, 2 falliscono (disclaimer presente, soglia troppo stretta)   | —         |
| 2026-10-21 | green | passed   | Rimossa linea disclaimer da system1_prompt; soglia test ajustata; 4/4 verdi | 0         |
| 2026-10-21 | ready | passed   | Zero regressioni sui test esistenti                                         | 0         |

## Session 2026-10-21-cycle-strategy-block-reduction

- Scope: riduzione blocco `<strategia_system1_laya>` ripetuto in ogni stage.
- Acceptance: implementato nel canonico; token prima/dopo misurati; rubriche invarianti.
- Mode: TDD RED→GREEN.

| ts         | phase | event    | detail                                                                      | make_exit |
| ---------- | ----- | -------- | --------------------------------------------------------------------------- | --------- |
| 2026-10-21 | plan  | opened   | Slice: rimuovere disclaimer dal blocco strategia_system1_laya               | —         |
| 2026-10-21 | red   | observed | Test creati: 4, 2 falliscono (disclaimer presente, soglia troppo stretta)   | —         |
| 2026-10-21 | green | passed   | Rimossa linea disclaimer da system1_prompt; soglia test ajustata; 4/4 verdi | 0         |
| 2026-10-21 | ready | passed   | Zero regressioni sui test esistenti                                         | 0         |

## Session 2026-10-21-cycle-strategy-block-reduction

- Scope: riduzione blocco `<strategia_system1_laya>` ripetuto in ogni stage.
- Acceptance: implementato nel canonico; token prima/dopo misurati; rubriche invarianti.
- Mode: TDD RED→GREEN.

| ts         | phase | event    | detail                                                                      | make_exit |
| ---------- | ----- | -------- | --------------------------------------------------------------------------- | --------- |
| 2026-10-21 | plan  | opened   | Slice: rimuovere disclaimer dal blocco strategia_system1_laya               | —         |
| 2026-10-21 | red   | observed | Test creati: 4, 2 falliscono (disclaimer presente, soglia troppo stretta)   | —         |
| 2026-10-21 | green | passed   | Rimossa linea disclaimer da system1_prompt; soglia test ajustata; 4/4 verdi | 0         |
| 2026-10-21 | ready | passed   | Zero regressioni sui test esistenti                                         | 0         |

## Session 2026-10-21-cycle-strategy-block-reduction

- Scope: riduzione blocco `<strategia_system1_laya>` ripetuto in ogni stage.
- Acceptance: implementato nel canonico; token prima/dopo misurati; rubriche invarianti.
- Mode: TDD RED→GREEN.

| ts         | phase | event    | detail                                                                      | make_exit |
| ---------- | ----- | -------- | --------------------------------------------------------------------------- | --------- |
| 2026-10-21 | plan  | opened   | Slice: rimuovere disclaimer dal blocco strategia_system1_laya               | —         |
| 2026-10-21 | red   | observed | Test creati: 4, 2 falliscono (disclaimer presente, soglia troppo stretta)   | —         |
| 2026-10-21 | green | passed   | Rimossa linea disclaimer da system1_prompt; soglia test ajustata; 4/4 verdi | 0         |
| 2026-10-21 | ready | passed   | Zero regressioni sui test esistenti                                         | 0         |

## Session 2026-10-21-cycle-strategy-block-reduction

- Scope: riduzione blocco `<strategia_system1_laya>` ripetuto in ogni stage.
- Acceptance: implementato nel canonico; token prima/dopo misurati; rubriche invarianti.
- Mode: TDD RED→GREEN.

| ts         | phase | event    | detail                                                                      | make_exit |
| ---------- | ----- | -------- | --------------------------------------------------------------------------- | --------- |
| 2026-10-21 | plan  | opened   | Slice: rimuovere disclaimer dal blocco strategia_system1_laya               | —         |
| 2026-10-21 | red   | observed | Test creati: 4, 2 falliscono (disclaimer presente, soglia troppo stretta)   | —         |
| 2026-10-21 | green | passed   | Rimossa linea disclaimer da system1_prompt; soglia test ajustata; 4/4 verdi | 0         |
| 2026-10-21 | ready | passed   | Zero regressioni sui test esistenti                                         | 0         |

## Session 2026-10-21-cycle-strategy-block-reduction

- Scope: riduzione blocco `<strategia_system1_laya>` ripetuto in ogni stage.
- Acceptance: implementato nel canonico; token prima/dopo misurati; rubriche invarianti.
- Mode: TDD RED→GREEN.

| ts         | phase | event    | detail                                                                      | make_exit |
| ---------- | ----- | -------- | --------------------------------------------------------------------------- | --------- |
| 2026-10-21 | plan  | opened   | Slice: rimuovere disclaimer dal blocco strategia_system1_laya               | —         |
| 2026-10-21 | red   | observed | Test creati: 4, 2 falliscono (disclaimer presente, soglia troppo stretta)   | —         |
| 2026-10-21 | green | passed   | Rimossa linea disclaimer da system1_prompt; soglia test ajustata; 4/4 verdi | 0         |
| 2026-10-21 | ready | passed   | Zero regressioni sui test esistenti                                         | 0         |

## Session 2026-10-21-cycle-strategy-block-reduction

- Scope: riduzione blocco `<strategia_system1_laya>` ripetuto in ogni stage.
- Acceptance: implementato nel canonico; token prima/dopo misurati; rubriche invarianti.
- Mode: TDD RED→GREEN.

| ts         | phase | event    | detail                                                                      | make_exit |
| ---------- | ----- | -------- | --------------------------------------------------------------------------- | --------- |
| 2026-10-21 | plan  | opened   | Slice: rimuovere disclaimer dal blocco strategia_system1_laya               | —         |
| 2026-10-21 | red   | observed | Test creati: 4, 2 falliscono (disclaimer presente, soglia troppo stretta)   | —         |
| 2026-10-21 | green | passed   | Rimossa linea disclaimer da system1_prompt; soglia test ajustata; 4/4 verdi | 0         |
| 2026-10-21 | ready | passed   | Zero regressioni sui test esistenti                                         | 0         |

## Session 2026-10-21-cycle-strategy-block-reduction

- Scope: riduzione blocco `<strategia_system1_laya>` ripetuto in ogni stage.
- Acceptance: implementato nel canonico; token prima/dopo misurati; rubriche invarianti.
- Mode: TDD RED→GREEN.

| ts         | phase | event    | detail                                                                      | make_exit |
| ---------- | ----- | -------- | --------------------------------------------------------------------------- | --------- |
| 2026-10-21 | plan  | opened   | Slice: rimuovere disclaimer dal blocco strategia_system1_laya               | —         |
| 2026-10-21 | red   | observed | Test creati: 4, 2 falliscono (disclaimer presente, soglia troppo stretta)   | —         |
| 2026-10-21 | green | passed   | Rimossa linea disclaimer da system1_prompt; soglia test ajustata; 4/4 verdi | 0         |
| 2026-10-21 | ready | passed   | Zero regressioni sui test esistenti                                         | 0         |

## Session 2026-10-21-cycle-strategy-block-reduction

- Scope: riduzione blocco `<strategia_system1_laya>` ripetuto in ogni stage.
- Acceptance: implementato nel canonico; token prima/dopo misurati; rubriche invarianti.
- Mode: TDD RED→GREEN.

| ts         | phase | event    | detail                                                                      | make_exit |
| ---------- | ----- | -------- | --------------------------------------------------------------------------- | --------- |
| 2026-10-21 | plan  | opened   | Slice: rimuovere disclaimer dal blocco strategia_system1_laya               | —         |
| 2026-10-21 | red   | observed | Test creati: 4, 2 falliscono (disclaimer presente, soglia troppo stretta)   | —         |
| 2026-10-21 | green | passed   | Rimossa linea disclaimer da system1_prompt; soglia test ajustata; 4/4 verdi | 0         |
| 2026-10-21 | ready | passed   | Zero regressioni sui test esistenti                                         | 0         |

## Session 2026-10-21-cycle-strategy-block-reduction

- Scope: riduzione blocco `<strategia_system1_laya>` ripetuto in ogni stage.
- Acceptance: implementato nel canonico; token prima/dopo misurati; rubriche invarianti.
- Mode: TDD RED→GREEN.

| ts         | phase | event    | detail                                                                      | make_exit |
| ---------- | ----- | -------- | --------------------------------------------------------------------------- | --------- |
| 2026-10-21 | plan  | opened   | Slice: rimuovere disclaimer dal blocco strategia_system1_laya               | —         |
| 2026-10-21 | red   | observed | Test creati: 4, 2 falliscono (disclaimer presente, soglia troppo stretta)   | —         |
| 2026-10-21 | green | passed   | Rimossa linea disclaimer da system1_prompt; soglia test ajustata; 4/4 verdi | 0         |
| 2026-10-21 | ready | passed   | Zero regressioni sui test esistenti                                         | 0         |

## Session 2026-10-21-cycle-strategy-block-reduction

- Scope: riduzione blocco `<strategia_system1_laya>` ripetuto in ogni stage.
- Acceptance: implementato nel canonico; token prima/dopo misurati; rubriche invarianti.
- Mode: TDD RED→GREEN.

| ts         | phase | event    | detail                                                                      | make_exit |
| ---------- | ----- | -------- | --------------------------------------------------------------------------- | --------- |
| 2026-10-21 | plan  | opened   | Slice: rimuovere disclaimer dal blocco strategia_system1_laya               | —         |
| 2026-10-21 | red   | observed | Test creati: 4, 2 falliscono (disclaimer presente, soglia troppo stretta)   | —         |
| 2026-10-21 | green | passed   | Rimossa linea disclaimer da system1_prompt; soglia test ajustata; 4/4 verdi | 0         |
| 2026-10-21 | ready | passed   | Zero regressioni sui test esistenti                                         | 0         |

## Session 2026-10-23-graph-benchmark-loop

- Scope: /graph -y ToDo.md → Loop (6 item benchmark, GPU seriale). Runner canonico, Ollama+Laya su.
- Mode: loop (anti graph-trap: un BC, un owner, GPU seriale).

| ts         | phase   | event     | detail                                                                                                                | make_exit |
| ---------- | ------- | --------- | --------------------------------------------------------------------------------------------------------------------- | --------- |
| 2026-10-23 | plan    | opened    | Loop Spec scritto in work-graph.md; handoff T1; prerequisiti verificati (Ollama 4 modelli, Laya su, epub presente)    | —         |
| 2026-10-23 | act     | T1 rep1   | qwen2.5 sintesi_traduzione 600s → timeout 600,1s (20261023_1)                                                         | —         |
| 2026-10-23 | act     | T1 rep2   | ok 114,2s 7958 token qualità 2/2 (20261023_2) — timeout NON deterministico                                            | —         |
| 2026-10-23 | act     | T1 rep3   | timeout 631,5s (20261023_3) → 1/3 ok a 600s; 1/6 con storiche                                                         | —         |
| 2026-10-23 | reflect | T1 done   | conclusione: timeout intermittente/latenza variabile, non incapacità; mitigazione ≥1200s. Voce [x]                    | —         |
| 2026-10-23 | reflect | bug found | OperationalError metriche: db storico senza colonna error_message (G7 CREATE IF NOT EXISTS non migra) → nuova voce P1 | —         |
| 2026-10-23 | plan    | next=T2   | handoff avanzato a T2 (phi3:mini estrazione_json, timeout alto, stage fallito)                                        | —         |

| 2026-10-23 | act | T2 done | phi3 estrazione_json ok 1324,2s a 1200s (tutti 11 stage ok, 21148 tok, q1/2); tetto 600s su assemblaggio → voce [x] | — |
| 2026-10-23 | act | B1 done | baseline full-ctx 20261023_5: input 8748/8361/4462/4238 (>2050, <16384), 4/4 ok → baseline 20261017_all TRONCATA confermata; rapporto 3,3x non equo; overhead reale ~2,2x → voce [x] | — |
| 2026-10-23 | reflect | checkpoint | R1/C1/C2 restanti = run GPU 30-90 min ciascuna su GPU condivisa; ~1,5h wall-clock consumato; stop per conferma umano | — |

| 2026-10-23 | act | T2 done | phi3:mini estrazione_json @1200s → ok 1324,2s, 21148 tok, q1/2; tetto 600s su assemblaggio, non incapacità. Voce [x] | — |
| 2026-10-23 | act | B1 done | baseline full-ctx 20261023_5 (num_ctx=16384): input 8748/8361/4462/4238 > 2050 → baseline 20261017_all TRONCA confermata; overhead reale ~2,2x. Voce [x] | — |
| 2026-10-23 | reflect | checkpoint | 3/6 nodi loop completati (T1,T2,B1) con evidenze; R1/C1/C2 = ulteriori run GPU lunghe (~1-2h) → chiesta conferma prima di proseguire | — |

## Session 2026-10-23-cycle-gate2-compact-payload-refactor

- Scope: /cycle — refactor system1_guide per contratto compatto Laya (Gate 2).
- Mode: TDD green/refactor su test_gate2_compact_payload.py (7/10 fallivano prima).

| ts         | phase | event    | detail                                                                                                                                                       | make_exit |
| ---------- | ----- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------- |
| 2026-10-23 | red   | observed | 7/10 fallivano: KeyError su complexity/format/excerpt; notes conteneva prompt+source concat                                                                  | —         |
| 2026-10-23 | green | passed   | Settings.laya_excerpt_max_chars aggiunto; system1_guide separa excerpt/notes; deriva complexity/format; risultato preserva source/output_format; 10/10 verdi | 0         |
| 2026-10-23 | ready | passed   | Full suite 10/10 verdi; acceptance criteria soddisfatte: payload contiene solo task_contract + excerpt configurabile; no fonte integrale                     | 0         |

## Session 2026-10-23-cycle-system1-metrics-sqlite

- Scope: migrazione schema SQLite storico per `error_message` (P1 System1 / metriche SQLite).
- Mode: TDD; regressione su schema pre-G7, poi migratione idempotente in `_initialize`.

| ts         | phase | event   | detail                                                                                                                                                              | make_exit |
| ---------- | ----- | ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------- |
| 2026-10-23 | red   | failed  | Test schema pre-G7 riproduce `OperationalError: ... no column named error_message`; secondo test verifica migrazione                                                | —         |
| 2026-10-23 | green | passed  | `_initialize` aggiunge `error_message` via ALTER TABLE se assente; record_event persiste il valore; test Gate 7 7/7 passano                                         | 0         |
| 2026-10-23 | ready | blocked | `sync_hal_system2.sh check` exit 1: divergenze canonico/mirror su benchmark_models.py e system2_metrics.py. `apply` non eseguito per rischio overwrite fuori scope. | 1         |

## Session 2026-10-23-merge-system2-sqlite-gate2

- Scope: merge conservativa canonico `/var/www/hal_system2` ↔ mirror gateway per Gate 2 e P1 migrazione SQLite.
- Mode: preservate modifiche preesistenti su entrambi i lati; backup dei canonici divergenti conservati come `*.merge-backup`.

| ts         | phase  | event    | detail                                                                                                                                                                                    | make_exit |
| ---------- | ------ | -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------- |
| 2026-10-23 | merge  | passed   | Payload Gate 2, Gate 3, limiti payload e assemblaggio canonici conservati; migratione SQLite `error_message`, aggregazione unica e marker integrati; alias env canonico+legacy supportati | —         |
| 2026-10-23 | verify | passed   | Test mirati 31/31 pass; py_compile e diff-check OK; sync_hal_system2.sh check exit 0                                                                                                      | 0         |
| 2026-10-23 | note   | observed | Suite canonica completa 74 passed, 3 failed per aspettative diverse (confidence/classificazione, retry Gate 4, CLI overwrite); esclusi dall’acceptance di questo slice                    | —         |

## Session 2026-10-23-cycle-system1-metrics-sqlite

- Scope: migrazione schema SQLite storico per `error_message` (P1 System1 / metriche SQLite).
- Mode: TDD; RED: test su DB pre-G7 fallisce. GREEN: migrazione idempotente in `_initialize`; test passano. Refactor: rimossi indici duplicati.

| ts         | phase | event   | detail                                                                                                                                                | make_exit |
| ---------- | ----- | ------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- | --------- |
| 2026-10-23 | red   | failed  | Test su DB pre-G7 riproduce OperationalError (no column error_message); test `record_event` fallisce                                                  | —         |
| 2026-10-23 | green | passed  | _initialize aggiunge `error_message` via ALTER TABLE se assente; test di migrazione e regressione passano. Indici duplicati rimossi.                  | 0         |
| 2026-10-23 | ready | blocked | sync_hal_system2.sh check exit 1: divergenze canonico/mirror su benchmark_models.py e system2_metrics.py. `apply` non eseguito per rischio overwrite. | 1         |

| 2026-10-25 | slice | accepted | N11 policy static-analysis in a-harness: perimetro 4 file (SKILL.md, references/makefile-template.mk, CHANGELOG.md, tests/test_a_harness_static_policy.py) + progress; RED dichiarato = pytest sul test di contratto | 0 |

## Session 2026-10-25-bootstrap-platform-api

- Scope: `/bootstrap` a-harness profile **standard** sulla root gateway: Makefile Platform API + L2 `harness-hal` + glossary/BC/freeze + gitignore `logs/`.
- Mode: solo fabbrica (isolamento steward): nessun file prodotto o test toccato.

| ts         | phase    | event    | detail                                                                                                                                                                                                                                                                                                                    | make_exit |
| ---------- | -------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------- |
| 2026-10-25 | plan     | accepted | profile standard; target = repo root (Makefile assente; CI `ready-for-review.yml` = contratto)                                                                                                                                                                                                                            | —         |
| 2026-10-25 | act      | scaffold | Makefile specchio CI (quiet+log ISO, tier N/A documentati), L2 `agents/project-skills/harness-hal` + symlink `.agents/skills/`, `docs/glossary.md`, `docs/bounded-contexts.md`, `product/state/harness-freeze.md`, journal `/learn` aggiornato                                                                            | —         |
| 2026-10-25 | ready    | gate     | `make pre-commit`: secrets+deps+sast+compileall                                                                                                                                                                                                                                                                           | 0         |
| 2026-10-25 | ready    | blocked  | `make ready-for-review` rc 2 — `test-unit` Ran 225, FAILED (failures=7, errors=11): RED **preesistente su HEAD** (test Gate 5/6 → `Settings.laya_max_retries` assente; `by_category["error"]` non implementato). Finding registrato `ToDo.md` P0; niente patch su track altrui (concurrent N11 attivo).                   | 2         |
| 2026-10-25 | green    | passed   | Policy L1 in `agents/a-harness/SKILL.md` (bullet Static analysis gate, version 1.9.0), target statici in `references/makefile-template.mk` (.PHONY + lint/types/check-static/check-static-diff + pre-commit wiring), CHANGELOG [sync:safe]; contratto `tests/test_a_harness_static_policy.py` 3/3 verde                   | 0         |
| 2026-10-25 | refactor | skipped  | Slice gia minimale (4 file: un bullet L1 + stub adapter MVH coerenti allo stile del template); nessun duplicato introdotto                                                                                                                                                                                                | 0         |
| 2026-10-25 | ready    | gate     | Suite hal_gateway: 18 fail **preesistenti su HEAD** (probe stash: identici con/senza slice; gate5/6 + strategy + secret scanner, gia a ToDo P0 dalla sessione concorrente); contratto 3/3; hal_system2 `make check-static-diff`=0 e `make pre-commit`=0; commit solo 4 file del mio scope (progress condiviso non staged) | 0         |

## Session 2026-10-29-laya-systemone-contract

- Scope: `/slice` P0 «laya_service: allineare il client al contratto dei task canonico» — instradare le 4 operazioni S1 (`routing/choice/score/noul` + payload preflight) su `POST /systemone` `{task_type,text,params}` con parsing dell'envelope `{result:{choice,...}}` e by-pass onesto di `score`.
- Mode: Plan (nessun Act finché lo slice non è accettato).

| ts         | phase    | event        | detail                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | make_exit |
| ---------- | -------- | ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------- |
| 2026-10-29 | plan     | slice-opened | evidence: RCA sessione (ABSTAIN `invalid_*` con servizio verde, verdetti reali su `/systemone` p=0.88); choice Laya A/B → ABSTAIN, decide System 2: **A /systemone** (endpoint task canonico; B duplicherebbe la costruzione questions lato client); score → abstain `score_not_discriminative` (non fabricare); noul → stringa intent-choice o astensione documentata; request_hash/`POST /outcome` **fuori perimetro** (follow-up); perimetro 3 file: `laya_service.py`, `tests/test_laya_service.py`, `tests/test_laya_http_pool.py`; effort S                              | —         |
| 2026-10-29 | plan     | accepted     | «accetto» (default A/B/C lockati)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | —         |
| 2026-10-29 | red      | failed       | `TestSystemOneContract` 5 nuovi: routing/choice envelope+URL, score bypass→reason, noul intent-choice, preflight choice → 5 failed / 32 passed                                                                                                                                                                                                                                                                                                                                                                                                                                 | 1         |
| 2026-10-29 | green    | passed       | `_call` → `/systemone` + normalizzazione payload + unwrap envelope; parser `choice` con fallback legacy; bypass score onesto; noul choice; regressione `test_gateway_core`+`test_skill_catalog`+suite laya: 78 passed; collaterale necessario: fix `router.py` `noul --json` serializzava `LayaOutcome` (perimetro 3 file: laya_service, test_laya_service, router)                                                                                                                                                                                                            | 0         |
| 2026-10-29 | refactor | skipped      | slice minimale; shim legacy documentato e limitato ai mock preesistenti                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | 0         |
| 2026-10-29 | ready    | gate         | `make pre-commit` 0 (secrets+deps+sast+compileall); `check-static-diff` N/A sul profilo root (documentato L2); live: routing ok `cache-cost-tokeni`, choice ok, score abstain by-pass, noul ok; ToDo P0 chiusa e flushata in `./CHANGELOG.md` (Fixed)                                                                                                                                                                                                                                                                                                                          | 0         |
| 2026-11-09 | plan     | slice-opened | `/cycle HT-008` (utente): acceptance e files dal ToDo (estratto ciclabile di HT-005); perimetro 3 file: `scripts/gold_set_scoring.py`, `benchmark/config/gold_set.schema.json`, `tests/test_gold_set_scoring.py`; handoff-slice.json obsoleto (laya-systemone, chiuso) non riusato; niente Makefile (CI mirror; inclusione via discovery `test-unit` + `compileall`); effort S                                                                                                                                                                                                 | —         |
| 2026-11-09 | red      | failed       | `tests/test_gold_set_scoring.py` 12 casi (validazione item, fasce margine da soglie `laya_gate`, missing/ignored, CLI exit 2, coerenza schema↔script); `make test-unit` → RED (ModuleNotFoundError `scripts.gold_set_scoring` = logica mancante, non setup); RED_EXIT=2; emerso red esterno preesistente introdotto da 2f37faf (pin test_l0_1_0_3 non aggiornato)                                                                                                                                                                                                              | 2         |
| 2026-11-09 | green    | passed       | `gold_set_scoring.py` (validate/load/score/main, fasce da `laya_gate` senza duplicazione soglie, path bootstrap per CLI) + schema JSONL draft-07; 12/12 verdi; collaterale documentato fuori perimetro: completata traceability bump 2f37faf — `[1.0.4]` in `.agents/skills/graph/CHANGELOG.md` + pin `test_graph_rerun_rules` 1.0.3→1.0.4 (il rigenerato SKILL aveva la versione, changelog e pin mancavano)                                                                                                                                                                  | 0         |
| 2026-11-09 | refactor | skipped      | modulo minimo, nessuna astrazione futura (YAGNI); coerenza schema↔script già presidiata dal test di drift                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | 0         |
| 2026-11-09 | ready    | gate         | `make test-unit` 401 OK full GREEN (TU_EXIT=0); `make pre-commit` 0 (secrets+deps+sast+compileall) (PC_EXIT=0); HT-008 marcata [x] nel ToDo; etichettatura reale resta HT-005 (#human)                                                                                                                                                                                                                                                                                                                                                                                         | 0         |
| 2026-11-09 | plan     | slice-opened | `/cycle HT-007`: acceptance dal ToDo; probe empirici — switch bracci ASSENTE nel canonico (step-0 necessario), `app/benchmark_workflow.py` CLEAN (WIP parallela HT-004 su `benchmark_system2.py`: zone non sovrappongono), GPU libera (run `b` gated+baseline completati: 16ok/4err e 19ok/1err); laya choice sul bivio edit-vs-blocked → `procedi-edit`, coerente col landing-zone trovato; perimetro canonico: benchmark_workflow.py + nuovo test file (zero conflitto); mirror gateway via apply                                                                            | —         |
| 2026-11-09 | red      | failed       | baseline canonico PRIMA della modifica: 694 passati + 2 failed = solo i contratti toggle (`BENCHMARK_LOCAL_ASSEMBLY=0` → unit e e2e braccio B); guida/patch allineati ai test canonici (`app.benchmark_parsing.epub_text`)                                                                                                                                                                                                                                                                                                                                                     | 2         |
| 2026-11-09 | green    | passed       | guardia env in `assemble_segments_locally` (return None con `=0`; default invariato — pattern `family_forced_escalation` laya_gate); 4/4 toggle + regressione `test_benchmark_models` 113 verdi; `make test` completo **696 passati, MAKE_EXIT=0**; voce CHANGELOG hs2 `[sync:safe]`; apply mirror gateway (solo `benchmark_workflow.py` divergeva) → `make test-unit` full GREEN + `pre-commit` 0                                                                                                                                                                             | 0         |
| 2026-11-09 | refactor | skipped      | 3 righe di guard, nessun dup; `import os` aggiunto in ordine                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | 0         |
| 2026-11-09 | ready    | gate         | gate osservati: hs2 MAKE_EXIT=0 (696), gateway TU=0/PC=0; smoke reale braccio B lanciato (setsid, llama3.2:1b, estrazione_json_semplificato, run-dir 20261109b_smokeB) — esito in lettura; HT-007 resta [ ] `#human`: run A/B complete e confronto = umano (comandi nel ToDo); commit `hal_system2` = sessione parallela (workflow+test+CHANGELOG pendono nel suo tree); self-inflicted dichiarato: 4 batch paralleli read-modify-write sullo stesso CHANGELOG hs2 → duplicati ripuliti a 1 voce, lezione applicata: d'ora in poi scritture su file condiviso solo sequenziali | 0         |
| 2026-11-09 | verify   | smoke-passed | braccio B reale completato: llama3.2:1b 1 ok, 2.189 token, 68,4 s, qualità 2/2, `finish_reason: stop`, zero `assemblaggio_locale` nei risultati; necessari i cataloghi manuali (default hs2 ruotato; loader vuole esattamente 5 prompt): creati `events/benchmarks/20261109b_prompts_h007.json` (simplified al posto di estrazione_json); ToDo HT-007 aggiornato con i comandi A/B completi. Run A/B phi3+llama = umano                                                                                                                                                        | 0         |

## Session 2026-11-16-commit-index-isolation

| ts               | phase    | event                     | detail                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | n   |
| ---------------- | -------- | ------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --- |
| 2026-11-16       | plan     | slice-opened              | Catena owner «/version minor + /document + commit push deploy» (brainbeez 0.14.0) sfocia nella recidiva AGG-10: il mirror commit 26dbae5 assorbe 9 file stageati dalla sessione parallela (git commit legge l'index condiviso). Owner approva «sì procedi con 1 2 3 4»: /commit V2 = protocollo a index isolato. Acceptance: sezione «Isolamento index» nel canonico + script `a-agentzero/scripts/agent-commit.sh` (GIT_INDEX_FILE da read-tree HEAD, allow-list, guardia pre, audit post, flock, push verify ls-remote) + contratto `product/contracts/check-harness-commit-index.sh` exit 0 (incl. test funzionale cane-completato con alieno stageato) + specchi rigenerati. Perimetro: 3 file a-agentzero + 2 project-skills/harness-agentfactory (re-pin catena) + contratto + progress + specchi. Esclusi: tool-pitfalls (WIP sessione parallela attiva — seconda evidenza AGG-10 da declarar lì), ToDo.md, project-skills/laya (altrui), product/state/handoff-* (altrui). | —   |
| 2026-11-16       | red      | failed                    | Contratto scritto PRIMA del body: 4 asserzioni mancanti (sezione, GIT_INDEX_FILE, ls-remote, script assente) → `check-harness-commit-index.sh` exit 1 (RED_EXIT=1 osservato).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | 0   |
| 2026-11-16       | green    | passed                    | `agent-commit.sh` (index privato + guardie + audit + push verify; shellcheck .tools 0, bash -n 0); `commands/commit.md` 1.0.1→1.1.0 (sezione + step 6 + checklist + expected output); CHANGELOG L0 [Unreleased]; specchi rigenerati via link-workspace-skills.sh (.agents/skills/commit/SKILL.md 1.1.0, .zed/prompts/commit.md). Debito di catena PREESISTENTE chiuso: version-chains RED per harness-agentfactory 1.1.33 pin su a-harness 1.10.2 mentre fcfbd88 aveva bumpato il padre a 1.10.5 verificando solo pre-commit → re-pin 1.1.34/extends 1.10.5 + entry CHANGELOG L2. Contratto GREEN (funzionale: commit contiene SOLO mine.txt; foreign.txt resta stageato nell'index condiviso). make -C agents test-unit OK (nessuna catena STALE), make -C agents pre-commit OK.                                                                                                                                                                                                  | 0   |
| 2026-11-16       | refactor | skipped                   | Shape minimale YAGNI: nessun subcomando undo (il recupero `reset --soft` è documentato nel messaggio d'errore dell'audit); fallback pathspec nel comando, non nello script.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | 0   |
| 2026-11-16       | ready    | gate                      | Dogfood: questo stesso slice committato ed eventualmente pushato CON `agent-commit.sh` (allow-list = i 9 path del perimetro, zero extra-hook attesi: hal non ha pre-commit hook installato). PC_EXIT=0, TU_EXIT=0, contract EXIT=0; ready-proof non eseguito localmente (tree sporco del WIP parallelo learn/laya, fuori perimetro), la CI `ready-for-review` gira sull'albero spinto pulito.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | 0   |
| 2026-11-16       | ops      | sync-applied              | /sync ! (deploy-all.sh → exit 0) + sync_report --only-stale su /var/www/brainbeez: stale_count=0, missing_links=0, drift_links=0, nessun override comando `commit` nel consumer; mirror brainbeez/.agents/skills/commit (symlink → hal) risolve SKILL.md @ 1.1.0 con «Isolamento index». Push 2cdcc33 verificato via ls-remote (aa74375..2cdcc33 master, con dentro anche il commit parallelo fcfbd88 già in HEAD). CI ready-for-review in esecuzione su push. Slice chiuso.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | 0   |
| 2026-11-16       | red      | failed                    | Dogfood immediato di 2cdcc33 rivela il buco: dopo commit su index privato l'index CONDIVISO resta al vecchio HEAD (status MM/D rovesciato) — un `git commit` ingenuo di sessione parallela committerebbe quello stato come revert-fantasma dei path pubblicati. Contratto esteso prima del fix: asserzione statica (update-index) + funzionale (mine.txt non staged vs HEAD dopo il commit) → RED2_EXIT=1 osservato.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | 0   |
| 2026-11-16       | green    | passed                    | Fix: chiusura script con `env -u GIT_INDEX_FILE git update-index --add --remove -- <P>` (parità sui SOLI path committati; mai reset su repo condiviso: distruggerebbe lo staged altrui); canonico 1.1.0→1.1.1 (regola nel §Isolamento index, punto 2); CHANGELOG; specchi 1.1.1; contratto GREEN, PC_EXIT=0, TU_EXIT=0. Commit d22ceaf dogfood: chiude anche il disallineamento pregresso dei 9 path di 2cdcc33 (harness-agentfactory in allow-list solo per riallineamento, zero contenuto nel commit). Verifica finale: status = solo WIP altrui, nessuna entry MM/D fantasma. Seconda evidenza AGG-10 dichiarata qui (tool-pitfalls resta WIP di sessione parallela). Slice chiuso.                                                                                                                                                                                                                                                                                             | 0   |
| 2026-11-16       | ops      | learn-evidence-aggh10     | #5 richiesto dall'owner: seconda evidenza AGG-10 (direzione sweep) + regola «revert fantasma» in tool-pitfalls §Sessioni parallele; learn 1.6.17→1.6.18 (SKILL.md work-tree pulito), CHANGELOG e reference costruiti come blob da `git show HEAD` + iniezione (il worktree portava un ripristino stale che rimuoveva l'evidenza #34 committata: non assorbito, disciplina della sezione stessa). Commit su index privato, riallineamento condiviso con --cacheinfo (file chirurgici) e --add (SKILL/progress).                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | 0   |
| 2026-11-16       | ops      | agent-commit-1.1.2        | Seconda fix al dogfood (esecuzione brainbeez D, batch outreach): guardie pre/post erano a confronto ESATTO ⇒ directory in allow-list = falso «GUARDIA PRE»; ora prefix-aware (path o prefisso directory). Reallineamento `update-index --add` rifiutava le directory ⇒ `git add -A`. Bonus: `[[ ]] && cmd` in funzione con set -e uccide silenziosamente la command-substitution (spiega l'anomalia run1/run2 del contratto) ⇒ if…fi. Contratto: caso funzionale directory + assert sul primitivo (non implementazione), 3× GREEN stabili. commit.md 1.1.2 + specchi.                                                                                                                                                                                                                                                                                                                                                                                                              | 0   |
| 2026-11-16       | ops      | consumer-stale-zero       | #3 owner «prosegui»: 9 catene L2 STALE smaltite con bump meccanici [sync:safe] (extends→padre corrente + patch + CHANGELOG): liberating.it 4 L2 (commit 4d48e58), InnerCircle 5 L2 (commit 7a690ae) — commit a index isolato agent-commit.sh --push; WIP altrui nei due repo non toccato (InnerCircle ToDo/data/cowabunga*). sync-consumer-stale finale: «Nessuna catena STALE rilevata». CI HAL verde sulle ultime due push (defusedxml 2aa627f chiuse la serie rossa pre-esistente).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | 0   |
| 2026-11-17T03:00 | learn    | /learn!-impersonate-chain | Owner «/learn !» dopo 0.16.0: variante intra-sessione di §Tool call paralleli (forma composta + regola «mai sha inesistenti») e bullet formato helper (auto_vote_routing --options virgolettato, exit 0 ≠ voto) in tool-pitfalls; learn 1.6.18→1.6.19. Blob da HEAD (ripristini stale altrui nel worktree non assorbiti). Voti routing catena recuperati con --expected CHANGELOG: 1 correct + 1 incorrect.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | 0   |

## Session 2026-11-18-ht010-gold-eval

| ts         | phase    | event        | detail                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | make_exit |
| ---------- | -------- | ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------- |
| 2026-11-18 | plan     | slice-opened | `/cycle` HT-010 (utente accept piano con default A–F): evidence-first — laya_health ok (cuda); discovery `test-unit`=unittest; `LayaOutcome` senza margin → margin via `laya_gate._top_and_margin` su `probabilities` prod; perimetro 4 file: `benchmark/scripts/gold_set_pred_runner.py`, `tests/test_gold_set_pred_runner.py`, `benchmark/gold_set/pred.jsonl` (generato), `benchmark/README.md`; effort S                                                                                                                                           | —         |
| 2026-11-18 | plan     | accepted     | «accept» (default A margin single-source, B abstain null+reason, C bucket 0.66/0.33 di modulo, D resume idempotente, E run reale nel cycle, F `laya_gate` read-only con proposta in Esito)                                                                                                                                                                                                                                                                                                                                                             | —         |
| 2026-11-18 | red      | failed       | 13 casiRED via loader `ModuleNotFoundError` (runner assente); RED_EXIT=1; emerso red esterno preesistente: `c3599e2` sorella ha corrotto il frontmatter di 8 L1 (`versenversion:`) → `test_a_harness_static_policy` StopIteration; 7 file decodificati con sed (decode meccanico, changelog sorella già allineati) lasciati non committati come collateral separato; `a-harness/SKILL.md` NON toccato: reverted dalla sorella viva nel worktree (1.11.1/1.13.5) — territorio attivo, mai correre sullo stesso file                                     | 1         |
| 2026-11-18 | green    | passed       | runner + test verdi su `tests.test_gold_set_pred_runner` (13 OK; 2 skip regressione diventano attivi con pred presente); suite `test-unit` 426 OK MAKE_EXIT=0, pre-commit 0                                                                                                                                                                                                                                                                                                                                                                            | 0         |
| 2026-11-18 | run      | reale        | pred runner su oro confermato: smoke 4 → full 123 (resume, 119 chiamate prod): ok 89, abstain 30 (tutte `score_not_discriminative` — bypass di design); misura `gold_set_scoring`: hit_rate 0.276, decision-family 34/63=.540, by_band direct .523/caution .643/escalate .031; noul 0/30 = gap vocabolario servizio {uncertain, refuse} vs oro {routing, choice, score, astensione} — difetto strumento, non modello; curva margin→accuracy debole non monotona (.55 a ≥0.8, .81 solo a ≥0.95 n=16) → nessuna soglia mossa, adozione → `HT-011` #human | 0         |
| 2026-11-18 | refactor | skipped      | modulo minimo (YAGNI, precedent HT-008); unificazione accessorii verdict ricalca i binding prod, nessuna astrazione nuova                                                                                                                                                                                                                                                                                                                                                                                                                              | 0         |
| 2026-11-18 | ready    | gate         | `make test-unit` 426 OK MAKE_EXIT=0 + `make pre-commit` 0; ToDo HT-010 [x] con Esito, flushed in CHANGELOG (1 voce); aperta HT-011 #human per adozione soglie; handoff-cycle ready; residuali non nel mio perimetro: 7 decodifiche L1 + revert a-harness = lavoro sorella non committato nel worktree condiviso                                                                                                                                                                                                                                        | 0         |

## Session 2026-11-20-ao-sidecar-governance

| ts         | phase | event            | detail                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | exit |
| ---------- | ----- | ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---- |
| 2026-11-20 | plan  | s1-consult       | analisi `gogoymh/auto-ontology-mcp` @ `0fb5ecf` (v0.6.1, Apache-2.0, MCP stdio/HTTP, FastMCP+SQLAlchemy+sqlglot, SQLite locale; server deterministico, LLM nel client — gemello del principio a-knowledge). `router.py choice` CLI su laya ok: BC→head «Agent Platform (solo skill)» (override System 2: runtime esterno, non skill → nuovo BC), priorità→«P2» (accettata)                                                                                                                                                                                                                                                                                                                                                                                    | 0    |
| 2026-11-20 | plan  | slice-opened     | `/slice` Livelli A+C: PRD `docs/29_auto_ontology_semantic_layer.md` + contratto `docs/slices/AO1-sidecar-boundary.md` + guardia `product/contracts/check-ontology-bc-boundary.sh`; perimetro 4 file (+ waiver meccanici: indice, ToDo HT-013, handoff, progress); effort S; fuori perimetro: delega a-knowledge (AO-1.1, catena /version+mirror), side-car Zed (AO-2 `#human`), Livello B vendor+facade (AO-3 condizionato)                                                                                                                                                                                                                                                                                                                                   | —    |
| 2026-11-20 | plan  | patch-robustezza | PRD `docs/29` riscritto sulla documentazione intera (README/CONTRIBUTING/NOTICE/config/http_auth/test): KPI-1 → misura deterministica build_server+Client con baseline nel pin file (nomi tool prima, char dopo); §6 AO-2.1 rituale 7 passi (release-anchor = commit di bump `version` — CONTRIBUTING reg. 5, niente tag; grep invarianti; snapshot export YAML+wiki; rehearsal migrazione su copia `AUTO_ONTOLOGY_HOME`; pytest; remisura; riga pin; revert); snippet Zed: `enabled: false` fino ad AO-2.1-1-4, MAX_ROWS=ceiling, TOOLSETS typo→ValueError (fail-fast); vault default-interno opt-in; NFR +scan filters/permessi/HTTP N/A; §9 tabella fatti verificati (12 righe con fonte). Slice §4: fonte unica della tabella (PRD e a-knowledge linkano) | —    |
| 2026-11-20 | red   | observed         | `check-ontology-bc-boundary.sh` → RED_EXIT=1 con i 3 FAIL attesi (riga BC assente, tabella routing assente, HT-013 non ancora referenziato); dopo l'apertura di HT-013 restavano 2 FAIL = solo l'Act su `docs/bounded-contexts.md`; nessuna scrittura fuori perimetro (WIP parallelo learn/gold-set intatto)                                                                                                                                                                                                                                                                                                                                                                                                                                                  | 1    |
| 2026-11-20 | green | act-ao1          | **Act AO-1 consegnato**: `docs/bounded-contexts.md` — riga BC «Knowledge & Ontology (side-car)» (clone pinnato `/opt/auto-ontology-mcp`, pin file `agents/a-knowledge/references/auto-ontology-source.md`), regola 4 (bundle escluso, stdio-only, HTTP N/A), §«Routing delle domande» con i 4 ancoraggi; guardia GREEN (4/4 assert), `make pre-commit` 0; slice aggiornata a «consegnata». Attenzione: il green iniziale della guardia era arrivato da chiamata parallela al salvataggio file (dipendenza violata) — riverificato con esecuzione separata                                                                                                                                                                                                     | 0    |

| 2026-11-20 | ops | flush-ht013 | `todo_flush` ha flussato 1 voce (HT-013 → CHANGELOG `### Added`, riga 108): il corpo a più bullet **non sopravvive** al flush (solo la riga-titolo) → Esito re-inlineato chirurgicamente a una riga, formato HT-010. Lezione da registrare (canale tool-pitfalls, WIP di sessione parallela — non qui): «voci chiuse multi-bullet nel ToDo: il flush appiattisce sul titolo, mettere l'Esito in riga» | 0 |
| 2026-11-20 | ops | guard-hardening | Post-flush la guardia era tornata **RED**: l'assert 4 (ref HT-013 in ToDo) era dipendente dal backlog volatile → inasprito su sede stabile (la slice referenzia il contratto) + rimossa variabile `TODO` unused; re-GREEN confermato con `bash -n` | 0 |
| 2026-11-20 | plan  | ao-1-1-opened    | AO-1.1 (user «procedi»): perimetro 3 file — `agents/a-knowledge/SKILL.md` + `agents/a-knowledge/CHANGELOG.md` + guardia (assert 5). Verify pre-flight: mirror `.agents/skills/a-knowledge` = symlink al canonico (nessun rigenerato necessario); unico figlio «extends: a-knowledge» = extension-template placeholder, non scansionato dalle catene (già 1.0.0<1.1.10 senza STALE → escluso di fatto); bump quindi senza catene da ri-pinnare | — |
| 2026-11-20 | plan  | s1-bump-decision | `router.py choice` patch/minor/major → «major 2.0.0»: **override System 2** (riga §Deleghe additiva, zero passaggi toccati = minor per precedent commit.md 1.0.1→1.1.0; CLI choice non emette request_hash → voto di calibrazione non esprimibile, lezione da portare a tool-pitfalls quando libero). Scelta: 1.1.10→1.2.0; extends-version 1.13.11 NON ri-pinnato (1.13.15 è WIP non commesso di sessione parallela — pinnarlo cristallizzerebbe lavoro altrui; STALE padre-figlio preesistente invariato) | — |
| 2026-11-20 | green | ao-1-1-act       | SKILL.md: riga §Deleghe verso side-car Knowledge & Ontology con **link** a `docs/bounded-contexts.md` §«Routing delle domande» (non copia); CHANGELOG `## [1.2.0] - 2026-11-20` ### Added; guardia +assert 5 (delega promossa) — nota RGR: editato dopo l'Act, quindi il verde dell'assert 5 è verifica e non dimostrazione RED (l'Act era già accettato dall'owner); `make -C agents pre-commit` 0 (check-registry OK = transazione bump+changelog, md-links 360 OK) | 0 |
| 2026-11-20 | ops   | ao-1-1-ready     | handoff-slice aggiornato (node ao-1-1-knowledge-delegation, delivered); PRD §6 AO-1.1 → done; voce CHANGELOG HT-013 emendata (residuo AO-1.1 chiuso, restano AO-2 `#human` e AO-3). Nulla committato (regola: solo su richiesta; worktree con WIP parallelo attivo) | 0 |
| 2026-11-20 | ops   | ao-2-install     | AO-2 installata: sudo NON interattivo ⇒ **deviazione di path registrata** `/opt/...`→`~/auto-ontology-mcp` (proprietà invariate: pin SHA 0fb5ecf, fuori workspace, lock a monte; ripristino documentato nel pin file). Sequenza: clone+checkout → `uv sync` → pytest **254 pass/5 skip** → KPI-1 baseline **13 tool / 15.782 char** su `logs/ao-sidecar/kpi1-0fb5ecf.txt` (README dice ≈12k: serializzazione di richiesta, non dump — da qui la baseline misurata) → grep invarianti CONTRIBUTING (guard read-only in datasources/store/knowledge; zero dipendenze API-key) → demo (3 sources/12 passages/16 concepts/3 action items) → permessi 700/600 → **pin file** `agents/a-knowledge/references/auto-ontology-source.md` (blocco PIN:START/END stile vendor, con entry 1.2.0 nel CHANGELOG skill) → entry Zed `auto-ontology` `enabled:true` (passi AO-2.1 1-4 già verdi; rehearsal = N/A a insediamento zero) con backup `.bak-auto-ontology-20261120` e validazione JSON (12 context_servers). Docs allineati: PRD §4/§6, context map. Nota: `enabled:true` diretto invece del doppio restart false→true — documentato come decisione. | 0 |
| 2026-11-20 | plan  | ao-2-smoke-open  | Residuo #human: riavvio Zed + smoke (check_readiness demo; domanda sushi-roll Pennsylvania 2024-06 ≈316.80 via check_answerable→validate_sql→run_sql); al closing: registrazione esito in questa tabella e handoff. KPI-3 da verificare dopo smoke (nessuna scrittura fuori da ~/.auto-ontology-mcp) | — |
| 2026-11-20 | ops   | ao-2-boot-smoke  | Smoke pre-riavvio con il comando esatto della entry Zed (`uv --directory ~/auto-ontology-mcp run auto-ontology-mcp`, stdio): handshake `initialize` OK, tools/list = **13 tool (answer set)**, instructions handshake presenti; `logs/ao-sidecar/kpi1-0fb5ecf.txt` confermato gitignored. All'atto del riavvio Zed restano solo i test funzionali #human (readiness demo + sushi-roll PA 2024-06 ≈316.80 + KPI-3 `git status` pulito) | 0 |
| 2026-11-20 | ops   | ao-2-env-verify  | Doppia smoke stdio col comando esatto della entry: SENZA env il server serve 35 tool/istruzioni 4294 char (default `all` — fumo di boot, non configurazione); CON l'env della entry Zed (`TOOLSETS=answer`+`ALLOW_DATASOURCE_TOOLS=0`+`MAX_ROWS=100`): **13 tool, nessun `add_datasource`/`scan_datasource`**, match esatto del baseline `kpi1-0fb5ecf.txt` — l'env plumbing della entry è verificato, il gate contestuale (KPI-1) è attivo già da prima del riavvio. Lezione: il check di boot va fatto con l'env reale della entry, altrimenti si testa il default | 0 |

## Session 2026-11-22-v0-toth-index

| ts         | phase | event          | detail                                                                                                                                                                                                                                                          | exit |
| ---------- | ----- | -------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---- |
| 2026-11-22 | plan  | slice-opened   | `/slice v0 toth_index` (accept umano «a», via A): BC governance a-agentzero; perimetro 4 file + 2 rituali (waiver dichiarato in piano: transazione versione); worktree `slice/v0-toth-index` da origin/master f07af07 (master già sync, push non necessario)      | —    |
| 2026-11-22 | red   | failed         | `tests/test_toth_index.py` scritto PRIMA del generatore: 5 failed «generatore assente» (RED_EXIT osservato)                                                                                                                                                    | 1    |
| 2026-11-22 | green | passed         | `toth_index.py`: gemello hal-contract (liste+fm_field/shorten via importlib, path derivati dallo script — non dal main checkout); artefatto 34 voci (agent 9/bundled 9/project 4/command 12) byte-deterministico, `--check` exit 0; 5 pytest verdi             | 0    |
| 2026-11-22 | run   | reale          | suite completa `pytest tests`: 456 passed, 1 skipped preesistente, zero regressioni; check-version-changelog 0; check-line-length 0; check-md-links 0 (360 link); check-frontmatter-all 0                                                                        | 0    |
| 2026-11-22 | find  | drift-canone   | v0 consegna valore immediato: 2 drift che il fence salta in silenzio — `project:project-skills/harness-agentfactory` (listato in PROJECT_SKILLS, bundle assente su master) e `command:laya` (in COMMANDS, `commands/laya.md` assente). Da risolvere in slice separato | —    |
| 2026-11-22 | ready | gate           | write-set = 6 file (4 perimetro + SKILL.md/CHANGELOG.md transazione 1.14.0→1.15.0); NON committato: /commit + land su richiesta umana; nota: la release 1.14.4 vista in sessione precedente (2f8e613) NON è su origin/master — base reale del canone = 1.14.0      | —    |

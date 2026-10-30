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

| ts         | phase    | event        | detail                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | make_exit |
| ---------- | -------- | ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------- |
| 2026-10-29 | plan     | slice-opened | evidence: RCA sessione (ABSTAIN `invalid_*` con servizio verde, verdetti reali su `/systemone` p=0.88); choice Laya A/B → ABSTAIN, decide System 2: **A /systemone** (endpoint task canonico; B duplicherebbe la costruzione questions lato client); score → abstain `score_not_discriminative` (non fabricare); noul → stringa intent-choice o astensione documentata; request_hash/`POST /outcome` **fuori perimetro** (follow-up); perimetro 3 file: `laya_service.py`, `tests/test_laya_service.py`, `tests/test_laya_http_pool.py`; effort S | —         |
| 2026-10-29 | plan     | accepted     | «accetto» (default A/B/C lockati)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | —         |
| 2026-10-29 | red      | failed       | `TestSystemOneContract` 5 nuovi: routing/choice envelope+URL, score bypass→reason, noul intent-choice, preflight choice → 5 failed / 32 passed                                                                                                                                                                                                                                                                                                                                                                                                    | 1         |
| 2026-10-29 | green    | passed       | `_call` → `/systemone` + normalizzazione payload + unwrap envelope; parser `choice` con fallback legacy; bypass score onesto; noul choice; regressione `test_gateway_core`+`test_skill_catalog`+suite laya: 78 passed; collaterale necessario: fix `router.py` `noul --json` serializzava `LayaOutcome` (perimetro 3 file: laya_service, test_laya_service, router)                                                                                                                                                                               | 0         |
| 2026-10-29 | refactor | skipped      | slice minimale; shim legacy documentato e limitato ai mock preesistenti                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | 0         |
| 2026-10-29 | ready    | gate         | `make pre-commit` 0 (secrets+deps+sast+compileall); `check-static-diff` N/A sul profilo root (documentato L2); live: routing ok `cache-cost-tokeni`, choice ok, score abstain by-pass, noul ok; ToDo P0 chiusa e flushata in `./CHANGELOG.md` (Fixed)                                                                                                                                                                                                                                                                                             | 0         |

# Changelog — HAL Project

Tutte le modifiche e le evoluzioni rilevanti del progetto HAL sono documentate in questo file.

Il formato è basato su [Keep a Changelog](https://keepachangelog.com/it/1.1.0/),
e questo progetto aderisce a [Semantic Versioning](https://semver.org/lang/it/).

## [Unreleased]

### Added

- Gate k-aware System 1 sul client gateway: choice/routing/preflight con probabilità verificano il verdetto con self-consistency (k≥4 mai diretto senza top1≥0,8), astensione `low_margin` quando non accettabile — soglie e helper ora nel modulo canonico `laya_gate.py` (symlink verso hal_system1), niente mirror manuale.

- Chiave Cache L1 a due livelli: prefix stabile + suffix append-only · Gateway Core
- Catalogo skill compatto con System 1 (Laya) come tool-search · System 1 (Laya) + Agent Platform
- ContextManager multi-turn nel Gateway Core: troncamento, rolling summary, retrieval · Gateway Core
- Telemetria `cached_tokens` e `cache_creation_input_tokens` nei runner e nei gate · Benchmark
- Retry su Laya con exponential backoff e jitter · System 1 (Laya)
- HTTPAdapter con pool dimensionato sulla `_session` Laya · System 1 (Laya)
- Timeout disaccoppiati connect/read/pool sulle chiamate Laya · System 1 (Laya)
- Idempotenza di submit: registro task_id anti-duplicato · Gateway Core
- Capability flag per-modelli per tool loading dinamico · Gateway Core
- Registry tool session-scoped append-only (carry-forward) · Gateway Core
- System prompt come `instructions`, fuori dal transcript append-only · Gateway Core
- Capability flag `context_cache` nei `SYSTEM_TWO_PROFILES` · Gateway Core
- Merge dei messaggi tool consecutivi same-role nel message builder · Gateway Core
- Costo di refill cache nel failover e nel fallback · Gateway Core
- Prezzi cache effettivi da tabella per modello/regione, non costanti · Benchmark
- Budget di polling per gli endpoint di gestione task (20 QPS) · Gateway Core
- Teardown della `_session` (close / context manager di run) · System 1 (Laya)
- `verify` configurabile con CA bundle invece di `verify=False` fisso · System 1 (Laya)
- Percorso di esecuzione streaming System 2 (SSE) per eliminare il timeout strutturale delle generazioni lunghe · Gateway Core
- Capability flag `streaming_only` per-modelli con validazione alla frontiera · Gateway Core
- Accumulo dei delta streaming per `tool_calls` e JSON Mode prima del parsing · Gateway Core
- Client riusato negli script skill (a-knowledge, a-seozoom, illustrator) · Agent Platform
- Regola System 1 task-vs-batch per workload ad alto volume · System 1 (Laya)

### Changed

- Allineare al gate 1 il gate `laya_recommended` del runner benchmark `#system1-gating #benchmark`
- Gate 2: passare a Laya un contratto compatto del task invece dell'intera fonte `#system1-gating #feature`
- Gate 3: verificare la coerenza tra famiglia task, strategia e modalità scelte da Laya `#system1-gating #feature`
- Gate 4: single-pass come default, plan-then-solve e segmentazione solo se giustificati `#system1-gating #feature`
- Gate 5: fallback conservativi sotto soglia e retry limitati `#system1-gating #feature`
- Gate 6: ridurre le chiamate Laya alle sole decisioni utili `#system1-gating #techdebt`
- Gate 7: verificare e completare gli eventi SQLite per run/fase/sistema/modello/task `#system1-gating #feature`
- Confronto baseline vs nuova run per coppia (modello, test) con overhead Laya `#system1-gating #benchmark`
- Chiudere il gate `ready-for-review` e risincronizzare i link Zed `#version-sync #infra`
- Registrare durata e token stimati degli stage andati in timeout o errore `#benchmark #feature`
- Misurare il costo reale del blocco `<strategia_system1_laya>` e la sua ripetizione in output `#benchmark #spike`
- Prova mirata `qwen2.5:1.5b` su `sintesi_traduzione` con `--timeout` più alto `#benchmark #spike`
- Prova mirata sullo stage fallito di phi3:mini `estrazione_json` `#benchmark #spike`
- Baseline a contesto pieno (phi3:mini, llama3.2:1b) per verificare se la fonte della baseline `20261017_all` era tagliata `#benchmark #spike`
- Ridurre il blocco `<strategia_system1_laya>` ripetuto in ogni stage, se la misura lo giustifica `#benchmark #techdebt`
- Verificare se i cambi 1.8.6 di `a-agentzero` richiedono adeguamenti ai L1 o solo il pin `#version-sync #spike`
- Aggiornare `extends-version` a 1.8.6 nei sette L1 con bump e voce CHANGELOG `#version-sync #infra`
- Aggiornare `extends-version` di `harness-agentfactory` a 1.8.6 `#version-sync #infra`
- Migrare lo schema di `system2_metrics.sqlite3` esistenti aggiungendo la colonna `error_message` `#system1-gating #bug`
- Risolvere timeout phi3:mini `sintesi_traduzione`: abilitare `source_chunks` per translation nel gate (`TASK_FAMILY_ALLOWED_MODES`); run validata in 167.8s (prima 3600s timeout) `#benchmark #fix`
- Generare Work Graph deterministico con `/graph -y` e multi-cycle sequenziale (N1 diagnostica → N2 fix → N3 wrapper → N4 registrazione) `#harness #graph`
- Registrare comando L0 `/knowledge` con subcomandi check|extract|distill|query|update per pipeline book-to-skill `#knowledge #feature`
- Creare skill `gdrive-sync-safe` per gestione mirror Google Drive locali e prevenzione freeze IDE `#infra #skill`
- Wrapper `extract.py` cost-aware per a-knowledge: `--check`, selezione estrattore per formato, cache sha256, routing capitolo Laya `#knowledge #feature`
- Eseguiire igiene ToDo.md con `/todo`: prune heading vuoti, chiusura item completati, rimozione sezioni duplicate `#chore`
- Bump versione skill modificate: `improve` 1.0.0→1.0.1, `review` 1.0.0→1.0.1 `#version-sync`
- Nuova run phi3:mini e llama3.2:1b per confermare l'effetto dell'assemblaggio locale
- Script wrapper cost-aware a-knowledge/scripts/: extract.py --check + selezione estrattore + routing capitolo Laya. Richiede book-to-skill installato. · #knowledge
- Registrazione comandi L0 /knowledge (check|extract|distill|query|update). · #knowledge
- source_chunks_task — Isolare l'assemblaggio locale — confermato su phi3:mini — 5/5 segmenti JSON valido, 17.169 token, overhead 1,80× vs baseline estrazione_json; llama3.2:1b 0,79×
- Benchmark — Token del middleware su phi3:mini e llama3.2:1b — chiuso (modelli rimossi da sys2; stack migrato a Gemini 3.5 Flash-Lite)
- Gate 5/6 + error-category: chiudere il RED preesistente su HEAD: retry bounded sotto soglia + fallback conservativo single_pass/strategy, `laya_call_count` (0 su skip), categoria `error` nel token breakdown, blocco `<strategia_system1_laya>` ridotto (127 chars), coerenza translation+`source_chunks` (fonte reale oltre soglia, fix phi3 preservato), registro `a-knowledge` in `AGENT_EXTERNAL_MODELS` (mode 0 invariato). `make test-unit` 225 GREEN; `make ready-for-review` Gate OK · #feature #system1-gating #benchmark
- Igiene repo: deseguiti 78 file `.pyc` dal tracking git e aggiunte regole `__pycache__/` + `*.pyc` a `.gitignore` · #chore #infra
- Allineare README e documentazione sulla razionalizzazione e sui 14 L1 storici — `agents/README.md`, `agents/MIGRATION.md`, `AGENTS.md` e `agents/AGENTS.md` descrivono la struttura corrente (14 L1 originari → 7 consolidati + `a-knowledge`, 9 agenti `a-`; elenco skill esposte allineato a `.agents/skills/`); gate `make -C agents pre-commit` OK
- `/sync !` eseguito: deploy L0+L1+comandi, link `.agents/skills` e wrapper rigenerati; tutte le 8 catene L1 allineate a `a-agentzero` 1.12.0 con bump patch [sync:safe] (`a-b2b` 2.3.1, `a-copywriter` 1.7.1, `a-design` 1.2.1, `a-harness` 1.9.1, `a-knowledge` 1.1.1, `a-product` 2.2.1, `a-seozoom` 1.10.1, `a-wordpress` 1.4.1) e voce CHANGELOG per ciascun figlio; verifica finale: zero catene STALE · #version-sync #infra
- Coordinamento versioni: comando canonico `graph` 1.0.1→1.0.2 (bullet appresi 2026-10-27 aggiunti al body, wrapper rigenerato idempotente); utility `learn` 1.5.7 con section changelog mancante recuperata; L0 `a-agentzero` invariato per regola utility nested (bump di `learn` non richiede bump del padre) · #version-sync
- Coordinamento versioni (release 2026-10-30): L0 `a-agentzero` rilasciato **1.13.0** (minor — nuove regole di protocollo `AGENT-PROTOCOL.md` §contesto/dichiarazioni/cache + fix `sync-agents.sh` §`report_workspace_links`); tutte le 8 catene L1 allineate a 1.13.0 con bump patch contrattuale [sync:safe] (`a-b2b` 2.3.2, `a-copywriter` 1.7.2, `a-design` 1.2.3, `a-harness` 1.9.2, `a-knowledge` 1.1.4, `a-product` 2.2.2, `a-seozoom` 1.10.3, `a-wordpress` 1.4.2) e voce CHANGELOG per ciascun figlio; catene harness allineate (`harness-agentfactory` 1.1.29, `harness-hal` 1.0.2, `extends-version` a-harness 1.9.2); skill `laya` 1.5.1 con comando canonico `commands/laya.md` @ 1.0.1 (fix path `router.py`, wrapper `laya-cmd` rigenerato); indice `docs/00_indice.md` allineato (25–27 censiti, conteggio 23→27); gate: `make -C agents version-chains` verde (zero STALE), `make -C agents pre-commit` OK, `make pre-commit` OK, `make test-unit` 369 GREEN · #version-sync #infra
- Regola di protocollo: mai reinserire `reasoning_content` nella history · Agent Platform
- Vincoli deployment SSE del serving documentati nel serving spec (proxy buffering, pool, fd) · Gateway Core
- Regola di protocollo append-only per dichiarazioni iniettate · Agent Platform
- Regola di protocollo ordering static-first: mai contenuto volatile in testa al prompt · Agent Platform + Gateway Core
- Regola di protocollo: persistere i risultati entro la retention del provider · Agent Platform
- Spike: session cache `x-dashscope-session-cache` via OrcaRouter/DashScope · Gateway Core
- Spike: supporto marker `cache_control` (explicit cache) a due strati — ESITO: non adottato via OrcaRouter (marker tollerati ma inerti, `cached_tokens=0` anche a caldo, docs/26); contratto backend già tollera i marker (flag `context_cache`, N14), builder guardrail rinviato a backend con cache esplicita misurabile · Gateway Core
- Metrica benchmark token/richiesta vs skill dichiarate · Benchmark
- Metrica connection reuse nella telemetria HAL · Benchmark + Gateway Core
- Astrazione conversation lato gateway (alternativa locale a `previous_response_id`) · Gateway Core

### Fixed

- `laya_service`: by-pass onesto del servizio mappato in `abstain` con reason documentata per **tutte** le operazioni S1 (`score_not_discriminative`, `noul_gpu_excluded`, …) — prima solo `score` lo surfacing, `noul` degenerava in `invalid_result`; test `test_noul_bypass_surfaces_reason` · System 1 (Laya)
- `laya_service`: header `Authorization: Bearer` risolto da `LAYA_API_KEY` (env → `.env` di repo → default `sk-local`) su `/predict`; il 401 non autenticato era la causa delle ABSTAIN `unavailable` di tutte le operazioni System 1 · System 1 (Laya)
- Includere dichiarazioni tool/skill nella chiave Cache L1 · Gateway Core
- Polling a backoff esponenziale con stati terminali completi · Skill illustrator (a-design) + Gateway Core
- Successo parziale nei task multi-output: iterare choices con `finish_reason` · Skill illustrator (a-design)
- `laya_service`: operazioni instradate su `POST /systemone` `{task_type,text,params}` con unwrap dell'envelope `{result:{choice,confidence,probabilities}}`; routing/choice rispondono `ok` con `choice` ∈ candidates, `score` astiene con reason documentata `score_not_discriminative` (by-pass onesto, mai un valore fabricato), `noul` restituisce la stringa intent-choice; coperto da `TestSystemOneContract` (5 nuovi test, suite `test_laya_*` 60 verdi) e da verifica CLI live; fix collaterale `router.py` (`noul --json` serializzava l'intero `LayaOutcome`) · System 1 (Laya)

## [2.3.0] - 2026-10-09

### Added

- Creazione della cartella `tests/` e migrazione di tutti i file di test unitari al suo interno, con configurazione del test discovery (`python3 -m unittest discover -s tests`).

## [2.2.0] - 2026-10-09

### Added

- Creazione della cartella `scripts/` e centralizzazione di tutti gli script di utilità e test eseguibili al suo interno (`check_secrets.py`, `check_deps.py`, `check_sast.py`, `bench_hot_paths.py`, `test_laya.py`), con aggiornamento dei riferimenti in CI e nei test suite.

## [2.1.0] - 2026-10-09

### Removed

- Rimozione definitiva di ogni cartella e riferimento a Cursor (`.cursor/`, `.agents/.cursor/` e relativi file di adapter e reference), rendendo il workspace focalizzato ed esclusivo per Zed.

## [2.0.0] - 2026-10-09

### Added

- Collegamento di `SystemTwoEngine` a backend configurabili / mock (`register_backend`) con gestione dei fallback e restituzione di metadati strutturati (`SystemTwoResponse`), validato da `test_system_two_provider.py`.
- Risoluzione del modello System 2 per profilo d'uso e capability indipendentemente dall'identità dell'agente (`resolve_model_for_profile`), con fallback condiviso `ACTIVE_MODEL_NAME` e validazione di sicurezza contro nomi modello arbitrari, testata da `test_system_two_provider.py`.
- Policy di instradamento System 1 / System 2 e riduzione del budget System 2 (`SystemRoutingPolicy`), che distingue decisioni chiuse (System 1), generazione semplice a basso rischio (System 2 ridotto) e richieste complesse/con side-effect o astensione (System 2 completo), testata da `test_system_two_provider.py`.
- Motore di evaluation offline (replay), shadow mode e metriche di gate con attivazione automatica del rollback (`SystemEvaluationEngine`), testato da `test_system_evals.py`.
- Integrazione completa della cache L1 Redis oltre il calcolo della chiave (`L1RedisCacheManager`), con hashing SHA-256 dei contenuti reali dei file rilevanti, TTL per profilo d'uso, validazione dei tool boundary e tracciamento della provenienza eventi (`cache_hit`, `cache_miss`), testata da `test_gateway_cache.py`.
- Integrazione del circuit breaker (`CircuitBreaker` e `ProviderResolverWithBreaker`) nella risoluzione e nel fallback dei provider, con limitazione a un solo probe half-open concorrente (`probe_in_flight`) e salto automatico dei provider degradati, testata da `test_circuit_breaker.py`.
- Controllo automatico low-noise dei segreti (`check_secrets.py`) integrato nel gate CI GitHub Actions e testato da `test_secret_scanner.py`.
- Dichiarazione delle dipendenze runtime (`requirements.txt`) e script di audit con supporto advisory (`check_deps.py`) integrato nel gate CI e testato da `test_deps_audit.py`.
- Controllo SAST Python a basso rumore per il codice gateway (`check_sast.py`), integrato nel gate CI GitHub Actions e testato da `test_sast.py`.
- Allineamento dello stato delle funzionalità e della documentazione (`README.md`), con etichettatura esplicita delle verifiche per ciascun modulo del Gateway Core.
- Gestore di retention automatica dei log eventi (corpo 30 giorni, metadati 12 mesi), cifratura a riposo dei payload ed enforcement dell'accesso controllato RBAC (`EventRetentionManager`), testato da `test_retention.py`.
- Pulizia dei riferimenti agli hook dell'editor nel `Makefile` (`agents/Makefile`) rimuovendo i path non esistenti.
- Implementazione del benchmark ripetibile dei percorsi caldi (`bench_hot_paths.py` e `test_benchmarks.py`) per normalizzazione prompt e regex redaction.
- Aggiunta del flag di completezza informativa WYSIATI (`augment_response_with_wysiati`) nei payload di risposta e monitoraggio della tensione cognitiva in `SystemRoutingPolicy` per impedire la pigrizia di System 2 su task complessi, testati da `test_kahneman_evolution.py`.

### Fixed

- Ripristinato il comando Laya `score` e `noul` in `router.py` (`handle_score`, `handle_noul`), risolvendo il `NameError` precedente e testato da `test_router_score.py`.

### Changed

- Rimosso ogni riferimento a Cursor, spostando i file di stato in `product/state/`, gli adapter in `product/adapters/`, e rimuovendo i fallback ai modelli interni Cursor dalle istruzioni e dai frontmatter degli agenti.
- Laya espone l’astensione su indisponibilità e output non validi; il triage evita instradamenti degradati.

### Changed

- Riallineate con sync selettivo le catene `extends-version` L1/L2 marcate `[sync:safe]`.
- Aggiunto il workflow root `ready-for-review` per i test gateway su push e pull request.
- Collegata la redaction di segreti e PII al writer JSONL; body rilevati o con scansione incerta non vengono persistiti.

## [1.9.0] - 2026-10-06

### Added

- **Cache L1 (`07`)**: Normalizzazione prompt, hashing SHA-256 canonico, chiavi Redis composte, TTL e invalidazione contesto `#techdebt` · P0
- **Retention & Redaction (`05`)**: Denylist regex avanzata, redaction in scrittura, scansione PII tramite preset Laya `#infra` · P0
- **Circuit Breaker & Session (`19`)**: Derivazione deterministica del `session_id` e State Machine del circuit breaker per i provider `#feature` · P1
- **Flush automatico ToDo**: Automazione del comando `/todo` per eseguire il flush della sezione «Già fatto» direttamente in `CHANGELOG.md` ad ogni invocazione `#infra`

## [1.8.0] - 2026-10-02

### Added

- Verificata la copertura dei contenuti post-razionalizzazione degli agenti (`#agents` · P2) nell'albero canonico HAL [sync:safe].

### Performance

- Ottimizzazione delle chiamate System 1 (Laya) tramite HTTP session pooling persistente (`requests.Session`) e decoratore `@lru_cache` (maxsize=128) per il caching in-memory delle query identiche (`choice`, `routing`, `score`, `noul`) in `laya_service.py`.

## [1.7.0] - 2026-10-02

### Added

- **Integrazione Zed Editor**: Configurazione workspace (`.zed/settings.json`), prompt mapping in `.zed/prompts/`, e pacchetti skill in `.agents/skills/` per il supporto multi-editor Cursor ⇄ Zed.
- **Script di Sincronizzazione Bidirezionale**: Aggiornato `agents/scripts/link-workspace-skills.sh` per rimuovere il frontmatter YAML di Cursor dai prompt di Zed e generare automaticamente skill conformi per tutti i comandi L0 (`/HAL:version`, `/HAL:document`, `/HAL:commit`, ecc.).
- **Layer Cognitivo System 1 (Laya) Esteso**:
  - Aggiunti metodi batch (`batch_score`, `batch_routing`) in `router.py` e `laya_service.py`.
  - Integrato Laya come pre-filtro e gating obbligatorio in **tutti gli 8 agenti L1** (`a-agentzero`, `a-harness`, `a-product`, `a-seozoom`, `a-design`, `a-copywriter`, `a-b2b`, `a-wordpress`).
- **Pubblicazione GitHub**: Inizializzato repository Git, tracciati tutti i file e pubblicato il repository pubblico su GitHub (`carlo-tara/HAL`).
- **Work Graph & Igiene ToDo**: Esecuzione del work graph (`/graph -y ToDo.md`) e igiene del backlog (`/todo`).

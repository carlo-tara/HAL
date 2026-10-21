# Changelog — HAL Project

Tutte le modifiche e le evoluzioni rilevanti del progetto HAL sono documentate in questo file.

Il formato è basato su [Keep a Changelog](https://keepachangelog.com/it/1.1.0/),
e questo progetto aderisce a [Semantic Versioning](https://semver.org/lang/it/).

## [Unreleased]

- Agent L0: `scripts/context_compress.py` compressione semantic-aware per skill/instruction file (classifica per tipo, regole deterministiche, dedup cross-file, stima token, validazione marker sicurezza); derivato da vidanov/context-compress. Nuovi eventi telemetrici `skill_compress` e `dedup_found` in `token_budget.py`. Riferimento `references/token-budget.md` aggiornato con strategie 14-17. Test in `tests/test_context_compress.py` (24 test). `a-agentzero` 1.10.1 · HAL
- Benchmark: `benchmark/scripts/compare_tokens.py` confronta per (modello, test) i token di baseline e middleware (token `n/d` non sommati, flag `baseline_input_sospetto`, costo del blocco strategia dal delta di input); test in `tests/test_compare_tokens.py` e in CI `#benchmark` · P1 · Progetto

- Correggere i passi di test in `.github/workflows/ready-for-review.yml`: i file `test_*.py` sono in `tests/`, quindi `python3 test_gateway_core.py` fallisce con `No such file or directory`; usare `PYTHONPATH=. python3 tests/test_*.py` #infra · P1
- Aggiungere un cooldown configurabile tra i modelli nel runner benchmark, o rendere il generatore ricorsivo #benchmark · P1
- Sincronizzare automaticamente `generate_benchmark_report.py` tra `hal_gateway/benchmark/scripts/` e `hal_system2/scripts/` #benchmark · P2
- Allineare la versione dei wrapper CLI generati con la sorgente canonica #version-sync · P2

- Benchmark: run `20261021_1` (middleware, Laya su GPU, pausa 180 s via `--cooldown`), storico in `benchmark/history/20261021_1/` con report e executive summary; confronto con `20261020_1` e tabella cross-run delle run completate (esclusa `20261019_1`, incompleta). Timeout `qwen2.5:1.5b` su `sintesi_traduzione` presente in 3 run su 3 con middleware, aggiornato in `ToDo.md` `#benchmark` · P1 · Progetto
- Benchmark: run `20261021_2`, prova mirata su `qwen2.5:1.5b` / `sintesi_traduzione` con `--timeout 1200` (una chiamata, esito ok in 211,8 s, 8.919 token, qualità 1/2). Storico in `benchmark/history/20261021_2/` con report, executive summary che confronta le sette run complete e aggiornamento di `ToDo.md` `#benchmark` · P1 · Progetto
- Versione: comando canonico `agents/a-agentzero/commands/version.md` (e wrapper `.agents/skills/version/SKILL.md`) 1.2.1 → 1.3.0 (minor: il wrapper ora deriva la versione dal frontmatter canonico); `a-agentzero` non bumpato (modifica confinata al comando) `#version-sync` · HAL
- README: preflight saltato per richieste atomiche, test in CI, sorgente della versione dei wrapper e `sync_hal_system2.sh check` `#docs` · Progetto
- `link-workspace-skills.sh`: la versione dei wrapper `SKILL.md` generati deriva da `version:` nel frontmatter del comando canonico (non più `1.0.0` fisso), così un bump sopravvive ai sync; `command_version` e script sourceable; `version.md` con `version:` nel frontmatter; test in `tests/test_link_workspace_skills.py` `#version-sync` · P2 · Progetto
- Benchmark: `benchmark/scripts/sync_hal_system2.sh check|apply` per tenere allineati generatore, runner e metriche del gateway con la sorgente `hal_system2`; test in `tests/test_sync_hal_system2.py` e in CI `#benchmark` · P2 · Progetto
- Runner benchmark: `--cooldown SECONDI` tra i modelli (canonico `hal_system2/app/`, mirror nel gateway); test in `hal_system2/tests/test_benchmark_models.py` e `tests/test_runner_token_gating.py` `#benchmark` · P1 · Progetto
- Runner benchmark: copia del gateway riallineata a `hal_system2/app/` (assemblaggio locale dei segmenti, `--segment-max-tokens`, stop su troncamento, `get_token_breakdown`); mirror verificato con `diff`; test di guardia in `tests/test_runner_token_gating.py` `#benchmark` · P1 · Progetto
- CI: i passi test di `ready-for-review.yml` usano `PYTHONPATH=. python3 -m unittest tests.<modulo>` dalla root, con installazione di `requirements-dev.txt` (nuovo: `httpx`, `python-dotenv`) e passi per `test_router_score`, `test_runner_token_gating`, `test_benchmarks` `#infra` · P1 · Progetto
- Gateway: il preflight Laya viene saltato per richieste atomiche, a basso rischio e brevi (`istruzione + fonte < PREFLIGHT_SHORT_MAX_CHARS = 400`); `LayaSystemOneService.preflight` restituisce `abstain` con `reason=preflight_skipped_atomic`, senza consumare il budget e preservando `source`/`output_format`; test in `tests/test_laya_service.py` `#system1-gating` · P1 · Progetto
- Benchmark: ripetizione `20261020_2` di `phi3:mini` e `llama3.2:3b` (Laya su GPU, pausa 300 s), storico in `benchmark/history/20261020_2/` con report, executive summary e confronto con `20261020_1`; timeout `phi3:mini` su `estrazione_json` aperto in `ToDo.md` `#benchmark` · P1 · Progetto
- Benchmark: run `20261020_1` (middleware nuovo, Laya su GPU, pausa 300 s), storico in `benchmark/history/20261020_1/` con report e executive summary; confronto con `20261019_3` e residui aggiornati in `ToDo.md` `#benchmark` · P1 · Progetto
- Versionati a 1.0.1 i documenti L0 `AGENT-PROTOCOL.md`, `references/agent-versioning.md`, `references/extension-scaffold.md`; modulo `a-agentzero` a 1.8.6 `#docs` · Progetto
- Benchmark: sezione "Vincoli operativi" nel README (`--output` dentro `--run-dir`, nessun cooldown nel runner, `setsid`, copie del generatore), storico `20261019_3` e residui in `ToDo.md` `#benchmark` · P1 · Progetto
- GitHub Actions portate a runtime Node 24: `actions/checkout@v5`, `actions/setup-python@v6` `#infra` · Progetto
- Ripristinata versione `version/SKILL.md` a 1.2.1 (frontmatter era regredito a 1.0.0) `#infra` · HAL
- Aggiunto `.gitignore` per escludere `.env` e `.env.*` (mantiene `.env.example`) `#infra` · Progetto
- Rafforzato `SystemEvaluationEngine`: promozione fail-closed su qualità per task, validazione semantica indipendente, latenza serving comparabile e rifiuto dei benchmark troncati; durata end-to-end separata dalla latenza. `#system2-gating` · P1 · HAL
- Ottimizzazione prompt e progressive disclosure per skill ad alto carico (@learn, @sync, @slice, @cycle) `#techdebt` · P1 · HAL
- Integrazione System 1 (Laya) per routing e scoring euristico (@learn, @version, @improve, @document) `#feature` · P1 · HAL
- Diff-tiering e pre-filtraggio contestuale working tree (@commit, @review, @improve) `#infra` · P1 · HAL
- Pipeline CLI deterministica per igiene backlog e flush changelog (@todo) `#infra` · P1 · HAL
- Script deterministico per bump semver e aggiornamento frontmatter (@version) `#infra` · P1 · HAL
- Standardizzazione contratti di output compatti e rimozione boilerplate (Tutti i 10 skill) `#techdebt` · P2 · HAL
- Modalità silenziosa diff-only e analizzatore CLI per sincronizzazione e generalizzazione (@sync) `#infra` · P2 · HAL
- Filtraggio e troncamento log per runner di test e gate Make (@cycle) `#infra` · P2 · HAL

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

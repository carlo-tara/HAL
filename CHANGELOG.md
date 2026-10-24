# Changelog — HAL Project

Tutte le modifiche e le evoluzioni rilevanti del progetto HAL sono documentate in questo file.

Il formato è basato su [Keep a Changelog](https://keepachangelog.com/it/1.1.0/),
e questo progetto aderisce a [Semantic Versioning](https://semver.org/lang/it/).

## [Unreleased]

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

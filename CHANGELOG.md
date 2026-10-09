# Changelog — HAL Project

Tutte le modifiche e le evoluzioni rilevanti del progetto HAL sono documentate in questo file.

Il formato è basato su [Keep a Changelog](https://keepachangelog.com/it/1.1.0/),
e questo progetto aderisce a [Semantic Versioning](https://semver.org/lang/it/).

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

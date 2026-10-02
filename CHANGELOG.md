# Changelog — HAL Project

Tutte le modifiche e le evoluzioni rilevanti del progetto HAL sono documentate in questo file.

Il formato è basato su [Keep a Changelog](https://keepachangelog.com/it/1.1.0/),
e questo progetto aderisce a [Semantic Versioning](https://semver.org/lang/it/).

## [Unreleased]

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

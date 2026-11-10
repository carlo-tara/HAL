# Changelog — a-knowledge

## [1.1.7] - 2026-11-09

### Changed

- Sync selettivo [sync:safe] da a-agentzero 1.13.3 (commit L0: passo 7 auto-voto post-commit T-33B98, gate steward risolto con ok esplicito): `extends-version` allineato, bump patch, nessun cambio al body.

## [1.1.6] - 2026-11-09

### Changed

- Sync selettivo [sync:safe] da a-agentzero 1.13.2 (voci solo infrastruttura L0: nota Tool `graph` 1.0.4 — builder handoff da consumer in `agents/scripts/harness-prompt-builder.sh`, e tool-pitfalls learn 1.6.4): `extends-version` allineato, bump patch, nessun cambio al body.

## [1.1.5] - 2026-11-01

### Changed

- Sync L0 a-agentzero `extends-version` 1.13.0 → 1.13.1: voce pending = sola aggiunta documentale `references/extension-scaffold.md` §4–5 (contratto naming loader per skill L2: `name` kebab-case pari alla directory; nessun delta di protocollo) [sync:safe]; body L1 invariato

Formato [Keep a Changelog](https://keepachangelog.com/it/1.1.0/). Versionamento semver, ownership di `/version`.

## [1.1.4] - 2026-10-30

### Changed

- Sync L0 a-agentzero `extends-version` 1.12.0 → 1.13.0: voci pending = quattro regole di protocollo in `AGENT-PROTOCOL.md` (§ contesto, dichiarazioni, cache: append-only dichiarazioni iniettate, mai reinserire `reasoning_content`, ordering static-first, retention provider) e fix infrastrutturale `scripts/sync-agents.sh` § `report_workspace_links` [sync:safe]; body L1 invariato

## [1.1.3] - 2026-10-29

### Changed

- `scripts/extract.py` (ToDo N24, doc QwenCloud §connection reuse): factory `laya_client(timeout)` con singolo `httpx.Client` per run riusato da `cmd_check` e `route_chapter_laya` (prima: due istanze `httpx.Client` dentro funzioni invocate in loop, nessuna `close()` → leak); chiusura registrata via `atexit`; contratto in `tests/test_bundle_http_reuse.py` [sync:safe]

## [1.1.2] - 2026-10-29

### Added

- Nota Batch API (-50% oltre soglia di volume) nello stub `cmd_distill` di `scripts/extract.py`, con rimando alla regola task-vs-batch in `docs/25_task_vs_batch.md` (ToDo N23, grafo 2026-10-28) [sync:safe]

## [1.1.1] - 2026-10-28

### Changed

- Sync L0 a-agentzero `extends-version` 1.11.0 → 1.12.0: voci pending solo infrastruttura L0 (comandi canonici cycle/graph, agent-todo.py flush, utility learn 1.5.0) [sync:safe]; body L1 invariato

## [1.0.0] - 2026-10-24

### Added

- Baseline agente L1 Knowledge / Context Engineering: pipeline a tre fasi `check → extract → distill → query` con separazione deterministico-locale / generativo.
- `references/pipeline.md` — modello di costo CPU/GPU/token e delta "o migliori" rispetto a book-to-skill.
- `references/extraction-matrix.md` — formato → tool → costo, install, `--check`, politica OCR e cache.
- `references/context-budget.md` — disclosure progressiva, discovery-loop tax, routing System 1, cache HAL.
- `references/modes.md` — modalità operative e mappa sui modi book-to-skill.
- Estrazione **CPU-first, zero GPU, zero token**; distillazione una-tantum su modello free/flash; query con routing Laya + un capitolo (~5k token).
- Campi `version` e `extends-version: 1.10.1` (allineato a a-agentzero 1.10.1) [sync:safe]

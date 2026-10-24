# Changelog — a-knowledge

Formato [Keep a Changelog](https://keepachangelog.com/it/1.1.0/). Versionamento semver, ownership di `/version`.

## [1.0.0] - 2026-10-24

### Added

- Baseline agente L1 Knowledge / Context Engineering: pipeline a tre fasi `check → extract → distill → query` con separazione deterministico-locale / generativo.
- `references/pipeline.md` — modello di costo CPU/GPU/token e delta "o migliori" rispetto a book-to-skill.
- `references/extraction-matrix.md` — formato → tool → costo, install, `--check`, politica OCR e cache.
- `references/context-budget.md` — disclosure progressiva, discovery-loop tax, routing System 1, cache HAL.
- `references/modes.md` — modalità operative e mappa sui modi book-to-skill.
- Estrazione **CPU-first, zero GPU, zero token**; distillazione una-tantum su modello free/flash; query con routing Laya + un capitolo (~5k token).
- Campi `version` e `extends-version: 1.10.1` (allineato a a-agentzero 1.10.1) [sync:safe]

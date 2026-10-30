# Changelog — competenza graph

Formato Keep a Changelog + Semantic Versioning. Tag sync sul padre `a-harness`.

## [Unreleased] - 2026-10-20

### Changed

- Rimossi riferimenti a Cursor nei percorsi: `.cursor/skills/` → `.agents/skills/`, `.cursor/product/` → `product/`, `.cursor/brands/` → `brands/`. Versioni: `graph` 1.3.2 [sync:safe]

## [1.4.2] - 2026-10-30

### Added

- `references/graph-extended.md`: regola «Gate passivi» (riverifica con misura diretta dei prerequisiti prima di marcare skip nei re-run) e nota «handoff-write fonde i campi» (passare sempre `--field date=` e i campi semantici aggiornati). Versione: `graph` 1.4.2 [sync:safe]

## [1.4.1] - 2026-10-28

### Fixed

- `references/graph-extended.md` § Lean: citava `product/handoff-graph.json` e l'esempio `handoff-write graph` senza `--dir` (default tool `product/` → shadow copy fuori canone, caso 2026-10-27); ora `product/state/` + `--dir product/state` obbligatorio con nota `tool-pitfalls` § Writer canonico. Versione: `graph` 1.4.1 [N21]

## [1.3.0] - 2026-09-18

### Added

- Lean/deterministic: prompt-builder ≤200 token + `handoff-graph.json`; multi-cycle legge solo handoff+nodo [sync:safe]

## [1.2.1] - 2026-09-18

### Added

- Frontmatter `model: orcarouter/deepseek/deepseek-v4-flash` + `model-fallback: cursor-default`; slash L0 `/graph` [sync:safe]

## [1.2.0] - 2026-09-15

### Added

- Competenza graph / Work Graph (baseline pre-changelog locale) [sync:safe]

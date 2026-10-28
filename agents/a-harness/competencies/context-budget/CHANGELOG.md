# Changelog — competenza context-budget

Formato Keep a Changelog + Semantic Versioning. Tag sync sul padre `a-harness`.

## [Unreleased] - 2026-10-20

### Changed

- Rimossi riferimenti a Cursor nei percorsi: `.cursor/skills/` → `.agents/skills/`, `.cursor/product/` → `product/`, `.cursor/brands/` → `brands/`. Versioni: `context-budget` 1.3.1 [sync:safe]

## [1.3.2] - 2026-10-28

### Fixed

- Regola 10: path canone handoff `product/state/handoff-{graph,slice,cycle,todo}.json` con `--dir product/state` esplicito (il default `product/` genera shadow copy — caso 2026-10-27, voce ToDo «Skill canoniche» N21). Versione: `context-budget` 1.3.2 [N21]

## [1.3.0] - 2026-10-14

### Added

- Quiet test default: output sintetico full GREEN / selective RED, log esteso rotante settimanale su file in `.gitignore` per preservare il context window [sync:safe]

## [1.2.0] - 2026-09-18

### Added

- Brief slash ≤200 token via `harness-prompt-builder.sh`; handoff-*.json anti context-bloat [sync:safe]

## [1.1.0] - 2026-09-15

### Added

- Baseline context-budget (≤4 file, progressive disclosure) [sync:safe]

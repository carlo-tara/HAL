# Changelog — competenza graph

Formato Keep a Changelog + Semantic Versioning. Tag sync sul padre `a-harness`.

## [Unreleased] - 2026-10-20

### Changed

- Rimossi riferimenti a Cursor nei percorsi: `.cursor/skills/` → `.agents/skills/`, `.cursor/product/` → `product/`, `.cursor/brands/` → `brands/`. Versioni: `graph` 1.3.2 [sync:safe]

## [Unreleased]

## [1.3.0] - 2026-09-18

### Added
- Lean/deterministic: prompt-builder ≤200 token + `handoff-graph.json`; multi-cycle legge solo handoff+nodo [sync:safe]

## [1.2.1] - 2026-09-18

### Added
- Frontmatter `model: orcarouter/deepseek/deepseek-v4-flash` + `model-fallback: cursor-default`; slash L0 `/graph` [sync:safe]

## [1.2.0] - 2026-09-15

### Added
- Competenza graph / Work Graph (baseline pre-changelog locale) [sync:safe]

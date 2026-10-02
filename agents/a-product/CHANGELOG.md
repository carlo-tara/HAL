# Changelog — a-product

## [Unreleased]

## [2.1.0] - 2026-10-02

### Added
- System 1 (Laya) Gating in Product Discovery: pre-filtro di intake (`router.py routing`), scoring euristico di backlog (`router.py score`) e categorizzazione rapida JTBD/ODI prima di attivare le analisi approfondite System 2 [sync:safe]

## [1.2.2] - 2026-09-18

### Changed
- Sync padre: extends-version a-agentzero → 1.6.15 (lean L0 cmds) [sync:safe]




## [1.2.1] - 2026-09-17

### Added
- Frontmatter `model: orcarouter/deepseek/deepseek-v4-flash-free` + `model-fallback: cursor-default` (OrcaRouter preferred; Cursor default se non raggiungibile) [sync:safe]
- Sync L0 a-agentzero `extends-version: 1.6.14` (preferred model frontmatter) [sync:safe]

## [1.2.0] - 2026-09-15

### Added
- Anti–**Build Trap** intake (Outcome vs Output, Success signal, reframe/`a-po` `/triage`) [sync:review]
- **Product Kata** light nello operating flow (Direction → Current state → Obstacles → Experiment path) [sync:review]
- Reference [references/escaping-build-trap-map.md](references/escaping-build-trap-map.md) [sync:safe]

### Changed
- Output contract outcome-first + learning / next Kata step; agents allineati [sync:review]

## [1.1.1] - 2026-09-15

### Changed
- Sync L0 a-agentzero `extends-version: 1.6.13` (/learn ! ToDo+docs pointer) [sync:safe]


## [1.1.0] - 2026-09-15

### Added
- § **Profilo B2B** (flow, Cascata post-strategia GTM, Pilot fit check) — canone da fold `a-b2b` [sync:review]

### Changed
- Pin `extends-version` a-agentzero → 1.6.12; `a-b2b` = facade ingresso, non orchestra peer separata [sync:review]

## [1.0.0] - 2026-09-15

### Changed
- Pin `extends-version` a-agentzero → 1.6.11 (registry birth) [sync:safe]

### Added
- L1 peer orchestrator: intake + delegation matrix (a-po, personas, jtbd, gherkin, enrichment; B2B → a-b2b)
- Non-goals freeze: no PRD authoring, no enrichment/BDD execution
- `deploy.sh`, `agents/a-product.md`, `extension-template.md` [sync:review]

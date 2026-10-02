# Harness changelog — HAL

Solo cambiamenti **fabbrica** (Makefile, hooks, rules, gate). Non feature prodotto/skill dominio.

## [Unreleased]


## [1.1.21] - 2026-09-17

### Changed
- Sync L1 a-harness `extends-version: 1.5.11` (OrcaRouter model frontmatter) [sync:safe]

### Changed
- `/document`: README + operativo + discovery + manuale harness — `a-product`, facade `a-b2b`, `/learn` ToDo/docs, `ToDo.md` in albero (2026-09-15)
- L2 `harness-agentfactory` **1.1.0** (minor): Platform API anti-dup + steward liste L1 / Unreleased hygiene
- Liste L1 in `docs/operativo.md` / comandi snapshot-test allineate a `sync-agents.sh`
- `/document`: README + operativo — Platform API, a-uiux/a-harness, RGR; rimossa tabella versioni shadow (2026-08-13)

### Removed
- Target Makefile `frontmatter-ok` (duplicato di `frontmatter-all`)
- Dead files root `helloworld.md`, `testo-prova.md`

## Released (fabbrica 2026-09-09 → 2026-09-10)

### Added
- Bootstrap profile **standard**: `Makefile` Platform API, `docs/glossary.md`, `docs/bounded-contexts.md`, `.cursor/product/agent-progress.md`, L2 `harness-agentfactory`
- RGR obbligatorio: `AGENTS.md`, `.cursor/rules/agents-rgr-mandatory.mdc`, `tdd-{red,green,refactor}.mdc`
- Hooks: `.cursor/hooks.json` + `agent-skill-{pretool,edit,stop}-rgr.sh`
- Quality pack: `frontmatter-all`, `shellcheck-ok`, `md-links`, `ready-proof` → `ready-for-review`
- Freeze + GHA `ready-for-review`; DoD in L2; `a-uiux`; `sync-consumer-stale`

### Changed
- L2 1.0.0 → 1.0.5 (RGR override, steward notes, stop+make, quality pack)
- `README.md` § Versioni: verità = `sync-agents.sh --dry-run`

### Removed
- Soft-only stop-hook (sostituito da stop+make + preToolUse deny)

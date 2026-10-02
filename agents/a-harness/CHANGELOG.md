# Changelog

Tutte le modifiche rilevanti a **a-harness** sono documentate in questo file.

Formato basato su Keep a Changelog e Semantic Versioning.
Tag figli: `[sync:safe]`, `[sync:review]`, `[sync:breaking]`.

## [Unreleased]

### Changed
- Appreso da sessione: when-stuck 1.0.1 — anti-pattern `pkill -f` self-match su shell Cursor

## [1.7.0] - 2026-09-18

### Added
- Lean cmd protocol: `scripts/harness-prompt-builder.sh` (≤200 token) + `handoff-*.json` per `/graph` `/slice` `/cycle` `/todo`; competenze graph 1.3.0, todo 1.2.0, context-budget 1.2.0 [sync:safe]

## [1.6.0] - 2026-09-17

### Added
- Coding model ladder (tier + cascata) su 5 modelli OrcaRouter; default `model: orcarouter/deepseek/deepseek-v4.1-flash` [sync:safe]

## [1.5.11] - 2026-09-17

### Added
- Frontmatter `model: orcarouter/deepseek/deepseek-v4-flash` + `model-fallback: cursor-default` (OrcaRouter preferred; Cursor default se non raggiungibile) [sync:safe]
- Sync L0 a-agentzero `extends-version: 1.6.14` (preferred model frontmatter) [sync:safe]

## [1.5.10] - 2026-09-15

### Added
- HFDP Fase 4: [references/gof-meta-patterns.md](references/gof-meta-patterns.md) [sync:safe]

## [1.5.9] - 2026-09-15

### Added
- HFDP Fase 3: stati Plan\|Act\|Stuck\|Ready + Strategy=fase in permission-modes [sync:safe]

## [1.5.8] - 2026-09-15

### Added
- HFDP Fase 2 UL: Adapter↔ACL, Facade↔Make/L1 (anti NEW competency GoF) [sync:safe]

## [1.5.7] - 2026-09-15

### Added
- `/cycle`: Template Method / Hollywood Principle (skeleton RGR + Make/hook) — HFDP Fase 1 [sync:safe]

## [1.5.6] - 2026-09-15

### Changed
- `graph` 1.2.0: `-y` = auto-accept + **multi-cycle** sequenziale fino a fine backlog (hard stop stuck/freeze/Make) [sync:review]

## [1.5.5] - 2026-09-15

### Changed
- `todo` 1.1.0: flush «Già fatto» → `./CHANGELOG.md` (Keep a Changelog / Unreleased, mapping tag→sezione, dedup, prune) [sync:safe]

## [1.5.4] - 2026-09-15

### Changed
- Sync L0 a-agentzero `extends-version: 1.6.13` (/learn ! ToDo+docs pointer) [sync:safe]


## [1.5.3] - 2026-09-15

### Changed
- Sync L0 a-agentzero `extends-version: 1.6.12` (a-product § Profilo B2B / a-b2b facade) [sync:safe]

## [1.5.2] - 2026-09-15

### Changed
- Sync L0 a-agentzero `extends-version: 1.6.11` (registry a-product) [sync:safe]


## [1.5.1] - 2026-09-15

### Changed
- `graph` 1.1.0: flag `-y` auto-accept / skip accept su tutte le modalità input; avvio immediato nodo `next` [sync:safe]

## [1.5.0] - 2026-09-15

### Added
- Competenza `graph` 1.0.0 + slash `/graph`: Loop / Work Graph da context|file|request → `.cursor/product/work-graph.md` (Plan-only, anti graph-trap); pin [graph-loop-source.md](references/graph-loop-source.md) [sync:safe]

### Changed
- `session-progress` 1.1.4: pointer Work Graph → `/graph` [sync:safe]

## [1.4.0] - 2026-09-15

### Added
- Competenza `todo` 1.0.0 + slash `/todo`: igiene Mappa residui `./ToDo.md` (scrivere, priorità, prune, chiarire con UL/BC, ambiguità/dup/conflitti, tag) — trigger su edit file [sync:safe]

### Changed
- `session-progress` 1.1.3: Mappa residui punta a `/todo` (no doppia ownership ops) [sync:safe]

## [1.3.1] - 2026-09-15

### Added
- Track concurrent esplicito: non patchare track altrui; wait+retry (`steward` + anti-pattern `sustainable-pace`) — promosso da harness-wtp [sync:safe]

## [1.3.0] - 2026-09-15

### Added
- Promosso da harness-wtp (alto/medio): proof gate fresco (`MAKE_EXIT`, no `| tail`, no Gate OK stale) in `pr-proof-checklist` + `sustainable-pace` + `session-progress` [sync:safe]
- Gate esclusivo multi-agente (astratto; path lock L2) in `steward` [sync:safe]
- Diff-tab / staged-only + Act ready≠commit in `consumer-platform-hygiene` [sync:safe]
- Accept range ⊆ grafo `require` loadable (ladder FCIS) in `functional-core` [sync:safe]

## [1.2.9] - 2026-09-15

### Changed
- Appreso da sessione: Reason why in description + regole di ingaggio subagent [sync:safe]



## [1.2.8] - 2026-09-15

### Added
- Appreso da sessione: mappa residui permanente `./ToDo.md` (session-progress + tabella artefatti); L0 pointer [sync:safe]

## [1.2.7] - 2026-09-15

### Added
- Appreso da sessione: `/cycle` ≠ accept (Plan aperto → ripeti scelte); `accept A+B` = ibrido se compatibile [sync:safe]

## [1.2.6] - 2026-09-15

### Added
- Appreso da sessione: `/accept` senza risposte clarify → lock default consigliati del Plan e Act (permission-modes) [sync:safe]

## [1.2.5] - 2026-09-12

### Added
- SAST / source-code-analysis + **find-and-fix** validato (principi SourceForge SCA + Strix, no runtime) [sync:safe]
- `steward` 1.2.0 → 1.2.1: SAST in CI, find-and-fix, authorized-only [sync:safe]
- `consumer-platform-hygiene.md`: `check-sast`, validated findings, PR/diff scope [sync:safe]

## [1.2.4] - 2026-09-12

### Added
- DevSecOps baseline (findarepo/security): secrets + deps CI-first, **low-noise**, non-goal offensive scanners [sync:safe]
- `steward` 1.1.1 → 1.2.0: mandato CI-first security [sync:safe]
- `consumer-platform-hygiene.md`: sezione DevSecOps opzionale (`check-secrets`, deps/SBOM) [sync:safe]

## [1.2.3] - 2026-09-12

### Added
- Plan **workflow context** (principi suite Scribe): evidence-first, maturity Discover→Agents, Sidekick/Guide Me mapping [sync:safe]
- `session-progress` 1.0.0 → 1.1.0: Capture/Evidence — progress = lavoro reale; stuck → priorità [sync:safe]

### Changed
- `/cycle` Plan: cita evidence-first e workflow context prima di Act [sync:safe]

## [1.2.2] - 2026-09-12

### Added
- Plan semantic layer: **capability-first** + **70/20/10** + pin glossario/BC vivi (Haara / enterprise semantic layer) [sync:safe]
- `ubiquitous-language` 1.0.0 → 1.1.0: glossario = ontologia operativa (entità, relazioni, regole) [sync:safe]
- `bounded-context` 1.0.0 → 1.1.0: Fit-to-whole / anti-silo sul backbone BC [sync:safe]

### Changed
- `/cycle` Plan: cita capability-first e 70/20/10 prima di Act [sync:safe]

## [1.2.1] - 2026-09-12

### Added
- Pin [github-spec-kit-source.md](references/github-spec-kit-source.md): mappa Spec-Driven Development (constitution→converge) → slash a-harness; adopt/non-adopt espliciti [sync:safe]
- `sustainable-pace` 1.1.0 → 1.1.1: passo converge post-`/ready` [sync:safe]

### Changed
- `/cycle` Plan: clarify + analyze cross-artefatto; `/ready` + slice residuo = converge (no silent expand) [sync:safe]
- `sustainable-pace`, `harness-architecture`, agent, handoff-from-gherkin: puntatori Spec Kit [sync:safe]

## [1.2.0] - 2026-09-12

### Added
- `tdd-red` 1.1.0: sezione obbligatoria **Pre-ottimizzazioni** (Prompt lean, Anti context-bloat, Delega per competenza) prima di scrivere i test [sync:review]
- `tdd-green` 1.1.0: pre-ottimizzazioni ereditate/riaffermate da RED (no re-espansione prompt/context; mappa deleghe) [sync:review]

### Changed
- Slash `/red` `/green` `/cycle` + Deleghe: citano pre-ottimizzazioni e Steward [sync:review]

## [1.1.8] - 2026-09-12

### Changed
- `cursor-hooks-recipe.md`: esempio leggero `stop` → whitelist (no `afterFileEdit` → full pre-commit); punta a `consumer-platform-hygiene.md` [sync:safe]

## [1.1.7] - 2026-09-12

### Added
- Reference `consumer-platform-hygiene.md`: whitelist `.cursor`, commit-scope, `test-coverage` / `check-dead-code`, hooks leggeri [sync:safe]
- `platform-api` 1.1.1 → 1.1.2: tabella target opzionali + puntatore hygiene [sync:safe]

## [1.1.6] - 2026-09-08

### Changed
- Sync L0 a-agentzero `extends-version: 1.6.4` (scaffold commit staged-only) [sync:safe]

### Changed
- Export pack Claude (`scripts/export-discovery-claude.sh`) include `a-harness`

## [1.1.5] - 2026-09-08

### Added
- `platform-api`: regole env-flag (`envFlagEnabled`, no `Boolean(process.env)`) e dual-canon asset (`check-parity` / `sync-assets`) [sync:safe]
- `makefile-template.mk`: stub opzionali `check-parity` / `sync-assets`; `pre-commit` dipende da parity [sync:safe]

## [1.1.4] - 2026-09-04

### Changed
- Appreso da sessione: ownership docs (SKILL/meta/manuale) + razionalizzazione per dedup senza togliere gate/competenze; `/slice`/`/cycle` solo in SKILL `[sync:safe]`
- Docs `harness-engineering.md` § Evoluzione e manutenzione (punti 5–6)

## [1.1.3] - 2026-09-04

### Changed
- Razionalizzazione senza perdita di gate: canone ownership docs (SKILL operativo, harness-engineering meta, manuale umano)
- Merge `five-layer` + `seven-stack` → `references/harness-architecture.md`
- Merge pin explainx/thetoolnerd/claudeskills → `references/pin-curated-lists.md`
- Policy evaluation points → `permission-modes.md`; effort map → `extension-template.md`
- Checklist steward → `references/steward-audit-checklist.md`; slim `steward` competency
- SKILL / agent / extension snelliti (no duplicazione principi/deleghe/indici) `[sync:safe]`

### Removed
- `five-layer-harness.md`, `seven-stack-harness.md`, `policy-evaluation-points.md`, `effort-map-template.md`
- `explainx-harness-source.md`, `thetoolnerd-harness-source.md`, `claudeskills-harness-source.md` (contenuto in pin-curated-lists)

## [1.1.2] - 2026-09-02

### Added
- Manuale utente sviluppatori: `docs/a-harness-manuale-utente.md` (§13 riferimento comandi stile man)

### Changed
- Appreso da sessione: canone man §13; chiarire perimetro prima di documentare «tutti» i comandi `[sync:safe]`
- SKILL: puntatore man + regola scope documentazione comandi
- Docs `harness-engineering.md` § Evoluzione punto 4 (documentazione comandi)

## [1.1.1] - 2026-09-02

### Changed
- Appreso da sessione: processo fonti → pin/piano → execute (no edit `.plan.md` in implementazione) `[sync:safe]`
- Docs `harness-engineering.md` § Evoluzione da fonti esterne

## [1.1.0] - 2026-09-02

### Added
- Competenze: `session-progress`, `when-stuck`, `functional-core`
- Slash `/progress`; Plan→Act; bootstrap profiles minimal|standard
- Reference: five-layer, seven-stack, component-decision, permission-modes, policy points, pr-proof, hooks recipe, effort/freeze/progress/learnings/changelog templates
- Pin 9 fonti esterne (`*-source.md`)
- Docs: omonimi Harness, maturity L3, Agent=Model+Harness
- Appreso da sessione: skill-layer positioning, Skills/MCP/Hooks mnemonic, non-goals runtime esterni `[sync:safe]`

### Changed
- `sustainable-pace` — medium slice, PR budget, anti-lazy-delete, PR-as-proof
- `steward` — CI-first, scorecard, freeze, promote→hook/Make
- `platform-api` — bootstrap profiles, no autonomy without make test
- `context-budget` — offload FS, progressive disclosure
- SKILL/agents/extension-template/scaffold → 1.1.0

## [1.0.0] - 2026-09-01

### Added
- L1 Meta-Harness: ciclo TDD XP (Red/Green/Refactor), Steward infra, guardrail DDD
- Competenze: `context-budget`, `sustainable-pace`, `platform-api`, `tdd-red`, `tdd-green`, `tdd-refactor`, `steward`, `ubiquitous-language`, `bounded-context`, `anti-corruption-layer`, `aggregate-root`
- Slash: `/slice`, `/red`, `/green`, `/refactor`, `/cycle`, `/ready`, `/steward`, `/bootstrap`
- Reference: makefile-template, harness-scaffold, glossary-template, bounded-context-map, handoff-from-gherkin
- Guida operativa: `docs/harness-engineering.md`

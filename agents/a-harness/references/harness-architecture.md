# Harness architecture — five-layer + seven-stack

**Agent = Model + Harness.** Due viste equivalenti della stessa skill-layer.

## Five-layer (operativa)

| Layer | a-harness |
|-------|-----------|
| **Interface** | Slash + Task |
| **Orchestration** | `/slice` (Plan: clarify + analyze) → `/cycle` (Act); personas via competenze |
| **Execution** | Env progetto; gate `make` |
| **Verification** | `make test` / `ready-for-review`; fix-until-green + when-stuck; residui → nuovo `/slice` (converge) |
| **Output** | PR-ready + [pr-proof-checklist.md](pr-proof-checklist.md); umano = **intent** |

SDD (Spec Kit) → mapping operativo: [github-spec-kit-source.md](github-spec-kit-source.md) (no CLI obbligatoria).

## Seven-stack (famiglie)

| Famiglia | Implementazione AF |
|----------|-------------------|
| Skills | Competenze path-based, progressive disclosure |
| MCP | Opt-in L2; default Makefile/CLI |
| Sub-agents | Navigator / Driver / Steward via competenze |
| Hooks | [cursor-hooks-recipe.md](cursor-hooks-recipe.md) + Make |
| Permissions | [permission-modes.md](permission-modes.md) |
| Memory | progress, learnings, glossary |
| Evals | `make ready-for-review` + scorecard steward |

Decisioni: [component-decision.md](component-decision.md)  
Pin: [cursor-cloud-harness-source.md](cursor-cloud-harness-source.md) · [pin-curated-lists.md](pin-curated-lists.md) · [github-spec-kit-source.md](github-spec-kit-source.md)

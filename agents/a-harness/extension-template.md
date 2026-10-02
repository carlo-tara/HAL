---
name: harness-{progetto}
extends: a-harness
version: 1.0.0
extends-version: 1.1.4
description: >-
  Delta harness per {progetto}: path Makefile, glossario, bounded contexts,
  profile bootstrap, freeze, override TDD/DDD.
---

# Harness — estensione progetto

Skill figlia (L2). Eredita da `a-harness`. All'avvio: L0 → L1 → **questo file**.

**Plugin** = override/path. **Preset** = `minimal` | `standard` al bootstrap.

## Progetto

| Campo | Valore |
|-------|--------|
| Nome | {nome-progetto} |
| Working directory | {path assoluto} |
| Stack | {es. Node/TS, Python, PHP} |
| Bootstrap profile | minimal \| standard |
| Effort default | fast \| thorough |

## Path locali

| Artefatto | Path |
|-----------|------|
| Platform API | `Makefile` (root) |
| Glossario | `docs/glossary.md` |
| Bounded contexts | `docs/bounded-contexts.md` |
| Progress | `.cursor/product/agent-progress.md` |
| Learnings (opz.) | `.cursor/product/session-learnings.md` |
| Freeze (opz.) | `.cursor/product/harness-freeze.md` |
| Features | `.cursor/product/features/` |
| Hooks (opz.) | `.cursor/hooks.json` |

## Target Makefile

| Target | Comando effettivo |
|--------|-------------------|
| `test-unit` | {es. npm test} |
| `pre-commit` | {es. npm run lint && npm run typecheck} |
| `ready-for-review` | {dipendenze reali} |

## Effort (opz.)

| Task type | Effort |
|-----------|--------|
| Bug one-liner / rename scoped | fast |
| Feature slice medium | thorough |
| Refactor cross-module | thorough (spezza slice) |
| Bootstrap / steward | thorough |

## Bounded context attivi

| Context | Path modulo | Note |
|---------|-------------|------|
| {es. Billing} | `src/modules/billing/` | {eventi pubblici} |

## Override workflow

{Se nessuno: «Nessun override — segui L1».}

Deleghe e slash: eredità L1 (`a-gherkin` / `a-po` / `/steward` / `/learn` / `/sync`).

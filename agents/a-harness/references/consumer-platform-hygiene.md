# Consumer Platform hygiene (optional Steward recipe)

Patterns validated on WTP App (`harness-wtp`). Promote into L2 as concrete Make targets + path lists; do **not** copy WTP denylist/path literals into other repos.

## Git whitelist for `.cursor/*`

Many repos ignore `.cursor/*` by default. Versioned agents/skills/rules need:

1. A registry file (e.g. `.cursor/versioned-cursor-paths`) listing paths that must remain trackable
2. Explicit `!` whitelist lines in `.gitignore`
3. A Make target (e.g. `check-cursor-whitelist`) that fails if a listed path is missing or gitignored

Always-on rule tip: document the three steps so agents update whitelist without re-prompt.

## Mixed commit scope

Optional Make target (e.g. `check-harness-commit-scope`) that fails when the git index mixes **Platform API / harness** paths with **product WIP** paths. Allowlist/denylist are **L2-specific**.

## Diff-tab / staged-only commits

When the UI / user action lists **staged files as authoritative** («do not stage additional» / commit-and-push on the current index):

1. `git commit` **only** what is already staged — no extra `git add` «for completeness»
2. Unstaged WIP stays out; push only if requested
3. If the index is **empty** and the listed paths are **already in HEAD** → do **not** empty-commit; push → up-to-date (or report nothing to commit)
4. If the index is **empty** but listed paths still have **unstaged** diffs vs HEAD → do **not** silent `git add`; push tip unchanged and tell the user to re-stage in UI
5. **Post-cycle:** if the slice is already in HEAD, commit only **your** residual (e.g. unblock gate / learn bump) — do not stage concurrent agents’ skill/docs tangles
6. **Act `ready=0` ≠ commit done:** green Plan/cycle with files still untracked → P0 is commit the loadable graph, not re-GREEN

L0 may already cover empty-index + authoritative path list; this section is the harness gate companion.

## Coverage & dead-code audits (optional, often outside `ready-for-review`)

| Target (name local) | Role |
|---------------------|------|
| `test-coverage` | Run coverage on the **full** unit suite (not a subset smoke) |
| `check-dead-code` | Heuristic unreferenced-module / orphan-test report; not a proof |

Wire real stack commands in L2. Do not gate `ready-for-review` on coverage thresholds until the team agrees a number.

## DevSecOps baseline (optional, CI-first)

Principio (findarepo/security *How to choose*): **secret scanning + dependency auditing in CI first**; prefer **low-noise** defaults; offensive tooling non è canone harness.

| Target (name local) | Role |
|---------------------|------|
| `check-secrets` | Fail su secret in tree / history scoped (gitleaks-class); mai secret in progress/skill |
| `check-deps` / SBOM | Audit dipendenze / misconfig (trivy-class) sul stack consumer |
| `check-sast` | Source-code analysis / SAST low-noise (PMD/cppcheck/Infer-class); preferisci FP bassi |
| (avoid) offensive scanners | Nuclei/AI pentest / Strix runtime — fuori Platform API a-harness; solo **authorized** esterno |

**Validated findings (find-and-fix):** uno finding entra in Act solo con evidence (fail riproducibile o gate). Preferisci **PR/diff scope** (file toccati), non full-repo scan come default di `/slice`.

Wire in L2. Non aggiungere target che il team silenzierà (low-noise). HAL meta-repo: secrets in progress = fail di processo; deps/SBOM/SAST N/A se non c’è app stack.

## Cursor hooks (optional)

Prefer Make as the guarantee. If using `.cursor/hooks.json`, keep hooks **light** (e.g. `stop` → whitelist check) — avoid full `make pre-commit` on every file edit.

See [cursor-hooks-recipe.md](cursor-hooks-recipe.md).

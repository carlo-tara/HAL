---
name: harness-hal
extends: a-harness
version: 1.0.0
extends-version: 1.8.1
description: >-
  Delta harness per HAL Gateway: Platform API root (Makefile specchio CI), path
  artefatti, profile bootstrap standard, N/A documentati (int/e2e/parity),
  freeze config modelli, mirror bundle agents/.
---

# Harness — estensione progetto (L2) — HAL Gateway

Skill figlia (L2). Eredita da `a-harness`. All'avvio: L0 → L1 → **questo file**.

**Plugin** = override/path. **Preset** = `standard` (bootstrap 2026-10-25).

## Progetto

| Campo | Valore |
|-------|--------|
| Nome | HAL Gateway |
| Working directory | `/var/www/hal_gateway` |
| Stack | Python 3.12 · unittest · requests/urllib3 (dev: httpx, python-dotenv) |
| Bootstrap profile | standard |
| Effort default | thorough |

**Confine chiave:** la root è l'**app gateway** (Platform API = `Makefile` root). Il bundle
agenti in `agents/` è un meta-repo con **propria Platform API** (`agents/Makefile`,
version-chains/sync). `/steward` root non tocca `agents/Makefile` e viceversa.

## Path locali

| Artefatto | Path |
|-----------|------|
| Platform API | `Makefile` (root) — rispecchia `.github/workflows/ready-for-review.yml` |
| Glossario | `docs/glossary.md` |
| Bounded contexts | `docs/bounded-contexts.md` |
| Progress (append-only) | `product/state/agent-progress.md` (convenzione del repo, non docs/) |
| Learnings (journal `/learn`) | `product/state/session-learnings.md` |
| Freeze | `product/state/harness-freeze.md` |
| Work graph / handoff | `product/state/work-graph.md`, `product/state/handoff-*.json` |
| Harness changelog | `docs/harness-CHANGELOG.md` |
| Residui | `ToDo.md` (root, Mappa residui) |
| Bundle L2 canonica | `agents/project-skills/harness-hal/` (symlink `.agents/skills/harness-hal`) |
| Log test (quiet, rotazione ISO) | `logs/test-YYYY-WW.log` (gitignored) |

## Target Makefile

| Target | Comando effettivo |
|--------|-------------------|
| `check-secrets` | `python3 scripts/check_secrets.py` |
| `check-deps` | `python3 scripts/check_deps.py` |
| `check-sast` | `python3 scripts/check_sast.py` |
| `test-unit` | `python3 -m unittest discover -s tests` (QUIET=1: summary unico se GREEN, solo FAIL/ERROR se RED; full log → `logs/`) |
| `test-int` | **N/A** — CI non separa un tier di integrazione; `@true` |
| `test-e2e` | **N/A** — nessuna suite browser/E2E → throttle 1h e mutex PID **non applicabili**; `@true` |
| `pre-commit` | `check-secrets check-deps check-sast` + `compileall -q *.py scripts` |
| `check-standards` | alias di `pre-commit` |
| `check-parity` | **N/A** dual-canon — i mirror del bundle (`.agents/skills`, `.zed/prompts`) sono governati da `agents/Makefile` (`sync-agents --dry-run`) e `agents/scripts/link-workspace-skills.sh`; dopo modifiche al bundle eseguire lo script di link |
| `sync-assets` | **N/A** — nessun artefatto canone→runtime nel gateway |
| `ready-for-review` | `pre-commit` + `test-unit` (+ tier N/A dichiarati) — parity con il workflow CI omonimo |
| `db-up` / `seed-data` | **N/A** — nessun DB effimero in CI; `system2_metrics.sqlite3` è locale |

## Regole L2 (delta su L1)

1. **CI-first:** ogni nuovo gate locale DEVE avere corrispondenza in
   `.github/workflows/ready-for-review.yml` (o il workflow va aggiornato nello stesso slice).
2. **Niente pytest nel gate:** CI installa solo `requirements-dev.txt` (senza pytest);
   `test-unit` usa `unittest discover` per non divergere. pytest resta ammesso interattivo.
3. **Modelli:** `SystemTwoEngine.ACTIVE_MODEL_NAME` in `global_config.py` è la fonte;
   non assegnare modelli diversi ai subagent (AGENTS.md root). Feature flag OrcaRouter:
   numeric `LLM_EXTERNAL_MODE` (`0/1`) — flag booleani sempre numerici, mai truthy-string.
4. **System 1 (Laya) pre-filtro:** prima di Act su routing/triage/choice usare
   `python3 router.py ...` (routing/score/choice/noul) come da L1.
5. **Doppio CHANGELOG:** `CHANGELOG.md` root = storia prodotto; `docs/harness-CHANGELOG.md`
   = solo fabbrica (Makefile, gate, regole). Non mescolare.

## Effort

| Task type | Effort |
|-----------|--------|
| Igiene / edit banale | fast |
| Gate 1–7 / router / cache slice | thorough |
| Refactor cross-modulo (gateway_core ↔ global_config) | thorough (spezza slice ≤4 file) |
| Bootstrap / steward | thorough |

## Bounded context attivi

| Context | Path modulo | Note |
|---------|-------------|------|
| Gateway Core | `gateway_core.py`, `global_config.py` | orchestrazione System 2, cache L1, provider |
| System 1 / Laya | `laya_service.py`, `router.py`, `system1_preflight.py` | gating Gate 1–7, triage/routing |
| Benchmark | `benchmark/`, `scripts/bench_hot_paths.py` | token gating, run baseline |
| Observability & Retention | docs `05`, `system2_metrics.sqlite3` | eventi, redaction, encryption |
| DevSecOps Tooling | `scripts/check_*.py` + test validatori | CI-first, low-noise |
| Agent Platform (bundle) | `agents/` | Platform API separata (`agents/Makefile`) |

Dettagli e regole di import: `docs/bounded-contexts.md`.

## Override workflow

Nessun override TDD/DDD — segui L1 (`a-harness` 1.8.1). Unici delta: tabella N/A sopra
(e2e/int/parity/db) e confine §"Confine chiave" con il bundle `agents/`.

Deleghe e slash: eredità L1 (`a-gherkin` / `a-po` / `/steward` / `/learn` / `/sync`).

---
name: harness-hal-mcp-tools
extends: a-harness
version: 1.1.1
extends-version: 1.10.1
description: >-
  Reason why: senza Platform API e gate, il progetto delegato resterebbe uno script privo di uscita verificabile.
  Delta harness per hal_mcp_tools (MCP test-runner/analytics): Makefile Platform API, path artefatti, N/A documentati, safety note specifiche del servizio MCP/locale.
---

# harness-hal-mcp-tools — delta L2

Skill figlia (L2). All'avvio: L0 `a-agentzero` → L1 `a-harness` → **questo file**. Solo override di path, stack e gate — non rieseguire il workflow L1 nel body.

## Progetto

| Campo             | Valore                                                                                                      |
| ----------------- | ----------------------------------------------------------------------------------------------------------- |
| Nome              | hal_mcp_tools (MCP test-runner/analytics)                                                                   |
| Working directory | `/var/www/hal_mcp_tools`                                                                                    |
| Stack             | Python 3.12 stdlib-only core (JSON-RPC stdio, pattern mcp_laya.py); `playwright` solo nel driver-subprocess |
| Bootstrap profile | **standard** (2026-10-31)                                                                                   |
| Effort default    | thorough                                                                                                    |

## Path locali

| Artefatto        | Path                                                                                                        |
| ---------------- | ----------------------------------------------------------------------------------------------------------- |
| Platform API     | `Makefile` (root)                                                                                           |
| Glossario        | `docs/glossary.md`                                                                                          |
| Bounded contexts | `docs/bounded-contexts.md`                                                                                  |
| PRD              | `docs/PRD.md`                                                                                               |
| Progress         | `docs/product/agent-progress.md`                                                                            |
| Preflight S1     | `app/s1.py` + `logs/s1-decisions.jsonl` (gitignored)                                                        |
| Installer Zed    | `app/install_zed.py` (CLI off-runtime)                                                                      |
| Browser driver   | `app/playwright_tools.py` (lato MCP) + `app/playwright_driver.py` (subprocess; env `HAL_PLAYWRIGHT_DRIVER`) |
| Residui          | `./ToDo.md`                                                                                                 |
| Changelog        | `CHANGELOG.md` (Keep a Changelog)                                                                           |
| Docker           | `Dockerfile` + `docker-compose.yml`                                                                         |

## Target Makefile

| Target             | Comando                                                   |
| ------------------ | --------------------------------------------------------- |
| \`test-unit\`      | \`\$(PY) -m pytest -q\` (quiet, full GREEN/RED selettivo) |
| \`pre-commit\`     | \`check-static-diff\` (ruff sul diff + parity N/A)        |
| `ready-for-review` | `check-standards test-unit test-int test-e2e`             |
| `install-zed`      | dry-run `app.install_zed`; `APPLY=1` scrive (passo umano) |

## N/A documentati (L1)

- \`test-int\`/\`test-e2e\`: nessun tier separato nel MVP — contract JSON-RPC in M2 (ToDo P2).
- \`check-parity\`/\`sync-assets\`: nessun dual-canon (server = \`app/\`, nessuna copia runtime).

## Bounded context attivi

Vedi `docs/bounded-contexts.md`; ogni `/slice` dichiara il context toccato.

## Safety note specifiche

- **Verità dell'exit**: `test_run` deve sempre propagare l'exit reale del processo (niente pipe mascheranti; `TIMEOUT` = esito dedicato 124, non errore di protocollo) — test dedicati in `tests/test_runner.py`.
- **Output budget**: risposta tool ≤ HEAD5+TAIL15+failed_lines con cap assoluto 4000 char (`truncated`); log integrali SOLO su file (`log_path`), mai in contesto.
- **Preflight fail-open**: `app/s1.py` non blocca mai il MCP (astensione = comportamento senza S1); modula solo la verbosità, status/exit restano deterministici (KPI-3).
- **Secret**: chiavi API solo da env (`LAYA_API_KEY`; il placeholder locale `sk-local` del reference non è un segreto), mai nei log.
- **Read-only**: mount del repo target `:ro` di default; store telemetria aperto in `mode=ro`; nessuna scrittura su `events/`.
- **Playwright fuori dal core**: `app/server.py` non importa mai `playwright` — solo il driver-subprocess `app/playwright_driver.py` (channel `chrome`/`msedge` = browser di sistema, nessun download). Il driver parte via file path ⇒ vietato in `app/` un modulo denominato `playwright.py` (shadowing del pacchetto). Contratti identici a `test_run`: exit reale, `TIMEOUT`=124, cap 4000 char, artefatti (screenshot/testo integrale) solo su file; e2e reale skipata se browser/playwright assenti, unit con fake driver via `HAL_PLAYWRIGHT_DRIVER`.
- **Rinomina in tree condiviso**: dopo aver rinominato moduli/file, grep dei letterali del vecchio nome (path, `with_name`, env, messaggi, docs) + e2e reale: un rename parziale da sessione parallela (2026-11-01) lasciò `DRIVER_FILE` su un file inesistente con test unit verdi.
- **Gate statico senza tool a host**: ruff/pyright non installabili (`pip --user` bloccato da PEP 668); mai creare `venv/` nel repo (il `PY` del Makefile lo userebbe senza pytest/playwright) — per i check usare un venv temporaneo esterno (es. `/tmp`) e rimuoverlo dopo.

## Ref cross-progetto

- Consumer/mandante: `hal_system2/ToDo.md` cluster «MCP delegation — token shrink» (`#token-shrink`).
- Shared: `agents` e `.agents` = symlink verso `/var/www/hal_gateway`; i gate L0/L1 valgono invariati.

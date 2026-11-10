---
name: harness-hal-mcp-tools
extends: a-harness
version: 1.2.2
extends-version: 1.10.4
description: >-
  Reason why: senza Platform API e gate, il progetto delegato resterebbe uno script privo di uscita verificabile.
  Delta harness per hal_mcp_tools (MCP test-runner/analytics): Makefile Platform API, path artefatti, N/A documentati, safety note specifiche del servizio MCP/locale.
---

# harness-hal-mcp-tools — delta L2

Skill figlia (L2). All'avvio: L0 `a-agentzero` → L1 `a-harness` → **questo file**. Solo override di path, stack e gate — non rieseguire il workflow L1 nel body.

## Progetto

| Campo             | Valore                                                                                                                                                                |
| ----------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Nome              | hal_mcp_tools (MCP test-runner/analytics)                                                                                                                             |
| Working directory | `/var/www/hal_mcp_tools`                                                                                                                                              |
| Stack             | Python 3.12 stdlib-only core (JSON-RPC stdio, pattern mcp_laya.py); `playwright`/`duckdb` solo nei driver-subprocess; scraping (`scrape`) puro stdlib, nessuna deroga |
| Bootstrap profile | **standard** (2026-10-31)                                                                                                                                             |
| Effort default    | thorough                                                                                                                                                              |

## Path locali

| Artefatto        | Path                                                                                                                                            |
| ---------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| Platform API     | `Makefile` (root)                                                                                                                               |
| Glossario        | `docs/glossary.md`                                                                                                                              |
| Bounded contexts | `docs/bounded-contexts.md`                                                                                                                      |
| PRD              | `docs/PRD.md`                                                                                                                                   |
| Progress         | `docs/product/agent-progress.md`                                                                                                                |
| Preflight S1     | `app/s1.py` + `logs/s1-decisions.jsonl` (gitignored)                                                                                            |
| Installer Zed    | `app/install_zed.py` (CLI off-runtime)                                                                                                          |
| Browser driver   | `app/playwright_tools.py` (lato MCP) + `app/playwright_driver.py` (subprocess; env `HAL_PLAYWRIGHT_DRIVER`)                                     |
| Scraping driver  | `app/scrape_tools.py` (lato MCP) + `app/scrape_driver.py` (subprocess **puro stdlib**; env `HAL_SCRAPE_DRIVER`)                                 |
| Product-Oracles  | `app/impersonate_tools.py` + registry statico `app/oracles.py` (tool `impersonate`, unico tool puramente in-process: zero subprocess, zero LLM) |
| Residui          | `./ToDo.md`                                                                                                                                     |
| Changelog        | `CHANGELOG.md` (Keep a Changelog)                                                                                                               |
| Docker           | `Dockerfile` + `docker-compose.yml`                                                                                                             |

## Target Makefile

| Target             | Comando                                                                            |
| ------------------ | ---------------------------------------------------------------------------------- |
| \`test-unit\`      | \`\$(PY) -m pytest -q -m "not int"\` (quiet, full GREEN/RED selettivo)             |
| `test-int`         | `$(PY) -m pytest -q -m int` (contract JSON-RPC su spawn reale, tier consegnato M2) |
| \`pre-commit\`     | \`check-static-diff\` (ruff sul diff + parity N/A)                                 |
| `ready-for-review` | `check-standards test-unit test-int test-e2e`                                      |
| `install-zed`      | dry-run `app.install_zed`; `APPLY=1` scrive (passo umano)                          |

## N/A documentati (L1)

- \`test-e2e\`/\`check-parity\`/\`sync-assets\`: nessun E2E dual-client oltre Zed (il contratto stdio è coperto da `test-int`, 2026-11-01); nessun dual-canon (server = \`app/\`, nessuna copia runtime).

## Tag ToDo dichiarati (L2)

Canone L1: `feature`, `bug`, `techdebt`, `uiux`, `docs`, `infra`, `spike`. Questo progetto dichiara inoltre (uso consolidato 2026-11-05/06, mapping flush → `### Changed` come «altri»):

- `#xp` — azione eseguibile micro-ciclo TDD/XP nata dalle letture degli oracoli code (`/impersonate kentbeck`/`unclebob`)
- `#product` — gate decisionale di prodotto con esperimento pre-registrato (falsificatore dichiarato)

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
- **Scraping senza motore**: `app/scrape_driver.py` è **puro stdlib** (`urllib` + `html.parser` + `robotparser`): nessuna deroga §5, nessun auto-skip, funziona anche in `python:3.12-slim`; contratti identici a `playwright_tools` (exit reale, TIMEOUT=124, cap 4000, artefatti solo in `out_dir`/`pages` + `index.json`). Test statico di confine: mai `import playwright`/`duckdb` nei moduli scraping, mai importare il driver come modulo. Ponte JS: `playwright_navigate` (`extract=html` + `save_text_path`) → `scrape` con `html_path`.
- **`RobotFileParser.read()` py3.12 non accetta argomenti**: fa da sé l'urlopen (perde l'UA custom) e passargli un fp alza `TypeError`; se inghiottito da un fail-open i robots restano silenziosamente OFF. Usare `parse(lines)` sulle righe già scaricate (vedi `_Robots` in `app/scrape_driver.py`) con test dedicato su robots.txt reale.
- **Skip-counter vs `<title>`/`<meta>`**: nell'estrattore stdlib le zone rumorose si tolgono con un contatore di profondità; `title`/`meta` vanno intercettati PRIMA del gate di skip (siti reali mettono il `<title>` in body dentro `<header>`: il counter si sbilancia e la pagina esce vuota) + fallback deterministico senza rimozione rumore quando il testo è quasi vuoto su HTML ricco (markup che abusa delle tag semantiche, caso info.cern.ch).
- **Smoke del driver nuovo prima della suite**: dopo `write_file` di un modulo driver lanciarlo subito via CLI (`python3 app/<driver>.py --request-json 'non-json'` ⇒ esito atteso 2): in sessione mancava `import sys` e il bug sarebbe emerso solo come 19 test falliti con stdout vuoto.

## Ref cross-progetto

- Consumer/mandante: `hal_system2/ToDo.md` cluster «MCP delegation — token shrink» (`#token-shrink`).
- Shared: `agents` e `.agents` = symlink verso `/var/www/hal_gateway`; i gate L0/L1 valgono invariati.

# Changelog — harness-hal-mcp-tools

Formato Keep a Changelog + Semantic Versioning. Tag figli: `[sync:safe]`, `[sync:review]`, `[sync:breaking]`.

## [1.1.3] - 2026-11-01

### Added

- Path «Scraping driver» (`app/scrape_tools.py` + `app/scrape_driver.py`, env `HAL_SCRAPE_DRIVER`) e 4 safety note apprese da sessione `scrape`: driver **puro stdlib** senza deroga §5 né auto-skip (contratti identici a `playwright_tools`, ponte JS via `html_path`); `RobotFileParser.read()` in py3.12 non accetta argomenti ⇒ usare `parse(lines)`, altrimenti il `TypeError` inghiottito dal fail-open spegne i robots in silenzio; `title`/`meta` intercettati prima del gate di skip nell'estrattore + fallback senza rimozione rumore su markup che abusa delle tag semantiche; smoke CLI del driver nuovo prima della suite (exit atteso 2 su `--request-json 'non-json'`) [sync:safe]

### Changed

- Cell «Stack» e tabella Target Makefile allineate allo stato reale: `test-unit` corre `-m "not int"`, `test-int` consegnato in M2 con spawn reale (N/A obsoleto rimosso, restano `test-e2e`/`check-parity`/`sync-assets`) [sync:safe]

## [1.1.2] - 2026-11-01

### Changed

- Allineata ad a-harness 1.10.2 (`extends-version` 1.10.1 → 1.10.2) — bump di sessione parallela non registrato nel changelog, documentato qui in sede di consolidamento [sync:safe]

## [1.1.1] - 2026-11-01

### Added

- Path «Browser driver» (`app/playwright_tools.py` + `app/playwright_driver.py`) e 3 safety note apprese da sessione `/learn !`: `playwright` solo nel driver-subprocess (mai import nel core; vietato modulo `app/playwright.py` per shadowing), grep dei letterali del vecchio nome dopo ogni rinomina in tree condiviso, gate statico via venv temporaneo esterno (PEP 668, mai `venv/` nel repo) [sync:safe]

## [1.1.0] - 2026-10-31

### Added

- Target `install-zed` (dry-run default, `APPLY=1` scrive) e nuovi path in tabella artefatti: `app/s1.py` + `logs/s1-decisions.jsonl`, `app/install_zed.py` [sync:safe]
- Safety note: preflight fail-open (KPI-3: S1 non tocca status/exit), secret solo da env, esito `TIMEOUT`=124 e cap 4000 char sulla risposta [sync:safe]

## [1.0.1] - 2026-10-31

### Changed

- Rinominata da `harness-hal_mcp_tools` (contratto naming loader Agent Skills promosso in `extension-scaffold.md` 1.13.1: `name` kebab-case pari alla directory; le violazioni con underscore erano scartate in silenzio) [sync:safe]
- Allineata a a-harness 1.10.1 (`extends-version` 1.10.0 → 1.10.1; policy «Copertura gate» non impatta il delta L2) [sync:safe]

## [1.0.0] - 2026-10-31

### Added

- Bootstrap harness `standard` (2026-10-31): delta L2 per hal_mcp_tools (MCP test-runner/analytics) — Makefile Platform API, path artefatti, N/A documentati, safety note del servizio.

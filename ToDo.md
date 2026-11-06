# Mappa residui — HAL

Backlog rinfrescabile (≠ Progress append-only). Igiene: `/todo`.

## P0

## P1

## P2

- [ ] Strumentazione gateway per KPI-1 token-shrink (delegata da `hal_mcp_tools`, nodo N12 del `/graph -y` 2026-11-06): riaprire la cattura eventi del gateway — ferma al 2026-11-01 perché il TDD gira diretto in Zed — così che la finestra «DOPO» dello spike M0 torni misurabile (strada (a) delle due in esame). `#infra` · P2
  - Perché utile: senza ≥5 sessioni strumentate con tool MCP in uso, il KPI-1 (−30% `context_trim`) di `hal_mcp_tools` resta non misurabile e ogni tool è output senza outcome (esito spike 2026-11-01: «DOPO non strumentata»).
  - Acceptance: eventi gateway datati dopo il 2026-11-01 per ≥5 sessioni TDD (count su `router.db`/JSONL); poi rieseguire `python3 /var/www/hal_mcp_tools/scripts/spike_m0.py` e annotare la riga `context_trim`/`body_bytes` in `hal_system2/ToDo.md` voce 2.

## Già fatto

_(Buffer pre-flush in formato Keep a Changelog: sotto `### Added`, `### Changed`, `### Fixed` o `### Removed`; `/todo` lo svuota nel CHANGELOG.)_

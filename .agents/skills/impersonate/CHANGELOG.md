# Changelog — skill `impersonate`

Formato Keep a Changelog + Semantic Versioning. Tag figli: `[sync:safe]`.

## [1.0.1] - 2026-11-06

### Added

- §Notes: filtro di missione del registry (finding `/impersonate martycagan` in sessione graph N6) — nuovo oracolo solo con lente assente + esperimento value verde; referenza incrociata al vincolo `_CARD_FIELDS` asserito dai test di `tests/test_impersonate.py` [sync:safe]

## [1.0.0] - 2026-11-05

### Added

- Skill comando `/impersonate` (L2, pool workspace): selezione oracoli con `?` (tool `impersonate` del server MCP `hal_mcp_tools`, registry `app/oracles.py` 28 schede), lazy-load del target, interpretazione in voce con griglia finding→domanda canonica→azione, telemetria token_budget su path reale del progetto, fallback a lettura diretta di `app/oracles.py` se l'MCP non è raggiungibile

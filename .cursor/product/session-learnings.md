## [2026-10-06] session_hal_gateway_01 — /learn !

### Progetto
- **Implementazione e validazione Cache L1, Retention & Redaction, e Circuit Breaker** (`07`, `05`, `19`) → `gateway_core.py` e `test_gateway_core.py` § Core logic
- **Pulizia Mappa residui ToDo e Flush in CHANGELOG** → `ToDo.md` e `CHANGELOG.md` § [Unreleased]

### HAL
- **Aggiornamento comando /todo** per imporre il flush automatico della sezione «Già fatto» verso il CHANGELOG ad ogni invocazione → `agents/a-agentzero/commands/todo.md`, `.agents/skills/todo/SKILL.md` e `a-harness/competencies/todo/SKILL.md` § Attivazione / Objective

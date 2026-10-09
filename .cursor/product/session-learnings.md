## [2026-10-06] session_hal_gateway_01 — /learn !

### Progetto
- **Implementazione e validazione Cache L1, Retention & Redaction, e Circuit Breaker** (`07`, `05`, `19`) → `gateway_core.py` e `test_gateway_core.py` § Core logic
- **Pulizia Mappa residui ToDo e Flush in CHANGELOG** → `ToDo.md` e `CHANGELOG.md` § [Unreleased]

### HAL
- **Aggiornamento comando /todo** per imporre il flush automatico della sezione «Già fatto» verso il CHANGELOG ad ogni invocazione → `agents/a-agentzero/commands/todo.md`, `.agents/skills/todo/SKILL.md` e `a-harness/competencies/todo/SKILL.md` § Attivazione / Objective

## [2026-10-09] learn-2026-10-09-system2-routing — /learn !

### Progetto
- (nessuno)

### HAL
- **Fallback Laya non distinguibile da una decisione valida**: indisponibilità può apparire come primo candidato o score `0.95` → `ToDo.md` · P1 · `#bug`
- **SystemTwoEngine non esegue un’inferenza reale**: `execute()` è dimostrativo, quindi selezione e modello servito non sono verificati → `ToDo.md` · P1 · `#feature`
- **Risoluzione OrcaRouter per agente in conflitto con il modello condiviso HAL**: `AGENT_EXTERNAL_MODELS` applica modelli distinti se si attiva l’esterno → `ToDo.md` · P1 · `#techdebt`

## [2026-10-09] learn-2026-10-09-graph-gate — /learn !

### Progetto
- (nessuno)

### HAL
- **Catene `extends-version` stale bloccano il gate canonico**: `make -C agents test-unit` si arresta prima dei test gateway per sette L1 e L2 `harness-agentfactory` → `ToDo.md` · P0 · `#infra`

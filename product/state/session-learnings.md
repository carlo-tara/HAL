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

## [2026-10-15] opt-token-2026-10-15 — /learn !

### Progetto

- (nessuno)

### HAL

- **Caricamento dinamico on-demand (Progressive Disclosure) per competenze e orchestratori L1**: Non iniettare nel system prompt (Context window) intere checklist, regole e reference. Trasferire il testo corposo in `references/` e caricarlo solo quando serve (`a-agentzero`, `a-seozoom`, `a-product`, `a-copywriter`, `a-design`, `a-wordpress`, `a-harness`). → `agents/a-*/SKILL.md`
- **Triage e Scoring System 1 (Laya)**: Obbligo assoluto di usare la CLI `router.py triage` o `router.py score` per ogni decisione di instradamento, classificazione patch/minor/major, selezione di documento target o validazione euristica, prima di spendere token di ragionamento LLM. → `agents/a-agentzero/SKILL.md` § System 1 (Laya)
- **Diff-Tiering e Pre-filtraggio contestuale**: Vietato il context-dumping di enormi CSV, diff o log di test nel system prompt. Usare `git status -s`, troncamento `head_lines: 5`/`tail_lines: 15` sui test runner e filtri CSV con script bash/python intermediari. → `agents/a-agentzero/commands/commit.md`, `agents/a-agentzero/commands/cycle.md`, `agents/a-seozoom/competencies/seo-import/SKILL.md`
- **Logica deterministica estrapolata dall'LLM**: Il flush della Mappa residui (ToDo) e il bump semver sono stati completamente spostati su script `bash`/`python` (es. `agent-todo.py`, `agent-version.sh bump`, `l2-analyzer.py`), lasciando al LLM solo il controllo della strategia. → `agents/a-agentzero/commands/todo.md`, `agents/a-agentzero/commands/version.md`, `agents/a-agentzero/sync/SKILL.md`
- **Output (Contratto)**: Niente discorsività "Reason why", preamboli, checklist di conferma verbale o ripetizioni. Emettere output grezzo in formato tabella, lista markdown, CSV o JSON. → (Tutti gli `SKILL.md` e `commands/`)

### Progetto

- **Sostituzione eccezioni alias con `OSError`** → `check_secrets.py`, `gateway_core.py`, `check_sast.py` § Exception handling
- **Organizzazione workspace (scripts/ e tests/)** → `scripts/`, `tests/` § Project structure
- **Decoupling totale da Cursor** → Rimozione definitiva delle cartelle `.cursor/` e `.agents/.cursor/` § Architecture

### HAL

- (nessuno)

## [2026-10-18] system2-gating-evidence — /learn !

### Progetto

- **Il gate System 1/System 2 deve separare stato tecnico, rubriche automatiche e qualità semantica indipendente; richiede latenza serving comparabile e blocca troncamenti/evidenza mancante.** Evidenza: i benchmark hanno avuto rubriche deboli per task e un caso logico errato passato 4/4; `seconds` includeva il caricamento del modello e non misurava la latenza serving. → `ToDo.md` · P1 · `#system1-gating`.

### HAL

- **La versione dei wrapper CLI generati non sopravvive al sync**: `link-workspace-skills.sh` scrive `version: 1.0.0` nei wrapper e può sovrascrivere un bump successivo; serve una sorgente unica e sync idempotente. → `ToDo.md` · P2 · `#version-sync`.

## [2026-10-20] learn-2026-10-20-ci-tests-node24 — /learn !

### Progetto

- **I test gateway vivono in `tests/` e vanno lanciati dalla root con `PYTHONPATH=.`**: `python3 test_gateway_core.py` fallisce (`No such file or directory`), `python3 tests/test_gateway_core.py` fallisce con `ModuleNotFoundError: gateway_core`; il comando corretto è `PYTHONPATH=. python3 tests/test_gateway_core.py` (11 test OK). Gli step del workflow `ready-for-review.yml` hanno lo stesso problema → `ToDo.md` · P1 · `#infra`.
- **Action GitHub su runtime Node 24**: `actions/checkout` portato a `@v5` e `actions/setup-python` a `@v6` in `.github/workflows/ready-for-review.yml`; `checkout` a `@v5` anche in `agents/.github/workflows/ready-for-review.yml`. Versioni non verificate contro i repo action; CI da rieseguire. (Fatto in sessione, nessuna voce ToDo.)

### HAL

- (nessuno)

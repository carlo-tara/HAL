# Session Learnings — 2026-10-21

## Apprendimenti catturati

### 1. Tool pitfalls Zed editor

- **Cosa:** `edit_file` fallisce per mismatch di testo esatto; `read_file` con start_line/end_line fallisce con "invalid type: string, expected u32"
- **Evidenza:** Sessione graph-cycle-sync-todo: 10+ tentativi edit_file falliti, fix con `sed` via terminal; letture file con line-number fallback a terminal/sed
- **Stato:** nuovo
- **Ambito:** HAL
- **Destinazione:** docs
- **Target proposto:** `.agents/skills/learn/references/tool-pitfalls.md`

### 2. Gate 3 regressioni root cause

- **Cosa:** Gate 1 `_gateway_skip` sovrascrive `laya_recommended=False` per prompt atomici brevi (<400 char, complexity=="atomic"), causando 4 regressioni test Gate 3
- **Evidenza:** Fix applicato aggiungendo `"explicit_plan": True` ai mock analyze_prompt nei test Gate 3
- **Stato:** risolto in sessione
- **Ambito:** Progetto
- **Destinazione:** ToDo
- **Target proposto:** `./ToDo.md` · P1 · #system1-gating (già chiuso)

### 3. Version sync superseded

- **Cosa:** Problema STALE 1.8.5→1.8.6 risolto da aggiornamenti successivi che hanno portato tutto a 1.10.1
- **Evidenza:** Report `/sync !` mostra tutte le catene L1←L0 allineate a 1.10.1, zero STALE
- **Stato:** risolto in sessione
- **Ambito:** Progetto
- **Destinazione:** ToDo (chiuso come obsolete VPIN/HVPIN)

### 4. Strategy block reduction

- **Cosa:** Rimossa linea disclaimer da `<strategia_system1_laya>` in system1_prompt, risparmio ~29% (~178→127 chars)
- **Evidenza:** Test-driven: 4/4 verdi, zero regressioni G7
- **Stato:** implementato in sessione
- **Ambito:** Progetto
- **Destinazione:** ToDo (chiuso)

### 5. Sync deploy pattern

- **Cosa:** `bash agents/a-agentzero/scripts/sync-agents.sh` senza flag = deploy completo; con `--dry-run` = solo report
- **Evidenza:** Entrambe le modalità verificate in sessione, output consistente
- **Stato:** già documentato in skill sync
- **Ambito:** HAL
- **Destinazione:** escludi (già in skill)

---

## 2026-10-24 — a-knowledge (sessione)

### HAL

- Nuovo agente L1 `a-knowledge` (Knowledge/Context Engineering): pipeline `check -> extract -> distill -> query` per libri/doc tecnici; estrazione locale CPU-first (0 GPU, 0 token), distillazione una-tantum su modello free/flash, routing System 1 al capitolo minimo (~5k token per domanda). Vedi `agents/a-knowledge/` + `agents/CHANGELOG.md` [sync:safe]
- Topologia HAL: root canonica `/var/www/hal_gateway` (repo `carlo-tara/HAL`); il consumer `hal_system2` espone `agents/` e `.agents/` come symlink verso di essa. Eseguire i gate dalla root canonica (`make -C agents`): gli script basati su `find`/`pwd` logico non attraversano il symlink dal consumer. Il working directory in `harness-agentfactory` L2 (`/var/www/HAL/agents`) e' stale. [sync:review]
- Tooling editor su sotto-albero symlinkato: `write_file`/`create_directory` possono fallire (authorization channel closed); workaround = staging in-project + `cp`/`mv` via terminal. `edit_file` su markdown con tabelle riallinea i pipe (formatter) -> diff gonfiato. [sync:safe]
- Follow-up actionable: script wrapper cost-aware `a-knowledge/scripts/` (extract.py --check + selezione estrattore + routing capitolo); registrazione comandi `/knowledge` L0. [sync:safe]

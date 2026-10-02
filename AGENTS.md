# HAL — istruzioni per Zed e Cursor

La fonte canonica di agenti e skill è `agents/`. Il repository AgentFactory è deprecato e non va consultato per l'uso o l'aggiornamento degli agenti.

- Le skill condivise Zed/Cursor sono esposte in `.agents/skills/` e puntano ai bundle canonici in `agents/`.
- I subagent e i comandi in `.cursor/` sono adapter Cursor; non duplicare lì le istruzioni canoniche.
- Il modello predefinito di esecuzione è System 2 (`SystemTwoEngine.ACTIVE_MODEL_NAME` in `global_config.py`). Non creare un runtime alternativo e non assegnare modelli diversi ai subagent.
- Preservare contenuti, gerarchia L0/L1/L2 e competenze. Gli 8 agenti primari portano il prefisso `a-` (`a-agentzero`, `a-b2b`, `a-copywriter`, `a-design`, `a-harness`, `a-product`, `a-seozoom`, `a-wordpress`), mentre le skill integrate e i comandi operativi non usano il prefisso (`personas`, `jtbd`, `gherkin`, `enrichment`, `uiux`, `charts`, `illustrator`, `laya`, `learn`, `sync`, `harness-agentfactory`).
- Non eseguire script dei bundle solo perché una skill è stata caricata.

## Architettura Cognitiva: System 1 (Laya) vs System 2 (Reasoning)

- **System 1 (Laya)**: Da usare SEMPRE per compiti preliminari, euristici, veloci o a basso costo cognitivo:
  - `routing`: classificazione/instradamento di richieste, file o artefatti tra percorsi predefiniti (`python3 router.py routing "<testo>" --routes ...`);
  - `choice`: selezione rapida tra alternative discrete o strategie operative determinate (`python3 router.py choice "<prompt>" --options ...`);
  - `score`: valutazione euristica di priorità, rischio o aderenza rispetto a criteri (`python3 router.py score "<testo>" --criteria ...`);
  - `noul`: elaborazione o pre-filtro rapido di primo livello (`python3 router.py noul "<testo>"`).
  *Regola per l'agente*: Prima di procedere con decisioni discrezionali di classificazione, triage o scelta tra alternative operative, l'agente deve consultare Laya System 1 tramite CLI (`python3 router.py ...` o modulo Python `router`).

- **System 2 (Agente / Active Model)**: Riservato al ragionamento complesso: pianificazione approfondita, generazione e modifica del codice, refactoring, esecuzione e analisi dei test, verifica semantica e decisioni architetturali vincolanti.

## Feature Flag Modelli Esterni (OrcaRouter)

L'utilizzo di OrcaRouter per ciascun agente è condizionato tramite tre parametri:
- `LLM_EXTERNAL_MODE`: flag numerico (`0` = disabilitato/off, `1` = abilitato/on).
- `LLM_EXTERNAL_URI`: endpoint del router esterno (default: `https://api.orcarouter.com/v1`).
- `LLM_EXTERNAL_MODEL`: modello OrcaRouter specifico per ciascun agente.

**Stato attuale**: `LLM_EXTERNAL_MODE = 0` per ogni agente. L'esecuzione di tutti gli agenti ricade sul default System 2 (`SystemTwoEngine.ACTIVE_MODEL_NAME`).

## Sincronizzazione Multi-Editor (Cursor ⇄ Zed)

La fonte canonica di comandi e skill è `agents/`. Per mantenere sincronizzati Cursor (`.cursor/commands`, `.cursor/agents`) e Zed (`.zed/prompts`, `.agents/skills`) in modo automatico:
- Eseguire sempre `bash agents/scripts/link-workspace-skills.sh` dopo aver aggiunto o modificato comandi o skill.
- Lo script crea link simbolici speculari sia verso `.cursor/commands/` che verso `.zed/prompts/`.

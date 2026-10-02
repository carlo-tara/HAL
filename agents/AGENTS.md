# Istruzioni per gli agenti HAL

La sorgente canonica degli agenti e delle skill è `HAL/agents/`. AgentFactory è deprecato: non usarlo per risolvere file, deploy, versioni o aggiornamenti.

## Regole di compatibilità

- Mantenere i bundle canonici in `agents/a-*/` e le skill in formato standard `SKILL.md`.
- Usare `.agents/skills/` come punto condiviso per Zed e Cursor. `.cursor/agents/` e `.cursor/commands/` sono adapter Cursor, non copie canoniche.
- Il modello di esecuzione è il System 2 predefinito (`SystemTwoEngine.ACTIVE_MODEL_NAME`); non aggiungere un executor indipendente né fissare modelli ai subagent Cursor.
- L'eventuale uso di OrcaRouter è condizionato dal feature flag `LLM_EXTERNAL_MODE` (`0` spento / default, `1` attivo), `LLM_EXTERNAL_URI` e `LLM_EXTERNAL_MODEL`, attualmente spento (`0`) per tutti gli agenti.
- Consultare Laya System 1 (`router.py`) per routing euristico, choice e scoring preliminari prima delle elaborazioni di System 2.
- Preservare `extends`, versioni, competenze, riferimenti e changelog. Gli 8 agenti canonici L0/L1 usano il prefisso `a-` (`a-agentzero`, `a-b2b`, `a-copywriter`, `a-design`, `a-harness`, `a-product`, `a-seozoom`, `a-wordpress`), mentre le skill integrate (`personas`, `jtbd`, `gherkin`, `enrichment`, `uiux`, `charts`, `illustrator`, `laya`, `learn`, `sync`, `harness-agentfactory`) non usano prefisso.
- Non eseguire script importati durante discovery o caricamento delle skill; eseguirli solo quando il task lo richiede e dopo averne verificato lo scopo.

Per ricreare gli entrypoint locali: `bash agents/scripts/link-workspace-skills.sh`.
Per controllare catene e integrità: `make -C agents test-unit` e `make -C agents pre-commit`.

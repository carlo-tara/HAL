# HAL agents

HAL è la fonte canonica per agenti, skill, competenze e asset eseguibili. Questo albero contiene la migrazione dei contenuti AgentFactory; AgentFactory è deprecato e non è una dipendenza di esecuzione o deploy.

## Compatibilità Zed e Cursor

Le skill di dominio usano il formato standard `SKILL.md`:

- `.agents/skills/` espone con symlink relativi gli agenti principali L0/L1, le skill integrate e operative (`charts`, `enrichment`, `gherkin`, `illustrator`, `jtbd`, `learn`, `laya`, `personas`, `sync`, `uiux`) e la skill L2 `harness-agentfactory`. Zed e Cursor leggono entrambi questo percorso.
- `.cursor/agents/` espone a Cursor i manifesti subagent conservati nei bundle. In Zed gli stessi domini si invocano come skill.
- `.cursor/commands/` espone a Cursor i comandi L0 originali; i comandi non sono agenti né skill.
- Le competenze restano nei bundle sotto `competencies/`, come risorse modulari caricate dall'agente di dominio. Non sono appiattite né rinominate.

Zed cataloga le skill poste direttamente in `.agents/skills/`; il caricamento delle competenze annidate resta affidato al workflow L0/L1 che ne legge i file. Cursor può rilevare anche le `SKILL.md` annidate secondo la propria scansione. I contenuti canonici non sono duplicati negli adapter.

Per ricreare gli entrypoint del workspace:

```bash
bash agents/scripts/link-workspace-skills.sh
```

I link sono relativi e non dipendono dal percorso assoluto della macchina.

## Modello di esecuzione

L'esecuzione usa il modello System 2 predefinito: `SystemTwoEngine.ACTIVE_MODEL_NAME` in `global_config.py`. Non viene introdotto un executor LLM alternativo. I subagent Cursor ereditano il modello attivo; le skill Zed vengono eseguite dal modello attivo dell'Agent Panel.

## Inventario

- **L0:** `a-agentzero` — protocollo, sicurezza, versioni, workflow e competenze comuni.
- **L1:** `a-b2b`, `a-copywriter`, `a-design`, `a-harness`, `a-product`, `a-seozoom`, `a-wordpress`.
- **Skill integrate:** `enrichment` (B2B); `charts`, `illustrator`, `uiux` (Design); `gherkin`, `jtbd`, `personas` (Product).
- **L2 in HAL:** `harness-agentfactory` e `laya`.

La struttura canonica è stata razionalizzata rispetto ai bundle L1 originari: le competenze di dominio restano disponibili come skill integrate, senza agenti L1 duplicati. La mappa è strutturale; non attesta una verifica contenuto-per-contenuto rispetto al repository AgentFactory deprecato.

## Verifiche

Dalla root HAL:

```bash
bash agents/scripts/link-workspace-skills.sh
make -C agents test-unit
make -C agents pre-commit
```

Origine e perimetro della migrazione: [MIGRATION.md](MIGRATION.md). Catalogo statico: [catalog.json](catalog.json).

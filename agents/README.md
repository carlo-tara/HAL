# HAL agents

HAL è la fonte canonica per agenti, skill, competenze e asset eseguibili. Questo albero contiene la migrazione dei contenuti AgentFactory; AgentFactory è deprecato e non è una dipendenza di esecuzione o deploy.

## Integrazione Zed

Le skill di dominio usano il formato standard `SKILL.md`:

- `.agents/skills/` espone con symlink relativi gli agenti principali L0/L1, le skill integrate e operative (`charts`, `enrichment`, `gherkin`, `gdrive-sync-safe`, `illustrator`, `jtbd`, `learn`, `laya`, `personas`, `sync`, `uiux`) e le skill L2 `harness-agentfactory`, `harness-hal`, `laya`.
- `product/adapters/agents/` espone i manifesti degli agenti conservati nei bundle. In Zed gli stessi domini si invocano come skill.
- `.agents/commands/` e `product/adapters/commands/` espongono i comandi L0; `.zed/prompts/` espone i comandi corrispondenti come prompt per Zed.
- Le competenze restano nei bundle sotto `competencies/`, come risorse modulari caricate dall'agente di dominio. Non sono appiattite né rinominate.

Zed cataloga le skill poste direttamente in `.agents/skills/`; il caricamento delle competenze annidate resta affidato al workflow L0/L1 che ne legge i file. I contenuti canonici non sono duplicati negli adapter.

Per ricreare gli entrypoint del workspace:

```bash
bash agents/scripts/link-workspace-skills.sh
```

I link sono relativi e non dipendono dal percorso assoluto della macchina.

## Modello di esecuzione

L'esecuzione usa il modello System 2 predefinito: `SystemTwoEngine.ACTIVE_MODEL_NAME` in `global_config.py`. Non viene introdotto un executor LLM alternativo. Le skill Zed vengono eseguite dal modello attivo dell'Agent Panel.

## Inventario

- **L0:** `a-agentzero` — protocollo, sicurezza, versioni, workflow e competenze comuni.
- **L1:** `a-b2b`, `a-copywriter`, `a-design`, `a-harness`, `a-knowledge`, `a-product`, `a-seozoom`, `a-wordpress`.
- **Skill integrate:** `enrichment` (B2B); `charts`, `illustrator`, `uiux` (Design); `gherkin`, `jtbd`, `personas` (Product).
- **L2 in HAL:** `harness-agentfactory`, `harness-hal` e `laya`.

La struttura canonica è stata razionalizzata rispetto ai bundle L1 originari: le competenze di dominio restano disponibili come skill integrate, senza agenti L1 duplicati. La mappa è strutturale; non attesta una verifica contenuto-per-contenuto rispetto al repository AgentFactory deprecato.

**Agenti primari L1 correnti:** `a-b2b`, `a-copywriter`, `a-design`, `a-harness`, `a-knowledge`, `a-product`, `a-seozoom`, `a-wordpress` (8 agenti totali, inclusi i 7 L1 consolidati da MIGRATION.md + `a-knowledge` aggiunto successivamente).

## Verifiche

Dalla root HAL:

```bash
bash agents/scripts/link-workspace-skills.sh
make -C agents test-unit
make -C agents pre-commit
```

Origine e perimetro della migrazione: [MIGRATION.md](MIGRATION.md). Catalogo statico: [catalog.json](catalog.json).

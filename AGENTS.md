# HAL — istruzioni per Zed

La fonte canonica di agenti e skill è `agents/`.

- Le skill condivise sono esposte in `.agents/skills/` e puntano ai bundle canonici in `agents/`.
- Il modello predefinito di esecuzione è System 2 (`SystemTwoEngine.ACTIVE_MODEL_NAME` in `global_config.py`). Non creare un runtime alternativo e non assegnare modelli diversi ai subagent.
- Preservare contenuti, gerarchia L0/L1/L2 e competenze. I 9 agenti primari portano il prefisso `a-` (`a-agentzero`, `a-b2b`, `a-copywriter`, `a-design`, `a-harness`, `a-knowledge`, `a-product`, `a-seozoom`, `a-wordpress`), mentre le skill integrate e i comandi operativi non usano il prefisso (`personas`, `jtbd`, `gherkin`, `enrichment`, `uiux`, `charts`, `illustrator`, `laya`, `learn`, `sync`).
- Le L2 di progetto vivono nei repo proprietari (`.agents/skills/` del consumer), mai nel mirror di hal_gateway. Lo stato di allineamento dei consumer (mount da rimuovere, catalogo da rigenerare) si gestisce con `python3 agents/scripts/hal-contract.py [--apply] [repo ...]` (dry-run di default, idempotente): toglie i symlink HAL residui e installa il fence «hal-contract» con il catalogo generato dai frontmatter del canonico. L'insieme dei repo consumer è canonico in `agents/consumers.list` (letto da hal-contract.py, prune-local-commands.py e sync-consumer-stale.sh; report: `make -C agents consumers-list`): aggiungere un repo è una riga lì, non una modifica di tre script.
- Non eseguire script dei bundle solo perché una skill è stata caricata.

## Architettura Cognitiva: System 1 (Laya) vs System 2 (Reasoning)

- **System 1 (Laya)**: Da usare SEMPRE per compiti preliminari, euristici, veloci o a basso costo cognitivo:
  - `routing`: classificazione/instradamento di richieste, file o artefatti tra percorsi predefiniti (`python3 router.py routing "<testo>" --routes ...`);
  - `choice`: selezione rapida tra alternative discrete o strategie operative determinate (`python3 router.py choice "<prompt>" --options ...`);
  - `score`: valutazione euristica di priorità, rischio o aderenza rispetto a criteri (`python3 router.py score "<testo>" --criteria ...`);
  - `noul`: elaborazione o pre-filtro rapido di primo livello (`python3 router.py noul "<testo>"`).
    _Regola per l'agente_: Prima di procedere con decisioni discrezionali di classificazione, triage o scelta tra alternative operative, l'agente deve consultare Laya System 1 tramite CLI (`python3 router.py ...` o modulo Python `router`).

- **System 2 (Agente / Active Model)**: Riservato al ragionamento complesso: pianificazione approfondita, generazione e modifica del codice, refactoring, esecuzione e analisi dei test, verifica semantica e decisioni architetturali vincolanti.

## Feature Flag Modelli Esterni (OrcaRouter)

L'utilizzo di OrcaRouter per ciascun agente è condizionato tramite tre parametri:

- `LLM_EXTERNAL_MODE`: flag numerico (`0` = disabilitato/off, `1` = abilitato/on).
- `LLM_EXTERNAL_URI`: endpoint del router esterno (default: `https://api.orcarouter.ai/v1`).
- `LLM_EXTERNAL_MODEL`: modello OrcaRouter specifico per ciascun agente.

**Stato attuale**: `LLM_EXTERNAL_MODE = 0` per ogni agente. L'esecuzione di tutti gli agenti ricade sul default System 2 (`SystemTwoEngine.ACTIVE_MODEL_NAME`).

## Integrazione Zed Editor

La fonte canonica di comandi e skill è `agents/`. Per mantenere sincronizzato Zed (`.zed/prompts`, `.agents/skills`):

- Eseguire sempre `bash agents/scripts/link-workspace-skills.sh` dopo aver aggiunto o modificato comandi o skill. La rigenerazione è ammessa **solo da hal_gateway**: lo script rifiuta (guardia realpath, «Guardia HAL») ogni scrittura che risolverebbe fuori dal workspace fisico — nei consumer che montano `.agents`/`.zed`/`agents` via symlink non va eseguito: il canonico si legge da `$HAL_ROOT` (path assoluto o MCP).
- Lo script crea i link simbolici verso `.zed/prompts/` e pota i vecchi wrapper locali `.agents/skills/<cmd>/`; `bash agents/scripts/publish-global-commands.sh` (o `deploy-all.sh`) pubblica le skill globali `~/.agents/skills/` — sede unica delle skill-comando L0 per ogni progetto, hal_gateway incluso (nel workspace restano solo i symlink `.agents/commands/*.md` e i prompt `.zed/prompts/`).

## Multi-sessione: worktree + branch per slice

Sessioni concorrenti NON lavorano sul main checkout: `bash agents/scripts/agent-worktree.sh new <nome>` crea worktree+branch da `origin/master`; il lavoro si chiude con `agent-worktree.sh land <nome>` (preview `merge-tree`, rebase con rerere, guardie `check-registry`, push ff-only verificato, cleanup). Il main resta verde per costruzione; i consumer (symlink `agents/`, mirror `.agents/skills`) vedono solo il landed. Protocollo completo: `agents/a-agentzero/references/worktree-land.md`.

<!-- BEGIN hal-contract: generato da a-agentzero 1.17.2 · tpl 2 — NON EDITARE TRA I FENCE -->
## HAL — contratto consumer

- HAL canonico: `/var/www/hal_gateway` (repo `hal_gateway`). **Da questo progetto**: mai modificare
  `agents/` del canonico, mai eseguire `link-workspace-skills.sh` / `deploy-all.sh` /
  `publish-global-commands.sh` (guardie: «Guardia HAL» e path assoluto), mai ricreare
  symlink HAL verso `.agents`/`agents`/`.zed`/`product` — i mount sono rimossi (de-racing).
- Script L0: invocarli con path assoluto, es. `bash /var/www/hal_gateway/agents/a-agentzero/scripts/<script>.sh`.
- Comandi L0 `/version`, `/document`, `/review`, `/improve`, `/commit`, `/todo`, `/slice`, `/cycle`, `/graph`, `/sync`, `/learn`, `/laya`: pubblicati come skill globali (`~/.agents/skills/`,
  rigenerate solo da hal_gateway via `publish-global-commands.sh`); una skill locale
  omonima ha priorità. Lettura del canone: `read`
  `/var/www/hal_gateway/agents/a-agentzero/commands/<cmd>.md`.
- **Delega MCP (scelta voce per voce)**: agenti L1 e skill embedded (jtbd, gherkin,
  enrichment, uiux, charts, illustrator, personas, laya…) NON sono globali né montati:
  il progetto le usa solo se servono, caricandole on-demand dai tool MCP del server
  hal_gateway (`skills_list` per il catalogo, `skill_read` per il SKILL.md integrale o
  un reference con `file`); fallback senza MCP: `read` del path in catalogo.
- Le skill `.agents/skills/` presenti in questo repo sono L2 di questo progetto.

### Catalogo HAL (generato — non editare a mano)

- **a-agentzero** — Agente radice HAL: ereditarietà a 3 livelli, competenze modulari, avvio multiprogetto, workflow generici, checklist e scaffold L2. Istruzioni: `read /var/www/hal_gateway/agents/a-agentzero/SKILL.md`
- **a-b2b** — Agente L1 per piloti B2B e contact/account research: orchestra il profilo B2B e include la skill enrichment per ricerca ICP, CRM cascade e lead valid…. Istruzioni: `read /var/www/hal_gateway/agents/a-b2b/SKILL.md`
- **a-copywriter** — Scrive e revisiona copy web generico (prodotti, categorie, blog, landing, meta, FAQ). Istruzioni: `read /var/www/hal_gateway/agents/a-copywriter/SKILL.md`
- **a-design** — Agente L1 Design & Visual Experience: unifica layout e accessibilità (uiux), grafici e data visualization (charts) e asset illustrativi (illustrator). Istruzioni: `read /var/www/hal_gateway/agents/a-design/SKILL.md`
- **a-harness** — Meta-Harness: TDD XP, Steward, DDD, Makefile gates, session progress, when-stuck, Plan→Act, L3. Istruzioni: `read /var/www/hal_gateway/agents/a-harness/SKILL.md`
- **a-knowledge** — Agente L1 Knowledge / Context Engineering: trasforma libri e documentazione tecnica (PDF, EPUB, DOCX, HTML, Markdown) in skill interrogabili on-demand. Istruzioni: `read /var/www/hal_gateway/agents/a-knowledge/SKILL.md`
- **a-product** — Agente L1 Product Management: discovery, PO (PRD, Lean Canvas, priorità, validazione), JTBD, Personas e BDD Spec. Istruzioni: `read /var/www/hal_gateway/agents/a-product/SKILL.md`
- **a-seozoom** — Agente SEO/GEO multi-progetto: orchestra import dati, analisi metriche, on-page, GEO/AEO, audit, schema, pSEO, IA, hreflang, topic-cluster e Google A…. Istruzioni: `read /var/www/hal_gateway/agents/a-seozoom/SKILL.md`
- **a-wordpress** — Analizza installazioni WordPress specifiche e sviluppa, mantiene e revisiona plugin (stabili e migrate). Istruzioni: `read /var/www/hal_gateway/agents/a-wordpress/SKILL.md`
- **charts** (in a-design) — Data Visualization integrata in a-design: scelta del tipo, encoding visuale, implementazione (SVG/D3/canvas/HTML) e QA. `read /var/www/hal_gateway/agents/a-design/charts/SKILL.md`
- **enrichment** (in a-b2b) — Contact/account enrichment B2B: dual entry (CRM cohort + domain-first), ICP/fit gates, HubSpot → Apollo → LeadMagic → SQLite master, lead-research ou…. `read /var/www/hal_gateway/agents/a-b2b/enrichment/SKILL.md`
- **gherkin** (in a-product) — QA Lead / BDD Spec integrato in a-product: suite Gherkin da jtbd seeds, inventory UI/IO, journey E2E, expand edge, /cover, add-scenario da NL, /secur…. `read /var/www/hal_gateway/agents/a-product/gherkin/SKILL.md`
- **illustrator** (in a-design) — Genera illustrazioni coerenti orchestrando stile-visivo, prompt-composizione, preview-render e qa-artefatti. `read /var/www/hal_gateway/agents/a-design/illustrator/SKILL.md`
- **jtbd** (in a-product) — Job Analyst / JTBD integrato in a-product: Jobs-To-Be-Done job-first, ODI needs/unmet, continuity di flusso, job stories e scenario seeds per BDD;. `read /var/www/hal_gateway/agents/a-product/jtbd/SKILL.md`
- **learn** (in a-agentzero) — Slash /learn con tripla modalità: /learn ? illustra gli apprendimenti dalla conversazione o sessione corrente;. `read /var/www/hal_gateway/agents/a-agentzero/learn/SKILL.md`
- **personas** (in a-product) — User Researcher integrato in a-product: definisce personas da PRD/mockup con intervista PO, verifica journey coherence vs mockup/PRD, aggiunge person…. `read /var/www/hal_gateway/agents/a-product/personas/SKILL.md`
- **sync** (in a-agentzero) — Sincronizza agenti HAL L0/L1 (deploy) e comandi Cursor L0 ereditabili;. `read /var/www/hal_gateway/agents/a-agentzero/sync/SKILL.md`
- **uiux** (in a-design) — UI/UX per siti statici e shell pagina integrato in a-design: stack M3/vanilla CSS, accessibilità WCAG, layout editoriale, pattern guida/chrome comuni…. `read /var/www/hal_gateway/agents/a-design/uiux/SKILL.md`
- **gdrive-sync-safe** — Guide to safely manage local Google Drive mirrors and prevent IDE freezes or recursive index locking. `read /var/www/hal_gateway/agents/gdrive-sync-safe/SKILL.md`
- **laya** — Interfaccia per Laya System 1: routing di categorie, choice tra opzioni, score euristico di rischio o aderenza, confidence 0-100%, context 0-100%, no…. `read /var/www/hal_gateway/agents/project-skills/laya/SKILL.md`
- **harness-hal** (solo gateway) — Delta harness per HAL Gateway: Platform API root (Makefile specchio CI), path artefatti, profile bootstrap standard, N/A documentati (int/e2e/parity)…. `read /var/www/hal_gateway/agents/project-skills/harness-hal/SKILL.md`
<!-- END hal-contract -->

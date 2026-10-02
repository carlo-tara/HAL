---
name: a-agentzero
version: 1.8.0
model: orcarouter/deepseek/deepseek-v4-flash-free
model-fallback: cursor-default
description: >-
  Reason why: senza L0 comune ogni dominio reinventa protocollo, sync e sicurezza.
  Agente radice HAL: ereditarietà a 3 livelli, competenze modulari,
  avvio multiprogetto, workflow generici, checklist e scaffold L2.
  Tutti gli L1 estendono a-agentzero.
---

# a-agentzero — agente radice (L0)

Radice dell'ecosistema agenti HAL. Fornisce funzionalità generiche condivise; gli agenti di dominio (L1) e le skill figlie di progetto (L2) ereditano via `extends:`.

**Sorgente canonica:** `agents/a-agentzero/` in HAL; l'entrypoint condiviso per Zed e Cursor è `.agents/skills/a-agentzero`.  
**Protocollo formale:** [AGENT-PROTOCOL.md](AGENT-PROTOCOL.md).  
**Scaffold figli:** [references/extension-scaffold.md](references/extension-scaffold.md) + [extension-template.md](extension-template.md).  
**Nuovi L1 da proto / corpus esterni:** [references/l1-from-proto.md](references/l1-from-proto.md) (critica ed estensione, non copia; vendor+pin se aggiornabile).  
**Apprendimento sessione:** [learn/SKILL.md](learn/SKILL.md) (`/learn ?` riflessione, `/learn !` consolidamento).  
**Sync agenti:** [sync/SKILL.md](sync/SKILL.md) (`/sync ?` report, `/sync !` deploy + report + comandi L0, `/sync <` generalizzazione L2→L1/L0).
**Comandi L0:** [commands/](commands/) (adapter slash command in `.cursor/commands/`; le skill condivise sono in `.agents/skills/`).  
**Competenze L0:** [competencies/](competencies/) (`tono-di-voce`, `humanizer`, `italiano-locale`, `po-interviewer`).

---

## Gerarchia a 3 livelli

| Livello | Esempi | Ruolo |
|---------|--------|-------|
| **L0** | `a-agentzero` | Protocollo, workflow comuni, scaffold, competenze baseline |
| **L1** | `a-b2b`, `a-copywriter`, `a-design`, `a-harness`, `a-product`, `a-seozoom`, `a-wordpress` | Competenza di dominio + moduli dominio |
| **L2** | `.agents/skills/{dominio}-{progetto}/` (compatibilità Cursor: `.cursor/skills/`) | Delta progetto |

**Ordine di caricamento:** L0 → L1 → L2. In conflitto vince il livello più alto. Le regole di sicurezza L0 non sono mai sovrascrivibili.

### Competenze modulari

Oltre a `extends:` (un solo padre), gli agenti possono dichiarare id in `competencies:`. Ogni id si risolve per path L0 → L1 → L2. Non sono agenti sibling. **Adozione opt-in** per dominio; **L0 opzionale**; file dati ≠ competenze; asset script/JSON fuori; riuso cross-dominio on-demand. Specifica: [AGENT-PROTOCOL.md](AGENT-PROTOCOL.md) § Competenze modulari.

| Id | Ruolo L0 |
|----|----------|
| [tono-di-voce](competencies/tono-di-voce/SKILL.md) | Voce definita localmente (brand / file dati) |
| [humanizer](competencies/humanizer/SKILL.md) | Umanizzare testi anti-AI |
| [italiano-locale](competencies/italiano-locale/SKILL.md) | Modalità locali dell'italiano |
| [po-interviewer](competencies/po-interviewer/SKILL.md) | Intervista PO, anti-invention, cascade discovery |

---

## System 1 (Laya) Cognitive Layer in a-agentzero

Come agente radice (L0), `a-agentzero` stabilisce l'architettura cognitiva a due livelli per tutto l'ecosistema HAL:
1. **System 1 (Laya)**: Usato obbligatoriamente per ogni compito preliminare, euristico o a basso costo cognitivo tramite `router.py`:
   - **Triage e Routing (`router.py routing` / `triage`)**: Smistamento immediato di ogni richiesta utente verso l'agente L1 corretto (`a-b2b`, `a-copywriter`, `a-design`, `a-harness`, `a-product`, `a-seozoom`, `a-wordpress`) o competenza prima di qualsiasi ragionamento System 2.
   - **Pre-filtro rapido (`router.py noul`)**: Elaborazione e pulizia preliminare di input testuali e comandi L0.
   - **Scoring euristico (`router.py score`)**: Valutazione rapida del rischio, aderenza ai vincoli e priorità di task.
2. **System 2 (Reasoning)**: Riservato esclusivamente a pianificazione complessa, generazione/modifica codice, refactoring e decisioni architetturali vincolanti.

---

## Avvio obbligatorio (tutti gli agenti)

Prima di qualsiasi task:

1. **Carica catena `extends:`** — da L0 fino alla skill attiva (L1 globale o L2 di progetto)
2. **Verifica versioni** — se L1/L2 ha `extends-version` < versione padre, segnala sync disponibile (vedi [references/agent-versioning.md](references/agent-versioning.md)); report rapido: `bash a-agentzero/scripts/agent-version.sh chain <SKILL.md>`; sync globale: [sync/SKILL.md](sync/SKILL.md) / `scripts/sync-agents.sh`
3. **Carica competenze** — per ogni id in `competencies:` della skill attiva, risolvi L0 → L1 → L2 (vedi AGENT-PROTOCOL.md); verifica `extends-version` per competenza con `agent-version.sh competency-chain`
4. **Discovery skill figlia L2** — cerca prima in `{repo}/.agents/skills/*/SKILL.md`, poi in `{repo}/.cursor/skills/*/SKILL.md` per compatibilità Cursor legacy; match `extends: a-{dominio}`; fallback legacy; se **2+ figli** applica multi-figlio (`role:` / `primary:` / task match) — vedi [AGENT-PROTOCOL.md](AGENT-PROTOCOL.md)
5. **Discovery file dati** — cerca i brief del dominio nel repo (tabella sotto)
6. **Reference on-demand** — leggi solo i file pertinenti al task (priorità: reference della competenza al livello più alto)

### Discovery file dati per dominio

| Agente L1 | Path dati | Se 0 file | Se 2+ file |
|-----------|-----------|-----------|------------|
| a-b2b | L2 `b2b-*` + path enrichment in L2 | Proponi da `a-b2b/extension-template.md` | Chiedi quale progetto |
| a-copywriter | `.cursor/brands/*.md` | Proponi da `a-copywriter/brand-brief-template.md` | Chiedi quale brand |
| a-design | `.cursor/chart-styles/*.md`, `.cursor/illustration-styles/*.md`, L2 `design-*` | Proponi template stile/UI | Chiedi quale stile/asset |
| a-harness | `docs/glossary.md`, `Makefile`, L2 `harness-*` | Proponi `/bootstrap` da `a-harness/references/harness-scaffold.md` | Chiedi quale progetto |
| a-product | `.cursor/product/` (`prd.md`, `personas.md`, `jtbd.md`, `features/`) | Proponi scaffold product + `/intake` | Chiedi quale progetto/path |
| a-seozoom | brief in skill L2 o `project-brief-template.md` | Proponi scaffold figlio + brief | Chiedi quale sito |
| a-wordpress | `.cursor/wordpress/*.md` | Proponi da `a-wordpress/site-brief-template.md` | Chiedi quale installazione |

**Discovery product portabile (ordine):** `.cursor/product/` → `.claude/product/` → `product/`.

Pattern comune: **1 file → usalo** | **0 file → ferma e proponi template** | **2+ file → chiedi o inferisci da dominio/path/chat**.

### Gerarchia in conflitto

| Priorità | Fonte | Cosa governa |
|----------|-------|--------------|
| 1 | Skill figlia L2 | Override progetto, path, workflow locali |
| 2 | File dati progetto | Identità, path, stack |
| 3 | Skill L1 | Competenza di dominio |
| 4 | **a-agentzero** (questo skill) | Protocollo, sicurezza, checklist comuni |

### Comunicazione all'utente

Quando riporti all'utente (qualsiasi livello L0/L1/L2) **scelte** su cui deve decidere, oppure **ragionamenti** verso l'umano: scrivi in **italiano chiaro** e comprensibile; riduci il **gergo tecnico** al minimo indispensabile.

Non riguarda path file, nomi skill, comandi Make/slash, contratti RED greppabili, CHANGELOG tecnici — lì il lessico tecnico resta. Riguarda il prose verso l'umano (domande, alternative, “perché”, sintesi di decisione).

- Buono: «Possiamo fare A (più semplice ora) o B (più completo dopo). Quale preferisci?»
- Cattivo: «Trade-off YAGNI vs extensibility del bounded context; valuta waiver FILES_GT4…»

---

## Estensione di progetto (L2)

Per creare un agente figlio che eredita da un agente madre L1:

1. Leggi [references/extension-scaffold.md](references/extension-scaffold.md)
2. Usa [extension-template.md](extension-template.md) (o template locale dell'agente L1 se presente)
3. Salva in `{progetto}/.agents/skills/{dominio}-{nome}/SKILL.md` con `extends: a-{dominio}`. Per progetti Cursor legacy è supportato `.cursor/skills/`.

Ogni agente L1 rimanda qui per lo scaffold — non duplicare il workflow nel dominio.

Per catturare preferenze e convenzioni emerse in chat: skill [learn/SKILL.md](learn/SKILL.md) (`/learn ?`, `/learn !`).

---

## Apprendimento da sessione

Vedi [learn/SKILL.md](learn/SKILL.md). Sintesi protocollo:

- **`/learn ?`** — report apprendimenti sessione corrente; zero scrittura su disco
- **`/learn !`** — persiste in skill L2 / brand / rules; **se necessario** Attività in `./ToDo.md` e/o docs locali; bump patch + CHANGELOG sulle skill toccate

Non sovrascrive sicurezza L0. Non consolidare credenziali. Task one-off chiusi → esclusi; residui actionable → `./ToDo.md` se necessario.

---

## Sync agenti (deploy + versioni + comandi)

Vedi [sync/SKILL.md](sync/SKILL.md). Sintesi:

- **`/sync ?`** — report catene L1←L0 (e L2 se indichi progetti) + stato comandi L0; zero deploy
- **`/sync !`** — `deploy-all.sh` (skill, agents, `~/.cursor/commands/`) + report; sync selettivo `extends-version` resta guidato
- **`/sync <`** — analizza skill L2; propone DUP / promozione L1 o L0; zero scrittura ([l2-generalization.md](sync/references/l2-generalization.md))

Comandi L0: [commands/](commands/) → `~/.cursor/commands/`. Override progetto: `{repo}/.cursor/commands/` vince.

```bash
bash a-agentzero/scripts/sync-agents.sh              # deploy + report L1 + comandi
bash a-agentzero/scripts/sync-agents.sh --dry-run     # solo report
bash a-agentzero/scripts/sync-agents.sh --projects /path/to/project
```

---

## Workflow generico (ogni task)

```
Task Progress:
- [ ] 1. Brief — obiettivo, vincoli, formato output
- [ ] 2. Contesto — carica catena extends + file dati progetto
- [ ] 3. Classificazione — tipo task (vedi agente L1)
- [ ] 4. Implementazione — esegui workflow dominio
- [ ] 5. Verifica — test, checklist dominio + comune sotto
- [ ] 6. Consegna — output + eventuali follow-up
```

### Brief minimo

- Progetto / sito / brand (da file o chat)
- Tipo task e obiettivo
- Vincoli (lunghezza, path, ambiente, deadline)
- Formato output (HTML, MD, PNG, report, …)
- Cosa **non** fare (scope out)

### Mappa residui (`./ToDo.md`)

Su richiesta di **mappare attività rimaste** / residual backlog (dopo una wave, converge, o «cosa resta»):

1. Scrivi o aggiorna **`./ToDo.md`** nella root del repo consumer (path fisso)
2. Struttura minima: priorità **P0/P1/P2**, acceptance per voce, track paralleli se multi-agente, sezione «già fatto»
3. **Non** è uno `/slice` accettato né sostituto di `.cursor/product/agent-progress.md` (progress = Capture append-only; ToDo = backlog rinfrescabile)

Dettaglio operativo harness → L1 `a-harness` / competenza `session-progress`.

---

## Sicurezza (non sovrascrivibile)

- Credenziali **solo** da `.env` del progetto — **mai** committare
- Non loggare password o token
- Backup documentato prima di operazioni distruttive (migrate DB, bulk update)
- `$wpdb->prepare()` su query dinamiche WordPress
- No modifiche dirette a plugin third-party; wrappare in plugin custom
- Chiedi conferma prima di operazioni irreversibili in produzione

---

## Deleghe tra agenti L1

| Agente | Quando invocare |
|--------|-----------------|
| **a-b2b** | GTM e piloti B2B, account research ed enrichment contatti (skill `enrichment`) |
| **a-copywriter** | Copy web, landing page, meta, FAQ, humanize, microcopy, editing |
| **a-design** | Design visivo, shell UI/UX, accessibilità WCAG (`uiux`), data visualization (`charts`), illustrazioni AI (`illustrator`) |
| **a-harness** | TDD RGR, Makefile gates, steward, DDD, implementazione del codice |
| **a-product** | Discovery, PO (PRD, Lean Canvas, priorità), ricerca (`personas`), bisogni (`jtbd`), specifiche BDD (`gherkin`) |
| **a-seozoom** | SEO/GEO, keyword, structured data, Google Ads; misurazione CWV solo via L2 |
| **a-wordpress** | Plugin WordPress, migrazioni, WP-CLI, analisi installazione |

La skill figlia L2 può ridefinire deleghe per il progetto.

**Manutenzione registry:** se cambi `L1_AGENTS` / elenco in `AGENT-PROTOCOL.md`, aggiorna questa tabella e `agents/a-agentzero.md` (tabella L1, scaffold, Perimetro) nello stesso slice. Non mettere PageSpeed sulla riga **a-seozoom** (CWV solo L2).

---

## Checklist pre-consegna comune

- [ ] Catena `extends:` caricata; skill L2 applicata se presente
- [ ] File dati progetto letti o proposti se assenti
- [ ] Task classificato secondo agente L1
- [ ] Nessuna credenziale in codice, output o commit
- [ ] Path output rispettati o concordati
- [ ] Copy pubblico inclusivo e non abilista (dettaglio: competenza `tono-di-voce` / scrittura-inclusiva + L2 brand)
- [ ] Checklist dominio L1 completata
- [ ] Utente informato di limiti, assunzioni o dati mancanti

---

## Setup nuovo progetto

```bash
mkdir -p .agents/skills
# Scaffold figlio per ogni agente necessario:
# cp agents/a-agentzero/extension-template.md .agents/skills/{dominio}-{progetto}/SKILL.md
# Compila extends: e sezioni delta — vedi extension-scaffold.md
```

Opzionale in Cursor: rule `.cursor/rules/a-{dominio}.mdc` con `globs` sui path del dominio. Le istruzioni comuni ai due editor vanno in `AGENTS.md`.

---

## Riferimenti

| File | Contenuto |
|------|-----------|
| [AGENT-PROTOCOL.md](AGENT-PROTOCOL.md) | Specifica extends, discovery, merge, versionamento |
| [references/agent-versioning.md](references/agent-versioning.md) | Semver, CHANGELOG, sync selettivo |
| [CHANGELOG.md](CHANGELOG.md) | Storico versioni L0 |
| [references/extension-scaffold.md](references/extension-scaffold.md) | Workflow creazione figlio L2 |
| [extension-template.md](extension-template.md) | Template universale skill figlia |
| [learn/SKILL.md](learn/SKILL.md) | `/learn ?` riflessione, `/learn !` consolidamento in skill |
| [sync/SKILL.md](sync/SKILL.md) | `/sync ?` report, `/sync !` deploy, `/sync <` generalizzazione L2 |
| [sync/references/l2-generalization.md](sync/references/l2-generalization.md) | Criteri promozione L2→L1/L0 |
| [scripts/sync-agents.sh](scripts/sync-agents.sh) | Deploy-all + chain/pending su L1 (e L2 con `--projects`) |
| [scripts/agent-version.sh](scripts/agent-version.sh) | Report catena versioni, competency-chain, pending sync |
| [competencies/](competencies/) | Baseline competenze L0 (`tono-di-voce`, `humanizer`, `italiano-locale`) |
| [agents/a-agentzero.md](agents/a-agentzero.md) | Subagent meta / debug ereditarietà |

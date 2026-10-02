# AGENT-PROTOCOL — Ereditarietà agenti a 3 livelli

Specifica formale per agenti HAL e skill figlie di progetto.

---

## Livelli

| Livello | Path | Frontmatter | Ruolo |
|---------|------|-------------|-------|
| **L0** | `HAL/agents/a-agentzero/` → `.agents/skills/a-agentzero` | `version` (radice) | Protocollo, workflow generici, scaffold figli |
| **L1** | `HAL/agents/a-{dominio}/` → `.agents/skills/a-{dominio}` | `extends: a-agentzero`, `version`, `extends-version` | Competenza di dominio |
| **L2** | `{progetto}/.agents/skills/{dominio}-{nome}/` (Cursor legacy: `.cursor/skills/`) | `extends: a-{dominio}`, `version`, `extends-version` | Delta progetto |

Agenti L1 disponibili: `a-b2b`, `a-copywriter`, `a-design`, `a-harness`, `a-product`, `a-seozoom`, `a-wordpress`.

---

## Frontmatter `extends:`

Ogni skill L1 e L2 **deve** dichiarare l'agente padre:

```yaml
---
name: copywriter-esempio
extends: a-copywriter
version: 1.0.0
extends-version: 1.0.0
description: >-
  Copy per esempio.it — eredita a-copywriter e aggiunge tono e path locali.
---
```

Regole:

- `extends` punta al **name** dell'agente padre (es. `a-agentzero`, `a-copywriter`)
- Una skill figlia ha **un solo** padre diretto
- La catena è ricorsiva: L2 → L1 → L0

---

## Ordine di caricamento runtime

All'avvio di un agente o subagent:

1. Risolvi la skill attiva (L1 globale o L2 di progetto se invocata/esplicita)
2. Carica la catena `extends:` dal L0 fino al livello corrente, **in ordine crescente** (L0 prima, L2 ultimo)
3. Applica i file dati di progetto (brand, site brief, style file, project brief, **product discovery**) come indicato dall'agente L1
4. In conflitto di istruzioni: **vince il livello più alto** (L2 > L1 > L0)

Percorsi risoluzione skill:

| Livello | Percorso primario | Fallback |
|---------|-------------------|----------|
| L0 | `{repo}/.agents/skills/a-agentzero/SKILL.md` o `~/.agents/skills/a-agentzero/SKILL.md` | `HAL/agents/a-agentzero/SKILL.md` |
| L1 | `{repo}/.agents/skills/a-{dominio}/SKILL.md` o `~/.agents/skills/a-{dominio}/SKILL.md` | `HAL/agents/a-{dominio}/SKILL.md` |
| L2 | `{repo}/.agents/skills/*/SKILL.md` con `extends: a-{dominio}` | Cursor legacy `{repo}/.cursor/skills/`; poi naming legacy (sotto) |

---

## Discovery skill figlia L2

Cerca prima in `{repo}/.agents/skills/`, poi in `{repo}/.cursor/skills/` per i consumer Cursor legacy:

1. **Primario:** qualsiasi `SKILL.md` con frontmatter `extends: a-{dominio}` (dominio = agente L1 attivo)
2. **Fallback legacy** (compatibilità progetti esistenti):

| Agente L1 | Pattern legacy / compatibilità |
|-----------|--------------------------------|
| a-b2b | `b2b-*`, `enrichment-*` |
| a-copywriter | `copywriter-*`, `*-tone-of-voice`, `*-voice` |
| a-design | `design-*`, `uiux-*`, `charts-*`, `illustrator-*` |
| a-harness | `harness-*` |
| a-product | `product-*`, `po-*`, `personas-*`, `jtbd-*`, `gherkin-*` |
| a-seozoom | `seo-*`, `seo-geo-*`, `seozoom-*` |
| a-wordpress | `wordpress-*` |

### Quanti figli

| Caso | Azione |
|------|--------|
| **0 figli** | Solo L0 + L1; proponi scaffold da `references/extension-scaffold.md` |
| **1 figlio** | Usalo come catena attiva |
| **2+ figli** | Vedi **Multi-figlio** sotto |

### Multi-figlio sullo stesso L1

Più skill possono estendere lo stesso L1 (es. SEO `role: data` + `role: editorial`; copywriter + `*-voice`).

Frontmatter opzionale:

```yaml
role: data | editorial | voice | default
primary: true   # un solo figlio primary per dominio, se serve default catena
```

**Risoluzione (in ordine):**

1. Match **task → `role`** (es. import CSV → `data`; title/preview → `editorial`; rewrite tono → `voice`)
2. Se un figlio ha `primary: true` e nessun role match → usalo come catena attiva
3. Inferisci da path/chat/working directory
4. Altrimenti **chiedi** quale skill
5. I sibling non scelti restano in **Deleghe** (carica on-demand, non nella catena extends primaria)

Non fondere due L2 nello stesso file: tieni perimetro separato e documenta la matrice ruoli nelle Deleghe.

---

## Regole merge / override

La skill figlia **può**:

- Aggiungere sezioni (capacità, path, workflow locali)
- Sovrascrivere workflow e checklist del padre
- Definire deleghe verso altre skill di progetto
- Specificare file dati obbligatori (`.cursor/brands/`, `.cursor/wordpress/`, …)

La skill figlia **non può**:

- Rimuovere o contraddire regole di **sicurezza** del L0 (credenziali in `.env`, no commit segreti, backup prima di migrate)
- Disabilitare il meccanismo `extends:` o la gerarchia
- Duplicare intere sezioni già nel padre senza delta (preferire rimando)

---

## Naming skill figlie L2

Convenzione consigliata: `{dominio}-{progetto}`

| Agente L1 | Esempio figlio |
|-----------|----------------|
| a-b2b | `b2b-explorer` |
| a-copywriter | `copywriter-esempio` |
| a-design | `design-esempio` |
| a-harness | `harness-esempio` |
| a-product | `product-esempio` |
| a-seozoom | `seozoom-esempio` |
| a-wordpress | `wordpress-esempio` |

Il campo `name` nel frontmatter deve essere unico nel repo.

---

## Gerarchia conflitti (unificata)

| Priorità | Fonte | Cosa governa |
|----------|-------|--------------|
| 1 | Skill figlia L2 (`.agents/skills/{dominio}-*/`; Cursor legacy: `.cursor/skills/`) | Override progetto, path, workflow locali |
| 2 | File dati progetto (`.cursor/brands/`, `.cursor/wordpress/`, `.cursor/illustration-styles/`, `.cursor/product/`, brief SEO, …) | Identità, path, stack, artefatti discovery |
| 3 | Skill L1 (`a-{dominio}`) | Competenza di dominio, reference, script |
| 4 | Skill L0 (`a-agentzero`) | Protocollo, sicurezza, scaffold, checklist comuni |

**Eccezione:** le regole di sicurezza L0 non sono mai sovrascrivibili da L2.

---

## Scaffold nuovo figlio

Workflow completo: [`references/extension-scaffold.md`](references/extension-scaffold.md)  
Template: [`extension-template.md`](extension-template.md)

Ogni agente L1 può avere un `extension-template.md` locale con sezioni pre-compilate per il dominio.

---

## Versionamento

Ogni agente ha **versione semver indipendente** e un `CHANGELOG.md` nella stessa directory di `SKILL.md`.

### Frontmatter per livello

| Campo | L0 | L1 | L2 |
|-------|----|----|-----|
| `version` | obbligatorio | obbligatorio | obbligatorio |
| `extends` | — | `a-agentzero` | `a-{dominio}` |
| `extends-version` | — | versione L0 integrata | versione L1 integrata |

Esempio L1 (valori illustrativi; verifica versioni live con `agent-version.sh`):

```yaml
---
name: a-copywriter
extends: a-agentzero
version: 1.0.1
extends-version: 1.1.1
description: >-
  ...
---
```

Esempio L2:

```yaml
---
name: copywriter-esempio
extends: a-copywriter
version: 1.0.0
extends-version: 1.0.0
description: >-
  ...
---
```

### Regola indipendenza

- La `version` del padre **non** incrementa quando cambia un figlio.
- La `version` del figlio **non** incrementa quando cambia il padre (solo `extends-version` al sync).
- Bump figlio quando cambia il **proprio** delta o quando integra novità del padre.

### Semver

| Bump | Quando |
|------|--------|
| **patch** | Chiarimenti, typo, fix non comportamentali |
| **minor** | Nuove capability retrocompatibili |
| **major** | Breaking change per i figli |

### Sync selettivo

Gerarchia lettura CHANGELOG:

- **L2** legge CHANGELOG del padre **L1**
- **L1** legge CHANGELOG del padre **L0**

Workflow: leggi voci > `extends-version` → classifica → applica solo delta al figlio → aggiorna `extends-version` → bump `version` figlio.

Tag obbligatori sulle voci che impattano i figli:

| Tag | Significato |
|-----|-------------|
| `[sync:safe]` | Retrocompatibile; sync opzionale |
| `[sync:review]` | Valutare adattamento delta L2 |
| `[sync:breaking]` | Richiede modifica esplicita del figlio |

Specifica completa: [`references/agent-versioning.md`](references/agent-versioning.md)  
Script report: [`scripts/agent-version.sh`](scripts/agent-version.sh) (`chain`, `competency-chain`, `pending`, `show`)

---

## Competenze modulari

Oltre alla catena agenti `extends:` (un solo padre per skill), un agente può dichiarare **competenze** riusabili. Le competenze **non** sono agenti L1 sibling: sono moduli path-based, caricati in ordine L0 → L1 → L2.

### Dichiarazione nell'agente

Nel frontmatter o nel body della skill attiva, elenco id:

```yaml
competencies:
  - tono-di-voce
  - humanizer
  - italiano-locale
```

### Path canonici

| Livello | Path |
|---------|------|
| **L0** | `a-agentzero/competencies/{id}/SKILL.md` (+ `CHANGELOG.md`) |
| **L1** | `a-{dominio}/competencies/{id}/SKILL.md` (+ `CHANGELOG.md`, `references/…`) |
| **L2** | `{progetto}/.agents/skills/{figlio}/competencies/{id}/SKILL.md` (solo override; Cursor legacy: `.cursor/skills/`) |

Id esempio (dominio copy): `tono-di-voce`, `humanizer`, `italiano-locale`.

### Frontmatter competenza

```yaml
---
name: {id}   # es. tono-di-voce
kind: competency
version: 1.0.0
# Solo L1/L2: versione della STESSA competenza al livello inferiore
extends-version: 1.0.0   # L1 → L0; L2 → L1
description: >-
  ...
---
```

- L0: `kind: competency`, `version`; **senza** `extends-version`
- L1/L2: `extends-version` allineato alla `version` della stessa id al livello inferiore
- Versionamento **indipendente** per competenza (semver proprio + CHANGELOG locale); non segue automaticamente la `version` dell'agente host

### Risoluzione runtime

Per ogni id in `competencies:` dell'agente attivo:

1. Carica L0 `a-agentzero/competencies/{id}/SKILL.md` se esiste
2. Carica L1 `a-{dominio}/competencies/{id}/SKILL.md` se esiste
3. Carica L2 `{repo}/.agents/skills/{figlio}/competencies/{id}/SKILL.md` se esiste; fallback `.cursor/skills/` per consumer Cursor legacy

In conflitto: **L2 > L1 > L0**. Reference on-demand dalla competenza al **livello più alto** che le espone.

L0 resta **sottile** (principi cross-dominio). L1 porta regole di dominio + corpus `references/`. L2 solo delta progetto.

**Baseline L0 opzionale:** una competenza può esistere **solo a L1** senza gemello in `a-agentzero/competencies/` (es. SEO: `a-seozoom/competencies/`; illustrazioni: `a-illustrator/competencies/`; charts: `a-charts/competencies/`). Non creare baseline L0 «per simmetria». In quel caso il frontmatter L1 omette `extends-version` (nessun livello inferiore della stessa id).

### Adozione opt-in per dominio

Dichiarare `competencies:` e mantenere `a-{dominio}/competencies/{id}/` è **opt-in** per l'agente L1 che ne ha bisogno (es. `a-copywriter` per `tono-di-voce`, `humanizer`, `italiano-locale`; `a-seozoom` per `seo-import`, `metriche-analisi`, `onpage-seo`, `geo-citabilita`; `a-illustrator` per `stile-visivo`, `prompt-composizione`, `preview-render`, `qa-artefatti`; `a-charts` per `scelta-tipo`, `leggibilita`, `implementazione`, `qa-grafici`).

- L1 di altri domini **non** devono copiare o dichiarare competenze non pertinenti solo perché esistono baseline L0.
- Al sync L1←L0, se le voci pending riguardano competenze di un altro dominio: allinea `extends-version` (+ bump patch) senza adottare i moduli; valuta adozione solo se il dominio le userà.

### File dati ≠ competenze

I **file dati di progetto** (`.cursor/brands/`, `.cursor/illustration-styles/`, `.cursor/wordpress/`, `.cursor/product/` / `.claude/product/` / `product/`, brief SEO, …) restano **dati**, non moduli `kind: competency`. La competenza governa *come* usarli (discovery, onboarding, coerenza); non spostare né duplicare i file dati sotto `competencies/{id}/`. Override L2 della competenza = regole/delta, non una seconda copia del brand/style brief.

**Discovery product (personas / JTBD / Gherkin):** ordine di lookup `.cursor/product/` → `.claude/product/` → `product/`. Artefatti tipici: `prd.md`, `mockup/`, `personas.md`, `jtbd.md`, `features/`. Guida: [`docs/discovery-pipeline.md`](../docs/discovery-pipeline.md). Competenza condivisa: `po-interviewer` (L0).

### Asset operativi fuori dalle competenze

Le competenze sono **workflow + canoni** (SKILL, markdown reference). **Non** ripackaging di codice o asset caricati dagli script:

- `scripts/`, CLI e path runtime restano sotto l'agente L1 (path stabili per i consumer)
- JSON/config letti dal codice (es. `export-manifest.json`, selettori UI) restano in `a-{dominio}/references/` (o path già usato dagli script), non obbligatoriamente sotto `competencies/{id}/`
- La competenza **punta** a quegli asset; spostarli richiede aggiornare gli script e i consumer

### Riuso competenze cross-dominio

Un L1 può **istruire** a caricare una competenza di un altro dominio (es. `a-seozoom` / `onpage-seo` → `a-copywriter/competencies/tono-di-voce` in scrittura title/meta/FAQ) senza dichiararla nel proprio frontmatter `competencies:` e senza duplicarne il corpus. Caricare on-demand solo quando il task lo richiede (non su puro import/analisi). Corpo copy lungo: continua a **delegare** all'agente L1 proprietario.

### Sync versioni competenza

Stesso schema agenti: se `extends-version` della competenza L1/L2 è inferiore alla `version` del livello inferiore, segnala sync. Report:

```bash
bash a-agentzero/scripts/agent-version.sh competency-chain a-copywriter/competencies/humanizer/SKILL.md
```

Dettaglio: [`references/agent-versioning.md`](references/agent-versioning.md) § Competenze.  
Override L2 in scaffold: [`references/extension-scaffold.md`](references/extension-scaffold.md).

---

## Apprendimento da sessione (`/learn`)

Skill L0 dedicata: [`learn/SKILL.md`](learn/SKILL.md).

| Invocazione | Effetto |
|-------------|---------|
| `/learn ?` | Illustra apprendimenti dalla conversazione corrente; **non** modifica file |
| `/learn !` | Consolida in skill L2 / brand / rules del repo attivo |

Gerarchia scrittura: L2 > file dati > rules > L1 (solo su richiesta esplicita). Sicurezza L0 non derogabile. Target per dominio: [`learn/references/consolidation-targets.md`](learn/references/consolidation-targets.md).

---

## Sync agenti (`/sync`)

Skill L0 dedicata: [`sync/SKILL.md`](sync/SKILL.md). Script: [`scripts/sync-agents.sh`](scripts/sync-agents.sh).  
Criteri generalizzazione L2: [`sync/references/l2-generalization.md`](sync/references/l2-generalization.md).

| Comando | Effetto |
|---------|---------|
| `/sync ?` | Report catene versioni L1←L0 (e L2 se path progetto) + stato comandi L0; **nessun** deploy |
| `/sync !` | `deploy-all.sh` (skill, agents, comandi L0) + report; sync selettivo `extends-version` resta guidato |
| `/sync <` | Analizza skill L2 nei progetti; propone taglio DUP o promozione a L1/L0; **nessuna scrittura** |

Non sostituisce il workflow in [`references/agent-versioning.md`](references/agent-versioning.md): dopo STALE leggere CHANGELOG padre e applicare solo il delta necessario.  
`/sync <` non applica promozioni: dopo conferma utente, edit mirati su L1/L0 + snellimento L2.

---

## Comandi Cursor L0

Baseline slash command ereditabili da ogni progetto. Canone: [`commands/`](commands/). Canale ufficiale: **`/sync !`**.

| Livello | Path | Ruolo |
|---------|------|-------|
| **L0** | `a-agentzero/commands/{nome}.md` | Baseline generica |
| **User** | `~/.cursor/commands/{nome}.md` | Symlink da L0 (deploy via `a-agentzero/deploy.sh`) |
| **Progetto** | `{repo}/.cursor/commands/{nome}.md` | Override: se presente, vince sul comando user |

Nomi L0: `version`, `document`, `review`, `improve`, `commit`.  
`/sync ?` e `/sync !` riportano `OK` / `MISSING` / `DRIFT` sui symlink; con `--projects` anche `override` vs `inherit` per repo.  
Non copiare i file L0 in ogni consumer: creare override solo se serve un workflow specifico.

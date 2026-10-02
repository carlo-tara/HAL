# Scaffold agente figlio di progetto (L2)

Workflow per creare una skill figlia che eredita da un agente madre L1.

Usare quando: nuovo progetto, nuova pubblicazione nel repo, o assenza di skill L2 per l'agente attivo.

Per **nuovi agenti L1** da proto-prompt o corpus skill esterni: segui [l1-from-proto.md](l1-from-proto.md) (critica ed estensione, non copia; vendor gitignored + pin + update se il repo va aggiornato nel tempo).

---

## Prerequisiti

- Agente madre L1 identificato (es. `a-copywriter`)
- Root del progetto nota (repo corrente)
- Nome progetto/pubblicazione concordato (es. `esempio`, `miosito`)

---

## Workflow

```
Task Progress:
- [ ] 1. Identifica agente madre L1
- [ ] 2. Carica catena L0 → L1 (extends:)
- [ ] 3. Verifica assenza figlio duplicato in .cursor/skills/
- [ ] 4. Crea directory .cursor/skills/{dominio}-{progetto}/
- [ ] 5. Copia e compila extension-template.md → SKILL.md
- [ ] 6. Aggiungi delta: path, override, capacità, deleghe
- [ ] 7. (Opzionale) Crea file dati progetto dal template L1
- [ ] 8. Verifica frontmatter extends: e assenza duplicazioni
- [ ] 9. Imposta versionamento: `version: 1.0.0`, `extends-version` = versione corrente L1
- [ ] 10. Crea CHANGELOG.md figlio da [changelog-template.md](../../a-agentzero/references/changelog-template.md)
```

---

## Step dettagliati

### 1. Identifica agente madre L1

| Dominio | Agente madre | Template dati opzionale |
|---------|--------------|------------------------|
| B2B / GTM | `a-b2b` | L2 `b2b-*` + path enrichment in skill figlio |
| Copy | `a-copywriter` | `.cursor/brands/{nome}.md` da `brand-brief-template.md` |
| Design (UI, Charts, Illustrazioni) | `a-design` | `.cursor/chart-styles/`, `.cursor/illustration-styles/` |
| Harness / Engineering / TDD | `a-harness` | `docs/glossary.md`, `Makefile`, L2 `harness-*` |
| Product (PO, Personas, JTBD, BDD) | `a-product` | L2 `product-*` + `.cursor/product/` (`prd.md`, `personas.md`, `jtbd.md`, `features/`) |
| SEO | `a-seozoom` | brief SEO da `project-brief-template.md` |
| WordPress | `a-wordpress` | `.cursor/wordpress/{nome}.md` da `site-brief-template.md` |

### 2. Carica catena ereditarietà

Leggi in ordine:

1. `~/.agents/skills/a-agentzero/SKILL.md`
2. `~/.agents/skills/a-{dominio}/SKILL.md`
3. (Se esiste) `a-{dominio}/extension-template.md` locale per sezioni dominio

Non copiare nel figlio ciò che è già nel base: il figlio contiene **solo delta**.

### 3. Verifica duplicati

```bash
ls .cursor/skills/
grep -r "extends: a-{dominio}" .cursor/skills/ 2>/dev/null
```

Se esiste già un figlio per lo stesso dominio+progetto, chiedi se aggiornare o creare variante.

### 4–5. Crea SKILL.md figlio

```bash
mkdir -p .cursor/skills/{dominio}-{progetto}
cp agents/a-agentzero/extension-template.md .cursor/skills/{dominio}-{progetto}/SKILL.md
# oppure, se presente:
# cp agents/a-{dominio}/extension-template.md .cursor/skills/{dominio}-{progetto}/SKILL.md
```

Compila frontmatter:

```yaml
---
name: {dominio}-{progetto}
extends: a-{dominio}
version: 1.0.0
extends-version: 1.0.0   # versione L1 al momento della creazione — leggi da SKILL.md padre
description: >-
  {Una riga: cosa aggiunge rispetto al base, per quale sito/progetto.}
---
```

Per la versione corrente del padre L1:

```bash
bash agents/a-agentzero/scripts/agent-version.sh show ~/.agents/skills/a-{dominio}
# oppure
bash agents/a-agentzero/scripts/agent-version.sh show agents/a-{dominio}
```

Copia il valore `Version` in `extends-version` del figlio.

### 6. Sezioni delta obbligatorie

Nel body del figlio, compila almeno:

| Sezione | Contenuto |
|---------|-----------|
| **Progetto** | Nome, dominio, working directory |
| **Path locali** | Dove scrivere output (content/, plugins/, assets/, seo/) |
| **Override workflow** | Solo ciò che differisce dal L1 |
| **Capacità aggiuntive** | Skill/regole specifiche del progetto |
| **Deleghe** | Sibling e altri agenti (vedi template sotto) |

Se esistono **più figli** sullo stesso L1, dichiara `role:` (e opz. `primary:`) nel frontmatter — vedi AGENT-PROTOCOL § Multi-figlio.

### Deleghe sibling (template)

```markdown
## Deleghe

| Agente / skill | Ruolo | Quando |
|----------------|-------|--------|
| `{sibling-data}` | data | Import, CSV, manifest, metriche |
| `{sibling-editorial}` | editorial | Title, meta, FAQ, CTA, publish checklist |
| `{slug}-voice` | voice | Tono, registri, rewrite vocale |
| `a-copywriter` | L1/L2 | Corpo lungo, humanize |
| `a-illustrator` | L1/L2 | Asset, copertine |
| `a-seozoom` / L2 SEO | L1/L2 | Keyword da dati reali |
| `a-charts` | L1/L2 | Grafici, serie, funnel visuali |
| `a-b2b` | L1/L2 | Facade B2B → a-product § Profilo B2B (delega po/enrichment) |
| `a-po` | L1/L2 | Product shape, validate, prioritize |
| `a-enrichment` | L1/L2 | Cascade HubSpot/Apollo/LeadMagic / gates |

**Conflitto tipico:** stuffing / CTA invasiva vs tono → vince voice/brand (non SEO).
```

Compila solo le righe pertinenti; non inventare sibling assenti.

### 7. File dati associati (opzionale)

Crea il file dati nel path standard del dominio, compilato dal template L1:

```bash
# Esempi
mkdir -p .cursor/brands
cp agents/a-copywriter/brand-brief-template.md .cursor/brands/{nome-sito}.md

mkdir -p .cursor/wordpress
cp agents/a-wordpress/site-brief-template.md .cursor/wordpress/{nome-sito}.md
```

### 9. Versionamento figlio L2

```bash
cp agents/a-agentzero/references/changelog-template.md \
  .cursor/skills/{dominio}-{progetto}/CHANGELOG.md
# Compila voce [1.0.0] con data e descrizione baseline progetto
```

Regole: vedi [agent-versioning.md](agent-versioning.md).

### 10. Verifica finale

- [ ] `extends: a-{dominio}` corretto nel frontmatter
- [ ] `name` unico in `.cursor/skills/`
- [ ] `version` e `extends-version` presenti; `extends-version` = versione L1 corrente
- [ ] Se multi-figlio: `role:` (e opz. `primary:`) documentati; Deleghe sibling complete
- [ ] `CHANGELOG.md` figlio creato con baseline 1.0.0
- [ ] Nessuna duplicazione di regole già in L0/L1
- [ ] Path progetto e working directory espliciti
- [ ] Deleghe verso altre skill di progetto documentate
- [ ] File dati creato se richiesto dal dominio
- [ ] Agent companion `.cursor/agents/{nome}.md` creato o aggiornato (`extends-version`, path)
- [ ] (Opzionale) Override competenze L2 solo come delta (sotto)
- [ ] Se `.cursor/` è in `.gitignore` del repo: dopo creazione/edit skill, `git add -f .cursor/skills/{dominio}-{progetto}/…` (altrimenti restano solo locali)

---

## Git: tracciare L2 quando `.cursor/` è ignorato

Molti repo ignorano l’intera cartella `.cursor/`. Le skill L2 sotto `.cursor/skills/` **non** entrano in commit/push se non forzate.

```bash
# Dopo scaffold, /learn !, o edit skill L2
git add -f .cursor/skills/{dominio}-{progetto}/SKILL.md \
  .cursor/skills/{dominio}-{progetto}/CHANGELOG.md \
  .cursor/skills/{dominio}-{progetto}/**/*.md
```

Vale anche per override comandi progetto (`.cursor/commands/`) e agent companion (`.cursor/agents/`) se devono vivere nel repo.

Anti-pattern: edit skill + commit solo di codice prodotto — le regole restano solo sulla macchina locale.

### Commit: lista UI vs index vuoto

Se la diff-tab / UI dell’IDE elenca file «staged» ma `git status` mostra **index vuoto**, ripristinare **solo** quella lista autoritativa (`git add` path per path; `git add -f` se sotto `.cursor/` gitignored) — **non** l’intero working tree. Path già in HEAD senza delta → skip.

---

## Agent companion (obbligatorio se usi subagent Cursor)

Se il progetto espone un agente in `.cursor/agents/{nome}.md` allineato alla skill L2:

1. Alla **creazione** L2: crea o aggiorna il companion con stessi `extends` / path competenze / working directory
2. A ogni **sync L2←L1** (bump `extends-version` o CHANGELOG skill): allinea anche il companion (`extends-version`, path `competencies/`, riferimenti SKILL)
3. Non lasciare companion con path legacy dopo un rename L1

Vedi anche [agent-versioning.md](agent-versioning.md) § Companion.

---

## Override competenze L2 (opzionale)

Se il dominio dichiara `competencies:` (es. copy: `tono-di-voce`…; SEO: `seo-import`…; illustrator: `stile-visivo`…), puoi aggiungere solo il delta progetto:

```bash
mkdir -p .cursor/skills/{dominio}-{progetto}/competencies/{id}
# Crea SKILL.md con kind: competency, version, extends-version = version L1 della stessa id
```

Frontmatter minimo:

```yaml
---
name: {id}
kind: competency
version: 1.0.0
extends-version: 1.0.0   # = version L1 a-{dominio}/competencies/{id}/
description: >-
  Override {id} per {progetto}.
---
```

Body: **solo** regole/path/esempi locali. Non duplicare il corpus L0/L1.  
Risoluzione: L0 → L1 → questo file (vince L2). Specifica: [AGENT-PROTOCOL.md](../AGENT-PROTOCOL.md) § Competenze modulari.

---

## Anti-pattern

- **Non** copiare intere sezioni dal L1 nel figlio — usa `extends:` e delta
- **Non** omettere `extends:` — il figlio deve dichiarare il padre
- **Non** mettere credenziali nel figlio — restano in `.env`
- **Non** creare figli generici senza nome progetto (es. `copywriter-generic` in un repo multi-brand: usa `{dominio}-{brand}`)
- **Non** creare agenti L1 sibling per una competenza (`a-humanizer`, ecc.): usa `competencies/{id}/`
- **Non** spostare file dati (brand, illustration-styles, brief) sotto `competencies/` — restano in `.cursor/…`
- **Non** fondere due ruoli (data+editorial) nello stesso L2 se i perimetri sono distinti — usa multi-figlio + `role:`
- **Non** dimenticare il companion `.cursor/agents/` dopo sync skill

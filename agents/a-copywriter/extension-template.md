---
name: copywriter-{progetto}
extends: a-copywriter
version: 1.0.0
extends-version: 1.1.0
competencies:
  - tono-di-voce
  - humanizer
  - italiano-locale
description: >-
  Copy per {progetto} — eredita a-copywriter e aggiunge tono, path e regole locali.
---

# Copywriter {progetto} — estensione progetto

Skill figlia (L2). Eredita `a-agentzero` → `a-copywriter` → **questo file**.  
Competenze: risolvi L0 → L1 → eventuali override sotto `competencies/{id}/`.

---

## Progetto

| Campo | Valore |
|-------|--------|
| Nome | {nome-progetto} |
| Dominio | {es. esempio.it} |
| Working directory | {path assoluto} |

---

## Brand e tono

| File | Path |
|------|------|
| Brand file | `.cursor/brands/{nome-sito}.md` |

### Quando serve una skill voice dedicata

Vedi L0 `tono-di-voce` § Brand file vs skill voice. Se il corpus vocale è pesante (registri per tipo, writing-rules, struttura post):

- Crea `.cursor/skills/{slug}-voice/SKILL.md` o `{slug}-tone-of-voice` con `extends: a-copywriter`
- Brand resta fonte di lessico/inclusività/PS; voice skill = registri e regole di scrittura
- Non duplicare tabelle Usa/Evita tra brand e voice

### Override tono (solo delta rispetto al brand file)

- Registro: {tu / Lei / neutro}
- {regola vocale 1}
- {parole vietate o preferite}
- Linguaggio inclusivo: estendi [scrittura-inclusiva.md](../../a-copywriter/competencies/tono-di-voce/references/scrittura-inclusiva.md) se il brand ha regole settoriali

Per override strutturato della competenza, vedi sezione **Competenze L2** sotto.

---

## Path locali

| Tipo contenuto | Path |
|----------------|------|
| {es. Pagine} | `{path}` |
| {es. SEO copy} | `{path}` |

---

## Override workflow

{Nessun override — segui a-copywriter | descrivi passi aggiuntivi.}

---

## Competenze L2 (opzionale)

Crea solo i file di override necessari. Path:

```
.cursor/skills/copywriter-{progetto}/competencies/
  tono-di-voce/SKILL.md      # delta voce / inclusività
  humanizer/SKILL.md         # delta anti-AI / ritmo
  italiano-locale/SKILL.md   # delta lessico / regionale / idiomi
```

Frontmatter esempio:

```yaml
---
name: tono-di-voce
kind: competency
version: 1.0.0
extends-version: 1.0.0   # = version L1 a-copywriter/competencies/tono-di-voce/
description: >-
  Override tono-di-voce per {progetto}.
---
```

Body: **solo delta**. Non copiare il corpus L1.  
Check: `bash agents/a-agentzero/scripts/agent-version.sh competency-chain .cursor/skills/copywriter-{progetto}/competencies/{id}/SKILL.md`

---

## Deleghe

| Agente / skill | Quando |
|----------------|--------|
| `a-seozoom` | Keyword, title/meta tecnici da dati reali |
| `{skill-progetto}` | {es. seo-geo-specialist} |

---

## Regole locali

- {regola 1}

---

## Versionamento

| Campo | Valore |
|-------|--------|
| `version` | Versione delta L2 |
| `extends-version` | Versione `a-copywriter` integrata |
| CHANGELOG | `.cursor/skills/copywriter-{progetto}/CHANGELOG.md` |

Alla creazione: `extends-version` = `version` corrente di `a-copywriter` (1.1.0+).  
Sync: [agent-versioning.md](../../a-agentzero/references/agent-versioning.md) — `agent-version.sh pending .cursor/skills/copywriter-{progetto}/SKILL.md`

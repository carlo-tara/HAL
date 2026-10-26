---
name: learn
parent: a-agentzero
version: 1.5.0
description: >-
  Slash /learn con doppia modalità: /learn ? illustra gli apprendimenti dalla
  conversazione o sessione corrente; /learn ! consolida nelle skill attive del
  progetto (L2, brand, rules), e — se necessario — Attività in ./ToDo.md e/o
  apprendimenti in docs locali; scrive changelog Progetto|HAL e bump
  patch (/version patch) sulle skill toccate.
disable-model-invocation: true
---

# /learn — apprendimento da sessione (L0)

Skill utility di **a-agentzero**. Cattura ciò che emerge dalla chat corrente e lo persiste nei file di configurazione progetto o HAL.

**Reference:**

- [consolidation-targets.md](references/consolidation-targets.md)
- [learn-guidelines.md](references/learn-guidelines.md) (per regole cosa apprendere, ambiti e formato scrittura)
- [tool-pitfalls.md](references/tool-pitfalls.md) (pitfall tool Zed validati in ≥2 sessioni)

---

## Invocazione

| Comando    | Modalità                                                                |
| ---------- | ----------------------------------------------------------------------- |
| `/learn ?` | **Riflessione** — report apprendimenti (nessuna scrittura file)         |
| `/learn !` | **Consolidamento** — scrive target + changelog + `/version patch` skill |
| `/learn`   | Mostra sintassi                                                         |

---

## Workflow `?` (Riflessione)

```
Task Progress:
- [ ] 1. Ricostruisci sessione: messaggi, decisioni, file toccati.
- [ ] 2. Usa `python3 router.py routing "<testo>" --routes skill ToDo docs escludi` per classificare ogni voce (System 1).
- [ ] 3. Verifica duplicati nei file in contesto.
- [ ] 4. Emetti report.
```

### Formato Output `?`

```markdown
# /learn ? — Apprendimenti

## Sintesi

[1-2 frasi]

## Apprendimenti

### 1. [Titolo breve]

- **Cosa:** [enunciato]
- **Evidenza:** [da chat]
- **Stato:** nuovo | già in skill/docs/ToDo
- **Ambito:** Progetto | HAL
- **Destinazione:** skill | ToDo | docs | escludi
- **Target proposto:** `path/file.md` (o `./ToDo.md` · P1 · #tag)

## Prossimo passo

Esegui `/learn !` per consolidare.
```

---

## Workflow `!` (Consolidamento)

```
Task Progress:
- [ ] 1. Estrai apprendimenti (se non fatto prima in sessione).
- [ ] 2. Applica diff minimo sui target (vedi `consolidation-targets.md`).
- [ ] 3. Se serve ToDo: `- [ ] Titolo #tag · P1` (non sovrascrivere `todo` tool).
- [ ] 4. Changelog apprendimenti in `product/session-learnings.md` (obbligatorio).
- [ ] 5. Bump patch version e agg. `CHANGELOG.md` delle `SKILL.md` toccate.
- [ ] 6. Emetti report finale.
```

### Formato Output `!`

```markdown
# /learn ! — Consolidamento completato

## Scritto

| Apprendimento | Ambito          | Destinazione          | File   |
| ------------- | --------------- | --------------------- | ------ |
| ...           | Progetto \| HAL | skill \| ToDo \| docs | `path` |

## Changelog

Appended: `product/session-learnings.md`

## Versioni

- `skill-name` 1.0.0 → 1.0.1
```

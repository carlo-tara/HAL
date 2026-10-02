---
name: backlog-prioritization
kind: competency
version: 1.1.0
description: >-
  Sceglie framework di prioritizzazione contestuale, Opportunity Score per
  problems, Now/Next/Later e rewrite outcome. Solo L1 (a-po).
---

# Competenza L1 — backlog-prioritization (a-po)

Decide **cosa prima** e in che forma (**Backlog slice** / outcome), non quanto “piace” una feature list.

Non confondere con **Slice** harness (≤4 file) — vedi `docs/glossary.md`.

---

## Quando applicare

- `/prioritize` su backlog, roadmap, growth bet, o post-validate
- Dopo `/scamper` se il PO ha adottato bet (ranking fine, non ideazione)
- Conflitto stakeholder su “cosa entra nel prossimo Backlog slice”
- Feature roadmap da riscrivere in outcome

## Quando NON applicare

- Nessuna strategy/outcome → framing o OKR prima
- Framework già funzionante e stabile — non cambiare per moda
- Story AC dettagliate / `.feature` → `a-gherkin` dopo il Backlog slice
- Se esiste `.cursor/product/prd.md`, prioritizza da **Epic/US** (status + outcome), non da wishlist parallela
- Iniziative ancora grezze / solution-first senza baseline → `/scamper` prima
- Dichiarare perimetro file harness → `a-harness` `/slice`

---

## Workflow

```
1. Chiedi (max 2): stage prodotto, dati disponibili, tipo decisione (sprint / quarter / bet)
2. Scegli framework (sotto) — dichiara perché
3. Se prioriti problems: Opportunity Score = Importance × (1 − Satisfaction) quando hai survey/proxy
4. Se initiatives: ICE o RICE se serve Reach; MoSCoW solo come forcing function
5. Bucket: Now | Next | Later | Icebox | Won't (con reason)
6. Rewrite top items come outcome:
   Enable [segment] to [customer outcome] so that [business impact]
7. Definition of Ready check (light) prima di handoff gherkin
8. Checkpoint: conferma Backlog slice + success signal
```

### Framework hint

| Context | Prefer |
|---------|--------|
| Customer problems / unmet | Opportunity Score |
| Ideas quick triage | ICE |
| Scale + reach data | RICE |
| Hard cut scope | MoSCoW |
| Time-critical | Cost of Delay (qualitative ok) |

---

## Definition of Ready (light)

Prima di handoff delivery/spec:

- [ ] Outcome e success signal chiari
- [ ] Dipendenze note
- [ ] Fit in un Backlog slice ragionevole (altrimenti split)
- [ ] Acceptance intent chiaro (dettaglio → `a-gherkin`)

---

## Regole ferree

1. Framework esegue strategy; non la crea
2. Prioritizza problems/opportunities prima delle soluzioni
3. Ogni Now item ha success signal
4. Non stimare story point senza team — T-shirt ok a livello roadmap

---

## Anti-pattern

- Framework whiplash ogni sprint
- Now pieno di zombie >90 giorni senza decisione
- Output roadmap come elenco feature senza outcome
- Chiamare “Slice” un pezzo di backlog (termine riservato all’harness)

---

## Output della fase

- Framework scelto + rationale (2 righe)
- Ranked Backlog slice / buckets Now–Won't
- Outcome statements + success signals
- Handoff: `a-gherkin` / `a-copywriter` / `a-charts` se serve

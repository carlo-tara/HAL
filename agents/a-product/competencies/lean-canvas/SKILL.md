---
name: lean-canvas
kind: competency
version: 1.0.0
description: >-
  Lean Canvas (Maurya): 9-box business hypothesis in fill order, versioning,
  pitfalls, vs BMC, stress-test → evidence-probe. Solo L1 (a-po).
---

# Competenza L1 — lean-canvas (a-po)

Cattura in **una pagina datata** le ipotesi di business early-stage: Problem, Segments, UVP, Solution, Channels, Revenue, Cost, Metrics, Unfair Advantage. Il canvas è un’**ipotesi**, non un deliverable finale.

Template: [lean-canvas-template.md](references/lean-canvas-template.md)

---

## Quando applicare

- `/canvas` o `/shape` su **new product** / early venture senza PMF
- Dopo `problem-framing` quando serve un modello di business testabile
- Pivot: nuova versione datata (non overwrite)

## Quando NON applicare

- Late-stage con PMF → preferisci BMC / modeling finanziario / OKR (fuori scope lean)
- Hardware multi-year R&D, marketplace multi-side (usa **un canvas per lato** + note network), regulated con pathway dominante → canvas incompleto o tool diversi
- Tool interno captive senza mercato
- Inventare ICP/personas/jobs: usa L2 o `a-personas` / `a-jtbd` (`hypothesis` se manca evidenza)

---

## Lean vs BMC (scelta rapida)

| Lean Canvas | Business Model Canvas |
|-------------|------------------------|
| Problem, Solution, Key Metrics, Unfair Advantage | Key Partners, Key Activities, Key Resources, Customer Relationships |
| Domanda: *c’è un business?* | Domanda: *come funziona il modello?* |

5 box condivise: Segments, UVP/Value Prop, Channels, Revenue, Cost.

---

## Workflow — ordine Maurya (non left-to-right)

```
1. Problem + Customer Segments (sempre in coppia; include existing alternatives + early adopters)
2. Unique Value Proposition (una frase; 5 draft → scegli; high-level concept X for Y)
3. Solution (top 3 feature mappate 1:1 ai top 3 problem — MVP only)
4. Channels (1–2 da testare, non 8)
5. Revenue Streams + Cost Structure (sempre in coppia; rough estimate > blank; include CAC)
6. Key Metrics (3–5 misurabili oggi; no vanity)
7. Unfair Advantage (spesso "TBD — to be earned")
8. Stress-test (sotto) → checkpoint → /validate (evidence-probe)
```

Se team multi-founder: ciascuno compila da solo, poi **diff** prima di reconciliare.

Path artefatto: `.cursor/product/lean-canvas-YYYY-MM-DD.md` (nuova data = nuova versione).

---

## Stress-test (3 domande)

1. Quale box ha **meno evidenza**? → riskiest assumption (test next)
2. Se un competitor leggesse questo, cosa vedrebbe come debole?
3. Quale box potresti rimuovere e avere ancora un business? Se “qualsiasi”, non hai capito il modello

Poi passa a `evidence-probe` (Build-Measure-Learn: smallest test sulla box più debole).

---

## Regole ferree

1. Specificità: persone, numeri, meccanismi — no “SMB / productivity / better software”
2. Estimate rough (anche low-confidence) > blank su Revenue/Cost
3. Date ogni versione; dopo interview cohort / MVP / pricing change → nuova data
4. Non inventare ICP, CAC, ARPU, metriche
5. UVP = benefit, non feature list; Unfair Advantage ≠ “first mover”
6. Canvas interno; per investitori/deck → traduci (non presentare il canvas come pitch)

---

## Anti-pattern

- Compilare una volta e non aggiornare
- Vapor in ogni box
- Saltare Revenue o Cost
- Canvas come deliverable investor
- Un solo canvas per tutta la vita del prodotto
- Feature creep nella Solution

---

## Output della fase

- Canvas markdown (9 box, ordine Maurya) + data versione
- Tag `evidence` | `hypothesis` per box critiche
- Riskiest 1–3 assumptions → next `/validate`
- Opz. handoff: `positioning-offer` (allinea Moore a UVP), `growth-loops` (Channels), `market-public-data` (sizing); `/prd` se serve Epic/US (canvas non le sostituisce)

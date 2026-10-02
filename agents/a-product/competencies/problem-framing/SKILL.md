---
name: problem-framing
kind: competency
version: 1.0.0
description: >-
  Framing del problema (Look Inward / Outward / Reframe) e OST light
  (outcome → opportunities → solutions → experiments). Solo L1 (a-po).
---

# Competenza L1 — problem-framing (a-po)

Assicura che il team risolva il **problema giusto** prima delle soluzioni. Produce problem statement / HMW e, se utile, un Opportunity Solution Tree leggero su **un solo outcome**.

---

## Quando applicare

- Dopo triage, o quando la richiesta è solution-first (“servono gamification / AI / dashboard”)
- Prima di `/shape` se manca un problema condiviso
- Branch **existing** (prodotto con utenti) vs **new** (concetto senza domanda validata)

## Quando NON applicare

- Problema già confermato dal PO e documentato → `positioning-offer` o `evidence-probe`
- Serve ricerca utenti primaria → delega `a-personas` / `a-jtbd` (consuma i loro output, non inventare)

---

## Workflow

### A — Canvas (MITRE-style, lean)

```
1. Look Inward — sintomi; perché non risolto; come siamo parte del problema (bias/assunzioni)
2. Look Outward — chi lo vive / non lo vive; chi è lasciato fuori; chi beneficia se resta
3. Reframe — restatement + How Might We [azione] as we aim to [obiettivo]
```

### B — OST light (opzionale, un outcome)

```
1. Desired outcome misurabile (una metrica)
2. 3–7 opportunities (problemi dal punto di vista cliente: “lotto a…”)
3. Opportunity Score qualitativo o Importance × (1 − Satisfaction) se hai dati
4. ≥3 solution ideas per opportunity top (PM/Design/Eng perspectives) — non scegliere la prima
5. 1–2 experiment ideas per solution promettente → handoff evidence-probe
```

Checkpoint: “quali 2–3 opportunity portare a shape/validate?”

---

## Regole ferree

1. Non brainstorm di soluzioni nel canvas A
2. Opportunities ≠ feature request
3. Un outcome per OST; etichetta hypothesis se i needs non sono validati
4. Existing vs new: per **new**, segnala gap di domanda e richiama `evidence-probe` (categorie GTM)

---

## Anti-pattern

- Accettare la soluzione dello stakeholder come frame
- Albero con cinque outcome in parallelo
- Inventare pains senza artefatti personas/JTBD o conferma PO

---

## Output della fase

- Problem statement + HMW
- Assunzioni etichettate
- OST light (se fatto): outcome | opportunities ranked | solutions | experiment hints
- Next: `/canvas` (`lean-canvas`) se new/early venture; `/prd` (`prd-authoring`) se serve backlog US/AC; `/scamper` se serve esplorare alternative su strategia/GTM; altrimenti `/shape` (`positioning-offer`) o `/validate` (`evidence-probe`)

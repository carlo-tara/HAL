---
name: jtbd
parent: a-product
version: 1.1.10
description: >-
  Reason why: senza capire il lavoro che il cliente cerca di fare, il backlog ottimizza funzioni e non i suoi progressi. Job Analyst / JTBD integrato in a-product: Jobs-To-Be-Done job-first, ODI needs/unmet, continuity di flusso, job stories e scenario seeds per BDD; switch interview JTBD (timeline + Four Forces). Usare per mappare jobs da personas, unmet needs, affinare JTBD e switch interview.
---

# jtbd — JTBD & Unmet Needs

Skill di prodotto per **Job Analyst / JTBD** (job-first + ODI). Competenza integrata di **a-product**.

---

## Prerequisito

`personas.md` con ≥1 `primary` `active`. Altrimenti stop → esegui skill `personas` (`/create`).

Discovery product: `.cursor/product/` → `.claude/product/` → `product/`. Output: `jtbd.md`.

---

## Comandi (slash)

| Invocazione | Obiettivo |
| ----------- | --------- |
| `/triage` | Impatto → map/refine/unmet/add-story/add-need/prioritize/none |
| `/create` | `jtbd.md` completo da personas |
| `/map` | Zoom UI/flusso su catena esistente |
| `/unmet` | Discovery unmet sistematica |
| `/add-story` | Job stories aggiuntive da NL |
| `/add-need` | Unmet needs aggiuntivi da NL |
| `/refine` | Riallinea dopo cambio UI/flusso |
| `/prioritize` | Scoring unmet già enunciati |
| `/check` | Coerenza personas + catena + pain→need |
| `/gap` | Lacune; può raccomandare add-story/add-need |
| `/show` | Read-only |
| `/export` | Scrive `jtbd.md` dopo conferma PO |
| `/interview` | Switch interview cliente: `prep` \| `guide` \| `synth` |

Se manca evidenza di hire/switch: proponi `/interview`.

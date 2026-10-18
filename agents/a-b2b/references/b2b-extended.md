2. Esegui [a-product § Profilo B2B](../../a-product/SKILL.md) (intake → discovery → shape/validate → charts/enrichment → consolidation + Pilot fit check).
3. Usa i reference locali sotto per brief e dettaglio delega.

Solo product shape (no pilot) → prefer **`a-product` diretto**.
Solo enrichment → invoca la skill **`enrichment`** (`/enrich`, `/gate`, `/domain`, `/research-batch`).
Product multi-step non-B2B → prefer **`a-product`**.

Detail: [references/delegation-playbook.md](delegation-playbook.md)

---

## System 1 (Laya) Integration in B2B Pilots

Prima di impegnare System 2 in analisi di account o pipeline di enrichment complesse, l'agente `a-b2b` utilizza **Laya (System 1)** per:
1. **Scoring ICP e Pilot Fit in batch (`router.py batch_score`)**: Valuta l'aderenza all'Ideal Customer Profile di account e contatti in millisecondi, filtrando i lead fuori target prima della cascata CRM.
2. **Routing GTM (`router.py routing`)**: Instrada rapidamente le richieste tra enrichment, pilot fit check e triage commerciale.

---

## Output contract

Come **a-product** § Profilo B2B (Decision summary, Pilot fit check, Package / Evidence / Enrichment status, Next actions) più **Outcome** / Success signal (non solo ship count).

Incomplete intake: [references/project-brief-template.md](project-brief-template.md)

---

## Non-goals / freeze

- **No authoring** PRD, Lean Canvas, package/offer o positioning — delega `a-po`
- **Cascade enrichment** — eseguita tramite la skill interna `enrichment` (`a-b2b/enrichment/SKILL.md`)
- **No** `.feature` / TDD / shell UI — `a-product` / `a-harness` / `a-design`
- **No** seconda copia della cascata GTM — canone in `a-product` § Profilo B2B
- Solo: ingresso B2B, bind L2 `b2b-*`, puntatore al canone, reference locali

---

## Discovery file dati

| Path | Uso |
|------|-----|
| `.agents/skills/b2b-*/` | L2 delta progetto (guardrail, path enrichment, ICP) |
| L2 enrichment paths | passed through to `a-enrichment` |
| L2 ICP / outreach templates | gate input + `a-copywriter` drafting |
| `a-product/SKILL.md` § Profilo B2B | canone orchestra |

---

## Apprendimento / Sync

Eredita `/learn` e `/sync` da a-agentzero.

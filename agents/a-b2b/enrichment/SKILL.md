---
name: enrichment
parent: a-b2b
version: 1.1.7
description: >-
  Reason why: senza arricchire e filtrare i contatti con criteri di aderenza, le liste restano nomi grezzi poco utili per vendere o collaborare. Contact/account enrichment B2B: dual entry (CRM cohort + domain-first), ICP/fit gates, HubSpot → Apollo → LeadMagic → SQLite master, lead-research output. Read-oriented CRM by default; strategy angles not outreach drafts. Invocabile con /enrich, /gate, /domain, /research-batch.
---

# enrichment — contact & account enrichment

Skill B2B per contact & account enrichment. Competenza integrata di **a-b2b**.

All'avvio: `a-b2b` → **questo skill** → L2 se presente (path ICP e scripts da `b2b-*`).

---

## Mission

Eseguire e governare enrichment contatti/account: dual entry, gate ICP/fit, cascade provider, master SQLite, output lead-research. Non scrivere CRM di default; non draftare outreach.

L2 supplies ICP, path master/scripts, skip flags.

---

## Comandi (slash)

| Invocazione | Obiettivo |
|-------------|-----------|
| `/enrich` | Cascade A (cohort/CRM) o run completo guidato |
| `/gate` | Solo ICP/fit check — no paid spend |
| `/domain` | Entrypoint B domain-first su un dominio |
| `/research-batch` | Lista lead con contratto fit-score |

Senza slash: dominio singolo → `/domain`; lista/cohort → `/enrich` o `/research-batch`; solo qualifica → `/gate`.

---

## Dual entry

| Entry | Quando | Reference |
|-------|--------|-----------|
| **A — Cohort / CRM-first** | Export batch, master DB | cascade sotto |
| **B — Domain-first** | Singolo dominio/account | [domain-enrichment-workflow.md](references/domain-enrichment-workflow.md) |

---

## Cascade A (canonical)

1. Export / cohort (CRM read)
2. **ICP / fit gate** — [enrichment-gates.md](references/enrichment-gates.md); stop o ask before paid phases
3. HubSpot enrich (read; write only if explicitly triggered)
4. Apollo on HubSpot misses — 3-step org→people→enrich quando discovery ([lead-research-output.md](references/lead-research-output.md))
5. LeadMagic on double misses (**optional**: skip se chiave assente o `SKIP_LEADMAGIC`; fill miss + verify + mobile se L2 lo prevede). Orchestrazione phase1/phase2: [leadmagic-orchestration.md](references/leadmagic-orchestration.md)
6. Merge to SQLite master DB

Phase gates (truthy skip): `SKIP_HUBSPOT`, `SKIP_APOLLO`, `SKIP_LEADMAGIC`.

**Defaults:** HubSpot/Mongo **read-oriented**. CRM updates opt-in. No Mongo write-back assumed.

**Master DB:** one SQLite master per product line; path via env/L2. **CSV = handoff only**, not a second master.

---

## Output contract

Ogni delivery enrichment:

- **Entry** (A/B) + fasi eseguite / skip
- **Gate result** (MATCH/NO MATCH + fit se batch)
- **Credits** per provider
- **Master path** + handoff CSV se richiesto
- Batch: summary + per-lead da [lead-research-output.md](references/lead-research-output.md)
- **Strategy/angle** — non email/call draft (→ `a-copywriter`)

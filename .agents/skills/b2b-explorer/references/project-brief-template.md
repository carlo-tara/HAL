# Project Brief Template — b2b-explorer (Lombardia)

Usa questo template prima di orchestrare un task pilota. Compila i guardrail dal L2 (`.cursor/skills/b2b-explorer/SKILL.md`); non inventare ICP/geo/prezzi.

Working directory: `/var/www/WTP_App`. Dati: `.shared/b2b/`. Env: **solo** `.env` in root.

## 1) Objective
- Business objective:
- Decision to make now:
- Expected output format:

## 2) Pilot fit check
- Geography: bacino **~3h auto da Chiasso** (LO+PI+ER+VE; no CH); spesso ≤2h operativo
- Company size / ICP: PMI **6–50** dipendenti
- Capacity: max **3 presenza + 3 online** / settimana (overflow = hold engagement)
- GTM bucket: advocacy · nicchie · tiepidi · freddi (no close a volume sui freddi)
- Disqualifiers in play:
- Primary counterpart: imprenditore/titolare (HR solo ops)
- Timeline: ago–ott 2026 (prova PMF)

## 3) Offer perimeter (→ a-po)
- Included products: MWK + Pensioni + ETF (Spread **fuori** dallo SKU commerciale)
- Packaging: **Base** / **Premium** (A–D ritirata)
- Price (Enrico 2026-08-17): Base **€5–7k + €100/pax**; Premium **€10k + €300/pax** — non quotare il vecchio 10k flat
- Welfare: erogazione solo da **società con sede in Italia**
- No-new-product confirmation: sì (tutor e sportello 8h = delivery, non nuovi prodotti finanziari)

## 4) Audience and personas
- Existing customers involved:
- New leads / enrichment cohorts involved:
- GTM: **70%** lista warm approvata · **30%** warming lookalike (zero close a volume sul 30%)
- Key persona assumptions:
- Unknowns to validate:

## 5) JTBD and value
- Top jobs to address:
- Suspected unmet needs:
- Key outcomes promised:

## 6) Data and evidence
- Available notes/data sources: `.cursor/product/`, `explorer/b2b/docs/`, `projects/b2b-piccoleimprese/`
- Enrichment DB: Postgres schema `enrichment.*` (`DATABASE_URL`; legacy `WTP_ENRICHMENT_DB_PATH` sqlite)
- Enrichment entry: A cohort/CRM / B domain-first / both:
- What is already validated:
- What is still hypothesis:

## 7) Delegation plan
- `a-po` task:
- `a-personas` task:
- `a-jtbd` task:
- `a-enrichment` task:
- `a-charts` task:
- `a-copywriter` task (outreach / UI explorer via `b2b-explorer-ui-ux`):

## 8) Success signals
- Pilot KPI: volume **5–6 close** entro fine 2026 (revenue = listino, non 50–60k su 10k flat)
- Stop criteria:
- Enrichment spend stop (ICP no-match / low fit):

---
name: b2b-{progetto}
extends: a-b2b
version: 1.0.0
extends-version: 2.1.0
description: >-
  Delta progetto per {progetto} rispetto a a-b2b facade (guardrail, path enrichment;
  canone orchestra = a-product § Profilo B2B).
---

# B2B — estensione progetto

Skill figlia (L2). Eredita da `a-b2b` (facade) via `extends:`. Canone orchestra: `a-product` § Profilo B2B.

All'avvio: `a-agentzero` → `a-b2b` → **questo file**.

## Progetto

| Campo | Valore |
|-------|--------|
| Nome | {nome-progetto} |
| Working directory | {path} |

## Pilot guardrails (hard constraints)

- Geography:
- ICP (employees):
- Primary counterpart:
- Product perimeter:
- Timeline:
- **Org / reward / CPO / bonus:** L2 only se serve (non-goal L1; no playbook HR in `a-b2b` / `a-product`)

## ICP detail (user asset)

Concrete ICP for gates (`a-enrichment`) and offer fit (`a-po`). Keep here — not in L1.

### Target industries
-

### Company size / revenue / stage
-

### Positive signals
-

### Disqualifiers (DO NOT PROCEED)
-

### Target decision-maker titles (priority order)
1.
2.
3.

### ICP evaluation checklist
- [ ] Industry match
- [ ] Size range
- [ ] Operational maturity
- [ ] Has key needs we solve
- [ ] No disqualifiers

**Default thresholds:** 4+ checked → proceed; ≤2 → stop and ask. Fit bands: `a-enrichment/references/enrichment-gates.md`.

### Outreach template paths (optional)
| Asset | Path |
|-------|------|
| Cold email template | |
| Cold call script | |

## Enrichment paths (local) — passed to a-enrichment

| Tipo | Path / env |
|------|------------|
| Enrichment dir | |
| Master SQLite | |
| Scripts | |
| Default entry | A cohort/CRM / B domain-first / both |

## Integrations (optional)

Composio / Rube / MCP: **opt-in** under `a-enrichment` L2 rules; same write gates.

| Integration | Enabled | Notes |
|-------------|---------|-------|
| | no | |

## Package status

- A/B/C/D assumptions: (authored via `a-po`)

## Override workflow

Nessun override — segui L1 salvo path e guardrail sopra.

## Deleghe

| Agente | Quando |
|--------|--------|
| a-po | Package / validation / growth |
| a-enrichment | Cascade / gate / lead research |
| a-personas | Personas / decision-maker |
| a-jtbd | Job stories / unmet needs |
| a-charts | KPI / funnel |
| a-copywriter | Draft outreach from templates / angles |

## Apprendimento / Sync

Eredita `/learn` e `/sync` da a-agentzero via L1.

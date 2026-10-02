# Delegation Playbook — a-b2b / a-product § Profilo B2B

## Scope
This playbook defines how the B2B profile (`a-product` § Profilo B2B; entry facade `a-b2b`) delegates work to specialist agents and merges their outputs.

## Pilot guardrails
Apply **L2 hard constraints** for the active project (geography, ICP, product perimeter, timeline).
If no L2 is loaded, ask for guardrails before packaging decisions.

## Delegation contract (common)
For each delegation, provide:
1. **Objective**: one clear question to answer.
2. **Context**: pilot constraints + known facts.
3. **Required output format**: exact sections expected.
4. **Acceptance checks**: what makes output usable.

## Specialist routing

### a-po
Use when:
- offer/package must be shaped or revised
- validation / evidence plan is needed
- PMM positioning or growth bets for the pilot

Expected output:
- product/package status + assumptions
- evidence plan and risks
- next actions for the product slice

### a-enrichment
Use when:
- cohort or domain enrichment is in scope
- ICP/fit gate, lead research, or SQLite master update is required

Expected output:
- entry A/B, gate result, credits
- contacts / batch lead contract (strategy ≠ draft)
- master path or CSV handoff

Pass L2 enrichment paths and ICP; do not re-run the cascade inside the orchestrator/facade.

### a-personas
Use when:
- target profile is unclear
- decision-maker vs champion path must be validated
- segment assumptions need refinement

Expected output:
- active personas list
- decision trigger and friction summary
- recruitment/validation suggestions for pilot accounts

### a-jtbd
Use when:
- needs must be translated into jobs
- value messaging should be anchored to outcomes
- unmet need prioritization is required

Expected output:
- job map and top job stories
- prioritized unmet needs
- testable scenario seeds for offer validation

### a-charts
Use when:
- KPI/segment/funnel communication is needed
- trade-offs must be visualized for decision speed

Expected output:
- chart spec aligned to question
- concise interpretation notes
- caveats on data quality/coverage

### a-copywriter
Use when:
- draft cold email or call script is required after enrichment/research
- messaging must follow L2 brand / outreach templates

Do **not** treat outreach drafting as part of enrichment.

Expected input:
- trigger signal / angle / conversation starters (from `a-enrichment` or `a-po`)
- ICP + template paths from L2
- evidence vs hypothesis marked

Expected output:
- draft email and/or call script aligned to templates

### Competitive messaging (optional input)
Competitor ad / messaging themes may feed `a-po` offer shaping or `a-copywriter`.
They must not invent or override L2 ICP.

## Direct-vs-orchestrate
| Request | Prefer |
|---------|--------|
| Solo product shape / backlog | `a-po` |
| Solo enrichment / domain research | `a-enrichment` |
| Full B2B pilot (multi-agent) | `a-b2b` (facade) or `a-product` § Profilo B2B |

## Future-agent onboarding (capability-based)
When a new agent appears:
1. Identify capability and fit vs current matrix.
2. Define input/output contract.
3. Add acceptance checks.
4. Keep backward-compatible fallback with current agents.

## Consolidation protocol
After all delegations:
1. Mark each finding as `evidence` or `hypothesis`.
2. Resolve conflicts by pilot guardrails first, evidence second.
3. Build one merged output:
   - decisions
   - open risks
   - next actions (owner, due date, dependency, success signal)

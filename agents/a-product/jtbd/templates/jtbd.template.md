---
version: 0.1.0
status: draft
personas_source: personas.md
---

# JTBD

## J-01

```yaml
id: J-01
persona: P-01
statement: "" # solution-agnostic
job_map:
  - id: JM-01a
    intent: ""
    flow_position: { prev: none, next: JM-01b }
    context_carries: []
exception_flows: []
job_stories:
  - id: JS-01
    when: ""
    i_want_to: ""
    so_that: ""
    maps_to: JM-01a
    flow_position: { prev: none, next: null }
    ui_bindings: []
    origin: create # create | add_nl
    status: hypothesis
emotional_jobs: []
social_jobs: []
needs:
  - id: N-01
    direction: minimize # minimize | increase
    metric: ""
    object: ""
    context: ""
    kind: performance
    discovery: analytic # analytic | intuitive | po_stated
    source: ""
    importance: null
    satisfaction: null
    opportunity: null
    status: hypothesis # hypothesis | unmet | met | unknown
    origin: create
unmet_ranking: []
scenario_seeds:
  - id: SS-01
    prose: ""
    links: [N-01, JS-01, P-01]
evidence: []
open_questions: []
```

# Pin — Graph & Loop Engineering (principi)

**Ruolo AF:** metodologia Loop/Work Graph mappata su slash a-harness; **non** dipendenza runtime.

## Fonti

| Fonte | URL | Uso |
|-------|-----|-----|
| Sarthak Rastogi — Harness, Graph, and Loop Engineering | https://sarthakai.substack.com/p/harness-graph-and-loop-engineering | Stack Prompt→Context→Harness→Loop→Graph; loop fields; graph patterns; graph-trap |
| 0xCodila / Andrew Ng — Loops to Graphs | https://substack.com/@0xcodila/note/c-316446147 | Reflection, tool use, planning, multi-agent → building blocks |
| Opinion AI — graph visual framing | https://substack.com/@opinionai/note/c-313482473 | Nodi, routes, checks, retries, decisions (conferma framing) |

## Adottato (idee operative)

| Idea | Dove in a-harness |
|------|-------------------|
| Preferisci Loop; Graph solo se ruoli/parallel/handoff; `-y` = multi-cycle fino a fine backlog | competenza `graph` |
| Termination + error triage + goal osservabile | Loop Spec → `/cycle` + `when-stuck` |
| Pattern pipeline / router / parallel / orchestrator-worker | Work Graph in `work-graph.md` |
| Reflection / tool / plan / multi-agent | Tipi nodo → slash / Make / L1 |
| Memoria condivisa nel grafo | progress + `.cursor/product/work-graph.md` |
| Agent = Model + Harness | già L1; graph non sostituisce harness |

## Non-adopt

- LangGraph / GraphRAG / knowledge-graph SaaS come Platform API
- Google A2A protocol come canone AF
- Cron Claude Code / Codex Automations come runner obbligatorio
- Secondo agent loop / CLI “graph runner” (anti self-harness)
- Act automatico dal Work Graph **senza** `-y` / senza accept sul primo nodo
- Con `-y`: mega-GREEN sul grafo intero (va cycle per nodo); bypass freeze/stuck/Make
- Statistiche virali non verificate (es. grant “Stanford” citati in folklore)

## Relazione con Spec Kit / `/cycle`

`/graph` = **Plan** di orchestrazione (come decomporre).  
`/slice` → `/cycle` = **Act** su un nodo alla volta.  
Converge residui → nuovo `/slice`, non silent expand del grafo in corso.

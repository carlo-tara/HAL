---
name: session-progress
kind: competency
version: 1.1.4
description: >-
  Progress append-only = Capture harness (lavoro reale): session_id, fasi/make,
  stuck/friction → priorità, flush on exit. Trajectory-light senza UI vendor.
  Mappa residui: ./ToDo.md → /todo; Work Graph: work-graph.md → /graph.
  ready=0 solo con MAKE_EXIT osservato.
---

# Competenza L1 — session-progress

Stato fuori dalla context window. Template: [agent-progress-template.md](../../references/agent-progress-template.md).

## Evidence / Capture

Il progress è il **Capture** leggero di come il lavoro harness è *effettivamente* andato — fasi, `make_exit`, stuck — non guesswork né riscrittura a posteriori.

- Append-only = audit trail riusabile (analogo “Page” operativa: una sessione composta da eventi)
- Eventi `stuck` / friction / fail ripetuti = **signal** per prioritizzare il prossimo `/slice` (evidence-first)
- Flush on exit = artefatto consultabile; niente segreti in chiaro nel progress
- Non confondere con `context-budget` (window/file) né col semantic layer (glossario/BC)

## Quando

- Inizio `/slice` o `/cycle` → crea/apri progress + `session_id`
- Ogni fase R/G/Rf/ready → append evento
- `/progress` → leggi e riassumi (no riscrittura history)
- Exit / timeout / stuck → flush evento `exit`

## Regole

1. Append-only; fork = nuovo `session_id` da checkpoint
2. Offload log/test lunghi su file, non in chat
3. Ownership header aggiornato
4. Resume: leggi ultimo progress prima di continuare Act
5. Prima di un nuovo `/slice`: scorri friction/stuck recenti — priorità da **lavoro reale**, non da opinion
6. Append `ready … | 0` / `exit flush` solo con `MAKE_EXIT:0` (o banner Gate OK) **osservato** nel log del run corrente — non su gate running/killed/parziale né su log di uno slice precedente (canone [pr-proof-checklist.md](../../references/pr-proof-checklist.md) § Proof del gate)
7. Post-accept / post-flush di un commit o wave: rinfrescare `./ToDo.md` (strip P0 stale già in HEAD) quando l’umano chiede residui o la mappa è chiaramente obsoleta

## `/progress`

1. Apri file progress corrente
2. Riporta fase, ultimi eventi, make_exit, stuck count
3. Se assente → crea da template e segnala fresh session
4. Se richiesto “cosa fare dopo”: evidenzia friction/stuck aperti come candidati evidence-first

## Mappa residui (`./ToDo.md`)

Backlog **rinfrescabile** (≠ Capture progress). Path fisso: **`./ToDo.md`** in root del repo consumer.  
**Igiene operativa** → competenza `todo` / slash **`/todo`** (questa sezione = pointer + quando rinfrescare).

**Quando scrivere/aggiornare**

- Richiesta esplicita di mappare attività rimaste / residual backlog / «cosa resta»
- Dopo una wave o converge con molti gap aperti (lista per umano, non Act automatico)
- Edit di `./ToDo.md` → carica `todo` e fai il pass di igiene

**Contenuto minimo** — sezioni P0/P1/P2, track paralleli, «già fatto»; dettaglio formato/tag/UL-BC in `todo`.

**Vincoli:** non è uno `/slice` accettato; non sostituisce `agent-progress.md`; niente segreti. Protocollo breve anche in L0 `a-agentzero` § Mappa residui.

## Work Graph (`.cursor/product/work-graph.md`)

Orchestrazione Plan-only (Loop o Work Graph). Path fisso consumer.  
**Igiene / generazione** → competenza `graph` / slash **`/graph`**. Non è Capture progress né Slice accettato; memoria condivisa col grafo = questo progress + `work-graph.md`.

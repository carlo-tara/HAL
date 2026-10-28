5. **Fine backlog** quando: `next` assente/`—`, oppure lista Richieste/Attività aperte della sorgente esaurita, oppure nodi restanti marcati skip (es. opz. con nota in progress)

**Hard stop (interrompe il multi-cycle, non bypassabile con `-y`):**

- `stuck@3` sullo stesso approccio
- Freeze violato / path freeze senza waiver
- Gate Make del nodo ≠ 0 e non recuperabile
- Blocco umano richiesto (auth, scelta PO, path consumer sconosciuto senza N/A)

Ogni nodo resta uno slice con perimetro proprio (≤4 file o WAIVER). `-y` autorizza la **catena** di cycle, non un mega-GREEN unico sul grafo intero.

## Risoluzione input

| Invocazione                                                           | Sorgente                                                                                 |
| --------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| `/graph` o `/graph -y` (no altri args)                                | **context** — chat + `./ToDo.md` (P0/P1 aperti se presenti) + friction/stuck in progress |
| `/graph ToDo.md` / `/graph -y ToDo.md` (path file esistente o `*.md`) | **file** — voci/sezioni del file come serie di Richieste                                 |
| `/graph <testo>` / `/graph -y <testo>` (altro)                        | **request** — una Richiesta esplicita (es. refactor della classe User)                   |

Se path ambiguo (file non trovato): trattalo come **request** e segnalalo nel meta `source`.

## Lean / deterministic (obbligatorio)

Orchestrazione (flag strip, next pointer, handoff) = **deterministica** — non ri-pianificare in chat.

1. **Brief ≤200 token** — prima di clarify/emit, costruisci un brief lean con:
   `bash scripts/harness-prompt-builder.sh render --max-tokens 200 --set goal='…' --set source='context|file|request' -- " /graph source={source} goal={goal}. Emit work-graph + handoff only."`
2. **Niente dump** — non incollare transcript, `ToDo.md` intero, né `work-graph.md` completo nel prompt; passa solo titoli/P0–P1 o il nodo `next`.
3. **Handoff compatto** — dopo Write, aggiorna `product/state/handoff-graph.json`:
   `bash scripts/harness-prompt-builder.sh handoff-write graph --dir product/state --field node_id=… --field next=… --field y=true|false --field brief='…'`
   (il `--dir` è obbligatorio: il default del tool è `product/` e genera shadow copy fuori canone — caso 2026-10-27, vedi `learn/references/tool-pitfalls.md` § Writer canonico)
4. **Multi-cycle (`-y`)** — ogni nodo: leggi **solo** `handoff-graph.json` + riga nodo in `work-graph.md`; non riaprire il contesto chat della `/graph` iniziale.

## Pipeline (`/graph`)

1. **Flags** — estrai `-y` (auto-accept + multi-cycle); strip dagli args (**deterministico**)
2. **Lean brief** — `harness-prompt-builder.sh render` (≤200 token)
3. **Resolve** — source = context | file | request; normalizza in lista Richieste (titoli, non body)
4. **Clarify lean** — goal osservabile; BC; termini glossario (`ubiquitous-language`); owner path (`bounded-context`)
5. **Decide** — Loop vs Work Graph (tabella sotto); motiva (anti **graph-trap**)
6. **Emit** — Loop Spec **oppure** nodi+archi + Mermaid
7. **Map AF** — ogni nodo → slash e/o L1; stop conditions; stuck@3
8. **Write** — `product/work-graph.md` (una scrittura)
9. **Handoff** — scrivi `handoff-graph.json`. Senza `-y`: next + “attendi accept”. Con `-y`: auto-accept → **multi-cycle** nodo→nodo fino a fine backlog o hard stop (stato solo da handoff + work-graph)

## Loop vs Graph

| Preferisci **Loop**           | Usa **Work Graph**              |
| ----------------------------- | ------------------------------- |
| Un obiettivo, un BC, un owner | Ruoli/L1 diversi                |
| Nessun parallelismo sicuro    | Fan-out indipendente            |
| Path lineare RGR              | Handoff auditabili o gate umani |

Default AF: **preferisci Loop**. Graph solo con motivazione esplicita nel file.

## Loop Spec (campi)

- Goal osservabile; context pack (file ≤4 / evidence)
- Azioni piccole; observe (make/test/diff)
- **Termination**; **error triage** (recuperabile vs hard blocker)
- `stuck@3` (`when-stuck`); mapping AF (`/cycle` o R→G→Rf)

## Work Graph

**Pattern:** `pipeline` | `router` | `parallel` | `orchestrator-worker`

**Nodo:** `id`, tipo (`plan|reflect|tool|act|review|human|delegate`), owner (slash o L1), input/output, stop, next

| Building block (Ng) | AF                                  |
| ------------------- | ----------------------------------- |
| Reflection          | pass critique / `/refactor` review  |
| Tool use            | `make` / Platform API               |
| Planning            | `/slice`                            |
| Multi-agent         | Deleghe L1 (`a-gherkin`, `a-po`, …) |

Memoria condivisa = **progress** + **work-graph.md** (non transcript chat).

### Template artefatto

```markdown
# Work Graph

- source: context|file|request
- auto_accept: false|true
- multi_cycle: false|true
- mode: loop|graph
- why_mode: …
- goal: …
- bc: …
- next: <node_id> — attendi accept | multi-cycle (-y) → /slice o /cycle

## Loop (se mode=loop)

…

## Graph (se mode=graph)

| id  | type | owner | in  | out | stop | next |
| --- | ---- | ----- | --- | --- | ---- | ---- |

\`\`\`mermaid
flowchart TD
…
\`\`\`
```

## Anti-pattern

- Graph trap (grafo dove basta un Loop)
- Act automatico multi-slice **senza** `-y` e senza `/slice` accettato
- Usare `-y` per bypassare freeze / stuck@3 / Make fail
- Con `-y`: un solo Act sul grafo intero invece di cycle per nodo
- Fermarsi dopo il primo nodo quando `-y` e il backlog ha ancora `next`
- Retry ciechi / termination assente
- Secondo harness loop / LangGraph-as-canone
- Sinonimi fuori glossario per Nodo/Arco/Loop/Work Graph
- Ri-pianificare in chat flag strip / next pointer (devono restare **deterministici**)
- Multi-cycle che re-dumpa transcript o `work-graph.md` intero invece di `handoff-graph.json` + nodo

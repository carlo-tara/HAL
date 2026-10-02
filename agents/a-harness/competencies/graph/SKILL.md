---
name: graph
kind: competency
version: 1.3.0
model: orcarouter/deepseek/deepseek-v4-flash
model-fallback: cursor-default
description: >-
  Genera Loop o Work Graph (Markdown + Mermaid) da contesto, file (es. /graph
  ToDo.md) o richiesta esplicita. Flag -y = auto-accept + multi-cycle sequenziale
  fino a fine backlog (ogni nodo = /slice|/cycle). Default Plan-only: scrive
  .cursor/product/work-graph.md; preferisci Loop (anti graph-trap). Lean brief
  ≤200 token + handoff-graph.json via prompt-builder. Use when user invokes
  /graph or needs loop/graph engineering from a series of requests.
---

# Competenza L1 — graph (Loop / Work Graph)

Progetta **come** correre una serie di Richieste nel harness — non esegue Act **salvo** `-y`.

Pin fonti / adopt / non-adopt: [graph-loop-source.md](../../references/graph-loop-source.md).

## Attivazione

1. L’utente invoca **`/graph`** (con o senza argomenti; opz. **`-y`**)
2. Richiesta esplicita di loop/graph engineering, work graph, decomposizione multi-nodo

**Default (senza `-y`):** scrivi `.cursor/product/work-graph.md`; proponi il primo nodo; **non avvia** `/red` / `/cycle` / Act finché l’umano non accept → poi `/slice` o `/cycle` (un nodo alla volta).

**Con `-y` (auto-accept + multi-cycle):** dopo il write, tratta il Work Graph come accettato e **esegui multi-cycle sequenziale** su tutti i nodi della pipeline fino a **fine backlog** (vedi sotto). Vale per **tutte** le modalità di input.

## Flag `-y`

1. Rileva token `-y` ovunque negli args (`/graph -y`, `/graph -y ToDo.md`, `/graph ToDo.md -y`, `/graph -y refactor User`)
2. **Strip** tutti i `-y` **prima** della resolve context | file | request
3. Pipeline identica fino a Write; poi ramo auto-accept + **multi-cycle**
4. In `work-graph.md` meta: `auto_accept: true` e `multi_cycle: true` quando `-y`

### Multi-cycle fino a fine backlog (`-y`)

Dopo il write, ripeti finché non sei a fine backlog:

1. Apri **`/slice` o `/cycle`** sul nodo `next` corrente (acceptance = stop del nodo)
2. Completa RGR del nodo (`stuck@3`, freeze, `make` / gate del nodo)
3. Aggiorna `work-graph.md` (`next` → successivo; progress append)
4. Se il nodo ha `next` non vuoto → ripeti sul nodo successivo **nella stessa invocazione**
5. **Fine backlog** quando: `next` assente/`—`, oppure lista Richieste/Attività aperte della sorgente esaurita, oppure nodi restanti marcati skip (es. opz. con nota in progress)

**Hard stop (interrompe il multi-cycle, non bypassabile con `-y`):**

- `stuck@3` sullo stesso approccio
- Freeze violato / path freeze senza waiver
- Gate Make del nodo ≠ 0 e non recuperabile
- Blocco umano richiesto (auth, scelta PO, path consumer sconosciuto senza N/A)

Ogni nodo resta uno slice con perimetro proprio (≤4 file o WAIVER). `-y` autorizza la **catena** di cycle, non un mega-GREEN unico sul grafo intero.

## Risoluzione input

| Invocazione | Sorgente |
|-------------|----------|
| `/graph` o `/graph -y` (no altri args) | **context** — chat + `./ToDo.md` (P0/P1 aperti se presenti) + friction/stuck in progress |
| `/graph ToDo.md` / `/graph -y ToDo.md` (path file esistente o `*.md`) | **file** — voci/sezioni del file come serie di Richieste |
| `/graph <testo>` / `/graph -y <testo>` (altro) | **request** — una Richiesta esplicita (es. refactor della classe User) |

Se path ambiguo (file non trovato): trattalo come **request** e segnalalo nel meta `source`.

## Lean / deterministic (obbligatorio)

Orchestrazione (flag strip, next pointer, handoff) = **deterministica** — non ri-pianificare in chat.

1. **Brief ≤200 token** — prima di clarify/emit, costruisci un brief lean con:
   `bash scripts/harness-prompt-builder.sh render --max-tokens 200 --set goal='…' --set source='context|file|request' -- " /graph source={source} goal={goal}. Emit work-graph + handoff only."`
2. **Niente dump** — non incollare transcript, `ToDo.md` intero, né `work-graph.md` completo nel prompt; passa solo titoli/P0–P1 o il nodo `next`.
3. **Handoff compatto** — dopo Write, aggiorna `.cursor/product/handoff-graph.json`:
   `bash scripts/harness-prompt-builder.sh handoff-write graph --field node_id=… --field next=… --field y=true|false --field brief='…'`
4. **Multi-cycle (`-y`)** — ogni nodo: leggi **solo** `handoff-graph.json` + riga nodo in `work-graph.md`; non riaprire il contesto chat della `/graph` iniziale.

## Pipeline (`/graph`)

1. **Flags** — estrai `-y` (auto-accept + multi-cycle); strip dagli args (**deterministico**)
2. **Lean brief** — `harness-prompt-builder.sh render` (≤200 token)
3. **Resolve** — source = context | file | request; normalizza in lista Richieste (titoli, non body)
4. **Clarify lean** — goal osservabile; BC; termini glossario (`ubiquitous-language`); owner path (`bounded-context`)
5. **Decide** — Loop vs Work Graph (tabella sotto); motiva (anti **graph-trap**)
6. **Emit** — Loop Spec **oppure** nodi+archi + Mermaid
7. **Map AF** — ogni nodo → slash e/o L1; stop conditions; stuck@3
8. **Write** — `.cursor/product/work-graph.md` (una scrittura)
9. **Handoff** — scrivi `handoff-graph.json`. Senza `-y`: next + “attendi accept”. Con `-y`: auto-accept → **multi-cycle** nodo→nodo fino a fine backlog o hard stop (stato solo da handoff + work-graph)

## Loop vs Graph

| Preferisci **Loop** | Usa **Work Graph** |
|---------------------|--------------------|
| Un obiettivo, un BC, un owner | Ruoli/L1 diversi |
| Nessun parallelismo sicuro | Fan-out indipendente |
| Path lineare RGR | Handoff auditabili o gate umani |

Default AF: **preferisci Loop**. Graph solo con motivazione esplicita nel file.

## Loop Spec (campi)

- Goal osservabile; context pack (file ≤4 / evidence)
- Azioni piccole; observe (make/test/diff)
- **Termination**; **error triage** (recuperabile vs hard blocker)
- `stuck@3` (`when-stuck`); mapping AF (`/cycle` o R→G→Rf)

## Work Graph

**Pattern:** `pipeline` | `router` | `parallel` | `orchestrator-worker`

**Nodo:** `id`, tipo (`plan|reflect|tool|act|review|human|delegate`), owner (slash o L1), input/output, stop, next

| Building block (Ng) | AF |
|---------------------|-----|
| Reflection | pass critique / `/refactor` review |
| Tool use | `make` / Platform API |
| Planning | `/slice` |
| Multi-agent | Deleghe L1 (`a-gherkin`, `a-po`, …) |

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
| id | type | owner | in | out | stop | next |
|----|------|-------|----|-----|------|------|

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

---
name: a-harness
extends: a-agentzero
version: 1.7.0
model: orcarouter/deepseek/deepseek-v4.1-flash
model-fallback: cursor-default
extends-version: 1.6.15
competencies:
  - context-budget
  - sustainable-pace
  - platform-api
  - session-progress
  - todo
  - graph
  - when-stuck
  - functional-core
  - tdd-red
  - tdd-green
  - tdd-refactor
  - steward
  - ubiquitous-language
  - bounded-context
  - anti-corruption-layer
  - aggregate-root
description: >-
  Reason why: senza test, gate Make e ritmi sostenibili, lo sviluppo non ha uscita verificabile né qualità stabile.
  Meta-Harness: TDD XP, Steward, DDD, Makefile gates, session progress,
  when-stuck, Plan→Act, L3. Skill-layer sopra Cursor/Claude.
  Not for product discovery or BDD authoring.
---

# a-harness — Meta-Harness

Orchestratore L1: implementazione **test-first** su medium slices, gate Make, DDD, Steward. Eredita da **a-agentzero**.

**Sorgente:** `a-harness/` · **Agente:** [agents/a-harness.md](agents/a-harness.md)  
**Architettura:** [references/harness-architecture.md](references/harness-architecture.md) · **Mnemonic:** [references/component-decision.md](references/component-decision.md)  
**Manuale umano:** [`docs/a-harness-manuale-utente.md`](../docs/a-harness-manuale-utente.md) (§13 man) · Meta: [`docs/harness-engineering.md`](../docs/harness-engineering.md)

All'avvio: `a-agentzero` → **questo skill** → L2 `harness-*` → competenze.

**Sempre attive:** `context-budget`, `sustainable-pace`, `platform-api`, `session-progress`, `when-stuck`.  
**On-demand:** `todo` (Mappa residui / edit `./ToDo.md`), `graph` (Loop / Work Graph → `work-graph.md`), `tdd-*`, `steward`, `functional-core`, 4 DDD.

**HFDP UL (anti-bloat):** **Adapter** = ACL (`anti-corruption-layer`); **Facade** = Make / Platform API e Facade L1 — **no** `competencies/{adapter,facade,strategy}/`.  
**Stati ciclo:** Plan \| Act \| Stuck \| Ready — tabella in [permission-modes.md](references/permission-modes.md); Strategy = competenza di fase.  
**HFDP map:** [references/gof-meta-patterns.md](references/gof-meta-patterns.md).

**Agent = Model + Harness.** Maturity target: **L3 Enforced**.  
Non-goals: dsh/Cordis, harness.lol CLI, Harness.io SaaS, MCP-first, parallelismo massivo, loop autonomo lungo (`/cycle` = verify/retry/stop lieve), CLI Spec Kit come runtime obbligatorio, **offensive scanners / AI pentest / Strix runtime come Platform API** (DevSecOps = secrets+deps+SAST CI-first, low-noise, **authorized**-only — vedi `/steward` + [consumer-platform-hygiene.md](references/consumer-platform-hygiene.md)).

## Coding model ladder

Per **coding Act** (implement/edit/debug/refactor codice): scegli e scala lungo questi rung OrcaRouter (costo → capacità). `model:` di sessione = rung (3); `model-fallback: cursor-default`. Cursor ha un solo modello per chat: in escalazione **chiedere all'utente** di passare al rung successivo prima di continuare Act — non inventare switch mid-chat. Allinea a `when-stuck`: niente 3° retry cieco sullo stesso modello.

1. `orcarouter/deepseek/deepseek-v4-flash-free`
2. `orcarouter/z-ai/glm-5.3-flash`
3. `orcarouter/deepseek/deepseek-v4.1-flash` — default frontmatter
4. `orcarouter/deepseek/deepseek-v4-pro-0813`
5. `orcarouter/kimi/kimi-k2.7-code`

**Tier start**

| Task | Rung |
|------|------|
| Igiene / flush / edit banale | (1) |
| Routine GREEN/REFACTOR ≤4 file | (2) o (3) |
| Hard (debug profondo, multi-ipotesi, architettura) | partire da (4) |
| Long-horizon / surgery repo ampia | (5); se Kimi non disponibile → (4) |

**Escalazione** al rung successivo se: modello non raggiungibile / **rate-limit** / free bloccato; oppure stesso approccio sbagliato **2×** (prima di stuck@3); oppure gate ancora rosso senza progresso dopo minimo GREEN.

**De-escalazione** se il lavoro torna banale.

Contratto: `.cursor/product/contracts/check-harness-coding-model-ladder.sh`.

---

## Prerequisito

Contratto: `.feature` (da `a-gherkin`) **oppure** US/AC (`a-po`) **oppure** task con perimetro file + bounded context. Se manca → delega; **non inventare** behavior.

**Spec-Driven (Spec Kit):** constitution/specify vivono fuori Act (L2 + contratto); in Plan fai *clarify* + *analyze* (cross-artefatto) prima di `/red`; *converge* = `/ready` + nuovo `/slice` sui residui — pin [github-spec-kit-source.md](references/github-spec-kit-source.md).

**Semantic layer (Plan):** glossario + mappa BC = backbone vivo (`ubiquitous-language`, `bounded-context`). Non confondere con `context-budget` (window/file). In `/slice`, prima di Act:

1. **Capability-first** — ancora acceptance a capability / value flow di business, non a stack o file
2. **70/20/10** — priorità termini: core universale (~70) → estensioni di BC/industry (~20) → fine-tuning progetto (~10)
3. **Analyze** — contratto ↔ glossario ↔ BC ↔ file; gap → aggiorna artefatti o delega, non inventare semantica in Act

**Workflow context (Scribe principles):** progress + semantic layer = contesto operativo per Act/delega (≠ `context-budget`). Principi, non SaaS.

1. **Evidence-first** — priorità `/slice` da friction/stuck/gate in progress, non da opinion
2. **Maturity** Discover → Centralize → Automate → Agents = contratto+semantic → Make/progress/ready-proof → `/cycle` → delega solo con brief+contesto (no parallelismo massivo)
3. **Sidekick-like** — progressive disclosure competenze della fase; **Guide Me-like** — `/cycle` a step con permission-modes

**DevSecOps (Plan/Steward):** secrets + dependency audit + **SAST** in CI **prima** di tool extra; gate **low-noise**; no offensive/Strix come canone — [consumer-platform-hygiene.md](references/consumer-platform-hygiene.md).

**Find-and-fix (validated):** finding → evidence → `/red` → `/green`; scope **PR/diff** / ≤4 file; dynamic solo **authorized** fuori harness.

| Artefatto | Path | Se 0 |
|-----------|------|------|
| Glossario | `docs/glossary.md` | [glossary-template.md](references/glossary-template.md) |
| Platform API | `Makefile` | `/bootstrap` o `/steward` |
| Bounded contexts | `docs/bounded-contexts.md` | [bounded-context-map-template.md](references/bounded-context-map-template.md) |
| Progress | `.cursor/product/agent-progress.md` | [agent-progress-template.md](references/agent-progress-template.md) |
| Residui (Mappa residui) | `./ToDo.md` (root repo) | competenza `todo` (`/todo`); pointer in `session-progress` |
| Work Graph | `.cursor/product/work-graph.md` | competenza `graph` (`/graph`); Plan-only Loop/Graph |
| L2 | `.cursor/skills/harness-*/SKILL.md` | [extension-template.md](extension-template.md) |

Invariants: Plan→Act · TDD exit Make · `ready-for-review` prima di review umana · stuck@3 · ≤4 file · Makefile = verità.

---

## Slash

| Invocazione | Competenza | Obiettivo |
|-------------|------------|-----------|
| `/slice` | orchestratore + Plan | Medium slice; ≤4 file; acceptance |
| `/red` | tdd-red | Pre-ottimizzazioni → solo test → `make test-unit` ≠ 0 |
| `/green` | tdd-green + when-stuck | Pre-ottimizzazioni ereditate + minimo YAGNI; stuck@3 |
| `/refactor` | tdd-refactor | Pulizia sotto verdi |
| `/cycle` | sequenza | slice→R→G→Rf→ready + progress (pre-opt in `/red` e `/green`) |
| `/ready` | sustainable-pace | Gate + [pr-proof-checklist.md](references/pr-proof-checklist.md) |
| `/progress` | session-progress | Stato append-only |
| `/todo` | todo | Igiene Mappa residui `./ToDo.md` (priorità, prune, tag, UL/BC); flush «Già fatto» → `./CHANGELOG.md` |
| `/graph` | graph | Loop o Work Graph → `work-graph.md`; `-y` = auto-accept + **multi-cycle** fino a fine backlog |
| `/steward` | steward | Audit infra ([steward-audit-checklist.md](references/steward-audit-checklist.md)) |
| `/bootstrap` | platform-api + steward | Profiles minimal\|standard |

Default ambiguo → chiedi fase. Eredita `/learn`, `/sync` (L0).  
Documentare «tutti» i comandi → chiarisci perimetro (harness+L0+Make vs discovery); sync slash → aggiorna man §13.

### Lean cmd protocol (`/graph` `/slice` `/cycle` `/todo`)

Orchestrazione **deterministica** + anti context-bloat (cmd lean):

1. **Prompt lean** — `scripts/harness-prompt-builder.sh render --max-tokens 200` prima di clarify/Act; niente dump transcript/ToDo/work-graph interi.
2. **Handoff JSON** — `.cursor/product/handoff-graph.json`, `handoff-slice.json`, `handoff-cycle.json`, `handoff-todo.json` via `handoff-write` / `handoff-read` (stato minimo: acceptance, files, node_id, next, summary, brief).
3. **Progressive disclosure** — competenze di fase on-demand (`context-budget`); non caricare tutto L1.
4. Flag espliciti only (`/graph -y`); nessun auto-Act senza accept o `-y`.

### `/cycle`

**Template Method / Hollywood Principle:** `/cycle` è lo **skeleton** fisso (slice → red → green → refactor → ready → flush); Make, hooks e permission-modes “chiamano” l’agente nei punti di estensione — non il contrario (Hollywood: *don’t call us, we’ll call you*). Le fasi TDD e le competenze on-demand sono i **hook** del template; non inventare un secondo loop fuori da questo skeleton.

1. `/slice` (Plan) → acceptance + progress; in Plan: **evidence-first**, **capability-first**, **70/20/10**, **clarify** + **analyze** (Spec Kit + semantic + workflow context)  
2. Handoff **Act** solo dopo slice accettato  
3. `/red` (pre-ottimizzazioni → contratto) → `/green` (pre-opt ereditate → minimo) → `/refactor`  
4. `/ready` (umano = intent); se restano gap rispetto al contratto → nuovo `/slice` (**converge**), non allargare lo slice in corso  
5. Flush progress  

**Accept senza risposte clarify:** se `/accept` (o accept esplicito 1–N) e il Plan ha già **default consigliati** per ogni clarify, lockare quei default e procedere Act — non ri-chiedere. Se un clarify non ha default nel Plan, chiedere prima di `/red`. Dettaglio: [permission-modes.md](references/permission-modes.md).  

**`/cycle` con Plan già aperto:** non equivale ad accept. Ripeti le scelte (`accept N` / `accept A+B`); **non** avviare `/red`. Un nuovo `/cycle` senza accept = reminder Plan, non Act.


**Pre-ottimizzazioni** (obbligatorie in `/red`, riaffermate in `/green`): prompt lean · anti context-bloat (`context-budget`) · delega per competenza — vedi `tdd-red` / `tdd-green`.

Policy warn/fail: [permission-modes.md](references/permission-modes.md).  
DDD tipici: RED → aggregate/ubiquitous/bounded/FCIS · GREEN → ACL + when-stuck · REFACTOR → glossario/BC.

---

## Deleghe

Prima di Act locale in `/red` (e in `/green` se emerge lavoro fuori perimetro): mappa sotto-task → agente; handoff con brief lean. Non assorbire lavoro fuori harness.

| Agente | Quando |
|--------|--------|
| `a-gherkin` | Manca `.feature` / BDD |
| `a-po` | Manca slice/US/PRD / discovery |
| `a-agentzero` | `/sync`, `/learn`, scaffold L2 |
| Steward (`/steward`) | Makefile, hooks, CI, freeze |

Scaffold: [harness-scaffold.md](references/harness-scaffold.md) · Handoff: [handoff-from-gherkin.md](references/handoff-from-gherkin.md)

### Reference essenziali

[makefile-template.mk](references/makefile-template.mk) · [bootstrap-profiles.md](references/bootstrap-profiles.md) · [permission-modes.md](references/permission-modes.md) · [pr-proof-checklist.md](references/pr-proof-checklist.md) · [agent-progress-template.md](references/agent-progress-template.md) · [cursor-hooks-recipe.md](references/cursor-hooks-recipe.md) · [consumer-platform-hygiene.md](references/consumer-platform-hygiene.md)

Pin: [cursor-harness-source.md](references/cursor-harness-source.md) · [pin-curated-lists.md](references/pin-curated-lists.md) · [github-spec-kit-source.md](references/github-spec-kit-source.md) · [graph-loop-source.md](references/graph-loop-source.md) · [madebywild-agent-harness-source.md](references/madebywild-agent-harness-source.md) · [harness-io-source.md](references/harness-io-source.md) · [harness-lol-source.md](references/harness-lol-source.md) · [deepseek-harness-source.md](references/deepseek-harness-source.md) · [cursor-cloud-harness-source.md](references/cursor-cloud-harness-source.md)

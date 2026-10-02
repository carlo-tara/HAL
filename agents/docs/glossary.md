# Glossario dominio — HAL

Documento **vivo**. Termini qui definiti sono obbligatori in skill, script e progress (`ubiquitous-language`).

HAL = sorgente canonica skill (meta-repo), non app consumer.

---

## Entità

| Termine canonico | Definizione | Sinonimi vietati |
|------------------|-------------|------------------|
| L0 | Radice protocollo (`a-agentzero`): sicurezza, scaffold, `/learn`, `/sync`, competenze baseline | Root agent (ambigua), base skill |
| L1 | Agente di dominio in repo (`a-copywriter`, `a-harness`, …) che `extends` L0 | Domain plugin (se inteso come agente) |
| Facade L1 | L1 ingresso/alias che punta a un canone peer (es. `a-b2b` → `a-product` § Profilo B2B); resta `extends: a-agentzero` — **non** `extends` un altro L1 | Alias skill, L1→L1 extends, seconda orchestra |
| Template Method | Skeleton fisso di algoritmo con hook — in AF: **`/cycle`** (slice→R→G→Rf→ready) | Secondo loop custom, competency `template-method` |
| Hollywood Principle | Il framework chiama te (Make/hooks/permission-modes), non il contrario | Polling ad hoc fuori Platform API |
| Adapter | Confini I/O verso sistemi esterni = **ACL** (`anti-corruption-layer`); non competency GoF separata | Adapter pattern OO standalone, `competencies/adapter/` |
| Facade (Make/L1) | Superficie unica verso l’agente: **Platform API** (`Makefile`) e/o **Facade L1** di ingresso; non catalogo GoF | Facade class tutorial, `competencies/facade/` |
| Profilo B2B | Sezione canone in `a-product` (flow pilota, cascata GTM, Pilot fit check); ingresso anche via facade `a-b2b` + L2 `b2b-*` | Orchestra B2B separata, merge body specialisti |
| L2 | Skill figlia di progetto (`.cursor/skills/{dominio}-{progetto}/`) con delta locale | Override file (troppo generico), fork skill |
| Skill | Unità caricabile con frontmatter `name` / `version` / opz. `extends` | Prompt pack, bot |
| Competency | Modulo path-resolved (`competencies/{id}/`) dichiarato in `competencies:` — non agente sibling | Sub-agent, nested agent |
| Platform API | `Makefile` root: unici target ammessi per verify/gate | Script ad hoc, npm scripts non mappati |
| Steward | Persona infra: Makefile, hooks, CI, freeze, potatura — non business code | DevOps generico (se sostituisce il ruolo) |
| Slice | Unità di lavoro medium (≤4 file, acceptance) prima di Act — dominio **Harness** | Ticket vago, mega-PR; **Backlog slice** (prodotto) se inteso come pezzo di roadmap |
| Backlog slice | Pezzo di backlog/outcome prodotto (Now/Next/Later) — dominio **a-po** `/prioritize` | Slice (harness), sprint ticket senza outcome |
| STALE | Catena versioni dove `extends-version` < versione padre | Outdated (senza catena), drift generico |
| Sync | Allineamento deploy/report versioni (`/sync`, `sync-agents.sh`) | Copy files, rsync manuale non documentato |
| Deploy | Pubblicazione symlink skill/agents/commands in `~/.cursor` e `~/.claude` | Install one-off |
| ready-for-review | Gate Make sustainable-pace: meccanica verde prima di review umana di intent | LGTM, merge-ready senza Make |
| Extends | Campo frontmatter al padre nella catena ereditarietà | Import, include |
| Extends-version | Versione del padre dichiarata dal figlio; confronto → STALE | Pin generico |
| Harness | Constraint layer (Make, TDD, DDD, progress) attorno al model | Autonomia illimitata, secondo agent loop |
| Bootstrap | Scaffold profile `minimal` \| `standard` della Platform API | Setup chat one-off |
| Progress | Log append-only sessione (`.cursor/product/agent-progress.md`) | Chat history come fonte di verità |
| Mappa residui | Backlog rinfrescabile in `./ToDo.md` (root repo); igiene via `/todo` | Progress, ToDo generico, backlog prodotto (`Backlog slice`) se inteso come roadmap PO |
| Attività | Voce nella Mappa residui: titolo, tag, priorità P0–P2, perché utile, acceptance | Task vago, ticket, item senza tag/priorità |
| Tag attività | Etichetta ordinabile su Attività (`feature`, `bug`, `techdebt`, `uiux`, `docs`, `infra`, `spike`) | Label ad hoc non catalogata, emoji-only |
| Loop | Ciclo autonomo con goal osservabile, azioni, observe, termination, error triage; path scelto dall’agente entro il harness (`/cycle`) | While infinito, retry cieco, secondo agent loop |
| Work Graph | Artefatto Plan (`.cursor/product/work-graph.md`): Nodi + Archi + Mermaid; percorsi dichiarati; via `/graph` | LangGraph-as-canone, agent org vaga, runtime multi-agent SaaS |
| Nodo | Unità di lavoro nel Work Graph (plan/reflect/tool/act/review/human/delegate) con owner slash o L1 | Step vago, task senza stop |
| Arco | Routing di stato tra Nodi (next/condizione) | Edge non tipizzato, handoff implicito in chat |
| Freeze | Lista file read-only anche in Act (se attiva) | Lock git |
| RGR | Ciclo obbligatorio Red→Green→Refactor su update agenti/skill | Edit diretto, big-bang skill change |
| Build Trap | Misurare il successo sugli **Output** (feature spedite) invece che sugli **Outcome** (valore) — dominio **a-product** intake | Feature factory (vago), “siamo agili” come scusa per ship-only |
| Outcome | Cambiamento di comportamento/valore per utente o business (success signal verificabile) — **a-product** / **a-po** | Output, deliverable, “abbiamo rilasciato” |
| Output | Deliverable o feature prodotto come **mezzo**, non come goal di successo — **a-product** | Outcome, KPI di valore |
| Product Kata | Spine di apprendimento: Direction → Current state → Obstacles → Experiment → reflect — routing in **a-product**; authoring in **a-po**/discovery | PDCA generico, sprint checklist senza outcome |
| Value Exchange | Scambio valore utente ↔ valore business che il prodotto deve ottimizzare — **a-product** Mission | Solo revenue interno, solo vanity metric |

## Verbi / azioni

| Termine canonico | Definizione | Sinonimi vietati |
|------------------|-------------|------------------|
| Bootstrap | Creare/adattare Makefile + artefatti profile | Init repo generico |
| Chain | Report catena L2→L1→L0 (o competency) via `agent-version.sh` | Version dump |
| Sync | Deploy e/o report stato versioni/comandi L0 | Push, publish (ambigui) |
| Deploy | Eseguire `deploy-all.sh` / `a-*/deploy.sh` | Symlink a mano non tracciato |
| Gate | Far passare un target Make (exit 0) | Check mentale |
| Slice | Dichiarare perimetro + acceptance in Plan | Scope creep |
| Red | Dichiarare contratto verificabile che fallisce (no body skill produzione) | Scrivere subito la skill |
| Green | Minimo YAGNI su skill/agente finché i gate Make passano | Over-engineering |
| Refactor | Pulizia sotto gate verdi senza comportamento nuovo | Rewrite con feature |
| Ready | Raggiungere `make ready-for-review` | Ship senza gate |
| Steward | Audit/evoluzione fabbrica | Refactor prodotto |

## Eventi (opz.)

| Evento | Payload minimo | Emesso da |
|--------|----------------|-----------|
| VersionChainStale | agentId, parentVersion, extendsVersion | Tooling / Sync-Deploy |
| ReadyForReviewPassed | session_id, make_exit=0 | Docs / Harness meta |
| BootstrapCompleted | profile=standard\|minimal | Docs / Harness meta |

## Note

- Naming directory agenti: `a-{dominio}` (L0/L1); L2: `{dominio}-{progetto}` (es. `harness-agentfactory`).
- Owner termini ambigui: Protocol/L0 per eredità/sync; Docs/Harness meta per Slice/ready/Platform API; Domain Agents `a-po` per Backlog slice.
- **Slice** ≠ **Backlog slice**: il primo è perimetro file harness; il secondo è prioritizzazione prodotto.
- Non inventare stack app (npm/pytest) in questo glossario.

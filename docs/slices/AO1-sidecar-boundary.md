# Slice AO-1 — Confine BC del side-car Auto Ontology (Livello C)

Stato: **consegnata (Act + guardia GREEN, 2026-11-20)** · Ref: PRD [`docs/29_auto_ontology_semantic_layer.md`](../29_auto_ontology_semantic_layer.md) §6 AO-1, `ToDo.md` `HT-013` · Bounded context attivo: **Knowledge & Ontology (side-car)** (aperto da questa slice)

## 1. Obiettivo

Chiudere la sovrapposizione tra il knowledge store di `auto-ontology-mcp` (record tipizzati + provenienza + FTS5) e il retrieval documentale di `a-knowledge`/`hal_mcp_docs` **prima** che il side-car sia attivo in Zed, fissando il confine nella context map canonica. Il Livello A (registrazione Zed) è `#human` e resta fuori dal perimetro di Act: qui si mette il paletto documentale che lo rende non ambiguo.

## 2. Acceptance (falsificabile)

`bash product/contracts/check-ontology-bc-boundary.sh` → **exit 0 (GREEN)**, cioè:

1. `docs/bounded-contexts.md` ha la riga di context map «Knowledge & Ontology (side-car)» con path (externo pinnato `0fb5ecf`), responsabilità e integrazioni.
2. `docs/bounded-contexts.md` ha la tabella «Routing delle domande» con i 4 ancoraggi di strumento (`chapter_route`, `validate_sql`, `find_join_path`, `get_source`): una sola famiglia → un solo destinatario per riga.
3. Il PRD `docs/29_...md` esiste e referenzia la context map.
4. `HT-013` nel `ToDo.md` punta a questo contratto.

Regola di verità: **RED prima dell'Act** — gli assert (1) e (2) fallivano in plan (3 FAIL osservati: riga BC, tabella routing, ref HT-013); il contratto è stato scritto PRIMA della modifica (RGR), non dopo. All'Act del 2026-11-20 gli assert 1-4 sono **GREEN** (`check-ontology-bc-boundary.sh` exit 0).

## 3. Perimetro (≤4 file + waiver)

| File                                              | Azione                                           |
| ------------------------------------------------- | ------------------------------------------------ |
| `docs/bounded-contexts.md`                        | **Act (dopo accept)**: riga BC + tabella routing |
| `docs/29_auto_ontology_semantic_layer.md`         | PRD (già scritto, Plan)                          |
| `docs/slices/AO1-sidecar-boundary.md`             | questo contratto (già scritto, Plan)             |
| `product/contracts/check-ontology-bc-boundary.sh` | guardia (già scritto, Plan → RED)                |

**Waiver** (meccanici, non logici): `docs/00_indice.md` (riga P2 per il PRD), `ToDo.md` (voce `HT-013`), `product/state/agent-progress.md` (append slice-opened), `product/state/handoff-slice.json` (handoff del `/slice`). Sono lo stato di piano previsto dal protocollo `/slice`, non modifiche di codice.

**Fuori perimetro (dichiarato):** `agents/a-knowledge/SKILL.md` §Deleghe (riga di delega) → merita slice propria AO-1.1 perché tocca la catena L1 (`/version` + extends-version + mirror `link-workspace-skills.sh`); non si mischia con un taglio di soli `docs/`.

## 4. Vincoli non negoziabili

- **Nessun Act prima dell'accept umano** (canone `/slice`/`a-harness`): la modifica a `docs/bounded-contexts.md` è il passo Red→Green, si fa solo dopo accept.
- Il side-car **non** entra in `agents/`, **non** tocca il bundle canonico, **non** aggiunge dipendenze a `requirements.txt` del gateway (FastMCP/SQLAlchemy/sqlglot restano confinati nel clone pinnato).
- La tabella di routing è **canonica**: vive SOLO in `docs/bounded-contexts.md` §«Routing delle domande»; il PRD e (da AO-1.1) `agents/a-knowledge/SKILL.md` la **linkano, non la duplicano**; una sola fonte di verità.
- Preservare il WIP parallelo nel worktree (learn/, tool-pitfalls, gold set): nessuna scrittura su quei file; eventuale commit solo a index isolato (`agent-commit.sh`), allow-list = i soli path del perimetro.

## 5. Effort e mano

- Effort: **S** (taglio di sola documentazione + 1 contratto bash; zero codice applicativo).
- Mano successiva dopo GREEN: `HT-013` passa `#human` per il Livello A (AO-2: clone pinnato + entry `context_servers` + `demo` + misura `tools/list` ≤13k char su `logs/`), poi decisione AO-3 (Livello B) solo se la misura non regge.

## 6. Come si chiude

Dopo accept: (a) modificare `docs/bounded-contexts.md` (assert 1-2), (b) `bash product/contracts/check-ontology-bc-boundary.sh` → GREEN, (c) `make pre-commit` 0, (d) `HT-013` → `[x]` con Esito + `/todo` flush in CHANGELOG `### Added`, (e) append riga `ready` in `agent-progress.md`.

# Changelog — a-b2b

## [2.3.10] - 2026-11-22

### Changed

- Sync selettivo `[sync:safe]` con a-agentzero 1.14.0→1.17.1: delta interamente infrastrutturale L0 nel range 1.14.0→1.17.1: slice v0-toth-index (`scripts/toth_index.py` + artefatto `references/toth-index.json`), gate `check-toth-index` nel Makefile, `COMMAND_SOURCE_OVERRIDES` (HT-017), §Manutenzione di `references/toth-routing-rules.md`, terzo tier SSH di `scripts/git-push-auth.sh` (HT-019), sotto-sezione pin SHA per corpus esterni in `references/l1-from-proto.md` (HT-015). `git diff --name-only 37215df..HEAD` su `commands/` e `competencies/` è vuoto → nessuna modifica al body (regola 4 di `agent-versioning.md`): solo `extends-version` + bump patch. Policy additiva, zero collisioni.
## [2.3.9] - 2026-11-20

### Changed

- Sync selettivo [sync:safe]: re-pin `extends-version` 1.13.11→1.14.0 (chiusura catena STALE post-HT-014 sul canone `a-agentzero`), bump patch.

## [2.3.8] - 2026-11-19

### Changed

- Sync selettivo [sync:safe] con a-agentzero 1.13.11: assorbite le regole di governance 1.13.9 (regola 14 flush→commit+push nello stesso turno; regole 15-16 worktree-land e § «Layout canonico» AGENT-PROTOCOL), la guardia 1.13.10 di `link-workspace-skills.sh` (rigenerazione ammessa solo da hal_gateway) e la rimozione 1.13.11 delle L2 di progetto dal mirror (ora nei repo proprietari). Policy additiva: collisione assente per grep, nessun passaggio del testo L1 toccato.

## [2.3.7] - 2026-11-18

### Changed

- Sync selettivo [sync:safe] da a-agentzero 1.13.5→1.13.9 (`/sync !`, conferma umana): voci pending solo infrastruttura L0 — regola 14 flush-transazione (commit+push dei soli file toccati su master), `.wt-extra` e fix registry-symlink in `agent-worktree.sh new`, builder test `wt_scratch` con self-test, regole 15-16 e § «Layout canonico» in AGENT-PROTOCOL. Nessun impatto sul body di a-b2b: `extends-version` allineata, bump patch, nessuna ricetta locale.

## [2.3.6] - 2026-11-18

### Changed

- Sync con L0 (`/sync !`): `extends-version` allineata 1.13.3→1.13.5; le voci pending del padre sono solo tooling (comando L0 `commit` 1.1.1/1.1.2, telemetria `token_budget` session_id) — nessun delta sul body di `a-b2b`, ricetta `[sync:safe]` §Versionamento (comandi/deploy non toccano il body L1). Bump patch via `agent-version.sh`; entry integrata a mano con dichiarazione (lo script non scrive il CHANGELOG).

## [2.3.5] - 2026-11-09

### Changed

- Sync selettivo [sync:safe] da a-agentzero 1.13.3 (commit L0: passo 7 auto-voto post-commit T-33B98, gate steward risolto con ok esplicito): `extends-version` allineato, bump patch, nessun cambio al body.

## [2.3.4] - 2026-11-09

### Changed

- Sync selettivo [sync:safe] da a-agentzero 1.13.2 (voci solo infrastruttura L0: nota Tool `graph` 1.0.4 — builder handoff da consumer in `agents/scripts/harness-prompt-builder.sh`, e tool-pitfalls learn 1.6.4): `extends-version` allineato, bump patch, nessun cambio al body.

## [2.3.3] - 2026-11-01

### Changed

- Sync L0 a-agentzero `extends-version` 1.13.0 → 1.13.1: voce pending = sola aggiunta documentale `references/extension-scaffold.md` §4–5 (contratto naming loader per skill L2: `name` kebab-case pari alla directory; nessun delta di protocollo) [sync:safe]; body L1 invariato

## [2.3.2] - 2026-10-30

### Changed

- Sync L0 a-agentzero `extends-version` 1.12.0 → 1.13.0: voci pending = quattro regole di protocollo in `AGENT-PROTOCOL.md` (§ contesto, dichiarazioni, cache: append-only dichiarazioni iniettate, mai reinserire `reasoning_content`, ordering static-first, retention provider) e fix infrastrutturale `scripts/sync-agents.sh` § `report_workspace_links` [sync:safe]; body L1 invariato

## [2.3.1] - 2026-10-28

### Changed

- Sync L0 a-agentzero `extends-version` 1.11.0 → 1.12.0: voci pending solo infrastruttura L0 (comandi canonici cycle/graph, agent-todo.py flush, utility learn 1.5.0) [sync:safe]; body L1 invariato

## [Unreleased]

### Changed

- Allineato a a-agentzero 1.8.0; body L1 invariato [sync:safe]
- Allineato a a-agentzero 1.8.5; body L1 invariato [sync:safe]

## [2.2.0] - 2026-10-02

### Added

- System 1 (Laya) Gating in B2B Pilots: batch scoring ICP e Pilot Fit (`router.py batch_score`) e routing GTM prima di attivare le cascate di enrichment System 2 [sync:safe]

## [2.1.4] - 2026-09-18

### Changed

- Sync padre: extends-version a-agentzero → 1.6.15 (lean L0 cmds) [sync:safe]

## [2.1.3] - 2026-09-17

### Added

- Frontmatter `model: orcarouter/z-ai/glm-5.3-flash` + `model-fallback: cursor-default` (OrcaRouter preferred; Cursor default se non raggiungibile) [sync:safe]
- Sync L0 a-agentzero `extends-version: 1.6.14` (preferred model frontmatter) [sync:safe]

## [2.1.2] - 2026-09-15

### Changed

- Anti–Build Trap: Outcome/Success signal + rimando a-product (facade allineata) [sync:safe]

## [2.1.1] - 2026-09-15

### Changed

- Sync L0 a-agentzero `extends-version: 1.6.13` (/learn ! ToDo+docs pointer) [sync:safe]

## [2.1.0] - 2026-09-15

### Changed

- **Facade L1:** canone orchestra → `a-product` § Profilo B2B; resta `extends: a-agentzero` (no L1→L1); L2 `b2b-*` invariati [sync:review]
- Pin `extends-version` a-agentzero → 1.6.12 [sync:safe]
- Rimossa body Cascata GTM (ora in a-product); reference locali conservati [sync:review]

## [2.0.7] - 2026-09-15

### Changed

- Sync L0 a-agentzero `extends-version: 1.6.11` (registry a-product) [sync:safe]

## [2.0.6] - 2026-09-15

### Changed

- Appreso da sessione: Reason why in description + regole di ingaggio subagent [sync:safe]

## [2.0.5] - 2026-09-12

### Changed

- Sezione **Non-goals / freeze** greppabile (no authoring PRD/canvas; no cascade enrichment) [sync:safe]

## [2.0.4] - 2026-09-08

### Changed

- Sync L0 a-agentzero `extends-version: 1.6.4` (scaffold commit staged-only) [sync:safe]

## [2.0.3] - 2026-08-20

### Added

- Cascata post-strategia (ordine artefatti GTM; SCAMPER non triggera; path da L2) [sync:review]

## [2.0.2] - 2026-08-15

### Changed

- Sync L0 1.6.3 (`extends-version: 1.6.3`): git-track L2 sotto `.gitignore` [sync:safe]

## [2.0.1] - 2026-08-15

### Changed

- Sync L0 1.6.2 (`extends-version: 1.6.2`): registry a-po/a-enrichment + l1-from-proto CC BY-NC-SA distill-only [sync:safe]

## [2.0.0] - 2026-08-15

### Changed

- Thin orchestrator: offer/validation → `a-po`; enrichment cascade → `a-enrichment` [sync:breaking]
- Delegation matrix + playbook + extension-template updated for new specialists [sync:breaking]
- Removed in-repo enrichment references (moved to `a-enrichment/`) [sync:breaking]

## [1.1.1] - 2026-08-14

### Changed

- Sync L0 1.6.0 (`extends-version: 1.6.0`): registry `a-b2b` [sync:safe]

## [1.1.0] - 2026-08-13

### Added

- Dual enrichment entry (cohort/CRM-first + domain-first) with ICP/fit gates, Apollo 3-step, lead-research output contract, CSV-vs-master rule [sync:review]
- References: `enrichment-gates.md`, `domain-enrichment-workflow.md`, `lead-research-output.md` [sync:review]
- Delegation to `a-copywriter` for outreach drafts; L2 extension ICP disqualifiers/checklist + optional MCP integrations [sync:review]

### Changed

- Enrichment pattern: gate before paid phases; LeadMagic optional roles; credits report; user assets in L2 [sync:review]

## [1.0.1] - 2026-08-13

### Changed

- Sync L0 1.5.7–1.5.8 (`extends-version: 1.5.8`): l1-from-proto [sync:safe]; humanizer Never inject — nessun delta body L1 [sync:review]

## [1.0.0] — 2026-08-13

### Added

- Baseline L1: orchestrazione pilot B2B, delegation matrix, output contract, enrichment pattern HubSpot→Apollo→LeadMagic→SQLite [sync:review]
- Promosso da L2 `b2b-explorer` (`/sync <` + conferma utente) [sync:review]

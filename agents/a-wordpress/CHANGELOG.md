# Changelog — a-wordpress

## [1.4.10] - 2026-11-22

### Changed

- Sync selettivo `[sync:safe]` con a-agentzero 1.14.0→1.17.1: delta interamente infrastrutturale L0 nel range 1.14.0→1.17.1: slice v0-toth-index (`scripts/toth_index.py` + artefatto `references/toth-index.json`), gate `check-toth-index` nel Makefile, `COMMAND_SOURCE_OVERRIDES` (HT-017), §Manutenzione di `references/toth-routing-rules.md`, terzo tier SSH di `scripts/git-push-auth.sh` (HT-019), sotto-sezione pin SHA per corpus esterni in `references/l1-from-proto.md` (HT-015). `git diff --name-only 37215df..HEAD` su `commands/` e `competencies/` è vuoto → nessuna modifica al body (regola 4 di `agent-versioning.md`): solo `extends-version` + bump patch. Policy additiva, zero collisioni.
## [1.4.9] - 2026-11-20

### Changed

- Sync selettivo [sync:safe]: re-pin `extends-version` 1.13.11→1.14.0 (chiusura catena STALE post-HT-014 sul canone `a-agentzero`), bump patch.

## [1.4.8] - 2026-11-19

### Changed

- Sync selettivo [sync:safe] con a-agentzero 1.13.11: assorbite le regole di governance 1.13.9 (regola 14 flush→commit+push nello stesso turno; regole 15-16 worktree-land e § «Layout canonico» AGENT-PROTOCOL), la guardia 1.13.10 di `link-workspace-skills.sh` (rigenerazione ammessa solo da hal_gateway) e la rimozione 1.13.11 delle L2 di progetto dal mirror (ora nei repo proprietari). Policy additiva: collisione assente per grep, nessun passaggio del testo L1 toccato.

## [1.4.7] - 2026-11-18

### Changed

- Sync selettivo [sync:safe] da a-agentzero 1.13.5→1.13.9 (`/sync !`, conferma umana): voci pending solo infrastruttura L0 — regola 14 flush-transazione (commit+push dei soli file toccati su master), `.wt-extra` e fix registry-symlink in `agent-worktree.sh new`, builder test `wt_scratch` con self-test, regole 15-16 e § «Layout canonico» in AGENT-PROTOCOL. Nessun impatto sul body di a-wordpress: `extends-version` allineata, bump patch, nessuna ricetta locale.

## [1.4.6] - 2026-11-18

### Changed

- Sync con L0 (`/sync !`): `extends-version` allineata 1.13.3→1.13.5; le voci pending del padre sono solo tooling (comando L0 `commit` 1.1.1/1.1.2, telemetria `token_budget` session_id) — nessun delta sul body di `a-wordpress`, ricetta `[sync:safe]` §Versionamento (comandi/deploy non toccano il body L1). Bump patch via `agent-version.sh`; entry integrata a mano con dichiarazione (lo script non scrive il CHANGELOG).

## [1.4.5] - 2026-11-09

### Changed

- Sync selettivo [sync:safe] da a-agentzero 1.13.3 (commit L0: passo 7 auto-voto post-commit T-33B98, gate steward risolto con ok esplicito): `extends-version` allineato, bump patch, nessun cambio al body.

## [1.4.4] - 2026-11-09

### Changed

- Sync selettivo [sync:safe] da a-agentzero 1.13.2 (voci solo infrastruttura L0: nota Tool `graph` 1.0.4 — builder handoff da consumer in `agents/scripts/harness-prompt-builder.sh`, e tool-pitfalls learn 1.6.4): `extends-version` allineato, bump patch, nessun cambio al body.

## [1.4.3] - 2026-11-01

### Changed

- Sync L0 a-agentzero `extends-version` 1.13.0 → 1.13.1: voce pending = sola aggiunta documentale `references/extension-scaffold.md` §4–5 (contratto naming loader per skill L2: `name` kebab-case pari alla directory; nessun delta di protocollo) [sync:safe]; body L1 invariato

## [1.4.2] - 2026-10-30

### Changed

- Sync L0 a-agentzero `extends-version` 1.12.0 → 1.13.0: voci pending = quattro regole di protocollo in `AGENT-PROTOCOL.md` (§ contesto, dichiarazioni, cache: append-only dichiarazioni iniettate, mai reinserire `reasoning_content`, ordering static-first, retention provider) e fix infrastrutturale `scripts/sync-agents.sh` § `report_workspace_links` [sync:safe]; body L1 invariato

## [1.4.1] - 2026-10-28

### Changed

- Sync L0 a-agentzero `extends-version` 1.11.0 → 1.12.0: voci pending solo infrastruttura L0 (comandi canonici cycle/graph, agent-todo.py flush, utility learn 1.5.0) [sync:safe]; body L1 invariato

## [Unreleased] - 2026-10-20

### Changed

- Rimossi riferimenti a Cursor nei percorsi: `.cursor/skills/` → `.agents/skills/`, `.cursor/product/` → `product/`, `.cursor/brands/` → `brands/`. Versioni: `extension-template.md` 1.0.1 [sync:safe]

## [Unreleased]

### Changed

- Allineato a a-agentzero 1.8.0; body L1 invariato [sync:safe]
- Allineato a a-agentzero 1.8.5; body L1 invariato [sync:safe]

## [1.3.0] - 2026-10-02

### Added

- System 1 (Laya) Gating in WordPress: routing rapido dei componenti WordPress e dei pattern di plugin (`router.py routing`) e classificazione degli errori di installazione prima di attivare le analisi approfondite System 2 [sync:safe]

## [1.2.11] - 2026-09-18

### Changed

- Sync padre: extends-version a-agentzero → 1.6.15 (lean L0 cmds) [sync:safe]

## [1.2.10] - 2026-09-17

### Added

- Frontmatter `model: orcarouter/z-ai/glm-5.3-flash` + `model-fallback: cursor-default` (OrcaRouter preferred; Cursor default se non raggiungibile) [sync:safe]
- Sync L0 a-agentzero `extends-version: 1.6.14` (preferred model frontmatter) [sync:safe]

## [1.2.9] - 2026-09-15

### Changed

- Sync L0 a-agentzero `extends-version: 1.6.13` (/learn ! ToDo+docs pointer) [sync:safe]

## [1.2.8] - 2026-09-15

### Changed

- Sync L0 a-agentzero `extends-version: 1.6.12` (a-product § Profilo B2B / a-b2b facade) [sync:safe]

## [1.2.7] - 2026-09-15

### Changed

- Sync L0 a-agentzero `extends-version: 1.6.11` (registry a-product) [sync:safe]

## [1.2.6] - 2026-09-15

### Changed

- Appreso da sessione: Reason why in description + regole di ingaggio subagent [sync:safe]

## [1.2.5] - 2026-09-08

### Changed

- Sync L0 a-agentzero `extends-version: 1.6.4` (scaffold commit staged-only) [sync:safe]

## [1.2.4] - 2026-08-15

### Changed

- Sync L0 1.6.3 (`extends-version: 1.6.3`): git-track L2 sotto `.gitignore` [sync:safe]

## [1.2.3] - 2026-08-15

### Changed

- Sync L0 1.6.2 (`extends-version: 1.6.2`): registry a-po/a-enrichment + l1-from-proto CC BY-NC-SA distill-only [sync:safe]

## [1.2.2] - 2026-08-14

### Changed

- Sync L0 1.6.0 (`extends-version: 1.6.0`): registry `a-b2b` [sync:safe]

## [1.2.1] - 2026-08-13

### Changed

- Sync L0 1.5.7–1.5.8 (`extends-version: 1.5.8`): l1-from-proto [sync:safe]; humanizer Never inject — nessun delta body L1 [sync:review]

## [1.2.0] - 2026-08-13

### Added

- `remote-wp-cli.md`: pattern `DISABLE_WP_CRON` + `wp cron event run --due-now`
  (host/Docker/SSH); job lunghi batch + reschedule [sync:safe]
- Reference `wp-cli-cheatsheet.md`: inventario, smoke, cache, plugin zip, migrate [sync:safe]
- `plugin-migrate.md`: sezione job lunghi (CLI chunk / nohup); checklist batch [sync:safe]
- `site-brief-template.md`: campi `DISABLE_WP_CRON` e cron runner [sync:safe]

## [1.1.0] - 2026-08-13

### Added

- Reference `remote-wp-cli.md`: apply WP-CLI lungo via `nohup` + poll log;
  fallimento `_elementor_data` ≠ gate SEO; verifica redirect Yoast vs CSV
  (import 0 / catena 301) [sync:safe]

## [1.0.13] - 2026-08-07

### Changed

- Sync L0 1.5.6: L1 `a-charts` registry/discovery → solo extends-version [sync:safe]

## [1.0.12] - 2026-08-03

### Changed

- Sync L0 1.5.5 voice-as-brand → solo extends-version (competenza tono-di-voce non adottata) [sync:safe]

## [1.0.11] - 2026-08-03

### Changed

- Sync L0 1.5.4: `/sync <` generalizzazione L2 → solo extends-version [sync:safe]

## [1.0.10] - 2026-08-03

### Changed

- Sync L0 1.5.3: multi-figlio / companion / learn → solo extends-version [sync:safe]

## [1.0.9] - 2026-07-28

### Changed

- Sync L0 1.5.2: `l1-from-proto` corpus skill esterni (vendor+pin) → solo extends-version [sync:safe]

## [1.0.8] - 2026-07-27

### Changed

- Sync L0 1.5.1: `[sync:safe]` comandi/deploy → solo extends-version [sync:safe]

## [1.0.7] - 2026-07-27

### Changed

- Sync L0 1.5.0: comandi Cursor L0 ereditabili (`commands/`) [sync:safe]

## [1.0.6] - 2026-07-27

### Changed

- Sync L0 1.4.1: `po-interviewer`/discovery opt-in (non adottato); regola authorship proto [sync:safe]

## [1.0.5] - 2026-07-27

### Changed

- Sync L0 1.3.1: file dati ≠ competenze (opt-in; non adottate in questo L1) [sync:safe]

## [1.0.4] - 2026-07-27

### Changed

- Sync L0 1.3.0: protocollo competenze (opt-in; non adottate in questo L1) [sync:safe]

## [1.0.3] - 2026-07-27

### Changed

- Sync L0 1.2.0: protocollo competenze modulari (opt-in; non adottate in questo L1) [sync:safe]

## [1.0.2] - 2026-07-16

### Changed

- Sync L0 1.1.2: skill `/sync` (deploy + report versioni) [sync:safe]

## [1.0.1] - 2026-07-13

### Changed

- Sync L0 1.1.1: sezione Apprendimento da sessione [sync:safe]

## [1.0.0] - 2026-07-13

### Added

- Baseline iniziale — plugin stabili/migrate, analisi installazione, packaging zip versionato
- Campi `version` e `extends-version: 1.0.0` (allineato a a-agentzero 1.0.0) [sync:safe]

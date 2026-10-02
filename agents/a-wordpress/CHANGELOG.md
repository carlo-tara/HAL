# Changelog — a-wordpress

## [Unreleased]

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

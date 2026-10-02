# Changelog — sync

## [Unreleased]


## [1.1.3] - 2026-09-17

### Added
- Frontmatter `model: orcarouter/deepseek/deepseek-v4-flash` + `model-fallback: cursor-default` (/sync preferred model) [sync:safe]

## [1.1.2] - 2026-09-17

### Changed
- Appreso da sessione: `/sync <` su cwd AgentFactory → scan L2 in-repo + consumer noti `/var/www/*/./.cursor/skills/` (discovery) [sync:safe]

## [1.1.1] - 2026-09-15

### Changed
- Appreso da sessione: dopo `/sync ?`/`!`, verificare L2 meta-repo (`harness-agentfactory` / `make version-chains`) anche se lo script senza `--projects` non segnala STALE L1 [sync:safe]

## [1.1.0] - 2026-09-12

### Added
- Baseline changelog co-located (utility nested); `/sync <` generalizzazione L2 — vedi `a-agentzero` CHANGELOG / sync skill 1.1.0

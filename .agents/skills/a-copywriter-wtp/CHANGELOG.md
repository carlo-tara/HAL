# Changelog — a-copywriter-wtp

## [Unreleased]

### Changed

- 1.0.11 → **1.0.12** — Rimossi riferimenti a Cursor: path `.cursor/brands/` → `brands/`, `.cursor/agents/` → `agents/`, `.cursor/rules/` → `docs/rules/`, `.cursor/skills/` → `.agents/skills/` `[sync:safe]`
- 1.0.9 → **1.0.10** — Sync padre: extends-version a-copywriter 1.6.0 → 1.6.1 `[sync:safe]`
- 1.0.8 → **1.0.9** — Skill base a-copywriter HAL Gateway collegata; `extends-version` 1.5.5→1.6.0 `[sync:safe]`
- 1.0.7 → **1.0.8** — Appreso da sessione: CTA fetch senza jargon provider («Recupera dati mancanti») `[sync:safe]`
- 1.0.6 → **1.0.7** — Appreso da sessione: Suggerimenti senza glossario inline tra parentesi (`llmGlossaryPolicyIt`) `[sync:safe]`
- 1.0.5 → **1.0.6** — Sync selettivo padre `a-copywriter` 1.5.2→**1.5.5** (L0 pin 1.6.11–1.6.13) `[sync:safe]`
- 1.0.4 → **1.0.5** — Sync selettivo padre `a-copywriter` 1.5.1→**1.5.2** (Reason why + regole subagent) `[sync:safe]`
- 1.0.3 → 1.0.4 — Appreso da sessione: msgid SoT `.po` (`CustomerSheet*`); no inventare chiavi; fallback `uiT` se catalog miss `[sync:safe]`
- 1.0.2 → 1.0.3 — Appreso da sessione: Sales Coach = suite; prodotti UI Liste WTP / Explorer B2B (catalogo condiviso) `[sync:safe]`
- 1.0.1 → 1.0.2 — Appreso da sessione: canone copy progresso job (`WtpProg_*` / Tempo·Avanzamento) `[sync:safe]`
- Appreso da sessione: frontmatter `extends: a-copywriter` + `extends-version: 1.5.1` per catena `/sync` `[sync:safe]`

## [1.0.1] — 2026-09-08

### Changed

- Catena L2 esplicita verso `a-copywriter` @ 1.5.1 (prima solo prosa «Base obbligatoria»)
- Whitelist git: `.agents/skills/a-copywriter-wtp/` in the agent path registry

## [1.0.0] - 2026-08-17

### Added

- Appreso da sessione: playbook demografico fail-closed; cache `customer-detail-*.json` dopo cambi matcher. [sync:safe]
- Convergence da `wtp-brand-voice` (fonte unica locale Sales Coach)

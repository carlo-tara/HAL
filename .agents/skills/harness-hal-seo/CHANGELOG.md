# Changelog — harness-hal-seo

## [0.1.4] - 2026-11-18

### Changed

- Sync selettivo [sync:safe] da a-harness 1.10.4→1.11.2 (conferma umana `/sync !`, classificazione di questa sessione): le voci pending del padre sono additive — policy «Costo del gate»/«stdout=file» (1.10.5, promozioni da L2 brainbeez) + «Chiusura outcome-driven» (1.11.0) — più sync infrastrutturali L0 (1.11.1, 1.11.2). Verifica di collisione: nessun figlio ridefinisce le policy (grep `Costo del gate|outcome-driven|stdout` = 0 nei figli) → eredità pulita, nessuna ricetta locale. `extends-version` allineata, bump patch via `agent-version.sh`.

## [0.1.3] - 2026-11-09

### Changed

- Sync selettivo [sync:safe] da a-harness 1.10.4: voce del padre solo infrastruttura L0/L1 (catene extends allineate), nessun delta L2 da adattare; bump patch del figlio.

## [0.1.2] - 2026-11-01

### Added

- Nota `/version patch` nel § Conflitto sessioni parallele: `SERVER_VERSION` 0.2.0 → 0.2.1 (release iniziale hal_mcp_seo su GitHub) [sync:safe]

## [0.1.1] - 2026-11-01

### Changed

- `extends-version` 1.10.1 → 1.10.2 ([sync:safe], promozione guard Makefile nel template `a-harness`)

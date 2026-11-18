# Changelog — harness-hal-translate

Formato Keep a Changelog + Semantic Versioning. Tag figli: `[sync:safe]`, `[sync:review]`, `[sync:breaking]`.

## [1.0.4] - 2026-11-18

### Changed

- Sync selettivo [sync:safe] da a-harness 1.10.4→1.11.2 (conferma umana `/sync !`, classificazione di questa sessione): le voci pending del padre sono additive — policy «Costo del gate»/«stdout=file» (1.10.5, promozioni da L2 brainbeez) + «Chiusura outcome-driven» (1.11.0) — più sync infrastrutturali L0 (1.11.1, 1.11.2). Verifica di collisione: nessun figlio ridefinisce le policy (grep `Costo del gate|outcome-driven|stdout` = 0 nei figli) → eredità pulita, nessuna ricetta locale. `extends-version` allineata, bump patch via `agent-version.sh`.

## [1.0.3] - 2026-11-09

### Changed

- Sync selettivo [sync:safe] da a-harness 1.10.4: voce del padre solo infrastruttura L0/L1 (catene extends allineate), nessun delta L2 da adattare; bump patch del figlio.

## [1.0.1] - 2026-10-31

### Changed

- Rinominata da `harness-hal_translate` (contratto naming loader Agent Skills promosso in `extension-scaffold.md` 1.13.1: `name` kebab-case pari alla directory; le violazioni con underscore erano scartate in silenzio) [sync:safe]
- Allineata a a-harness 1.10.1 (`extends-version` 1.10.0 → 1.10.1; policy «Copertura gate» non impatta il delta L2) [sync:safe]

## [1.0.0] - 2026-10-31

### Added

- Bootstrap harness `standard` (2026-10-31): delta L2 per hal_translate (MT locale LibreTranslate/Argos) — Makefile Platform API, path artefatti, N/A documentati, safety note del servizio.

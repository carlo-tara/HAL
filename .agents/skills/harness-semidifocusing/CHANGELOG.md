# Changelog — harness-semidifocusing

## [2.1.2] - 2026-11-18

### Changed

- Sync selettivo [sync:safe] da a-harness 1.10.4→1.11.2 (conferma umana `/sync !`, classificazione di questa sessione): le voci pending del padre sono additive — policy «Costo del gate»/«stdout=file» (1.10.5, promozioni da L2 brainbeez) + «Chiusura outcome-driven» (1.11.0) — più sync infrastrutturali L0 (1.11.1, 1.11.2). Verifica di collisione: nessun figlio ridefinisce le policy (grep `Costo del gate|outcome-driven|stdout` = 0 nei figli) → eredità pulita, nessuna ricetta locale. `extends-version` allineata, bump patch via `agent-version.sh`.

## [2.1.1] - 2026-11-09

### Changed

- Sync selettivo [sync:safe] da a-harness 1.10.4: voce del padre solo infrastruttura L0/L1 (catene extends allineate), nessun delta L2 da adattare; bump patch del figlio.

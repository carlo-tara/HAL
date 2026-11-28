# Changelog — uiux

Formato: [Keep a Changelog](https://keepachangelog.com/it/1.1.0/). Versionamento: SemVer.
Registro avviato il 2026-11-09; i bump 1.0.x precedenti sono documentati nelle catene dei figli L2 (es. `wtp-ux-ui` CHANGELOG «Skill base a-uiux HAL Gateway collegata»).

## [1.2.1] - 2026-11-28

### Added

- § Pattern guida & chrome comuni: regola «state layer M3 solo in `opacity:`» + insidia IACVT del fallback `var(--token, fallback)` (token definito ma valore invalido ⇒ dichiarazione scartata in silenzio) — promossa da brainbeez /improve ui/ux M3 2026-11-07 (**evidenza singola, soglia ≥2 forzata su indicazione owner**, AGG-07) [sync:safe].

## [1.1.0] - 2026-11-09

### Added

- § «Pattern guida & chrome comuni (shell)»: guide collassabili `<details>`, empty state con azione, «come leggere» a una riga, click→risultato — promossi dai L2 `wtp-ux-ui`/`b2b-explorer-ui-ux` (dedup `/sync <` 2026-11-09; pattern tema-indipendenti validati su 2 consumer) [sync:safe]

### Changed

- § Pattern guida & chrome comuni: promossi 3 canoni generici (slot brand vs meta di pagina; azioni di output nel menu File della suite; copy UI da origine i18n con fallback) finora doppiati in `wtp-ux-ui` #9/#13 e `b2b-explorer-ui-ux` § Chrome suite; le L2 restano con gli override di progetto + puntatore (richiesta esplicita utente al report `/sync <`).


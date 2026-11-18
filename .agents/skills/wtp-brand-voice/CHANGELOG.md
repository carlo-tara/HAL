# Changelog — wtp-brand-voice

## [2.0.0] - 2026-11-18

### Changed

- **Unificazione (richiesta esplicita dell'utente sul candidato NEED-N di `/sync <`)**: il corpo della fonte Sales Coach — perimetro, fonti WTP, gerarchia, regole voce/narrativa/registri/UI-i18n/LLM-export, workflow 8–12 — migra integralmente da `a-copywriter-wtp` (che diventa alias) a questo file, che da guscio-alias diventa la fonte unica. Frontmatter dichiarato alla catena L2: `extends: a-copywriter` con `extends-version: 1.7.7` (allineato; chiude anche la catena stale 1.7.5 che portava l'ex sorgente). Breakings per chi invocava il vecchio alias: nessuno (alias mantenuto con puntatore). [sync:safe]

### Added

- Nota esplicita: `references/` (export-pdf-copy, locale-patterns, llm-field-guide) è **pianificata, oggi assente** — da creare alla prima referenza reale.

## [1.0.0] - 2026-10-16

### Added

- Guscio alias verso a-copywriter-wtp (all'epoca la fonte viveva lì).

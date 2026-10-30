# Changelog — learn

## [1.5.10] - 2026-10-29

### Added

- `learn-guidelines.md` regola 8 «Cause ereditate — riverificare»: mai replicare verbatim una diagnosi di sessione precedente senza verifica empirica (validato 2026-10-29: la dizione «servizio non raggiungibile» nascondeva tre cause distinte — 401 client, mismatch endpoint `/v1/predict` vs `/systemone`, path morto `/laya`) [sync:safe]
- `tool-pitfalls.md` § «Assenze da verificare»: regola nuovo-strato — ABSTAIN `invalid_*` con servizio verde (verdetti reali su `POST /systemone`) = mismatch di contratto client↔endpoint, non disservizio; sondare `/systemone` prima di incolpare il server [sync:safe]

### Changed

- `tool-pitfalls.md` § «Parametri numerici»: decima conferma (sessione fix laya_service + /learn 2026-10-29: `read_file` `start_line`+`end_line` respinto 2×, `terminal timeout_ms=60000` respinto 1× → `sed -n`/omissione) [sync:safe]
- Ripristinata in questo file la sezione `[1.5.9]` risultata assente dal worktree a metà turno (mutazione concorrente esterna; il contenuto di `tool-pitfalls.md` da essa documentato è rimasto integro) [sync:review]

## [1.5.9] - 2026-10-29

### Changed

- `tool-pitfalls.md` § «Parametri numerici»: nona conferma (sessione diagnosi Laya ABSTAIN 2026-10-29: `read_file` range respinto 3× anche con parametri numerici, `terminal timeout_ms` respinto 1× → `sed -n`/omissione) [sync:safe]
- `tool-pitfalls.md` § «Assenze da verificare»: nuova regola ABSTAIN — prima di dichiarare «servizio non raggiungibile» verificare path canonico router (`/var/www/hal_system1`, non `/var/www/HAL` morto) + `GET :8091/health`; righe `Broken pipe` in `log.sqlite` su `/systemone` = client-timeout, non disservizio (validato: sessione Laya 2026-10-29 + precedente regola ABSTAIN-retry 2026-10-26) [sync:safe]

## [1.5.8] - 2026-10-28

### Added

- `tool-pitfalls.md`: nuova voce «Frammenti CJK nel testo italiano generato» — il candidato della sessione doc-review (regola: aprire voce alla seconda sessione) è stato validato dalla sessione models-catalog 2026-10-28; rimedio `grep -rnP '[\x{4e00}-\x{9fff}]'` post-scrittura, scope esteso anche agli heredoc terminal [sync:safe]

### Changed

- `tool-pitfalls.md` § «Parametri numerici»: ottava conferma (sessione models-catalog 2026-10-28, `terminal timeout_ms` respinto 2× con `invalid type: string, expected u64` → omesso) [sync:safe]

## [1.5.7] - 2026-10-28

### Changed

- `tool-pitfalls.md` §Writer canonico: chiarito che il default di `handoff-write` è risolto dalla root dello script (hal_gateway); nuova regola workspace consumer: sempre `--out product/state/handoff-<kind>.json`; evidenza shadow copy stale 2026-10-26/28 (sessione brainbeez /todo+/graph) [sync:safe]

## [1.5.6] - 2026-10-28

### Added

- `tool-pitfalls.md`: nuovo pitfall «writer canonico per handoff JSON» — `handoff-<kind>.json` via `bash agents/scripts/harness-prompt-builder.sh handoff-write <kind> --field …` (default `product/state/`, campi `ts`/`cmd`/`token_budget` auto-compilati), non con `write_file` manuale; dalla root HAL il path dello script è `agents/scripts/`, non `scripts/` come in alcuni comandi [sync:safe]
- `learn-guidelines.md` regola 7: clausola `Non applicabili: …` con motivo nella riga Delta quando parti della fonte vendor non sono adottabili, così `/todo` non le ripropone (validato dai delta Connection pooling e Streaming, 2026-10-28) [sync:safe]

### Changed

- `tool-pitfalls.md`: conferme da sessione QwenCloud streaming 2026-10-28 — «parametri numerici respinti come stringhe» (`read_file` range 2× → `sed -n`, settima sessione di osservazione) e «batch `edit_file` non atomico» (`ToDo.md` 67→151 righe tra lettura e scrittura per append concorrenti; index 1 di batch da 2 fallito → rilettura coda reale, riapplicato solo il mancante) [sync:safe]

## [1.5.5] - 2026-10-28

### Changed

- `tool-pitfalls.md`: sesta conferma del pitfall «parametri numerici respinti come stringhe» (sessione QwenCloud async-task-management 2026-10-28, `read_file` range 3× anche con un solo parametro + `terminal timeout_ms` 2× → `sed -n`/omissione) [sync:safe]
- `tool-pitfalls.md` § «Batch `edit_file` non atomico»: nuovo bullet — file condivisi (`./ToDo.md`, `tool-pitfalls.md`) mutati da sessioni parallele tra lettura e scrittura invalidano le ancore; mai due edit a cascata con ancore sovrapposte nello stesso batch (rischio troncamento contenuto; osservato su voce P0 di `ToDo.md`, ripristinata alla chiamata successiva) [sync:review]
- `learn-guidelines.md` regola 7: estesa con clausola `Vincoli trasversali: …` da accodare alla riga Delta quando la fonte pone vincoli implementativi (validato dai delta Context cache e Async task, 2026-10-28) [sync:safe]

## [1.5.4] - 2026-10-28

### Changed

- `tool-pitfalls.md`: quinta conferma del pitfall «parametri numerici respinti come stringhe» (sessione QwenCloud connection-pooling 2026-10-28, `read_file` range 4× → `sed -n`); nessuna nuova regola [sync:safe]

## [1.5.3] - 2026-10-28

### Added

- `tool-pitfalls.md`: nuovo pitfall `list_directory` con path `.` → stringa vuota senza errore; usare il nome della root di progetto (validato in 2 sessioni: Kimi 2026-10-28 osservazione singola, QwenCloud 2026-10-28 verifica per contrasto) [sync:safe]
- `learn-guidelines.md`: regola di scrittura «batch ToDo da doc vendor» — riga `Delta YYYY-MM-DD da <fonte docs> (<URL>): N voci sotto` nell'header di `./ToDo.md` e fonte citata nel `Perché utile` (validato sessioni Kimi e QwenCloud, 2026-10-28) [sync:safe]

### Changed

- `tool-pitfalls.md`: quarta conferma del pitfall «parametri numerici respinti come stringhe» (sessione QwenCloud 2026-10-28, `read_file` range 2× → `sed -n`) [sync:safe]

## [1.5.2] - 2026-10-28

### Changed

- `tool-pitfalls.md`: terza conferma del pitfall «parametri numerici respinti come stringhe» (sessione /learn 2026-10-28, `read_file` range + `terminal timeout_ms`); nessuna nuova regola [sync:safe]

## [1.5.1] - 2026-10-27

### Added

- `tool-pitfalls.md`: output di `terminal`/`read_file` lunghi restituiti a frammenti → verificare con comandi corti/mirati, non fidarsi del display; corollario `edit_file` post-reflow [sync:safe]

## [1.5.0] - 2026-10-26

### Added

- Riferimento `references/tool-pitfalls.md`: pitfall tool Zed validati in ≥2 sessioni (parametri numerici → `sed`/ometti `timeout_ms`; batch `edit_file` non atomico; verifica assenze prima di ToDo; `ABSTAIN` routing → fallback System 2) [sync:safe]

## [1.3.1] - 2026-10-20

### Fixed

- Changelog apprendimenti spostato da `.cursor/product/session-learnings.md` a `product/session-learnings.md` (SKILL e target di consolidamento) [sync:safe]

## [1.2.5] - 2026-10-16

### Fixed

- Session consolidation for diagnostics and coding standards.

## [1.2.1] - 2026-09-17

- fix: session consolidation for diagnostics and coding standards.

## [1.2.1] - 2026-09-17

### Added

- Frontmatter `model: orcarouter/openai/gpt-4o-mini` + `model-fallback: cursor-default` (/learn preferred model) [sync:safe]

## [1.2.0] - 2026-09-15

### Added

- Routing destinazione: skill/brand vs `./ToDo.md` (Attività) vs docs locali — scrittura **se necessario** su `/learn !` [sync:review]
- `/learn ?`: campi **Destinazione** e target ToDo/docs nel report [sync:safe]
- consolidation-targets: righe ToDo + glossary/BC/operativo [sync:safe]

## [1.1.0] - 2026-09-12

### Added

- `/learn !`: Changelog apprendimenti obbligatorio in `.cursor/product/session-learnings.md` con sezioni `### Progetto` e `### AgentFactory` [sync:safe]
- `/learn !`: `/version patch` obbligatorio su ogni `SKILL.md` modificato [sync:safe]
- `/learn ?`: campo **Ambito** (Progetto | AgentFactory) nel report [sync:safe]

## [1.0.1] - 2026-08-03

### Changed

- Baseline pre-changelog dedicato (anti-grasso L2, promozione ≥2 progetti) — vedi `a-agentzero` 1.5.3

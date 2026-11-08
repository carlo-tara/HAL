# Changelog — learn

## [1.6.1] - 2026-11-08

### Added

- tool-pitfalls: nuova sezione «Shell di lavoro `sh`/dash» — process substitution `<(...)` e quoting `bash -c` annidato falliscono nel terminal (sh/dash), rimedio file temporanei / python heredoc; due evidenze (brainbeez /todo rv17 2026-11-07 + /cycle CIC 2026-11-08) → promozione ex policy ≥2. Bullet «diagnosi hang» nella sezione docker: exit 124 ≠ fallimento; ordine read-exit → `docker ps` orfani → handle aperti del runner (jsdom senza dispose arena `node --test` identico a una contesa compose); terza evidenza della sezione.

## [1.6.0] - 2026-11-07

### Changed

- `tool-pitfalls.md` due appendici di evidenza sorella (brainbeez sessione /improve ui/ux M3, /learn ! #23): §«Parametri numerici» (`read_file` range respinto 2× su `web/index.html`, identico al retry, e 2× sul reference stesso → `sed -n`; 75 righe senza range → outline, corollario run-4), §«grep/find_path» (quattro include_pattern senza prefisso root — `web/**`, `web/**/*`, `web/**/*.css`, `web/src/**/*.js` — → falsi «No matches» su contenuto reale, ri-verifica `grep -rn` via terminal come da regola).
- Versione 1.5.27 → 1.6.0 (minor: /version minor richiesto dall'owner, assorbe il patch 1.5.28 applicato in sessione). Brainbeez: nuova voce ToDo P1 `#bug` (card.js: token di opacità `--bb-state-*` usati come colori → focus ring e hover rotti, fix in attesa di GO), nuova HOLD P2 `#sync` (regola IACVT «fallback di var() non scatta su valore invalido per la proprietà» → candidata a `uiux` L1 alla seconda evidenza), «Commit HAL» estesa a learn 1.6.0.

## [1.5.27] - 2026-11-07

### Added

- `tool-pitfalls.md` §«Batch `edit_file` non atomico»: bullet nuova **«Àncora «caposaldo» consumata in singolo edit»** — `old_text` che include un heading confinante, non reproduced alla fine di `new_text`, lo inghiotte silenziosamente (nessun errore; l'edit basta applica). Evidenza brainbeez #22: heading `## [0.7.0]` del CHANGELOG sparito e committato rotto (9e84b86), riparato con chirurgia asserita; classe gemella delle ancore sovrapposte di #21, variante single-edit.

### Changed

- `tool-pitfalls.md` tre appendici di evidenza sorella (brainbeez sessione S75–S77, /learn ! #22): §«Parametri numerici» (`read_file` range 2× anche a ordine invertito, `terminal timeout_ms` 2×), §«Frammenti CJK» (frammento «吞» intra-commento di heredoc python, prima occorrenza), §«Path dei comandi L0» (MCP `todo_flush` respinto col default `repo/agents/...` sul workspace senza symlink: passare `script` esplicito sul bundle).
- Versione 1.5.26 → 1.5.27. Brainbeez: voce ToDo «Commit HAL» estesa (work tree HAL non committato, gate umano).

## [1.5.26] - 2026-11-07

### Changed

- `tool-pitfalls.md` quattro appendici di evidenza (brainbeez /graph -y rv16 + S74, /learn ! #21): §«Parametri numerici» (read_file range + timeout_ms respinti anche con interi; corollario run-4 riverificato), §«Batch edit_file non atomico» (cascata di ancore sovrapposte su `CHANGELOG.md` → titolo voce troncato; **variante nuova**: edit nullo su tabella padded che ne reflowa l'intera griglia — riverificare i pipe dopo l'edit), §«Frammenti CJK» (due frammenti in una sessione, `路径` in codice JS generato + `绑定` in heredoc — perimetro sweep esteso al sorgente), §«compose run orfani» (pattern setsid+`.ec` rivalidato 4 gate, `docker ps` post-timeout pulito).

## [1.5.25] - 2026-11-06

### Changed

- `tool-pitfalls.md` §«Parametri numerici respinti come stringhe»: evidenza estesa alla classe `head_lines`/`tail_lines` del terminale (`invalid type: string, expected usize`), oltre a `read_file` range e `timeout_ms` — rimedi invariati (omissione + loop bounded) [sync:safe]
- `tool-pitfalls.md` §«`docker compose run` ucciso da fuori»: nuovo bullet sul pattern `setsid` + marcatore `EXIT_CODE=$?` nel log come unica prova del verdetto per gate lunghi dal contesto (`test_run` context-timeout e `nohup` alla chiusura pty = kill esterni; `--rm` non lascia exit code consultabile) + terza evidenza della classe (brainbeez /learn ! #20, 2026-11-06) [sync:safe]
- `tool-pitfalls.md` §«Frammenti CJK nel testo italiano generato»: evidenza estesa ai **messaggi commit** generati («14条目» inside `git commit -m`, amend riparatore) — rimedio validato: file messaggio + sweep `grep -P` pre-commit + `git commit -F` [sync:safe]

## [1.5.24] - 2026-11-05

### Changed

- `tool-pitfalls.md` §«`grep` con `include_pattern`» estesa a §«`grep`/`find_path`: pattern matchati sul path completo dalla root» — accorpata l'evidenza sorella di /learn ! #18 (2026-11-05, registrata nel ToDo consumer come obbligo di promozione): `find_path` con glob `web/**/*` → «No matches» malgrado `web/src/*.js` esista (`**/*.py` matcha); il matching sul path completo dalla root non riguarda solo `include_pattern`; nuovo bullet + catena evidenza [sync:safe]
- `tool-pitfalls.md` §«Frammenti CJK nel testo italiano generato» — appendice evidenza (brainbeez /graph -y rv11, 2026-11-05): frammento heredoc «闭合urabili» in `work-graph.md` a catena in corso, intercettato dallo sweep post-scrittura `grep -rnP` esteso a tutti i file toccati dalla sessione (riconferma: perimetro = sessione, non ultimo file) [sync:safe]

## [1.5.23] - 2026-11-05

### Added

- `tool-pitfalls.md`: nuova sezione «`grep` con `include_pattern`: match sul path completo dalla root» — promozione del candidato §grep (1ª evidenza brainbeez S40 2026-11-02, 2ª evidenza sessione triage feedback beta 2026-11-04, entrambe registrate nel ToDo consumer): `include_pattern` matchato sul path completo dalla root di progetto → falsi negativi su pattern di sottorecarte senza prefisso; regola: ri-verificare le assenze con una seconda query [sync:safe]
- `tool-pitfalls.md`: nuova sezione «`docker compose run` ucciso da fuori: container orfani e hang» — promozione del candidato ⑤ §terminal (1ª evidenza HAL 2026-10-30, 2ª evidenza brainbeez /graph -y rv11 2026-11-05: container `pytest -q` orfano «Up» ~3h dopo cancello esterno a metà `make test-unit`): `--rm` non scatta se il client muore; `docker ps` prima di dichiarare «non ha fatto in tempo», `docker rm -f` per pulizia, gate bounded con `timeout` + exit reale (policy L1 «verità del gate») [sync:safe]

## [1.5.22] - 2026-11-05

### Changed

- `tool-pitfalls.md` §«Parametri numerici respinti come stringhe»: appendice evidenza sessione analisi Kent Beck brainbeez (/learn !, 2026-11-05) — `read_file` range respinto 2× anche con valori identici al retry; outline-only su file di 138 righe anche CON terminal (corollario run-4 riverificato). Nessuna regola nuova: pattern già canonico [sync:safe]

## [1.5.21] - 2026-11-05

### Changed

- `tool-pitfalls.md` §«Parametri numerici respinti come stringhe»: corollario run-4 — con range respinto, `read_file` senza range è outline-only anche CON terminal su file ~100 righe (ToDo.md 104), unico accesso `sed -n` a chunk; appendice evidenza sessione analisi telemetria Laya + /learn ! (2026-11-05) [sync:safe]
- `tool-pitfalls.md` §«Path dei comandi L0»: rifiuto `read_file` esteso alle **sottocartelle symlinkate sotto l'alias** (`.agents/skills/a-product/competencies/…` → `hal_gateway`, confermato da `readlink -f`); fallback `skill` tool / `cat` [sync:safe]
- `tool-pitfalls.md` §«Assenze da verificare»: conferma su finestra ampia (16,6k righe) della causa broken-pipe del 2026-10-29 — cluster 25–29 ott, zero post-guard/timeout (analisi telemetria 2026-11-05; Regola 8: ha fatto riscrivere una voce ToDo che spacciava la causa per ignota) [sync:safe]

## [1.5.20] - 2026-11-04

### Changed

- `tool-pitfalls.md` § «Parametri numerici respinti come stringhe»: bullet di fallback per runtime **senza terminal** (`sed -n`/omissioni non esistono: `read_file` senza range = integrale dei piccoli, **outline** dei grandi; guardie di lettura sorgente per viste non importabili) + evidenza sessione brainbeez /learn ! #17; ripulita la coda duplicata della riga Evidenza [sync:safe]
- `tool-pitfalls.md` § «Assenze da verificare prima di ToDo/claim»: regola tool dichiarato nello schema ma assente nel runtime (stop dopo 2 congetture di nome, dichiarare il limite) + corollario regola-8 estesa al transcript (tool-result asseriti ≠ prova; ri-verificare con letture reali e `git --no-pager log` quando il terminale torna) [sync:safe]

## [1.5.19] - 2026-11-04

### Changed

- 1.5.19: Evidenza in § «Parametri numerici respinti come stringhe» — `read_file` con range respinto 2× in due chiamate (`invalid type: string, expected u32`, retry identici; fallback: lettura integrale senza range), sessione fix pyright brainbeez (/learn ! 2026-11-04 #16). Nessuna regola nuova: pattern già documentato.

## [1.5.18] - 2026-11-04

### Changed

- `tool-pitfalls.md` § «Path dei comandi L0: canonico vs mirror generato»: nuova evidenza sessione RCA-500 brainbeez (2026-11-04: consumer senza symlink `agents/` → override `script` assoluto per `version_pending`/`agent-version.sh`; `git -C` per il cross-repo, `cd` del terminale accetta solo root di progetto) [sync:safe]

## [1.5.17] - 2026-11-04

### Changed

- `tool-pitfalls.md` § «Parametri numerici respinti come stringhe»: nuova evidenza sessione RCA-500 prod brainbeez (2026-11-04: `terminal timeout_ms` respinto 2× con `expected u64` → omesso) [sync:safe]

## [1.5.16] - 2026-11-03

### Changed

- `tool-pitfalls.md` § «Parametri numerici respinti come stringhe»: nuova evidenza sessione menubar brainbeez (2026-11-03: `read_file` range respinto 4× anche con parametri numerici identici al retry; `terminal timeout_ms` respinto 2× → `sed -n`/omissione) [sync:safe]

## [1.5.15] - 2026-11-01

### Added

- `tool-pitfalls.md` § «Parametri numerici respinti come stringhe» + § «Batch `edit_file` non atomico»: nuova evidenza sessione hal_seo seozoom-imports (2026-11-01: `read_file` range respinto 2× anche con interi → `sed -n`; anchor `old_text` invalidato da reflow formatter tra `write_file` ed `edit_file`, batch parzialmente applicato → riscrittura integrale; `rules.py` con `KIND_ORDER` duplicato da merge parallelo) [sync:safe]

## [1.5.14] - 2026-10-31

### Added

- `tool-pitfalls.md` § «Batch `edit_file` non atomico»: nuova evidenza «file condivisi mutati da sessioni parallele» — `.agents/skills/harness-wtp/SKILL.md` 1.1.4→1.1.5 tra due letture nella stessa sessione (2026-10-31, sessione fix naming L2 harness-*) [sync:safe]

## [1.5.13] - 2026-10-31

### Added

- `tool-pitfalls.md` § «Parametri numerici respinti come stringhe»: nuova evidenza — sessione orcarouter add+remove modelli (2026-10-31: `read_file` range respinto 3×, `terminal timeout_ms` respinto 2× → `sed -n`/omissione) [sync:safe]

## [1.5.12] - 2026-10-30

### Added

- `tool-pitfalls.md` § «Path dei comandi L0: canonico vs mirror generato»: `edit_file`/`write_file` non risolvono gli symlink intermedi (usare alias `.agents/skills/...` o heredoc terminale fuori progetto); i mirror `.agents/skills/<cmd>/SKILL.md` dei comandi L0 sono rigenerati da `link-workspace-skills.sh` — bump sempre sul canonico `a-agentzero/commands/<cmd>.md`, mai solo sul mirror (caso graph 1.0.3, 2026-10-30) [sync:safe]

## [1.5.11] - 2026-10-30

### Added

- `tool-pitfalls.md` § «Batch `edit_file` non atomico»: tre regole promosse via `/sync <` da brainbeez — ① mai ricostruire `old_text` a memoria (rilettura prima di ogni edit); ② un solo `edit_file` per file per chiamata (anche ancore simili → fuzzy al sito sbagliato); ③ tabelle markdown padded → append via `cat >>` heredoc quotato, non `edit_file`. Evidenze multiple 2026-10-28 → 2026-10-30 (brainbeez + QwenCloud) [sync:safe]

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

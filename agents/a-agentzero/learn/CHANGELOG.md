# Changelog — learn

## [1.8.5] - 2026-11-22

### Changed

- tool-pitfalls, due estensioni di evidenza da sessione Toth v0/HT-017 (2026-11-22): §comandi L0/worktree (il `cd` del terminale rifiuta il worktree fuori root come `write_file` — su HAL regime normale: patch via heredoc python); §Writer canonico (flag sconosciuto consumato come KIND → file `handoff---help.json`; `files` stringa comma-separated; post-write sanity con `handoff-read` + `ls`). Classi «parametri numerici» e «`<(...)` sh» risultate GIÀ in skill senza informazione nuova: nessuna riga (anti-grasso).

## [1.8.4] - 2026-11-22

### Changed

- `/learn !` hal_gateway (#2, residui sessione HT-014, post a11571c): due blocchi datati in `tool-pitfalls.md` — §Sessioni parallele estensione writer canonico (autostash-pop conflittato su file altrui con writer canonico → `restore --source=HEAD`, variante WIP nello stash per il proprietario; mai lasciare path unmerged nell'index condiviso; variante controllata per log append-only: stash single-file → ff → pop, auto-merge) e §Replay/stale canone item 4 (letture di contenuto ri-emesse con marker nuovi finché torna il conteggio righe atteso; chunk con esclusione della riga ostile). Fuori bundle: bullet calibrazione prefissi commit in `docs/28_laya_model_card.md` §Limiti misurati (1/5 correct, feat↔docs sistematico su diff non-codice). Aperte `HT-018` (refresh fence ×21 post a-agentzero 1.16.0) e `HT-019` (gh auth refresh + fallback SSH in git-push-auth.sh) in ToDo via blob surgery. Voce `### HAL` in `product/session-learnings.md`.

## [1.8.3] - 2026-11-22

### Changed

- `/learn !` hal_gateway (chiusura sessione HT-014/consumer-push, post 702aeb6): tre blocchi datati in `tool-pitfalls.md` — §Push HTTPS interattiva estensione (no-op silenzioso del modulo eseguito direttamente → guardia `BASH_SOURCE` in 4af90d3 + 3 test; fallback SSH BatchMode a URL esplicito con helper gh scaduto; push a URL esplicito non aggiorna i remote-tracking ref → verità = `ls-remote`), §Parametri numerici ricorrenza (`read_file` range respinto 2× `expected u32` → `sed -n`; nessuna regola nuova), §Replay/stale ricorrenza (collasso a singola riga su tutti i canali 2026-11-20/22; sanificazione keyword + probe negative → non filtro di contenuto; workaround marker nuovi + chunk con esclusione riga sopravvissuta). Aperto `HT-016` in ToDo (push 4 consumer rimasti + remote gDrive_ops). Voce `### HAL` in `product/session-learnings.md`.

## [1.8.2] - 2026-11-21

### Changed

- `/learn !` hal_gateway (chiusura sessione comandi L0, dopo commit+push 37215df): tre righe datate in `tool-pitfalls.md` — **grep non ancorato = falso positivo** (§grep, 1ª occorrenza: `grep -m1 version` legge `name: version`, il confronto canone↔mirror diede uno «stale» falso su mirror già allineato; canone: ancora `^version:` o guardia `check-version-changelog.sh`); **recupero auto_vote post-commit saltato** in sessione (§Parametri numerici, estensione del bullet helper: «registrato (correct)» rc=0 con lo stesso hash); **`--all` delegato come inclusione dichiarata** su tree condiviso (§Sessioni parallele: allow-list esplicita + gate verdi + messaggio che dichiara, la gara si chiude). Ricorrenza §Parametri numerici (`timeout_ms 300000`/`600000` rifiutati come `expected u64` → omessi, nessuna regola nuova). Esclusi anti-grasso: riverifica fatti con read-only (regola 9/§7 già riversata da HT-012 in 1.8.1), HEAD drift/replay (§Strumenti: risultati replay/stale), canoni (a)(b)(c) della transazione (già in 1.8.0). Voce `### HAL` in `product/session-learnings.md`.

## [1.8.1] - 2026-11-21

### Changed

- HT-012 (`/graph -y`): riversati nei target canonici i canoni 1-5 + §7-§9 della nota de-racing 2026-11-19/20 (`docs/apprendimenti-de-racing-2026-11-20.md`): §1 → nuova sezione «Strumenti: risultati replay/stale del canale tool» in `references/tool-pitfalls.md`; §2 → §Path dei comandi L0; §3+§5 → §Sessioni parallele sullo stesso repo; §4+§8 → §Shell di lavoro `sh`/dash; §7 → §Assenze da verificare (Percorsi citati come evidenza, 2ª occorrenza) + estensione regola 9 di `references/learn-guidelines.md`; §9 → §Tool call paralleli. §6 non riversato (già consolidato in `AGENTS.md`/`operativo.md`, da acceptance HT-012). Voce `### HAL` 2026-11-21 in `product/session-learnings.md`; voce brace di `ToDo.md` chiusa; convenzione ID (`HT-nnn` zero-padded) uniformata.

## [1.8.0] - 2026-11-20

### Changed

- `/learn !` hal_gateway (sessione dismissione wrapper locali comandi L0): nuovo bullet datato in `tool-pitfalls.md` §Path dei comandi L0 — mirror soppresso (sede unica: globale) con le tre regole della transazione: prima di `rm -rf` su superfici generate, ispezionare il git dei dati non rigenerabili (i CHANGELOG unici nei mirror trasferiti al canone `commands/CHANGELOG.md`); estendere lo sweep dei riferimenti alle auto-descrizioni dei canoni (refuso di memoria: `learn.md` e §specchi di `version.md` rimasti indietro dopo la correzione di `sync.md`); baseline dei test prima di ripuntarli (due RED preesistenti emersi: pin graph 1.0.4≠1.0.5, fixture COMMANDS 9/11). Ricorrenza §Parametri numerici (terminal `timeout_ms 300000` rifiutato come `expected u64` — classe già documentata dal 2026-11-04, nessuna regola nuova).

## [1.7.1] - 2026-11-18

- Sezione nuova «Push HTTPS interattiva: mai in una land» (evidenza: incidente t107 del 2026-11-18 — helper credenziali scaduto a metà sessione, land in ostaggio sul prompt username con flock acquisito). Canone L0 associato: modulo `agents/scripts/git-push-auth.sh` (GIT_TERMINAL_PROMPT=0 + classificatore auth + fallback helper gh) integrato in land/commit; config repo `credential.helper='!gh auth git-credential'` applicata su hal_gateway e hal_system2. 3 test in `tests/test_git_push_auth.py`.

### Fixed

- `tool-pitfalls.md`: nuovo bullet «percorsi citati come evidenza vanno verificati» (prima occorrenza classe allucinazione-evidenza: `pyright-conventions.md` citato come fonte, file inesistente). Consolidata in `product/session-learnings.md` §HAL la catena pyright HT-010 (assert ModuleSpec, `(__doc__ or "")`, spec-arg) come convenzione cross-progetto (brainbeez 2026-11-04 + HAL 2026-11-18); ricorrenza §Parametri numerici (read_file range, interi, 4×) registrata senza nuovo bullet — già documentata dal 2026-11-04.

## [1.6.26] - 2026-11-18

- `/learn !` hal_system2 2026-11-18 (catena T1-03 → strategie anti-frizione → sync): §Batch `edit_file` non atomico — **promossa a canone** la variante «duplicazione da batch a cascata con doppio success» (candidato 2 del 2026-11-17, seconda osservazione raggiunta: `_t103_recon.py`, contatori raddoppiati con entrambi gli edit «Edited successfully»); §Sessioni parallele — file messaggio di `agent-commit.sh -m` risolto dalla ROOT dopo il `cd` interno (rc 128, evidenza 78caae0). Candidati 1 (`write_file` backslash) e 3 (propagazione `ls-remote`) **rinviati con dichiarazione**: le occorrenze odierne appartengono ad altre classi (enumerazione worktree a inizio sessione; dipendenze tra tool call) e non costituiscono seconda osservazione della stessa classe. Nessuna promozione per «blob chirurgico»: già canonico in §Sessioni parallele.
- `/learn !` hal_gateway (sessione HT-005→HT-010, stesso giorno, seconda consolidazione): consolidati in `tool-pitfalls.md` §Sessioni parallele — (1) prefisso di directory nell'allow-list assorbe i transitori nati tra `status` e `add` (lockfile LibreOffice pushato in 1822d3e; recupero senza reset: blob surgery con `rm --cached` su index privato, 9ceb108 — `git add` non stagea la cancellazione di un file ancora su disco); (2) verde preso in prestito: origin può restare rosso da bump meccanico corrotto altrui (`c3599e2` `versenversion:`) mentre il worktree condiviso è già a posto per la sorella — rieseguire il gate che legge i file bumpati e verificare `git diff` sui file letti dal gate prima di chiamarlo «CI verde»; `sync !`/deploy-all pubblica lo stato del worktree. §Tool call paralleli: sesta evidenza (tre ricadute producer→consumer autoinflitte, nessuna regola nuova). Carta `docs/28_laya_model_card.md`: N/A «eval raw assente» → prima eval misurata su oro confermato (hit_rate 0.276, direct band 0.523, caveat vocabolario noul/bypass score), adozione soglie gated `HT-011`. Esclusi (anti-grasso): auto-vote commit-type 3/4 incorrect (già nel loop telemetria Laya), coercizione parametri numerici (già 1.6.25), warning estensioni DV openpyxl (osservazione singola).

## [1.7.0] - 2026-11-18

### Added

- `tool-pitfalls.md` §Sessioni parallele: ricetta «`pull --rebase --autostash` in worktree condiviso con sorella attiva» — conflitto del proprio commit si risolve tenendo entrambe le modifiche, il UU su file ALTRUI si riporta a HEAD (`git reset -- <file> && git checkout -- <file>`) lasciando lo stash autostash intatto; mai drop del lavoro altrui.
- `tool-pitfalls` §Frammenti CJK: evidenza di ieri (assorbito `吸收` nel session-learnings generato in /learn !, sweep `grep -rP` post-scrittura ha preso il refuso prima del commit).

## [1.6.27] - 2026-11-18

### Changed

- `learn-guidelines.md`/`consolidation-targets.md`: ritirato il wording di dismissione AgentFactory (routing su HAL, `brands/hal.md`); la fonte canonica ora punta a file che esistono.

## [1.6.25] - 2026-11-18

- turno hal_system2 «strategie 1-7» (2026-11-18): le recidive documentate come **estensioni di sezioni esistenti**, non nuove massime — il collo di bottiglia non era l'assenza di dottrina ma il non ripescarla al momento dell'uso: §Parametri numerici (client che serializza i numerici, ~20ª occorrenza), §Tool call paralleli (variante «dipendenza autoinflitta»: 4 occorrenze nel turno stesso che implementava la regola), §Path dei comandi L0 (topologia HAL.git app+registry, cd via symlink consumer, worktree appena creato invisibile ai file tool). Referenza canonica nuova: AGENT-PROTOCOL § «Layout canonico»; regole 15-16 in worktree-land.

## [1.6.24] - 2026-11-18

- `/learn !` brainbeez rv19/chiusura S149 (2ª sessione `/learn` del giorno, dopo 1.6.23): consolidate le **2 promozioni pending dichiarate nell'entry #37** del registro progetto, entrambe verificate una 2ª volta oggi: (1) §Sessioni parallele — gate pre-commit che legge il disco ⇒ commit in `git worktree add --detach`; (2) §Sessioni parallele — lane di test parallele condividono il DB dev del compose ⇒ red transitori da attribuire con lock di riga.
- Nota di gara: collisioni odierne sui registri (etichetta S148→S149, voce S146 cancellata a metà in CHANGELOG, worktree HAL in M/M) — le due regole chiudono il cerchio appena aperto.

## [1.6.23] - 2026-11-18

- `/learn !` brainbeez rv19 (catena S149 «cluster vs company + tab Aziende», slice rinumerata da S148 per collisione): 2 nuovi bullet in §Sessioni paralleli di `tool-pitfalls.md` — (1) etichette di slice in gara: next SNN/QNN = max(HEAD, worktree), riverifica prima del primo write, rinumerazione two-phase con validazione completa prima di scrivere; (2) baseline rossa da WIP altrui: attribuire con `git diff HEAD` e dichiarare, mai riapplicare Act non propri (evidenze: 3 `KeyError: 'lead_score'` da staged removal di altra sessione, 11 rossi web da revert V4 non mio). Chiude i due PENDING dichiarati nell'entry #37 del registro progetto.

## [1.6.22] - 2026-11-18

- Consolidamento `/learn !` (brainbeez rv19, catena commit S146/V4 in gara con sessione parallela). 3 bullet nuovi in `references/tool-pitfalls.md` §Sessioni paralleli: hook che rigenerano file da disco (commit in worktree pulito su HEAD), affermazioni di assunzione/perdita misurate solo su `git show HEAD:<path>`, guardia-base che blocca ⇒ rifare il merge sulla nuova HEAD; marcati «in attesa di conferma su seconda sessione» (sessione singola, evidenza riproducibile). 1 bullet in §Parametri numerici: classi sorelle di validazione-schema (`terminal` senza `cd` → `missing field cd`; MCP laya `options` come stringa → «at least two distinct options are required»). 1 variante in §Shell di lavoro: heredoc non quotato con prosa parentetata. Controparti specifiche di progetto persistite in L2 `harness-brainbeez` (1.5.38). Nota di gara: la voce 1.6.21 è stata committata dal gemello parallelo (commit 28d4a59); la 1.6.22 (questa) resta l'unica non committata nella tree di hal_gateway.

## [1.6.21] - 2026-11-18

- `/learn !` in gara (sessione /learn parallela): consolidata l'evidenza del batch multi-edit non atomico nel bullet «Variante cross-tool» di §Tool call paralleli — applicato **solo il primo edit** della chiamata (il file era cambiato tra lettura e scrittura); i due edit successivi (falso positivo su ricerca di stringa già presente, duplicazione di un bullet) non atterrati. Rimedio: sostituzioni Python mirate con assert, pulizia di 2 blank line residue tra bullet fratelli. Verifica post-scrittura in risposta separata: la regola di §Verifica dopo scrittura ha funzionato, ed è il motivo per cui la gara è stata rilevata.
- Nuova bullet in §Sessioni paralleli: **collisione `/tmp` tra sessioni parallele** — `read_file` di `/tmp/learn_state.txt` restituiva contenuto della sessione gemella; rimedio: stato intermedio nel root del progetto (`.tmp_*`), non `/tmp`. La classe «parametri numerici passati come stringhe» (`read_file end_line`, `terminal timeout_ms`) risulta già documentata in §Parametri numerici: nessun aggiornamento della catena d'evidenza è stato tentato per non scrivere sul bullet condiviso da 7k carattere in gara (rischio > valore informativo).

## [1.6.20] - 2026-11-17

### Changed

- `references/tool-pitfalls.md` §terminal/pytest: unificazione del wording «Verità del gate» — la formula autoritativa è la policy L1 `a-harness` §Verità del gate; il bullet pitfall resta come ricetta operativa con puntatore. Origine: /sync < 2026-11-17, AGG-05 (brainbeez).

## [1.6.19] - 2026-11-17

### Changed

- `references/tool-pitfalls.md` §«Tool call paralleli»: **nuova variante della classe** «batch intra-sessione con dipendenze interne» (catena brainbeez /impersonate → release 0.16.0, 2026-11-17) in forma composta — batch parallelo con dipendenze interne (producer/consumer su /tmp, errore taciuto da `2>/dev/null` + fallback `||`, bashism `<( )` fuori da `bash -c`) + regola nuova **mai citare sha non ancora esistenti** (mirror con placeholder scartato con `reset --soft` prima del push; guardie autrici del blocco: script + pre-push). [sync:safe]

### Added

- `references/tool-pitfalls.md` §«Parametri numerici respinti come stringhe»: bullet sui formati taciuti dai helper — `auto_vote_routing --options` è **virgolettato**, spaziato ⇒ no-vote con exit 0; prima occorrenza della classe «exit 0 ≠ voto registrato». [sync:safe]

Nota di trasparenza: il worktree portava ripristini stale di CHANGELOG e tool-pitfalls (rimuovevano 1.6.17/1.6.18) — blob costruito da `git show HEAD`, non assorbito, come prescrive la sezione «Sessioni parallele» del reference stesso.

## [1.6.18] - 2026-11-16

### Added

- `references/tool-pitfalls.md` §«Sessioni parallele sullo stesso repo»: **seconda evidenza AGG-10 nella direzione simmetrica** (commit che assorbe lo staged altrui — brainbeez release 0.14.0, mirror commit con 9 file WIP parallelo) + nuova regola «revert fantasma da commit out-of-band» (l'index privato lascia il condiviso al vecchio HEAD: riallineare con `update-index`/`--cacheinfo` sui soli path committati, mai `reset`) + puntatore alla contromisura canonica `agent-commit.sh` (L0 `/commit` 1.1.0/1.1.1, HAL 2cdcc33/d22ceaf, stessa data). Nota di trasparenza: il worktree aveva un ripristino stale di questa sezione (rimuoveva l'evidenza #34 già committata in aa74375) — il blob è costruito da `git show HEAD` senza assorbirlo, come da regola della sezione stessa. [sync:safe]

## [1.6.17] - 2026-11-16

### Changed

- `references/tool-pitfalls.md`: §Output lunghi, nuovo bullet «Evidenza numerica in artefatti persistenti ≠ display» (hal_system2 `/graph -y` rv8 N31: rate 0,788 e 1.460 voti scritti in ToDo/grafo da output troncato/mescolato fra finestre — reali 0,999 su 1.038 voti e 6 voti; corretta solo con rimisurazione in container, /learn ! #34); §sh/dash, variante `docker exec` senza `-i` (heredoc scartato → exit 0 con output vuoto, fallimento silenzioso; canone: script in `/tmp` + `docker cp` + `-e PYTHONPATH=/app`, one-liner `python3 -c`); §Batch edit_file, ribadita la variante «esito ≠ applicato» (reflow padding-only su work-graph con `git diff -w` vuoto; àncora ricostruita a memoria fallita — evidenza della regola già canonica); §Parametri numerici, evidenza #34 (`read_file` range 4× `expected u32` → `sed -n`; `timeout_ms` 1× `expected u64` → omesso; nessuna regola nuova).
- `references/learn-guidelines.md`: nuova regola 9 di scrittura «Evidenza numerica — verbatim o rimisura» (operazionalizza il lato scrittura della voce «Escludi: metriche non verificate»: citare solo dal risultato tool che ha prodotto il numero nella stessa chiamata, altrimenti rimisurare bounded).
- Nota di trasparenza: al momento di questo `/learn !` il frontmatter era già 1.6.16 senza entry omonima in CHANGELOG (bump di sessione parallela non riverificato qui); `agent-version.sh bump patch` ha portato 1.6.16→1.6.17. Entry redatta a mano con dichiarazione — lo script non tocca il CHANGELOG.

## [1.6.16] - 2026-11-16

### Changed

- `references/tool-pitfalls.md` §«Tool call paralleli»: **quinta evidenza** (brainbeez rv18 onda L, /learn ! #34) — variante peggiore della classe: esiti «successful» mai atterrati su disco e un intero segmento di risposta con tool-call/risultati verosimili ma mai eseguiti (finti gate, finti canoni di nodi mai corsi). Discriminante: disallineamento stato-discorso, non messaggio d'errore. Rimedio sistematico (estende «rilettura in risposta successiva»): alla prima evidenza di troncamento/incoerenza, re-baseline da disco prima di ogni passo dipendente (grep marker registri + `git diff HEAD --stat` + `git log -1` + handoff + contatore slice); riapplicare solo ciò che la misura dichiara assente. Bump `agent-version.sh` 1.6.15→1.6.16; entry integrata a mano (dichiarazione: lo script non scrive l'entry).

Nota di trasparenza (recupero 2026-11-18, catena `/version patch` + `/commit` su HAL): sezione e bullet risultati smarriti in una gara stale-restore 1.6.15→1.6.16 (il changelog pubblicato già saltava «1.6.16», come dichiarato dalla nota della voce [1.6.17]); recuperati dal worktree contaminato via blob surgery (§Sessioni parallele) e reintegrati in `tool-pitfalls.md` §Tool call paralleli.

## [1.6.15] - 2026-11-16

### Changed

- `references/tool-pitfalls.md`: §Writer canonico, bullet «Schema fisso, niente fusione» (hal_system1 rv10 2026-11-16: chiavi non passate azzerate, chiavi fuori schema cadono, `--dir` inesistente nel builder — contraddizione con la nota di fusione 2026-10-30 marcata da riverificare, non cancellata); §sh/dash, bullet heredoc-con-comando-dopo-EOF (3 run hal_system1 11-15/16 + rimedio script-in-file); §Batch edit_file, variante «batch abortito CON reflow» (esito tool ≠ contenuto applicato: sonda grep + `git diff -w`; celle solo via python anchor assertito); §CJK, estensione del rimedio (a) pre-scrittura dalle escapes JSON alle stringhe python di heredoc (2 occorrenze corrette prima della persistenza). Bump frontmatter via `agent-version.sh`; entry CHANGELOG integrata a mano con dichiarazione (lo script non tocca il CHANGELOG).

## [1.6.14] - 2026-11-16

### Added

- `references/tool-pitfalls.md` nuova sezione «Sessioni parallele sullo stesso repo: index git condiviso e file di stato in gara» — promozione di AGG-10 via `/sync <` (evidenze: brainbeez S123 2026-11-15, staging selettivo via blob da HEAD trovato indipendentemente; brainbeez rv18 release 0.13.2 2026-11-16, index azzerato tra add e commit → regola `add && commit` in un'unica invocazione + verifica a risposta separata; /learn ! #33 2026-11-16, file HAL sovrascritto tra scrittura e verifica → non riaprire la corsa sul file). Contesto: §shell marcata «già canonica in HAL» (terza evidenza presente nel reference; il marker HOLD nel report `/sync <` era obsoleto). Entry CHANGELOG integrata a mano con dichiarazione — `agent-version.sh` bumpa solo il frontmatter (1.6.13→1.6.14).

## [1.6.13] - 2026-11-16

### Changed

- Evidenze #33 in `references/tool-pitfalls.md` (frontmatter bumpato via `agent-version.sh` 1.6.12→1.6.13; entry CHANGELOG redatta a mano con dichiarazione: lo script non scrive l'entry — suo `cd` relativo — e una sessione parallela HAL ha sovrascritto il file tra la mia prima stesura e la verifica, caso live della classe §Tool call paralleli): §«Parametri numerici» occorrenze brainbeez rv18 resume+release 2026-11-16 (`read_file` range 2× `expected u32` identici al retry, `terminal timeout_ms=180000` 1× `expected u64` → omettere, default retto anche su gate+hook; nessuna regola nuova); §«Tool call paralleli» **quarta evidenza** cross-tool — verifica emessa nello stesso batch di una scrittura = falsi negativi ricorrenti (ImportError fantasma su helper `_queue.py` già su disco, `grep -c` 0 su righe appena appese, `awk` «not found» su entry appena aggiunta): mai ri-applicare l'edit sulla base di una verifica stesso-batch, e mai fidarsi del «successful» dello strumento: rilettura in risposta successiva; §«Shell sh/dash» **terza evidenza** `diff <(...)` sotto sh nel taglio chirurgico del CHANGELOG di release → file in /tmp, promozione già ammissibile. Fonte: rv18 N131–N136 + release 0.13.2 (brainbeez /learn ! #33). Candidati ToDo HOLD AGG-10 (git index condiviso multi-sessione: `add && commit` atomico + blob chirurgico mixed-[Unreleased]) e AGG-11 (voto MCP: `auto_vote_commit.py` no-vote su hash da `laya_choice` ⇒ `laya_outcome(expected=…)`) — evidenza singola, non in HAL.

## [1.6.12] - 2026-11-15

### Changed

- Evidenze/varianti #32 in `references/tool-pitfalls.md`: §«Parametri numerici» occorrenze brainbeez 2026-11-15 (`read_file` range ~5×, `timeout_ms` 1×, `head_lines`/`tail_lines` 2× — nessuna regola nuova); §«Batch `edit_file` non atomico» **variante format-on-save** (lo strumento ri-wrappa il proprio `new_text` nello stesso turno: àncore dei follow-up da rileggere dal file, mai dalla stringa inviata); §«Tool call paralleli» terza evidenza brainbeez + variante red transiente mid-save di sessione terza (ri-eseguire prima di attribuire); §«Frammenti CJK» **sottoclasse byte: BOM U+FEFF invisibile agli sweep CJK/mojibake** → `od -c`/grep `EF BB BF` sulle righe toccate da inserzioni in header di stato, e nota sugli sweep con token CJK intenzionali tra virgolette (conteggio dichiarato, non azzerato). Fonte: audit codebase + catena S114 (brainbeez /learn ! #32).

## [1.6.11] - 2026-11-14

### Changed

- Evidenze #31 in `references/tool-pitfalls.md`: §«Parametri numerici» occorrenze brainbeez 2026-11-12 (`read_file` range 2×, `timeout_ms` 2× — nessuna regola nuova); §«Tool call paralleli» variante **doppio side-effect identico** (stesso comando con effetto emesso due volte in un blocco parallelo → deployment gemello REMOVED; audit via `railway deployment list`). Fonte: catena header colonna 0.10.3 + chore .railway (/learn ! #31).

## [1.6.10] - 2026-11-13

### Added

- Nuova modalità **redigi** (`/learn! redigi <file> per <target>`): redazione comunicativa di documenti con quattro regole non negoziabili (niente nome/costi fornitore interno verso l'esterno, terzi anonimizzati senza autorità, fedeltà al canone del documento, claim ancorati ai file citati) + sweep CJK/mojibake obbligatorio a chiusura. Nata nella catena 0.11.0 (redazione partnership-perfills: «fornitore che vende a noi non si nomina a chi potrebbe comprarlo da noi»; il refuso `副作用` scappato proprio durante una redazione è l'evidenza scatenante). La redazione non è apprendimento: non innesca di per sé `/learn !`.

## [1.6.9] - 2026-11-13

### Changed

- tool-pitfalls: appendite evidenze **/learn ! #28** (catena /cycle AGG → /todo flush → /version 0.10.4 → push/deploy): §«Parametri numerici» (read_file ×2 → `sed -n`; timeout_ms ×3 → omesso, budget `for … sleep`); §«Frammenti CJK» **nuova variante di generazione** — escapes `\uXXXX` scritti a mano nel JSON di `edit_file` (non più solo heredoc): `già文档ato`/`功能` arrivati fin dentro HEAD committato e pushato; rimedio: carattere diretto, assert pre-scrittura `any('\u4e00'<=c<='\u9fff')` sull'oggetto in memoria, sweep solo con `grep -P` (con `-oE` il range escaped fallisce); §«Tool call paralleli» (estensione della classe `MAKE_EXIT` da pipe a `git push`: PUSH_EXIT=0 su push respinto; catena producer→consumer python→`git commit -F` emessa parallela → exit 128 — **parziale duplicazione dichiarata** con la variante cross-tool già consolidata dalla sessione parallela in 1.6.8/#29: stessa classe, istanze diverse); §«Processi distaccati» (riverifica timeout≠esito: `test_run make test-unit` in context timeout ma il gate completò davvero ec=0 — non ri-lanciare, pollare artefatti).
- Dichiarazione di gara: il numero #28 è stato attribuito dopo il #29 della sessione parallela ruoli/digest (stesso giorno, HAL condiviso) — disordine cronologico dei contatori, non collisione; le appendute sono in sezioni diverse o su istanze distinte.

## [1.6.8] - 2026-11-13

### Changed

- tool-pitfalls §«Parametri numerici respinti come stringhe»: evidenza #29 (brainbeez catena ruoli/digest 2026-11-13: `timeout_ms` 3× respinto → omesso; `read_file` range 4× → `sed -n`; classe già canonica). §«Tool call paralleli»: variante **cross-tool** (seconda evidenza della classe producer→consumer) — `write_file`+`terminal` dipendente, `edit_file`+`git commit`, `edit_file`+lint nella stessa batch: 3 casi reali con esito (ENOENT, commit pre-edit pushato, check obsoleto); regola: ogni chiamata che dipende da una scrittura della stessa risposta va rinviata alla successiva. §tabelle padded: variante append riga su decision-log PRD (àncora di fine-riga con padding ignoto; chirurgia python con width dall'ultima riga e padding PRIMA del pipe; rimozione cella via `sed` per riga). §«Frammenti CJK»: variante **mojibake latino** (`perchÃ©` da byte UTF-8 ri-encodati) + artefatto fuzzy-a-catena sul testo corrotto; sweep esteso a `grep -nP 'Ã|Â'`.

## [1.6.7] - 2026-11-10

### Changed

- tool-pitfalls §«Parametri numerici respinti come stringhe»: evidenza #27 (brainbeez /learn !, newleads-enrichment 2026-11-10: `terminal timeout_ms` respinto 5× → omesso, `timeout` bounded in-shell; `read_file` range 2× → `sed -n`; classe già canonica, nessuna regola nuova). §«Processi distaccati»: variante **pkill** — il pattern nel `sh -c` chiamante matcha se stesso e `pkill -f` uccide la shell del comando composito (exit 1, zero output); usare `[p]attern` o chiamata isolata.

## [1.6.6] - 2026-11-09

### Changed

- tool-pitfalls §«Parametri numerici respinti come stringhe»: evidenza #26 (hal_system2 `/learn !` HT-003 2026-11-09: `terminal timeout_ms` respinto 2× (`120000`, `300000`, `expected u64`) → omesso; nessuna regola nuova, classe già canonica).

## [1.6.5] - 2026-11-09

### Added

- tool-pitfalls: nuova sezione «Chiamate parallele su stato condiviso» (scritture/gate/bump seriale; MAKE_EXIT da processo non da pipe; casi (a)-(d) sessione laya 2026-11-09, cicli T-6C1B2→T-73140) + sub-emendamento «commenti con prefisso direttiva» (`# pyright:` in prosa = 3 errori, candidato ≥2 sessioni).

## [1.6.4] - 2026-11-09

### Added

- tool-pitfalls: nuova sezione «Processi distaccati via tool MCP: timeout ≠ esito, mai fidarsi di pgrep» (timeout MCP orfanizza o uccide i subprocess: misura da artefatti, `setsid nohup` per deploy lunghi; pgrep -f self-match) — evidenza h2b 2026-11-05 + d9 2026-11-09, laya.
- tool-pitfalls §tabelle padded: variante distruttiva rv9 (fuzzy su token `planned` che riscrive riga limitrofa, `new_text` con trailing `|` che genera celle vuote, `__underscore__` fuori backtick corrotto in bold; canone chirurgia python + verifica pipe su tutte le righe).
- tool-pitfalls §Writer canonico + graph 1.0.4: builder handoff presente nei consumer via `agents/scripts/harness-prompt-builder.sh` (symlink HAL) — falsificazione «non presente nel repo» da path-miss rv9.

## [1.6.3] - 2026-11-09

### Changed

- tool-pitfalls §«Parametri numerici»: evidenza #25 (hal_system2 `/graph -y` rv7 — `read_file` `start_line`/`end_line` respinto 3× `expected u32` anche con interi monolitici e ordine invertito, `terminal timeout_ms` respinto 2× `expected u64` → omissione, `sed -n`/`awk`; outline senza range riverificato anche su file di 94 righe). Nessuna regola nuova: classe già canonica (≥15ª sessione).

## [1.6.2] - 2026-11-09

### Changed

- tool-pitfalls §«Parametri numerici»: aggiunta evidenza di sessione #24 (brainbeez S89 2026-11-09 — `read_file` range respinto 2× `expected u32`, `terminal head_lines` respinto `expected usize`, `timeout_ms` respinto `expected u64` → omissione totale dei parametri numerici opzionali, `sed -n`/`timeout` di shell). Nessuna regola nuova: classe già canonica (evidenza ≥14ª sessione).

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

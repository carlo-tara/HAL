# Changelog — a-agentzero

## [1.13.9] - 2026-11-18

### Added

- Builder riusabile per i test di protocollo: `tests/wt_scratch.py` (`make_scratch`: origin bare + seed pushato + clone con untracked d'ambiente, opzioni `.wt-extra` e registry-symlink; `new_slice`: esegue il vero `agent-worktree.sh new`) e refactor di `tests/test_agent_worktree.py` sul builder con 2 self-test (6 verdi, refactor senza cambio di comportamento).

### Changed

- Regola 14 estesa fino a git: il flush riuscito su master è transazione che si chiude nello stesso turno con commit+push dei soli file toccati; `commands/todo.md` e AGENT-PROTOCOL §Multi-sessione recepiscono (evidenza hal_system2: chiusura T1-03 flushata-non-committata ≈ 15 chiamate di forensics+rebase il giorno dopo).
- Regole 15-16 in `references/worktree-land.md` (confine di slice = contratto; foto di apertura del turno); AGENT-PROTOCOL: nuovo § «Layout canonico» (topologia HAL.git app+registry, symlink consumer, `.wt/`); conteggio regole 13→16 allineato nei due riferimenti.


## [1.13.8] - 2026-11-18

### Fixed

- `agent-worktree.sh new` non aborta più sui consumer con registry via symlink tracciata (hal_system2, brainbeez…): il riuso `.tools/shellcheck` copia solo se il path non è già valido nel worktree — prima il `cp` same-file sotto `set -e` uccideva il comando a metà (evidenza: adoption hal_system2 2026-11-18; test `test_new_survives_registry_symlinked_to_main` con seed a registry symlinkata).

## [1.13.7] - 2026-11-18

### Added

- `agent-worktree.sh new` supporta il tracciato `.wt-extra` alla radice del repo: un file per riga (commenti `#` ignorati) di path untracked necessari al checkout (es. `.env`) viene symlinkato dal MAIN nel nuovo worktree; sorgente assente = warning non-fatale, file già presente nel checkout = salto. Documento nel ciclo di vita di `references/worktree-land.md` e in AGENT-PROTOCOL §Multi-sessione; `.wt-extra` del gateway dichiara `.env`. 3 smoke test in `tests/test_agent_worktree.py` (repo scratch con origin bare: symlink valido, assenza file non rotta, sorgente mancante degradata).

## [1.13.6] - 2026-11-18

### Changed

- Flush come transazione di consolidamento (regola 14 in `references/worktree-land.md`): `agent-todo.py` rifiuta il flush sui branch slice (le `[x]` restano nel ToDo e le trasporta il merge per ID; `--force` per eccezioni umane) e scrive sotto il flock cooperativo `agent-commit.lock` (stesso di `agent-commit.sh` e del land; timeout 60 s, `lock_wait_s` regolabile; fuori da una repo le guardie degradano a no-op, comportamento storico). Contratto di appiattimento documentato in `commands/todo.md`: sopravvivono titolo + figlio `Esito:`, i report lunghi nascono nella final-home (nota datata in `docs/`). 3 test nuovi in `tests/test_agent_todo.py` (rifiuto su slice + force, serializzazione a lock occupato, degrado fuori repo).
- `references/worktree-land.md`: regola 14 + sezione «Residui del modello — massime dal campo» (read-the-tool-before-the-tool; final-home; contratti `#human` leggibili-macchina) con evidenze hal_system2 2026-11-18.

## [1.13.5] - 2026-11-18

### Changed

- Header di convalida (check-version-changelog.sh --fix): il bump era nel frontmatter senza registro — voce da integrare a mano.

## [Unreleased]

### Added

- Comando L0 `commit` **1.1.0** — sezione «Isolamento index (gare multi-sessione)» + script `scripts/agent-commit.sh`: `git commit` legge l'index CONDIVISO, quindi con sessioni parallele il commit assorbe i file altrui già stageati (evidenza: brainbeez release 0.14.0, 2026-11-16 — mirror commit con 9 file WIP parallelo) o arriva vuoto per reset altrui (AGG-10, già in tool-pitfalls). Il script: index privato `GIT_INDEX_FILE` seminato da `read-tree HEAD`, `flock` cooperativo, guardia pre (`staged ⊆ allow-list`), audit post (`committed ⊆ allow ∪ extra-hook`), push con verifica `ls-remote` + retry; fallback documentato: `git commit -F <msg> -- <pathspec>` + audit. Limiti dichiarati: protegge l'index non il work-tree (stesso file in due mani ⇒ write set disgiunti / `git worktree`). Contratto RGR: `product/contracts/check-harness-commit-index.sh` (RED 2026-11-16: 4 asserzioni + funzionale ⇒ GREEN, test dogfood in repo usa-e-getti con file alieno stageato). Nessuna SKILL.md toccata: la catena L1 resta su 1.13.3, `commit` è versionato sull'asse proprio del comando; [sync:safe] ⇒ riallineo figli opzionale (chiusura completa a bundle, precedenti 5e8d4d9/2f37faf). Specchi rigenerati via `link-workspace-skills.sh` (`.agents/skills/commit`, `.zed/prompts/commit.md`).

- Comando L0 `commit` **1.1.1** (fix scoperta al dogfood dello 1.1.0, stesso giorno): dopo il commit su index privato, l'index CONDIVISO restava al vecchio HEAD; un `git commit` ingenuo di una sessione parallela lo avrebbe committato come revert-fantasma dei path appena pubblicati. Lo script chiude ora con `env -u GIT_INDEX_FILE git update-index --add --remove -- <P>` (parità sui soli path committati, mai `reset` su repo condiviso); contratto esteso con asserzione statica + funzionale (dopo il commit, il path committato non deve risultare staged vs HEAD). [sync:safe]

- Comando L0 `commit` **1.1.2** (seconda fix al dogfood, stessa catena: esecuzione brainbeez D): le guardie pre/post confrontavano staged/committed con la allow-list per uguaglianza ESATTA ⇒ un path-directory in allow-list («docs/newleads/outreach») faceva scattare «GUARDIA PRE» su tutti i suoi file (falso positivo, riprodotto). Guardie ora prefix-aware (path esatto o prefisso directory); realineamento finale dell'index condiviso passato da `update-index --add` (rifiuta le directory: «is a directory - add files inside instead») a `git add -A`; contratto esteso con caso funzionale directory + assert sul primitivo `env -u GIT_INDEX_FILE` (non sull'implementazione). Scoperta collaterale: `[[ ]] && cmd` dentro funzione con `set -e` ammazza silenziosamente il command-substitution ⇒ condizioni interne ora `if…fi`. [sync:safe]

- `token_budget.py` — **attribuzione di sessione alla telemetria** (a-agentzero 1.13.4→1.13.5): `init` genera `session_id` (uuid hex 16, formato omogeneo ai `session_id` gateway) nel SESSION_FILE; `_append_event` stampa il campo `session` su OGNI evento JSONL (`null` per sessioni legacy senza campo → lettura `.get()` retrocompatibile, nessun writer rotto). Una coorte è ora contabile per sessioni distinte e non per proxy di cluster orario (gate esperimento P1 `impersonate`, hal_mcp_tools). RGR: +4 test in `tests/test_token_budget_gates.py` (RED 4f/7p → GREEN 11/11); `references/token-budget.md` 1.0.0→1.1.0 con §Schema eventi. Slice cross-repo WAIVER 6 file (5 pool + 1 riga ToDo consumer), accept umano via `/cycle` 2026-11-17.

## [1.13.3] - 2026-11-09

### Added

- Comando L0 `commit`: passo 7 «Auto-voto post-commit» (T-33B98, ok steward esplicito 2026-11-09) — dopo commit esito 0, voto cieco `expected`+`source=commit` via `scripts/auto_vote_commit.py` sul `request_hash` ecoato dal choice di step 1 (ora con `--json`); best-effort: mai far fallire il commit, skip se non c'è hash reale; ground truth `laya_routing` = file modificato. Skill `laya` 1.9.1 (eccezione commit nel bullet Calibrazione). Prelazione nel guard implementata nel logger laya (stack rv9, waiver un meccanismo). [sync:safe]
- Comando L0 `commit` **1.0.1**: front matter `version:` applicata al canonico — il file aveva un `---` orfano senza versione, quindi `command_version()` di link usava il default 1.0.0 e il bump del passo 7 restava invisibile negli specchi; specchi rigenerati via `link-workspace-skills.sh` (.agents/skills, .zed/prompts, product/adapters). [sync:safe]

## [1.13.2] - 2026-11-09

### Changed

- Comando L0 `graph` 1.0.3 → 1.0.4 (canonico `commands/graph.md`): nota Tool — da workspace consumer il builder handoff canonico è `agents/scripts/harness-prompt-builder.sh` (symlink HAL), non `scripts/` del consumer; la nota rv9 «builder non presente nel repo, brief a mano» in `product/state/work-graph.md` era un path-miss, non un'assenza (evidenza laya rv9 2026-11-08/09, /learn !). [sync:safe]
- Skill `learn` 1.6.3 → 1.6.4: tool-pitfalls nuova sezione «Processi distaccati via tool MCP: timeout ≠ esito, mai fidarsi di pgrep» (evidenze h2b+d9 laya) + variante distruttiva tabelle padded e corollario writer canonico nei consumer. [sync:safe]

## [1.13.1] - 2026-10-31

### Added

- `references/extension-scaffold.md` §4–5: contratto naming del loader Agent Skills per le skill L2 — `name` kebab-case (`^[a-z0-9]+(-[a-z0-9]+)*$`) pari alla directory, sanificazione degli underscore dei nomi progetto allo scaffold, «su disco ≠ in catalogo» come sintomo di scarto silenzioso. Promossa via `/sync <` da `harness-agentfactory` (validata su 4 L2 `harness-hal_*`, 2026-10-31). Contratti: `product/contracts/check-harness-skill-naming.sh` (RED 2026-10-31 → GREEN), enforcement `check-frontmatter-all.sh`. [sync:safe]

## [1.13.0] - 2026-10-30

### Fixed

- `scripts/sync-agents.sh` § `report_workspace_links`: `expected` risolto con `resolve_link` prima del confronto (loop skill condivise e comandi L0): nei workspace con `agents/` symlinkato il confronto letterale stringa-vs-realpath produceva sempre «DRIFT» falsipositivi (×29 in hal_system1). Red (DRIFT su tutti i link corretti) → Green (tutti OK) validato 2026-10-29; gate `check-shellcheck.sh` OK. [sync:review]

### Added

- `AGENT-PROTOCOL.md` § "Regole di protocollo: contesto, dichiarazioni, cache": quattro regole da doc Kimi/QwenCloud 2026-10-28 (append-only dichiarazioni iniettate; mai reinserire `reasoning_content` nella history; ordering static-first con divieto di normalizzazione sul body inviato; persistere i risultati entro la retention del provider 24h/30g) — chiude le voci ToDo P1 `#docs` append-only/reasoning/ordering e la P2 `#docs` retention provider [sync:safe]

### Changed

- Skill `learn` 1.5.6 → 1.5.7: `tool-pitfalls.md` §Writer canonico — chiarito che il default di `handoff-write` è risolto dalla root dello script (hal_gateway); nuova regola workspace consumer: sempre `--out product/state/handoff-<kind>.json`; evidenza shadow copy stale 2026-10-26/28 (sessione brainbeez /todo+/graph) [sync:safe]

## [1.12.0] - 2026-10-26

### Changed

- Comandi canonici `cycle.md`/`graph.md` @ 1.0.1: bullet appresi da /learn 2026-10-25 (condizione STOP; celle `work-graph.md` senza pipe grezzi) spostati dal wrapper al canonico, frontmatter `version:` corretta — la rigenerazione dei wrapper via `link-workspace-skills.sh` ora è idempotente [sync:safe]
- `scripts/agent-todo.py flush`: guardia esplicita con `RuntimeError` se la sezione `[Unreleased]` manca dopo l'inserimento [sync:safe]
- Skill `learn` 1.4.0 → 1.5.0: nuovo reference `learn/references/tool-pitfalls.md` (pitfall tool Zed validati in ≥2 sessioni) [sync:safe]

## [1.11.0] - 2026-10-24

### Changed

- Voce retroattiva (commit `3ddc96f`): rimozione dei campi modello preferito dal frontmatter di tutti gli agenti, con bump di versione coordinati [sync:safe]

## [1.10.1] - 2026-10-21

### Added

- Protocollo Token Budget (L0): 13 strategie per ridurre l'output token senza perdere informazioni o qualità. Riferimento: [references/token-budget.md](references/token-budget.md).
- Modulo telemetria `scripts/token_budget.py`: traccia tokens in/out, chiamate System1 vs System2, file letti, diff size, violazioni regole. Output JSONL in `events/token-budget.jsonl`.
- Regole globali di budget: max 500 token output/sessione, lazy-load per file >100 righe, attachment filtering per liste lunghe, skip preamble enforced.
- `scripts/context_compress.py`: compressione semantic-aware per skill/instruction file (classifica per tipo di contenuto, regole deterministiche per livello, deduplicazione cross-file, stima token, validazione marker comportamentali); derivato da vidanov/context-compress. Test in `tests/test_context_compress.py` (24 test).
- `token_budget.py`: nuovi eventi telemetrici `skill_compress` e `dedup_found` per tracciare risparmio da compressione e deduplicazione skill files.
- Riferimento `references/token-budget.md`: strategie 14-17 integrate (semantic compression, dedup, stats, validation).

## [1.8.7] - 2026-10-21

### Fixed

- `scripts/agent-todo.py flush`: rimuove le voci `[x]` insieme alle loro sotto-voci (prima restavano orfane sotto la voce precedente) e scrive nel CHANGELOG in formato Keep a Changelog: sezione dal tag (`#bug` → Fixed, `#feature` → Added, altri → Changed), `### Added/Changed/Fixed/Removed` di «Già fatto» rispettati, tag e priorità tolti, righe `Esito:` accodate al titolo, deduplica e ordine standard delle sezioni. Test in `tests/test_agent_todo.py`.

## [1.8.6] - 2026-10-20

### Changed

- Aggiornati i path di esempio da `.cursor/` a `.agents/` in `references/agent-versioning.md` e `references/extension-scaffold.md`; allineato l'ordine di lookup product in `AGENT-PROTOCOL.md` (`.claude/product/` → `product/`). Versioni dei tre documenti: 1.0.1.

## [1.8.5] - 2026-10-16

### Added

- Coding Standards: added `references/coding-standards.md` for HAL agents.
- Python: promoted `datetime.UTC` and `# noqa` patterns for silent failures.

## [1.8.0] - 2026-10-02

### Added

- Ottimizzazioni avanzate di System 1 (Laya): caching in-memory `@lru_cache` (maxsize=128) e HTTP session pooling persistente (`requests.Session`) in `laya_service.py` [sync:safe]

## [1.7.1] - 2026-10-02

### Added

- Layer cognitivo System 1 (Laya) in `a-agentzero`: definizione formale del protocollo di routing globale (`router.py routing` / `triage`), pre-filtro (`noul`) e scoring euristico (`score`) obbligatori prima di invocare il ragionamento System 2 [sync:safe]

## [1.7.0] - 2026-10-02

### Added

- Zed editor integration: workspace settings (`.zed/settings.json`), automatic prompt mapping (`.zed/prompts/`), and command-to-skill packaging in `.agents/skills/` for seamless multi-editor support (Cursor ⇄ Zed) [sync:safe]
- Automatic frontmatter stripping for Zed prompts and skills via `agents/scripts/link-workspace-skills.sh` [sync:safe]

## [1.6.15] - 2026-09-18

### Changed

- L0 `/graph` `/slice` `/cycle` `/todo`: lean brief via `harness-prompt-builder` + `handoff-*.json` [sync:safe]

### Added

- Appreso da sessione: selezione modelli OrcaRouter (costo a parità; no image-gen come LLM) in agent-versioning [sync:safe]
- Comandi L0: frontmatter `model` + `model-fallback: cursor-default` (OrcaRouter; fallback Cursor default) [sync:safe]
- Comando L0 `/todo` (Mappa residui → competenza a-harness `todo`; modello `deepseek-v4-flash-free`) [sync:safe]
- Comandi L0 `/slice`, `/cycle`, `/graph` (→ a-harness; modello `deepseek-v4-flash`) [sync:safe]

## [1.6.14] - 2026-09-17

### Added

- Frontmatter `model: orcarouter/deepseek/deepseek-v4-flash-free` + `model-fallback: cursor-default` (OrcaRouter preferred; Cursor default se non raggiungibile) [sync:safe]

## [1.6.13] - 2026-09-15

### Changed

- Appreso da sessione: `/learn !` può scrivere `./ToDo.md` e docs locali (se necessario) — sintesi § Apprendimento [sync:safe]

## [1.6.12] - 2026-09-15

### Changed

- Deleghe: `a-b2b` = facade B2B; canone orchestra in `a-product` § Profilo B2B [sync:review]

## [1.6.11] - 2026-09-15

### Added

- Registry L1 `a-product` (orchestratore peer multi-step); Deleghe + agents + PROTOCOL [sync:safe]

## [1.6.10] - 2026-09-15

### Changed

- Appreso da sessione: Reason why in description + regole di ingaggio subagent [sync:safe]

## [1.6.9] - 2026-09-15

### Added

- Appreso da sessione: Comunicazione all'utente — scelte e ragionamenti in italiano chiaro, gergo tecnico minimo (prose verso l'umano) [sync:safe]

## [1.6.8] - 2026-09-15

### Added

- Appreso da sessione: mappa residui permanente → `./ToDo.md` in root repo (≠ progress append-only) [sync:safe]

## [1.6.7] - 2026-09-15

### Changed

- Appreso da sessione: manutenzione registry → allineare § Deleghe + `agents/a-agentzero.md` nello stesso slice; no PageSpeed su L1 seozoom [sync:safe]

## [1.6.6] - 2026-09-15

### Changed

- Deleghe L1 complete (13) + CWV/PageSpeed solo L2; companion `agents/a-agentzero.md` tabella/scaffold/perimetro allineati [sync:safe]
- Description L0: reason-why esplicita (protocollo/sync/sicurezza condivisi) [sync:safe]

## [1.6.5] - 2026-09-15

### Changed

- Appreso/ottimizza: registry L1 completo + legacy po/harness/uiux/enrichment [sync:safe]

## [1.6.4] - 2026-09-08

### Changed

- Scaffold § Git: commit staged-only quando UI elenca file ma index vuoto (lista autoritativa + `-f` se gitignored) [sync:safe]

## [1.6.3] - 2026-08-17

### Changed

- Scaffold: sezione Git per tracciare skill L2 (`git add -f`) quando `.cursor/` è in `.gitignore` [sync:safe]

## [1.6.2] - 2026-08-15

### Changed

- Appreso da sessione: `l1-from-proto` — CC BY-NC-SA / non-commercial = distillazione + attribution only, no redistribuzione pack [sync:safe]

## [1.6.1] - 2026-08-15

### Added

- Registry L1 `a-po`, `a-enrichment`: discovery file dati + elenco L1 [sync:safe]

## [1.6.0] - 2026-08-13

### Changed

- Registry L1 `a-b2b`: deploy-all, sync-agents, discovery, naming L2 `b2b-*` [sync:safe]

## [1.5.8] - 2026-08-13

### Changed

- `humanizer` L0 1.1.0: principio Never inject (togliere/affilare, non aggiungere voice/fatti) [sync:review]

## [1.5.7] - 2026-08-13

### Changed

- Appreso da sessione: `l1-from-proto` — multi-corpus, no-SPDX, override conflitti, no runtime-upstream; `docs/operativo` Ship L1 (anche bump) con tree sporco [sync:safe]

## [1.5.6] - 2026-08-07

### Added

- L1 `a-charts`: registry deploy/sync, discovery `.cursor/chart-styles/`, deleghe, naming L2 `charts-*` [sync:safe]

## [1.5.5] - 2026-08-03

### Changed

- `tono-di-voce` L0 1.0.2: voice-as-brand (brand file opzionale se skill voice è unica fonte) [sync:review]

## [1.5.4] - 2026-08-03

### Added

- `/sync <`: analisi L2 per generalizzazione L1/L0 (report only); reference `sync/references/l2-generalization.md`; sync skill 1.1.0 [sync:safe]

## [1.5.3] - 2026-08-03

### Added

- Multi-figlio L2: `role:` / `primary:`, risoluzione task→ruolo (AGENT-PROTOCOL) [sync:review]
- Agent companion sync dopo L2←L1 (extension-scaffold, agent-versioning) [sync:review]
- Template deleghe sibling + conflitto voice vs SEO (extension-template) [sync:safe]
- `/learn`: anti-grasso L2, promozione ≥2 progetti, brand vs voice skill [sync:review]
- L0 `tono-di-voce` 1.0.1: brand file vs skill voice [sync:review]

## [1.5.2] - 2026-07-28

### Changed

- Appreso da sessione: `l1-from-proto` esteso a corpus skill esterni (vendor gitignored + pin + update; adozione opt-in; no dump) [sync:safe]

## [1.5.1] - 2026-07-27

### Changed

- Appreso da sessione: `[sync:safe]` su comandi/deploy L0 → L1 allinea solo `extends-version` (nessun delta body) in `agent-versioning.md` + `sync/SKILL.md` [sync:safe]

## [1.5.0] - 2026-07-27

### Added

- Comandi Cursor L0 ereditabili in `commands/` (`version`, `document`, `review`, `improve`, `commit`) pubblicati in `~/.cursor/commands/` via deploy/`/sync !` [sync:safe]
- Report stato comandi L0 (`OK`/`MISSING`/`DRIFT`) e override vs inherit in `scripts/sync-agents.sh` [sync:safe]

## [1.4.1] - 2026-07-27

### Added

- Appreso da sessione: regola authorship L1 da proto-prompt (critica/estensione, non copia) in `references/l1-from-proto.md` [sync:safe]

## [1.4.0] - 2026-07-27

### Added

- Competenza L0 `po-interviewer` (engagement PO, anti-invention, cascade triage discovery) [sync:review]
- Discovery file dati per L1 `a-personas`, `a-jtbd`, `a-gherkin` (path product portabili) [sync:review]
- Target `/learn` per pipeline discovery in `consolidation-targets.md` [sync:safe]

## [1.3.1] - 2026-07-27

### Changed

- Appreso da sessione: file dati ≠ competenze; esempi L1-only SEO + illustrazioni; lista competenze a-illustrator in adozione opt-in [sync:safe]

## [1.3.0] - 2026-07-27

### Added

- Release minor protocollo competenze: L0 opzionale, asset operativi fuori da competencies, riuso cross-dominio on-demand, adozione opt-in (regole già in 1.2.1–1.2.2) [sync:safe]

## [1.2.2] - 2026-07-27

### Changed

- Appreso da sessione: baseline L0 competenze opzionale; asset operativi fuori da competencies; riuso cross-dominio on-demand [sync:safe]

## [1.2.1] - 2026-07-27

### Changed

- Appreso da sessione: adozione competenze opt-in per dominio; sync L1←L0 senza copiare moduli non pertinenti [sync:safe]

## [1.2.0] - 2026-07-27

### Added

- Competenze modulari path-based L0→L1→L2 (`kind: competency`): protocollo, risoluzione runtime, versionamento indipendente per id [sync:review]
- Baseline L0: `competencies/tono-di-voce`, `competencies/humanizer`, `competencies/italiano-locale` [sync:review]
- Script `agent-version.sh competency-chain` per confrontare versioni stessa competenza [sync:safe]
- Note in `agent-versioning.md` e `extension-scaffold.md` su override competenze L2 [sync:review]

## [1.1.2] - 2026-07-16

### Added

- Skill L0 [sync/SKILL.md](sync/SKILL.md): `/sync ?` (report) e `/sync !` (deploy-all + report versioni) [sync:safe]
- Script [scripts/sync-agents.sh](scripts/sync-agents.sh) e comando Cursor `.cursor/commands/sync.md` [sync:safe]
- Deploy: symlink top-level `~/.cursor/skills/sync` (come `learn`) [sync:safe]

## [1.1.1] - 2026-07-13

### Changed

- `learn/references/consolidation-targets.md`: target generici AgentFactory + pattern consumer, rimossi riferimenti a progetti specifici [sync:safe]

## [1.1.0] - 2026-07-13

### Added

- Skill L0 [learn/SKILL.md](learn/SKILL.md): `/learn ?` (riflessione sessione) e `/learn !` (consolidamento in skill) [sync:safe]
- Reference [learn/references/consolidation-targets.md](learn/references/consolidation-targets.md) [sync:safe]
- Sezione Apprendimento da sessione in SKILL.md e AGENT-PROTOCOL.md [sync:safe]

## [1.0.0] - 2026-07-13

### Added

- Versionamento semver e protocollo sync selettivo [sync:safe]
- Campo `version` nel frontmatter L0
- Reference [agent-versioning.md](references/agent-versioning.md) e script `scripts/agent-version.sh` [sync:safe]
- Sezione Versionamento in [AGENT-PROTOCOL.md](AGENT-PROTOCOL.md) [sync:safe]

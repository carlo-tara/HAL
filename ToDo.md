# Mappa residui — HAL

Backlog rinfrescabile (≠ Progress append-only). Igiene: `/todo`.

Convention: ID stabile `HT-nnn` (3 cifre zero-padded, es. `HT-012`; non cambia a seguito di riordino — header e voci uniformati 2026-11-21 da `HT-012`); tag di chiusura — `#cycle` = richiudibile con `/cycle` (slice → red → green → refactor sotto gate Make), `#human` = richiede intervento umano (sessioni reali, step cross-repo, validazione).

Delta 2026-11-09 da `/impersonate karpathy hal_gateway` (lente registry `hal_mcp_tools`): le voci HT-003…HT-007 derivano dai finding della lettura (residuo aperto al 2026-11-16: solo HT-005 e HT-007; HT-003/004/006/008/009 chiuse, esiti in CHANGELOG); praise «modello-usato-come-funzione» (`system1_preflight.TaskContract`/`PreflightDecision`) e «calibrazione da telemetria» (`laya_gate.py`) sono già architetture consolidate, senza voce.

Delta 2026-11-18 (sessione HT-005): consegnati strumento e draft oro — `benchmark/gold_set/HT-005_labeling.xlsx` + generator/exporter (`1822d3e`, fix pyright `8f17fb0`) e `benchmark/gold_set/gold_set.jsonl` con 123 casi draft (`f1cdb94`). Aperta e **chiusa in giornata** `HT-010` (estratto ciclabile: pred runner + regressione + misura) — esito: hit_rate 0.276, banda direct 0.52 → nessuna soglia mossa; aperta `HT-011` `#human` per la decisione di adozione; `HT-005` resta `#human` per il completamento a ~200/famiglia e l'allineamento del vocabolario noul (prime 123 label confermate da umano).

## P0

## P1

## P2

- [ ] `HT-005` — Gold set etichettato per l'eval raw di Laya (~200 casi/famiglia task) `#human` · P2 · System 1 (Laya)
  - STATO 2026-11-18: infrastruttura e strumento consegnati (HT-008 schema+scoring; workbook con 800 id/famiglia e workflow nel foglio Istruzioni, export `benchmark/scripts/gold_set_xlsx_to_jsonl.py`). Draft versionato in `benchmark/gold_set/gold_set.jsonl`: 123 casi validati (choice 31, routing 32, score 30, noul 30) con label **confermate da umano il 2026-11-18** (`f1cdb94`). Residuo umano: (a) confermare/rettificare le 123 label — **FATTO 2026-11-18** (conferma in sessione Zed; note del workbook aggiornate a «confermata»), (b) redigere i casi mancanti fino a ~200/famiglia, re-esportando dopo ogni sessione di etichettatura. La parte automatizzata dell'acceptance è estratta in `HT-010` (sull'orma dell'estratto `HT-008`).
  - Perché utile: l'accuracy ~96,5% del gate è misurata su **traffico di produzione** (8k chiamate, telemetria margini), non su casi con risposta nota: è calibrazione della soglia, non eval del modello. Un gold set rende l'eval di Laya una regressione riproducibile (benchmark, non impressione) ed è la baseline che il reject di `/impersonate karpathy` chiede («feature AI senza baseline»).
  - Acceptance: set versionato (choice/routing/score/noul, ~200 casi con label **confermate da umano**) + script di scoring in `benchmark/` (già consegnato, HT-008); il gate e le soglie di `laya_gate.py` ricalibrati sul set e la run di regressione agganciata a una make target esistente — estratti in `HT-010`.
  - Esito (2026-11-18, conferma umano): 123 casi confermati e misurati dal primo run HT-010. Residuo: estendere il set verso ~200/famiglia e **allineare il vocabolario noul** (le label dell'oro usano {routing, choice, score, astensione}, lo spazio di risposta del servizio è testo normalizzato → 0/30 sistematico, difetto dello strumento non del modello); la parte gate si decide con `HT-011` (la misura ora esiste).

- [ ] `HT-011` — Adozione delle soglie System 1 proposte da `HT-010` (ricalibrazione `laya_gate` + binding allineate) `#human` · P2 · System 1 (Laya)
  - Perché utile: il set draft (`benchmark/gold_set/gold_set.jsonl`, 123 casi) non era mai stato misurato contro il modello: HT-010 ha colmato il vuoto e prodotto la misura; ora serve decidere se e come muovere le soglie — decisione umana perché il dato al draft è ambiguo (debolezza del modello vs label non verificate).
  - Acceptance: rieseguire il runner sul set esteso; con n≥150 decision-family rivalutare la curva margin→accuracy; se una soglia regge, bump `FAST_MARGIN` (e coerenza con `ROUTE_FAST`) via `/cycle`, con guardia che le tre binding restino allineate; altrimenti documentare N/A e chiudere con esito negativo dichiarato (precedent HT-003). Campionare a mano 10 miss ad alto margine (es. c001: regola AGENTS «/sync ? prima di /sync !» violata con margin 0.85) per distinguere errore-modello da errore-label.

- [ ] `HT-007` — Misura dell'effetto assemblaggio locale vs `assemblaggio_finale` via modello `#human` · P2 · Benchmark
  - STATO (2026-11-09, /cycle step-0 CHIUSO): lo switch mancava (verificato sul canonico) — ora c'è: `BENCHMARK_LOCAL_ASSEMBLY=0` nell'ambiente del processo fa ritornare `None` a `assemble_segments_locally` (braccio B), default invariato (braccio A). Lato `hal_system2`: `app/benchmark_workflow.py` + test `tests/test_benchmark_local_assembly_toggle.py` (4 casi, RED 2/694 → suite 696 MAKE_EXIT=0) + voce CHANGELOG `[sync:safe]` — tutto non committato lì (commit responsabilità della sessione parallela HT-004); mirror gateway allineato, suite verde. Smoke braccio B **reale completato**: llama3.2:1b, 1 ok, 2.189 token, 68,4 s, qualità 2/2, trace con `assemblaggio_finale` e ZERO `assemblaggio_locale` (run-dir `events/benchmarks/20261109b_smokeB`). catalogs usati (necessari, il default hs2 è ruotato e il loader vuole esattamente 5 prompt): `--models events/benchmarks/20261109b_models_ht003.json` + `--prompts events/benchmarks/20261109b_prompts_h007.json` (creato: 5 canonici con `estrazione_json` sostituito dal simplified) + `--prompt estrazione_json_semplificato`.
  - Run da lanciare (umano, bracci appaiati, in `hal_system2`): ARM A `setsid python3 -m app.benchmark_models --models events/benchmarks/20261109b_models_ht003.json --model phi3:mini --model llama3.2:3b --prompts events/benchmarks/20261109b_prompts_h007.json --prompt estrazione_json_semplificato --provider ollama --cooldown 180 --timeout 1200 --run-dir events/benchmarks/20261109_h07A --output events/benchmarks/20261109_h07A/results.json`; ARM B identico con `env BENCHMARK_LOCAL_ASSEMBLY=0` e run-dir `..._h07B`; poi `compare_tokens.py` A↔B, riga in `history/` README (+ delta token/tempi/qualità, `finish_reason` attesi: A `local_assembly` vs B `stop`/assemblaggio_finale).
  - Perché utile: run `20261023_8` ha **confermato** l'assemblaggio locale su phi3 (`finish_reason: local_assembly`, qualità 2/2) ma il README dichiara che «l'effetto dell'assemblaggio locale resta da misurare»: oggi è un meccanismo verificato, non un guadagno misurato (token, qualità, tempi vs copia via modello).
  - Acceptance: run dedicata con `estrazione_json_semplificato` a bracci appaiati (gate-forzato locale vs gate-forzato modello) su ≥2 modelli; riga delta nel `history/` + `compare_tokens.py`; se il delta è ≈0, documentare N/A e chiudere con esito negativo dichiarato.


- [ ] `HT-016` — Push dei 4 fence consumer HT-014 pendenti e remote gDrive_ops da correggere `#human` · P2 · #infra
  - Perché utile: il fence a-agentzero 1.13.15 è committato in tutti i 16 consumer git, ma 4 push restano pendenti: brainbeez (commit parallelo 44069e7 sopra il fence 23b286c), InnerCircle (6 commit altrui in coda a 52cf926), liberating.it (1 commit altrui in coda a 3dced2a) — usciranno con le push dei rispettivi proprietari, mai pubblicarli al posto loro; gDrive_ops: remote `carlo/gDrive_ops` non trovato su GitHub (il fence 483d869 è pushabile solo dopo `git remote set-url origin <url-corretto>`). Finché le push non avvengono i fence non sono visibili dagli origin.
  - Acceptance: ramo remoto dei 4 repo contenente il commit fence (verifica `ls-remote` == HEAD locale, non `@{u}`); gDrive_ops con remote corretto e pushato. Ref: CHANGELOG root `[Unreleased]` ESITO HT-014 (702aeb6).
  - Aggiornamento 2026-11-22 (da HT-018): 3 dei 4 push sono atterrati e verificati via `ls-remote` — brainbeez `fcb5d59`, InnerCircle `973ab45`, liberating.it `3733686` (fence `a-agentzero 1.17.1`, `ahead=0`/`behind=0`). Resta solo il remote gDrive_ops: `master` senza upstream e AGENTS.md symlink a `/var/www/hal_gateway/AGENTS.md`, quindi il blob in HEAD è il path testuale e non c'è fence consumer da pushare.





- [ ] `HT-023` — Certificare (o potare) i Terms non certificati dei datasource `demo` e `knowledge` del side-car Auto Ontology `#human` · P2 · #knowledge
  - Perché utile: `check_readiness` riporta `demo` 11 terms / **0 certificati** e `knowledge` 26 terms / **0 certificati**, con la nota «answers will cite draft Terms until a person certifies them»: le risposte su quei due datasource citano bozze non validate da umano. `railway_prod` è invece 16/16 certificati (+ 10 SQL attributes e, dal 2026-11-22, 6 example queries) — la certificazione è quindi l'unico differenziale che separa un datasource affidabile da uno che non lo è.
  - Acceptance: per `demo` e `knowledge`, decisione umana registrata per ciascun Term — certificato, riscritto o rimosso — con `check_readiness` che riporta `certified == total` oppure la rimozione del datasource dallo store; la certificazione resta atto umano (nessun bump automatico da parte dell'agente). Ref: `docs/29_auto_ontology_semantic_layer.md` §6 AO-2, pin `agents/a-knowledge/references/auto-ontology-source.md`.

- [ ] `HT-024` — Voci L2 da inserire nei 4 consumer con `ToDo.md` occupato da lavoro parallelo `#sync` · P2 · #infra
  - Perché utile: i due `[sync:safe]` del canonico (`3ce3c3a` → a-agentzero 1.17.1 e `ec1876d` → 1.17.2, HT-025) lasciano 22 L2 consumer indietro; 10 sono già registrate nei ToDo di 7 repo (hal_mcp_tools, hal_mcp_docs, hal_translate, semidifocusing, brainbeez, liberating.it con commit pushati, pickwaise non-git) e corrette ai target correnti. Le 12 di `hal_seo` (1), `hal_tts` (1), `WTP_App` (5) e `InnerCircle` (5) sono state saltate perché il loro `ToDo.md` era sporco di sessione parallela: committarlo avrebbe assorbito lavoro altrui (il caso reale è `hal_mcp_docs` `5d04050`, ora mitigazione canonica in `commands/commit.md` §Isolamento index punto 5, 1.4.0). Senza questa voce restano invisibili nel report `/sync`.
  - Acceptance: una voce per repo nei rispettivi `ToDo.md` con i target correnti (a-harness **1.11.6**, a-b2b **2.3.11**, a-copywriter **1.7.11**, a-design **1.2.12**, a-seozoom **1.10.13**; canonico `ec1876d`), inserita solo con `ToDo.md` pulito — ricontrollare `git status --porcelain -- ToDo.md` immediatamente prima del commit, non al censimento; in alternativa `agent-worktree.sh` per non condividere il checkout. Verifica finale: `sync_report` con `projects` → 0 catene L2 STALE.


## Già fatto

_(Buffer pre-flush in formato Keep a Changelog: sotto `### Added`, `### Changed`, `### Fixed` o `### Removed`; `/todo` lo svuota nel CHANGELOG.)_

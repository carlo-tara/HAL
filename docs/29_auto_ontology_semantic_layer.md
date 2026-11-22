# PRD — Auto Ontology side-car nell'ecosistema HAL (Livelli A+C)

Stato: **attivo — AO-1 + AO-1.1 consegnate; AO-2 smoke completato 2026-11-22** (run_sql 316.8/4 = match README, example query salvata, entry revert `answer` con riavvio pendente) · Ref: `HT-013`; analisi e verifica documentazione 2026-11-20 su [`gogoymh/auto-ontology-mcp`](https://github.com/gogoymh/auto-ontology-mcp) @ `0fb5ecf` (v0.6.1, Apache-2.0) · Slice: [`docs/slices/AO1-sidecar-boundary.md`](slices/AO1-sidecar-boundary.md)

## 1. Problema (evidenze)

- Text-to-SQL fallisce in silenzio e il KB testuale di `a-knowledge` non ha un posto dove mettere **fatti tipizzati con provenienza citabile** (numeri che si possono sommare, non aritmetica su prosa). L'analisi del repo upstream mostra che il suo design è _gemello_ del principio HAL (regola ferrea `a-knowledge` §Principio): server deterministico, lavoro linguistico al modello, artefatti fuori contesto.
- Il cluster `#token-shrink` non copre il dominio _database business_: `hal_mcp_docs` possiede documenti (chunk, manifest), non schema/ontologia/validazione SQL. Un modello che scrive SQL su schemi non presidiati paga il costo degli errori a valle (re-run, contesti infetti da numeri sbagliati).
- Rischio speculare: registrare il server senza regole di ingaggio aggiunge **52k caratteri di tool definitions a ogni richiesta** e apre una seconda KB parallela (conflitto di routing con `a-knowledge`/`hal_mcp_docs`).

## 2. Obiettivo e KPI

Formalizzare l'ingresso di `auto-ontology-mcp` come **MCP server side-car parsimonioso** (Livello A) e **chiudere la sovrapposizione con il retrieval documentale tramite confini documentati** (Livello C). Livello B (vendor + facade `ontology_*` dentro `hal_mcp_tools`) è deliberatamente **rinviato** (Non goal §5).

- **KPI-1 (footprint contesto)** — misura deterministica, non soglia indovinata: script nel clone pinnato (pattern `tests/test_context.py`: `build_server` con `Settings` da env `AUTO_ONTOLOGY_TOOLSETS=answer` + Client `list_tools()`) che serializza la risposta e stampa **char count + insieme dei nomi tool** su `logs/ao-sidecar/kpi1-<sha>.txt` (mai in contesto). Il dato upstream (≈52k full → ≈12k answer) è _riferimento_, non acceptance: **acceptance = baseline registrato nel pin file a ogni bump**, con gate **prima sull'insieme dei nomi** (un tool nuovo nel set `answer` è cambiamento strutturale) e poi sui caratteri (la deriva numerica si documenta, non si accetta in silenzio).
- **KPI-2 (zero collisione di routing)**: per ogni famiglia di domanda — «capitolo di un libro», «fatto sommativo con fonte», «query su DB business», «percorso di join» — la **tabella canonica** in [`docs/bounded-contexts.md`](bounded-contexts.md) §«Routing delle domande» designa **esattamente un** destinatario. Guardia: contratto `product/contracts/check-ontology-bc-boundary.sh` (deterministica, exit reale; assert sugli ancoraggi `chapter_route`/`validate_sql`/`find_join_path`/`get_source`); GREEN osservato all'Act 2026-11-20.
- KPI-3 (superficie di scrittura nulla nel workspace): dopo lo smoke, nessuna directory/file creati fuori da `~/.auto-ontology-mcp` (guardia su `git status` del workspace HAL invariato rispetto al pre-smoke); `AUTO_ONTOLOGY_ALLOW_DATASOURCE_TOOLS=0` di default (datasource solo da CLI).
- Non regressione: gate di `hal_mcp_docs`/`hal_mcp_tools`/`hal_system1` e pipeline `a-knowledge` **inalterati** (il side-car non importa codice HAL e non è importato).

## 3. Utenti

- **Agente Zed (System 2)**: domande su DB business (glossario HAL: `product/`, `benchmark/`) e su fatti personali/di progetto con provenienza; scelte discrezionali pre-via Laya (System 1) già regolate da AGENTS.md.
- **`a-knowledge` (L1)**: consuma il confine (§4) per delegare al side-car ciò che richiede record tipizzati/SQL invece di capitoli.
- **Owner umano**: registra il side-car in Zed (config, step `#human`), decide l'apertura dei toolset `model`/`knowledge`/`share` on-demand.

## 4. Scope MVP — Livello A + C

### A. Side-car MCP in Zed (config, zero codice HAL)

Voce `context_servers` in `~/.config/zed/settings.json` (pattern esistente `hal-mcp-tools`/`systemone`; backup one-shot `settings.json.bak-<slug>`, dry-run prima dell'applicazione come `install_zed.py` di `hal_mcp_tools`):

```jsonc
"auto-ontology": {
  "command": "/home/carlo/.local/bin/uv",
  "args": ["--directory", "/home/carlo/auto-ontology-mcp", "run", "auto-ontology-mcp"],
  "env": {
    "AUTO_ONTOLOGY_TOOLSETS": "answer",              // typo qui = ValueError al boot (config.py), non fallback ad all
    "AUTO_ONTOLOGY_ALLOW_DATASOURCE_TOOLS": "0",     // datasource solo da CLI (credenziali in chiaro in ontology.db)
    "AUTO_ONTOLOGY_MAX_ROWS": "100"                  // CEILING assoluto (config di default 500; il default per-chiamata di run_sql è 100)
  },
  "enabled": false,                                   // true solo dopo i passi 1-4 del rituale AO-2.1 (§6)
  "timeout": 60
}
```

Decisioni: clone pinnato con SHA (non `uvx --from git+…`: la cache uvx silenzia gli aggiornamenti; `uvx --refresh` resta escape-hatch non registrato, quindi fuori policy) in `~/auto-ontology-mcp` — **deviazione registrata**: il PRD prevedeva `/opt/auto-ontology-mcp`, ma il 2026-11-20 `sudo` non era interattivo in sessione agente; proprietà invariate (pin, fuori workspace, lock a monte), ripristino documentato nel pin file; toolset `answer` di default — **scelta anche di igiene di routing, non solo token**: con `answer` l'handshake omette le istruzioni modeling/knowledge (§7, §9) — `model`/`knowledge`/`share` solo on-demand (progressive disclosure in stile HAL); store fuori dal workspace (`~/.auto-ontology-mcp`, permessi §7); `AUTO_ONTOLOGY_VAULT` **non impostato di default**: vault = `~/.auto-ontology-mcp/wiki/knowledge`, quindi backup a directory singola e zero scritture sul vault Obsidian reale — il puntamento al vault esistente è opt-in esplicito.

### C. Confine con il retrieval documentale (documentazione canonica)

Il side-car apre un **nuovo bounded context** nella context map (`docs/bounded-contexts.md`), non una estensione di Retrieval:

| Context                         | Path modulo                                                                                                                                                   | Responsabilità                                                                                                                                                                                  | Integrazioni                                                                                                               |
| ------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| Knowledge & Ontology (side-car) | `auto-ontology-mcp` esterno, clone pinnato `~/auto-ontology-mcp` (SHA + `version` + KPI nel pin file `agents/a-knowledge/references/auto-ontology-source.md`) | layer semantico su DB (scan, profiling, inferenza chiavi, `validate_sql`, `run_sql` read-only) e KB a fatti tipizzati con provenienza (records/concepts/passages/sources, FTS5, vault Obsidian) | ← Agente via MCP `tools/call`; ← Benchmark (misure toolset/footprint); → `~/.auto-ontology-mcp` (unico punto di scrittura) |

**Tabella di routing delle domande — fonte unica canonica in [`docs/bounded-contexts.md`](bounded-contexts.md) §«Routing delle domande»** (righe: capitolo→`chapter_route`/`doc_search`; fatto sommativo→`run_sql`+`get_source`; DB business→`check_answerable`→`validate_sql`→`run_sql`; collegabilità→`find_join_path`). Il PRD **linka, non duplica**; `a-knowledge` linkerà ad AO-1.1 — stessa disciplina di una fonte sola.

Regole di confinamento: il chunk-store di `hal_mcp_docs` **non** accoglie record tipizzati; il knowledge store del side-car **non** indicizza capitoli di libri (solo passages estratti dal modello); originals: vault **unico e default-interno** (`AUTO_ONTOLOGY_VAULT` unset → dentro `~/.auto-ontology-mcp`; opt-in per il vault reale, mai duplicato).

## 5. Non goals

- **Livello B** (clone in `agents/vendor/` + facade `ontology_*` a driver-subprocess dentro `hal_mcp_tools`, esito ≤4000 char): rinviato; il core stdlib-only di `hal_mcp_tools` non deve fondersi con FastMCP/SQLAlchemy/sqlglot. Precedente per deroga: `playwright_driver.py`/`analytics_duckdb_driver.py` — si applica solo se la misura di KPI-1 rende il side-car diretto troppo pesante.
- Nessuna modifica a `gateway_core.py`, `laya_*`, `router.py`, `agents/scripts/*`; nessun import incrociato HAL↔side-car (vincolo NFR §5 del cluster `#token-shrink` resta intatto).
- Niente serving HTTP/tunnel, niente embedding/reranking (coerente con CPU-first HAL), niente multi-tenancy.
- Nessuna migrazione del corpus `a-knowledge` nel KB del side-car.

## 6. Roadmap

- **AO-0 (done, 2026-11-20)**: analisi repo, consultazione System 1 (§8), PRD + slice + contratto di guardia (RED osservato in plan: 3 FAIL).
- **AO-1 (done, 2026-11-20)**: Livello C — Act su `docs/bounded-contexts.md` (riga BC + §«Routing delle domande»); guardia `check-ontology-bc-boundary.sh` **GREEN**.
- **AO-1.1 (done, 2026-11-20)**: riga di delega in `agents/a-knowledge/SKILL.md` §Deleghe — **link** alla tabella canonica, non copia (`a-knowledge` 1.1.10→1.2.0, CHANGELOG dedicato; mirror via symlink, nessun rigenerato; unico figlio «template» placeholder escluso dallo scan catene; STALE padre-figlio preesistente non ri-pinnato perché pinnerebbe WIP non commesso della sessione parallela). Guardia estesa con assert 5 (delega promossa), GREEN.
- **AO-2 (done 2026-11-22)**: side-car installato e smoke completato in sessione Zed viva. #1 readiness PASS (demo catalogato, knowledge ready, ALLOW_DATASOURCE_TOOLS enforced, vault interno). #2 Plan B (modeling completo): entry temporaneamente `answer,model` → review join (self-ref manager_id accept; sales_rep_id add con containment 100%; delivery_city is_default) → 11/11 tabelle modellate (Terms draft) → SQL attribute `Revenue` created+validated → `check_answerable`/`get_query_context`/`validate_sql`/`run_sql` → **316.8 / 4 order line = match README esatto** → `save_example_query`. Entry revertata `answer` (backup -c, riavvio per applicare). Nota governance: la coverage entity di `check_answerable` non indicizza i nomi degli SQL attribute («revenue» resta not_covered benché l'attributo esista e sia trovabile da `search_ontology` score 1.0) — scelta deliberata: colonna «Line Total» fedele + measure «Revenue» governata, anziché il rename che nel README rendeva covered; certificazione Terms/measure = decisione umana. Rituale bump = AO-2.1 (già scritto nel pin file).
- **AO-2.1 — rituale di aggiornamento (ricorrente: alla prima installazione e a ogni bump)**:
  1. `git fetch --tags --prune` nel clone; `git log PIN..origin/main -- pyproject.toml` → i commit che toccano `version` **sono** le release (niente tag né release GitHub; CONTRIBUTING reg. 5 + squash-merge a frase = log di `main` che è changelog).
  2. `git diff --stat PIN..NEW`; grep dei **3 invarianti CONTRIBUTING**: `run_sql` non scrive, nessun invio dati fuori dal client, nessuna dipendenza che richieda API key.
  3. Snapshot **logici** prima del bump (oltre al `cp -a ~/.auto-ontology-mcp`): `export NAME -o ontology.yaml` per ogni datasource + `export-wiki` (KB → pagine).
  4. Rehearsal di migrazione su **copia** (`AUTO_ONTOLOGY_HOME=/tmp/ao-dry`) + `uv run pytest` sul nuovo checkout (verde richiesto; copre anche `test_existing_store_is_upgraded` e `test_toolsets_limit_tools_and_instructions`).
  5. Bump: `git pull --ff-only` + `uv sync` (lock a monte) + **re-misura KPI-1** (insieme nomi prima, char dopo).
  6. Nuova riga nel **pin file** `agents/a-knowledge/references/auto-ontology-source.md` (blocco `PIN:START/END`, stile vendor HAL): `version`, SHA, subject PR, delta nomi tool/char KPI-1.
  7. Regressione → revert allo SHA del pin precedente (il pin file è il registro: nessuna cartella in più sul workspace).
- **AO-2.2 (done 2026-11-22)**: ricetta d'installazione **codificata in `/bootstrap`** — sezione §Bootstrap di `agents/project-skills/harness-hal` (delta L2 letto dal profilo `standard`, bump 1.0.8→1.1.0): pin file come fonte unica, gate sync→pytest→KPI-1, permessi 700/600, Zed con backup e re-read sequenziale, **cadenza mining** (`suggest_sql_attributes` a soglia `query_log` ≥10 o a bump, `save_example_query`, certificazione umana) e rituale AO-2.1. Nessuno script installatore: `/bootstrap` è procedura documentata (a-agentzero SKILL, passo 3 «harness delta»), e il runtime resta fuori dal bundle. Correzione dell'owner del 2026-11-22: l'installazione era avvenuta a mano in chat — il *gesto* resta valido su questa macchina, ma la *ripetibilità* ora vive nel canone.

- **AO-3 (condizionato)**: Livello B (vendor + facade `ontology_*`) solo se KPI-1/KPI-2 del side-car diretto non reggono; in tal caso `LICENSE`+`NOTICE` preservati e attribuzione NVIDIA nel pin file (opera derivata da NVIDIA Auto Ontology, §9).

## 7. Requisiti non funzionali e sicurezza

- Dipendenze isolate: `uv` (presente) + `uv run` nel clone pinnato; runtime HAL **non** tocca pip (fastmcp/sqlalchemy/sqlglot restano fuori dal requirements del gateway).
- `ontology.db` salva gli URL dei datasource **in chiaro** → policy HAL: account DB **read-only** obbligatorio, credenziali mai nei prompt del modello, `AUTO_ONTOLOGY_ALLOW_DATASOURCE_TOOLS=0`; il guard SQL del server (3 livelli) è l'ultima linea, non l'unica.
- Back-up = copia di `~/.auto-ontology-mcp` (single-user; nessun watchdog: la re-ingestione di una fonte cambiata è un lavoro del modello, documentare nel flusso).
- Il side-car invia il proprio workflow come MCP instructions all'handshake, **potate per toolset** (`guidance.py: server_instructions(toolsets)`): con `answer` escono anche le istruzioni modeling/knowledge, quindi la leva sul routing si riduce alla fonte; i vincoli della tabella canonica §«Routing delle domande» prevalgono comunque — l'agente non usa `run_sql` dove serve `chapter_route` e viceversa.
- Scan su DB di produzione: `AUTO_ONTOLOGY_SCAN_TABLES`/`--tables` **sempre con filtro** (glob case-insensitive, `!` per escludere; precedenza: argomento > saved > env > tutti) — senza, lo scan di migliaia di tabelle «takes hours» (README) e blocca il tool MCP.
- Permessi filesystem: `chmod 700 ~/.auto-ontology-mcp`, `600 ontology.db` (URL datasource in chiaro), `AUTO_ONTOLOGY_STORE` su path protetto/crittato su macchine condivise; `AUTO_ONTOLOGY_ALLOW_DATASOURCE_TOOLS=0` già nello snippet.
- Trasporto: **stdio** (Zed). `serve --transport http` = **N/A documentato** (HAL non espone la porta; per il caso futuro: token obbligatorio fuori localhost con anti DNS-rebinding e `hmac.compare_digest`, verificato in `http_auth.py`).

## 8. Decisioni e consultazioni System 1 (regola AGENTS.md)

| Bivio                                       | Esito Laya (choice CLI)                       | Decisione System 2                                                                                                                                                                                                                                                         |
| ------------------------------------------- | --------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Contesto che possiede il layer semantico+KB | head shortlist: «Agent Platform (solo skill)» | **Override**: il side-car è un _runtime esterno_ consumato da più BC (a-knowledge, benchmark), non una skill del bundle → nuovo BC «Knowledge & Ontology» (§4). Il segnale S1 è coerente solo finché si legge «nessun codice HAL dentro agents/»: confermato dal Non-goal. |
| Priorità                                    | «P2 backlog»                                  | **Accettata**: nessun blocco in corso; il valore è evitare la collisione (KPI-2) prima che il side-car sia attivo.                                                                                                                                                         |

Nota di calibrazione: i due verdetti S1 vivono in `logs/`/`route-events` dove il binding li registra; il voto di outcome (correct/incorrect) va dato al closing di AO-2 (la misura reale è l'evidenza).

**Post-riesame 2026-11-20 (documentazione intera verificata)**: due correzioni di procedura recepite nel PRD — (a) il pin anchor non è uno SHA qualsiasi ma il **commit di bump `version`** (§6 AO-2.1-1); (b) il vault è **default-interno, opt-in-esterno** (§4); (c) KPI-1 da soglia a **misura con baseline** (§2). Tutte ancorate ai fatti §9.

## 9. Fatti verificati sulla documentazione intera (2026-11-20)

Ispezione: README, CONTRIBUTING, NOTICE, `config.py`, `http_auth.py`, `server.py`/`guidance.py` (TOOL_GROUPS + instructions), test. Nota: in upstream `docs/` contiene **solo `assets/`** (banner) — non esiste altra documentazione fuori da quella letta.

| Fatto                                                                                                                                         | Fonte                                                                           | Uso nella proposta                                                                                                                    |
| --------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| Nessun tag né release                                                                                                                         | `list_tags`/`list_releases` = `[]`                                              | pin per SHA + release-anchor `version` (§6 AO-2.1-1)                                                                                  |
| «Leave the version alone… il maintainer bumps `pyproject.toml`, `__init__.py` e `uv.lock`»; squash-merge con titolo a frase                   | CONTRIBUTING §Pull requests (reg. 5, cap. finale)                               | commit-bump = release; log di `main` = changelog                                                                                      |
| `_toolsets`: `ValueError` su toolset sconosciuto; `answer` sempre incluso                                                                     | `config.py`                                                                     | snippet Zed: typo = boot rifiutato, **non** fallback silenzioso a `all` (§7)                                                          |
| Con `answer`: ~52k→~12k char **e** istruzioni modeling/knowledge fuori dall'handshake                                                         | README §Tools; `guidance.py`                                                    | KPI-1 come misura (§2); meno collisione di routing (§7)                                                                               |
| Migrazione store «upgraded the first time the new version opens it» + test dedicato                                                           | README §Quick start; `tests/test_textindex.py::test_existing_store_is_upgraded` | AO-2.1-3/-4: snapshot logici + rehearsal su copia prima del bump                                                                      |
| Guard HTTP: `hmac.compare_digest`; aperti solo `/health` e `/.well-known/`; rifiuto non-localhost senza token (anti DNS-rebinding)            | `http_auth.py` + README §Safety                                                 | §7: HTTP N/A documentato (stdio-only)                                                                                                 |
| Invarianti vincolanti per le PR: `run_sql` non scrive; nessun invio dati fuori dal client; nessuna dipendenza con API key                     | CONTRIBUTING §Safety rules                                                      | AO-2.1-2: grep a ogni bump                                                                                                            |
| NOTICE: derivata da NVIDIA Auto Ontology (Apache-2.0) con file adattati elencati (`guidance`/`profiling`/`sqlcheck`/`validation`/`structure`) | NOTICE                                                                          | AO-3: LICENSE+NOTICE preservati + attribuzione nel pin file; regole `guidance.py` = proto da distillare, non dump (regola vendor HAL) |
| `AUTO_ONTOLOGY_MAX_ROWS` = ceiling (default 500; `run_sql` per chiamata 100)                                                                  | `config.py` + README §Safety                                                    | snippet commentato (§4)                                                                                                               |
| `AUTO_ONTOLOGY_VAULT` unset → vault = `~/.auto-ontology-mcp/wiki/knowledge`                                                                   | README §Personal KB; `config.py`                                                | §4: default interno (blast radius zero), opt-in per il vault reale                                                                    |
| Client web (ChatGPT/claude.ai) solo via HTTPS pubblico + tunnel/token                                                                         | README §Quick start                                                             | Non goal confermato (§5): HAL usa stdio, niente tunnel                                                                                |

Regola di verità: `guidance.py` è un **canale d'istruzione**: le regole a monte possono spingere il modello verso i propri tool; per questo la tabella canonica (§«Routing delle domande») è il confine, e il default `answer` ne riduce la superficie (§7).

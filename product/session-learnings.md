# Session Learnings — 2026-10-21

## Apprendimenti catturati

### 1. Tool pitfalls Zed editor

- **Cosa:** `edit_file` fallisce per mismatch di testo esatto; `read_file` con start_line/end_line fallisce con "invalid type: string, expected u32"
- **Evidenza:** Sessione graph-cycle-sync-todo: 10+ tentativi edit_file falliti, fix con `sed` via terminal; letture file con line-number fallback a terminal/sed
- **Stato:** nuovo
- **Ambito:** HAL
- **Destinazione:** docs
- **Target proposto:** `.agents/skills/learn/references/tool-pitfalls.md`

### 2. Gate 3 regressioni root cause

- **Cosa:** Gate 1 `_gateway_skip` sovrascrive `laya_recommended=False` per prompt atomici brevi (<400 char, complexity=="atomic"), causando 4 regressioni test Gate 3
- **Evidenza:** Fix applicato aggiungendo `"explicit_plan": True` ai mock analyze_prompt nei test Gate 3
- **Stato:** risolto in sessione
- **Ambito:** Progetto
- **Destinazione:** ToDo
- **Target proposto:** `./ToDo.md` · P1 · #system1-gating (già chiuso)

### 3. Version sync superseded

- **Cosa:** Problema STALE 1.8.5→1.8.6 risolto da aggiornamenti successivi che hanno portato tutto a 1.10.1
- **Evidenza:** Report `/sync !` mostra tutte le catene L1←L0 allineate a 1.10.1, zero STALE
- **Stato:** risolto in sessione
- **Ambito:** Progetto
- **Destinazione:** ToDo (chiuso come obsolete VPIN/HVPIN)

### 4. Strategy block reduction

- **Cosa:** Rimossa linea disclaimer da `<strategia_system1_laya>` in system1_prompt, risparmio ~29% (~178→127 chars)
- **Evidenza:** Test-driven: 4/4 verdi, zero regressioni G7
- **Stato:** implementato in sessione
- **Ambito:** Progetto
- **Destinazione:** ToDo (chiuso)

### 5. Sync deploy pattern

- **Cosa:** `bash agents/a-agentzero/scripts/sync-agents.sh` senza flag = deploy completo; con `--dry-run` = solo report
- **Evidenza:** Entrambe le modalità verificate in sessione, output consistente
- **Stato:** già documentato in skill sync
- **Ambito:** HAL
- **Destinazione:** escludi (già in skill)

---

## 2026-10-24 — a-knowledge (sessione)

### HAL

- Nuovo agente L1 `a-knowledge` (Knowledge/Context Engineering): pipeline `check -> extract -> distill -> query` per libri/doc tecnici; estrazione locale CPU-first (0 GPU, 0 token), distillazione una-tantum su modello free/flash, routing System 1 al capitolo minimo (~5k token per domanda). Vedi `agents/a-knowledge/` + `agents/CHANGELOG.md` [sync:safe]
- Topologia HAL: root canonica `/var/www/hal_gateway` (repo `carlo-tara/HAL`); il consumer `hal_system2` espone `agents/` e `.agents/` come symlink verso di essa. Eseguire i gate dalla root canonica (`make -C agents`): gli script basati su `find`/`pwd` logico non attraversano il symlink dal consumer. Il working directory in `harness-agentfactory` L2 (`/var/www/HAL/agents`) e' stale. [sync:review]
- Tooling editor su sotto-albero symlinkato: `write_file`/`create_directory` possono fallire (authorization channel closed); workaround = staging in-project + `cp`/`mv` via terminal. `edit_file` su markdown con tabelle riallinea i pipe (formatter) -> diff gonfiato. [sync:safe]
- Follow-up actionable: script wrapper cost-aware `a-knowledge/scripts/` (extract.py --check + selezione estrattore + routing capitolo); registrazione comandi `/knowledge` L0. [sync:safe]

---

## 2026-10-24 — rimozione modello preferito (sessione)

### HAL

- **Rimozione `model:` da tutti i frontmatter agent.** Eliminato il campo `model: orcarouter/…` dal frontmatter di tutti gli agenti HAL (8 L0/L1, 10 competenze, 2 skill utility sync/learn), di tutti i comandi L0 (9 file) e della documentazione `commands/README.md` (colonna tabella + sezione). Il modello è sempre quello con cui viene chiamato l'agente; non si fissa più un preferred model nei frontmatter. [sync:safe]
- **Versioning coordinato:** bump minor su 21 SKILL.md (`a-agentzero` 1.10→1.11, L1 da 2.2→2.3 / 1.6→1.7 / 1.1→1.2 / 1.7→1.8 / 1.0→1.1 / 1.9→1.10 / 1.3→1.4); allineamento `extends-version` su tutti i 8 L1 al nuovo padre `1.11.0`. Catene pulite, zero STALE. [sync:safe]
- **Pulizia note:** rimosse le righe «Modello preferito» dalle sezioni Notes di `cycle.md`, `graph.md`, `slice.md`, `todo.md`. [sync:safe]

---

## 2026-10-28 — Kimi dynamic tool loading → HAL (sessione)

### Progetto

- Analisi doc Kimi «Dynamically Loaded Tools» (platform.kimi.ai/docs/guide/use-dynamic-tool-loading): tool definition bloat, iniezione dichiarazioni via messaggio `system`+`tools` solo-append (mai `content` nello stesso messaggio), pattern `search_tools`, regole prefix caching (append mai insert, carry-forward dichiarazioni invariate, tool core globali stabili); supporto solo kimi-k3/k3.1-pro. [sync:safe]
- Mapping HAL: L0 = core top-level fisso, L1/L2 = caricamento on-demand, Laya `routing` ≈ `search_tools`. Gap concreto: chiave Cache L1 in `gateway_core.py` ignora le dichiarazioni tool (hash del solo `content`) → falsi hit. Consolidato come 6 voci in `./ToDo.md` (1 P0 `#bug`, 3 P1, 2 P2). [sync:safe]

### HAL

- Pitfall Zed «parametri numerici respinti come stringhe» confermato alla 3ª sessione (`read_file` start/end_line 3×, `terminal timeout_ms` 1× → `sed -n`/omissione); integrata evidenza in `agents/a-agentzero/learn/references/tool-pitfalls.md`, skill `learn` 1.5.1→1.5.2. [sync:safe]
- Fallback `ABSTAIN` di `router.py routing` → classificazione delegata alla tabella Destinazione (System 2): già documentato in tool-pitfalls, riapplicato senza retry. Escluso dalla consolidazione: `list_directory` con path `.` restituisce stringa vuota (osservazione singola, radice non verificata). [sync:safe]

---

## 2026-10-28 — QwenCloud multi-turn → HAL (sessione)

### Progetto

- Analisi doc QwenCloud «Multi-turn conversations» (docs.qwencloud.com/developer-guides/run-and-scale/multi-turn): API stateless con array `messages` lato client; strategie di gestione del contesto (troncamento ultimi N turni, rolling summary a soglia ~70% del contesto, retrieval vettoriale on-demand); thinking model: in history solo `content`, mai `reasoning_content`; `previous_response_id`/Conversations API con item a scadenza 7 giorni, parametri mutuamente esclusivi, `instructions` separate dalla history; context cache automatico su Qwen-Max/Plus/Flash/Coder. [sync:safe]
- Mapping HAL: prefix caching, compattazione (docs/15) e tool append-only già coperti dal delta Kimi; consolidati 5 gap in `./ToDo.md` (2 P1, 3 P2) con riga header «Delta 2026-10-28 da QwenCloud docs»: ContextManager multi-turn, regola `reasoning_content`, system come `instructions`, flag `context_cache`, spike conversazione lato gateway. [sync:safe]

### HAL

- Pitfall Zed `list_directory` con path `.` → stringa vuota promosso da «osservazione singola» a validato in 2 sessioni: ricorrente in questa sessione e verificata per contrasto la radice (nome root `hal_gateway` → ok). Documentato in `tool-pitfalls.md`; skill `learn` 1.5.2→1.5.3. [sync:safe]
- Conferma n. 4 del pitfall «parametri numerici respinti come stringhe» (`read_file` `start_line`/`end_line` 2× → `sed -n`); evidenza rinforzata nella stessa sezione. [sync:safe]
- Nuova regola di scrittura `/learn` in `learn-guidelines.md`: batch ToDo da doc vendor con riga `Delta YYYY-MM-DD da <fonte> (<URL>)` nell'header (validata su sessioni Kimi e QwenCloud). `router.py routing` `ABSTAIN` 2× sulle destinazioni → fallback alla tabella Destinazione (System 2) senza retry, come da protocollo. [sync:safe]

---

## 2026-10-28 — QwenCloud connection pooling → HAL (sessione)

### Progetto

- Analisi doc QwenCloud «Connection reuse and pooling» (docs.qwencloud.com/developer-guides/run-and-scale/connection-pooling): riuso TCP via Session/pool dimensionato sul carico, timeout disaccoppiati (connect ≠ read ≠ pool), retry con exponential backoff, SSL validation, teardown sessioniale, monitoring con target reuse ratio >95% e pool utilization 60–80%; WebSocket/TTS object pooling non applicabile (HAL non usa API realtime), QPS cap già coperto da `LayaCallBudget`.
- Mapping HAL: `laya_service.py` ha già la `_session` persistente (riuso corretto) ma senza `HTTPAdapter` di pool, con `LAYA_TIMEOUT` unico, retry in loop stretto senza attesa, `verify=False` fisso e nessun teardown; gli script skill (a-knowledge `httpx.Client` per chiamata senza close, a-seozoom `requests.post` nudo, illustrator `urlopen` per poll) non riusano le connessioni; pattern corretto già presente in `benchmark/runner/benchmark_models.py`. Consolidati 7 gap in `./ToDo.md` (3 P1, 4 P2) con riga «Delta 2026-10-28 da QwenCloud docs «Connection reuse and pooling»», applicando la regola batch-vendor n. 7.

### HAL

- Conferma n. 5 del pitfall «parametri numerici respinti come stringhe» (`read_file` `start_line`/`end_line` respinto 4× in due tentativi paralleli → `sed -n`); evidenza rinforzata in `tool-pitfalls.md`; skill `learn` 1.5.3→1.5.4. [sync:safe]
- `router.py routing` `ABSTAIN` 3× sulle destinazioni di consolidamento → fallback alla tabella Destinazione (System 2) senza retry, come da protocollo. [sync:safe]
- Osservazione singola, NON consolidata (in attesa di validazione su ≥2 sessioni, stesso protocollo di `list_directory`): `./ToDo.md` è modificato da più sessioni agente in parallelo (durante questa sessione sono comparse le voci «Async task management»/«Streaming output») → un `edit_file` ancorato a una lettura precedente può inserare le voci nella sezione sbagliata (accaduto: 3 voci P1 finite dentro P2, ripristinate con re-anchor); pratica proposta: re-grep `^## ` prima dell'insert e verifica `^## |^- \[ \]` dopo, senza fidarsi delle posizioni lette in sessioni lunghe.

---

## 2026-10-28 — QwenCloud context cache → HAL (sessione)

### Progetto

- Analisi doc QwenCloud «Context cache» (docs.qwencloud.com/developer-guides/run-and-scale/context-cache): tre modalità — explicit (marker `cache_control ephemeral`, max 4/request, 125% creazione / 10% hit, TTL 5 min con reset on hit), implicit (automatica, non disattivabile, 20% on hit), session (header `x-dashscope-session-cache: enable` + `previous_response_id`); vincoli trasversali: prefisso ≥1024 token, lookback ≤20 content block dal marker, cache isolata per account e per modello; tool descriptions cachate col marker; parallel tool calls → fondere i messaggi `tool` same-role; evidenza in `usage.prompt_tokens_details.cached_tokens`/`cache_creation_input_tokens`; rapporti di prezzo non standard per `qwen3.8-flash`/`qwen3.8-max` (variano per regione). [sync:safe]
- Mapping HAL: la Cache L1 (`gateway_core.py`) è exact-match sul contenuto normalizzato = cache di risposta; il context cache provider riusa il prefisso a livello di computazione — strati complementari, non allineare i TTL né scaldare la cache sui batch (Laya sta sotto soglia 1024 token e resta sulla sua `lru_cache`). `normalize_prompt` (lowercase + strip timestamp) è legittimo solo per la chiave Redis: applicato al testo inviato rompe il match byte-per-byte del prefisso lato provider. `SystemTwoEngine` è mock/backend: i punti di integrazione reali sono il contratto dei backend (ordering static-first, marker, merge tool) e i runner benchmark (parsing usage). [sync:safe]
- Consolidati 7 gap in `./ToDo.md` (2 P1, 5 P2) con riga header «Delta 2026-10-28 da QwenCloud docs «Context cache»» + vincoli trasversali in header: ordering static-first, telemetria `cached_tokens`/`cache_creation_input_tokens`, marker explicit a due strati, merge tool same-role, costo refill cache nel failover, prezzi cache effettivi per modello/regione, spike session cache via OrcaRouter. [sync:safe]

### HAL

- Regola `/learn` n. 7 «Batch ToDo da doc vendor» (`learn-guidelines.md`, 1.5.3) convalidata da sessione concorrente: questa sessione ha applicato lo stesso pattern (riga Delta + fonte citata nei «Perché utile») prima della scrittura della regola; nessuna nuova scrittura, regola già presente. Nessun `SKILL.md` toccato da questa invocazione → nessun bump: `learn` è già a 1.5.3 per consolidamento concorrente. [sync:safe]
- `router.py routing` `ABSTAIN` 3× sulle destinazioni → fallback tabella Destinazione (System 2) senza retry, come da protocollo. Pitfall «parametri numerici respinti come stringhe» recidivo (`read_file` range 3× → `sed -n`): evidenza identica, già in `tool-pitfalls.md` → escluso dalla consolidazione (anti-grasso). [sync:safe]

---

## 2026-10-28 — QwenCloud async task management → HAL (sessione)

### Progetto

- Analisi doc QwenCloud «Async task management» (docs.qwencloud.com/developer-guides/run-and-scale/async-task-management): Task API submit→poll con macchina a 6 stati (`UNKNOWN` = id scaduto, cancellabile solo da `PENDING`), endpoint di gestione (query/list/cancel) condivisi a 20 QPS, retention metadati+URL 24h; Batch API −50% (JSONL ≤50k/500MB, finestra 24→336h, retention 30g); best practice: backoff esponenziale per modaltà (immagine 3s ×1.5, video 15s ×1.5), download immediato dei risultati, iterazione `choices` con `finish_reason` su multi-output, dedup dei submit contro i task duplicati. [sync:safe]
- Mapping HAL: `poll_synthesis_task` dell'illustrator usa intervallo fisso 8s con 2/6 stati terminali; `gateway_core.py` ha cache L1 sulle risposte ma nessuna idempotenza di submit; `CircuitBreaker` non ha budget di frequenza sui poll; `cmd_distill` (a-knowledge) e replay `benchmark/` candidati Batch API. Consolidati 6 gap in `./ToDo.md` (2 P1, 4 P2) con riga Delta + clausola vincoli trasversali. [sync:safe]

### HAL

- Sesta conferma del pitfall «parametri numerici respinti come stringhe» (`read_file` range 3× anche con un solo parametro, `terminal timeout_ms` 2× → `sed -n`/omissione): evidenza accorpata nella sezione esistente di `tool-pitfalls.md` (una idea, un posto canonico). [sync:safe]
- Nuovo bullet in «Batch `edit_file` non atomico»: i file condivisi mutati da sessioni parallele tra lettura e scrittura invalidano le ancore (osservato: `./ToDo.md` mutato due volte, `tool-pitfalls.md` una) e i batch con 2 edit a cascata su ancore sovrapposte possono troncare contenuto (titolo voce P0 troncato e ripristinato alla chiamata successiva) → regola «una inserzione = un edit». [sync:review]
- Regola 7 di `learn-guidelines.md` estesa: clausola opzionale `Vincoli trasversali:` nella riga Delta quando la fonte pone vincoli hard (limiti, stati, retention) — pattern già usato dai delta Context cache e Async task. Skill `learn` 1.5.4→1.5.5. [sync:safe]
- `router.py score`/`choice`/`routing` → `ABSTAIN` (servizio `laya.local` non raggiungibile): nessuna retry, delega alla tabella Destinazione (System 2) come da protocollo; la scelta task-vs-batch per i job bulk è codificata come voce ToDo, la sua esecuzione dipende da S1 disponibile. [sync:safe]

---

## 2026-10-28 — QwenCloud streaming → HAL (sessione)

### Progetto

- Analisi doc QwenCloud «Streaming output» (docs.qwencloud.com/developer-guides/run-and-scale/streaming): `stream_options={"include_usage": true}` con usage solo nell'ultimo chunk (OpenAI-compat) vs usage per-chunk in DashScope (monitoraggio costi ed early-stop); thinking a due fasi (`reasoning_content` → `content`); argomenti tool call come delta JSON parziali da concatenare per `index` prima di `json.loads` (tre fasi con thinking); modelli streaming-only (Qwen3 open-source, QwQ, QVQ, Omni: non-streaming fallisce o restituisce vuoto); Nginx `proxy_buffering off`, pool/fd sotto concorrenza; JSON Mode valido solo sull'output concatenato; qualità invariata. [sync:safe]
- Consolidati 4 gap in `./ToDo.md` con riga Delta + clausola «Non applicabili» (endpoint regionali/SDK DashScope, nota frontend web): percorso streaming SSE System 2 (P1, rimedio strutturale ai 504 da timeout upstream già evidenza nei report benchmark), flag `streaming_only` nel resolver (P2), accumulo delta tool-call/JSON Mode (P2), vincoli deployment SSE nel serving spec (P2). [sync:safe]

### HAL

- Settima osservazione del pitfall «parametri numerici respinti come stringhe» (`read_file` range 2× → `sed -n`) e nuova osservazione del batch `edit_file` non atomico con causa concorrente: `ToDo.md` 67→151 righe tra lettura e scrittura per append di sessioni parallele, index 1 del batch fallito → rilettura della coda reale e riapplicato solo il mancante. Evidenze accorpate nelle sezioni esistenti di `tool-pitfalls.md`. [sync:safe]
- Nuovo pitfall «writer canonico per handoff JSON»: il primo handoff di sessione è stato scritto a mano con `write_file` e solo dopo normalizzato con `bash agents/scripts/harness-prompt-builder.sh handoff-write todo --field …` (default `product/state/` già allineato; la nota `--dir` del 2026-10-27 è superata). [sync:safe]
- Regola 7 di `learn-guidelines.md` estesa con clausola `Non applicabili:` (validata dai delta Connection pooling e Streaming); complementare alla clausola `Vincoli trasversali:` aggiunta in 1.5.5. Skill `learn` 1.5.5→1.5.6. [sync:safe]
- `router.py routing` `ABSTAIN` 3× sulle destinazioni → fallback tabella Destinazione (System 2) senza retry, come da protocollo. Escluso dalla consolidazione (anti-grasso, già in padre): pattern generale batch-ToDo-da-doc (regola 7), lettura outline di `read_file` su file grandi. [sync:safe]

---

## 2026-10-29 — fix laya_service + contratto /systemone → HAL (sessione)

### Progetto

- RCA completa delle ABSTAIN System 1 (tre strati distinti): (1) `laya_service.py` non inviava `Authorization` → 401 su `/v1/predict` → `abstain unavailable` (fix con risoluzione chiave env `LAYA_API_KEY` → `.env` di repo → default `sk-local`; Red→Green `TestAuthHeader` in `tests/test_laya_http_pool.py`, suite `test_laya_*` 55 verdi; voce `### Fixed` in `./CHANGELOG.md`); (2) mismatch di contratto — il client invia `{task,routes,options,criteria}` a `/v1/predict`, che accetta solo nativo `{state,questions}` o shorthand `{text}` (→ intent-only), mentre il task endpoint canonico è `POST /systemone` `{task_type,text,params}` → `{result:{choice,confidence,probabilities},request_hash}` (localhost, senza auth): servizio sano, verdetti reali ottenuti (routing marker→`cache-cost-tokeni` p=0.88; 7/7 voci ToDo instradate, diverse sotto confidenza 0.3 → escalation System 2); (3) path morto del comando `/laya` (scoperto e sistemato da sessione parallela, `laya` 1.4.2).
- Voce P0 di `./ToDo.md` riscritta (da «servizio guasto» — diagnosi parziale ereditata dalla stessa sessione — a «client da allineare al contratto canonico», `#bug`); nota della voce task-vs-batch corretta. By-pass onesto di `score` (`score_not_discriminative`, distribuzione misurata non discriminante): non fabricare punteggi. Rilevato: `/var/www/laya/log.sqlite` è una directory vuota (sqlite3 «unable to open» ≠ corruzione); il log del servizio è `/var/www/hal_system1/log.sqlite`.
- Correzione d'inventario HAL: `laya_service.py` del gateway aveva `_call` senza auth; i consumer (`benchmark/`, `a-knowledge/extract.py`, `scripts/test_laya.py`) usavano già l'header — il client gateway era l'outlier.

### HAL

- `laya` 1.4.2→1.4.3: § «Diagnosi rapida — ABSTAIN» estesa con contratto degli endpoint (auth solo su `/predict`, task su `/systemone` senza auth), by-pass `score`, log canonico `/var/www/hal_system1/log.sqlite`, `confidence < 0.3` non prova [sync:safe]
- `learn` 1.5.9→1.5.10: `learn-guidelines.md` regola 8 «Cause ereditate — riverificare»; `tool-pitfalls.md` regola mismatch-contratto + decima conferma dei parametri numerici (`read_file` range 2×, `timeout_ms` 1×) [sync:safe]
- Concorrenza: la sezione `[1.5.9]` del `learn/CHANGELOG.md` è risultata sparita dal worktree a metà turno (mutazione esterna, contenuto `tool-pitfalls.md` integro) → ripristinata; ottava conferma del pitfall «file condivisi mutati da sessioni parallele» [sync:review]
- Candidati a osservazione singola (NON consolidati, regola: aprire voce alla seconda sessione): `edit_file` fallito con «file changed on disk» quando l'`old_text` era ricostruito a memoria («ha astenuto» vs il verbatim «ha abstenuto»); `edit_file` con anchor breve su heading di versione genera match fuzzy multipli (usare block lungo con titolo file come ancora).

---

## 2026-10-31 — fix naming L2 harness-* + copertura gate frontmatter → HAL (sessione)

### HAL

- Contratto naming del loader Zed: `name` kebab-case (`^[a-z0-9]+(-[a-z0-9]+)*$`) e uguale alla directory; le 4 L2 scaffoldate in giornata con underscore (`harness-hal_mcp_docs|_mcp_tools|_translate|_tts`) erano scartate in silenzio (presenti su disco, assenti dal catalogo skill). Rinominate in kebab + riferimenti allineati nei 4 Makefile/CHANGELOG consumer. Consolidato in `harness-agentfactory` 1.1.30→1.1.31 (§ Steward notes); candidato a promozione L1 via `/sync <` (validato su 4 progetti, nessuna richiesta esplicita in sessione). [sync:safe]
- Bug di copertura in `check-frontmatter-all.sh`: scan `-path "$ROOT/.agents/skills/*"` con ROOT=`agents/` mai matchato → gate verde senza controllare i L2 reali, e `name` mai validato. Fix: `find` separato sulle directory reali `.agents/skills/harness-*/SKILL.md` (senza seguire symlink) + verifica name/regex/directory. Lezione generalizzata ai gate: uno scan a zero match è un vacuous pass, va contato e fatto fallire a zero. [sync:review]
- Infra HAL: `hal_mcp_docs`, `hal_mcp_tools`, `hal_translate`, `hal_tts` hanno `.agents` symlink → `/var/www/hal_gateway/.agents` (stesso inode) — le loro L2 vivono come directory reali sotto `.agents/skills/` di questo repo; listando quei progetti si vede il contenuto di HAL, non è duplicazione. [sync:safe]
- Concorrenza: `harness-wtp/SKILL.md` mutato 1.1.4→1.1.5 (bump di sessione parallela) tra due letture nel turno → evidenza accodata a `tool-pitfalls.md`, learn 1.5.13→1.5.14. Seconda conferma parametri numerici (`read_file` range 2× → `sed -n`) NON accodata: evidenza orcarouter già registrata in 1.5.13 per la stessa giornata (anti-grasso). [sync:safe]
- Esclusi dalla consolidazione: catene STALE note (`harness-hal` 1.9.2, `wtp`/`semidifocusing` 1.7.3 vs `a-harness` 1.10.0 — bump di competenza consumer via `sync-consumer-stale`); `sed -i` terminale su file fuori progetto riuscito (osservazione singola, aprire voce alla seconda sessione). [sync:safe]

## 2026-11-18 — HT-005 oro + HT-010 prima eval raw misurata → HAL (sessione)

### HAL

- `tool-pitfalls.md` §Sessioni parallele: prefisso di directory nell'allow-list P assorbe i transitori nati tra `git status` e l'add — lockfile LibreOffice del workbook HT-005 committato e pushato (1822d3e «4 file» attesi 3); recupero documentato senza reset su repo condiviso (blob surgery 9ceb108; `git add` non stagea la cancellazione di un file ancora su disco, serve `rm --cached`). Pattern `*~lock*#*` in `.gitignore`. [sync:safe]
- `tool-pitfalls.md` §Sessioni parallele (verde preso in prestito): `c3599e2` della sorella ha pushato bump meccanico corrotto (`versenversion:` su 8 L1) — `test_a_harness_static_policy` rosso su origin ma verde locale perché il worktree condiviso aveva già il revert WIP della sorella. Regole: ri-eseguire il gate che legge i file bumpati prima di chiudere un flusso `[sync:safe]`; verificare `git diff --stat HEAD` sui file letti dal gate prima di dichiarare CI verde; il deploy `sync !` pubblica lo stato del worktree, borrowed green compreso. Non riaprire la corsa sul file sporco altrui. [sync:review]
- `tool-pitfalls.md` §Tool call paralleli: sesta evidenza, direzione autoinflitta — generator+export, edit+`todo_flush`, status+append emessi nello stesso batch (3 ricadute, tutte autorigenate alla rilancia); nessuna regola nuova. [sync:safe]
- `docs/28_laya_model_card.md`: l'N/A «eval raw con gold set assente» diventa **prima misura** (HT-010, run 2026-11-18 su 123 oro confermati): hit_rate 0.276, decision-family .540, banda direct .523, curva debole non monotona; caveat strumento (score by-pass 30/30 by design; noul {uncertain, refuse} vs vocabolario oro → allineamento nel residuo HT-005). Nessuna soglia mossa; adozione gated su copertura piena → `HT-011` #human. Comandi di riproduzione incorporati nella carta. [sync:review]
- Esclusi dalla consolidazione: auto-vote commit-type 3/4 incorrect di oggi (veri nella telemetria Laya tramite il loop `request_hash` — un solo posto canonico, anti-grasso); coercizione `timeout_ms`/`start_line` (già registrata in 1.6.25, nessuna nuova occorrenza-regola); warning `Data Validation extension` openpyxl su xlsx ri-salvati da LibreOffice (osservazione singola: load+save openpyxl la elimina, eventualmente alla seconda). [sync:safe]

## 2026-11-18 — AgentFactory fuori dal canone + [sync:safe] completato + dedup chrome UX → HAL (sessione brainbeez)

### HAL

- Decisione d'inventario (utente, 2026-11-18): AgentFactory non tornerà → rimossa la skill L2 `harness-agentfactory` (canone + 5 symlink consumer), `MIGRATION.md`, i 15 symlink rotti in `~/.cursor/agents` (bersaglio `/var/www/AgentFactory/` inesistente); wording di dismissione ritirato da AGENTS/README/docs/routing learn; docstring `seozoom_lib` allineata. I riferimenti nei registri storici (CHANGELOG, session-learnings) restano: sono record, non istruzioni. [sync:safe]
- Chiusura [sync:safe] 8 L1←a-agentzero 1.13.9: dopo il fix 516146c (decodifica `versenversion:` in 7 skill) `a-harness` era rimasta indietro — riallineata 1.11.2/1.13.9 in questo flusso. Regola già registrata in tool-pitfalls §Sessioni parallele («rieseguire il gate che legge i file bumpati») — qui rispettata in chiusura, non ri-appresa. [sync:review]
- `uiux` L1 1.2.0 assorbe 3 canoni chrome dalle L2 `wtp-ux-ui`/`b2b-explorer-ui-ux` (puntatori + override restanti): prima promozione L1 con trigger esplicito dell'utente su report `/sync <` (regola ≥2 progetti soddisfatta da due superfici dello stesso DS WTP). [sync:safe]

## 2026-11-18 — pipeline /learn ! + /sync + /version minor + /document → HAL (sessione)

### HAL

- Consolidamento: voce `tool-pitfalls.md` §Sessioni parallele su `pull --rebase --autostash` in worktree condiviso (ricetta reset+checkout-sullo-stash-altrui) + terza evidenza CJK → `learn` 1.6.27→1.7.0 (bump minor via `agent-version.sh bump minor`). [sync:safe]
- Chiuso il debito 2026-11-09 «Promozione L1 uiux delle parti generiche rinviata»: `a-design/uiux` 1.2.0 con i 3 canoni chrome (slot brand/meta, output nel menu File, copy da origine i18n) e L2 ridotte a puntatore+override; registrato in `docs/harness-CHANGELOG.md` §Changed. [sync:safe]
- Esclusi (anti-grasso): brace-expansion sh (candidato già in ToDo HAL, unica sessione), `versenversion:`/verde preso in prestito (già voce sorella in tool-pitfalls §Sessioni parallele).

### HAL (addenda unificazione copy WTP)

- NEED-N risolto per via 1-bis della regola (richiesta esplicita): unificazione `a-copywriter-wtp`→`wtp-brand-voice` con **inversione del verso dell'alias** (la tana vuota diventa fonte, il corpo diventa guscio) per non rompere i 12 symlink consumer; catena L2 dichiarata solo sul vero sorgente. Ricetta riutilizzabile ogni qualvolta il canone di naming vorrebbe il nome X ma i link vivi puntano Y. [sync:safe]
- Auto-evidenza CJK: il mio stesso writer ha generato `逆流` dentro il body (classe Frammenti CJK, rimedio sweep pre-commit). Il canone si autoverifica: lo sweep post-scrittura resta il gate di chiusura di ogni `/learn !`. [sync:safe]

---

## 2026-11-18 — fix pyright HT-010 runner + consolidazione /learn ! → HAL (sessione)

### HAL

- **Convenzione pyright per import dinamici in test (2° progetto → pattern cross-progetto consolidato):** `importlib.util.spec_from_file_location` restituisce `ModuleSpec | None`; il guard canonico è `assert _spec is not None and _spec.loader is not None` prima di `spec.loader.exec_module(mod)` (non `cast`). Analogo per l'argomento `spec=` di `ModuleType`: o `ModuleSpec` valido o non passarlo. In questo repo il pattern era già in `tests/compare_tokens.py`; la sessione brainbeez 2026-11-04 (#16) lo aveva applicato su `main.py`. Non serve documentarlo in a-harness: è pratica da codice esistente + questi appunti; se emergono altre due occasioni valutare riferimenti L1 dedicati.
- **Guard `__doc__` under strict:** `description=__doc__.splitlines()[0]` è `str | None` → `Optional` non ammesso; canone del repo: `(__doc__ or "")`, es. `compare_tokens.py:190`, `benchmark/scripts/gold_set_pred_runner.py:195`.
- **Acceptance gate statico:** dopo fix typing, rieseguire test di destinazione (`pytest tests/test_gold_set_pred_runner.py -q`, 13/13 PASS) + smoke `--help` dello script toccato; i diagnostics pyright vanno riletti post-edit, non fidarsi dello stato pre-rinfresco.
- **Punto ricorrenza pitfall tool (già documentato, nessuna nuova voce):** `read_file` con `start_line`/`end_line` respinto 4–5 volte anche passando interi (`invalid type: string, expected u32`) — coerente con §Parametri numerici respinti come stringhe in `learn/references/tool-pitfalls.md`; fallback canone terminal/lettura integrale, già in atto.
- **Nuovo pitfall consolidato (1ª occorrenza, registrato in `learn/references/tool-pitfalls.md`):** citare path come «evidenza documentata» senza verifica fresca — in sessione ho attestato `agents/a-harness/references/pyright-conventions.md` come fonte della convenzione importlib: file inesistente (verificato con `find`), l'attestazione era un'inferenza da output di comandi troncati.

## 2026-11-20 — Dismissione wrapper locali comandi L0 + /learn ! → HAL (sessione)

### HAL

- **Cosa:** la sede delle skill-comando L0 diventa unica (globale `~/.agents/skills/`): `link-workspace-skills.sh` non genera più i mirror `.agents/skills/<cmd>/` e li pota, `check-editor-links.sh` inverte l'invariante (assenza wrapper), `sync-agents.sh` non pretende più i symlink learn/sync. Chiusa anche la catena STALE preesistente con sync selettivo [sync:safe]: 8 figli L1 re-pinnati 1.13.11→1.14.0 (per a-design/a-knowledge solo pin — bump in transazione parallela), harness-hal 1.0.8 su a-harness 1.11.4, padre a-agentzero 1.14.0.
- **Evidenza:** 26 test verdi (moduli guard/l0/canonical/rerun + `test_link_workspace_skills` riscritto sul contratto prune — era CI-red per funzione dismessa; due RED preesistenti emersi: pin graph 1.0.4≠mirror 1.0.5, fixture COMMANDS 9/11); `make -C agents pre-commit` + `test-unit` OK; tool `skill` risolve `commit` dal globale (`<source>global</source>`); i CHANGELOG unici nei mirror (graph/cycle/version) trasferiti al canone `agents/a-agentzero/commands/CHANGELOG.md`.
- **Stato:** consolidato — bullet datato in `learn/references/tool-pitfalls.md` §Path dei comandi L0 (learn 1.7.2), canoni doc allineati (sync/SKILL.md 1.2.3, extended-rules, commands/README), comandi sync 1.0.1 / version 1.3.3 / learn 1.0.1 ripubblicati.
- **Ambito:** HAL. **Destinazione:** skill (learn deep) + `commands/CHANGELOG.md`.

---

## 2026-11-21 — HT-012: riversamento canoni de-racing nei target canonici (sessione `/graph -y`)

### HAL

- 2026-11-19/20 — de-racing completo hal_gateway↔consumer: guardia realpath su rigenerazione (1.13.10), L2 nei repo proprietari (1.13.11), contratto - catalogo fence `hal-contract.py` (1.13.12), comandi L0 globali `~/.agents/skills` + sync/learn promossi a comandi (67f365f), delega MCP `skills_list`/`skill_read` per L1/embedded (hal_mcp_tools 1.10.0). Appresi i canoni 1–5 di questa nota. - 2026-11-20 (step B) — fonte unica consumer: `agents/consumers.list` + loader `consumers_list.py`; hal-contract/prune/sync-consumer-stale de-hardcodati (21 consumer, includeva pickwaise e gDrive_ops invisibili alle tre liste); gate `make -C agents consumers-list` (`STRICT=1`); guardia canone aggiunta a hal-contract.py. Consolidati: §6 (AGENTS.md + `agents/docs/operativo.md`), nati §7-§9 (riversamento §7-§9 → tool-pitfalls vincolato a HT-012); residue applicativo → HT-014.
- **Dove:** `agents/a-agentzero/learn/references/tool-pitfalls.md` (§1 nuova sezione; estensioni §2/§3/§4/§5/§7/§8/§9), `agents/a-agentzero/learn/references/learn-guidelines.md` (regola 9), learn 1.8.0→1.8.1 (`SKILL.md` + `CHANGELOG.md`), `ToDo.md` (voce brace + `HT-012` chiuse con Esito; convenzione ID uniformata in L5), `product/work-graph.md` (rv 2026-11-21, nodi N35/N36).

## 2026-11-21 — /learn ! chiusura sessione comandi L0 (voto recuperato + anchor grep) → HAL (sessione)

### HAL

- **Cosa:** consolidati i residui non ancora canonici della sessione de-racing (chiusa con commit 37215df + push): nuovo bullet §grep «grep non ancorato = falso positivo» (1ª occorrenza: `grep -m1 version` legge `name: version`, canone `^version:` o guardia `check-version-changelog.sh`); estensione §Parametri numerici «auto_vote post-commit saltato: recupero in sessione» (rc=0, «registrato (correct)», stesso hash); bullet §Sessioni parallele «`--all` delegato = inclusione dichiarata» (allow-list esplicita + gate verdi + messaggio, la gara sullo shared tree si chiude). Bump learn 1.8.1→1.8.2 + voce changelog.
- **Esclusi (anti-grasso):** riverifica dei fatti con comando read-only (regola 9/§7 — già riversata da HT-012 in 1.8.1 oggi); drift HEAD e output replay (§Strumenti: risultati replay/stale — già copre il «37215df credeva HEAD, poi 01613f0/f07af07»; il ri-assetto del turno non ha fabbricato claim); canoni (a)(b)(c) della transazione wrapper-dismissione (già in 1.8.0); provenienza alias `laya-cmd` (già documentata in `publish-global-commands.sh`); ricorrenza `timeout_ms` 300000/600000 registrata senza regola nuova.
- **Evidenza:** auto_vote_commit rc=0 «registrato (correct)» (hash 83298bbf…, commit 37215df); `make -C agents pre-commit` OK, check-registry/check-lines OK, 26 test verdi (moduli l0/canonical/rerun/guard).
- **Ambito:** HAL. **Destinazione:** skill (learn deep, `tool-pitfalls.md`) + questo registro. Nessuna voce ToDo (niente actionable residuo).

## 2026-11-22 — /learn ! chiusura HT-014: contratto consumer applicato, push SSH, fix git-push-auth → HAL (sessione)

### HAL

- **Cosa:** HT-014 chiuso e deployato: `hal-contract.py --apply` sui 21 repo di `agents/consumers.list` (61 mount residui rimossi — pickwaise 41, liberating.it 18, gDrive_ops 2; fence a a-agentzero 1.13.15: refresh ×11, append ×2, create ×8; dry-run post-apply 0 mount + current ×21; `consumers-list STRICT=1` verde); commit nei 16 repo git con allow-list stretta (AGENTS.md + mount tracciati, zero WIP altrui assorbito) e **12/16 pushati via SSH** con verifica `ls-remote` (guardie: HEAD==sha-fence, ahead==1 — mai pubblicare commit altrui). Bugfix `git-push-auth.sh`: esecuzione diretta usciva 0 in silenzio senza spingere (falso successo) → guardia `BASH_SOURCE`, push effettiva con rc propagato, exit 2 su detached HEAD, 3 test di regressione (4af90d3). Consolidati in `tool-pitfalls.md`: §Push HTTPS estensione (no-op silenzioso + lezione «modulo sourcato = guardia di esecuzione»; fallback SSH BatchMode a URL esplicito; push a URL esplicito non aggiorna i tracking ref → verità = ls-remote), §Parametri numerici ricorrenza (read_file range 2× `expected u32`), §Replay/stale ricorrenza (collasso a singola riga su tutti i canali, sanificazione+probe negative → non filtro di contenuto; workaround: marker nuovi + chunk con esclusione della riga sopravvissuta). Aperto `HT-016` (push dei 4 consumer rimasti + remote gDrive_ops da correggere). learn 1.8.2→1.8.3.
- **Esclusi (anti-grasso):** ricetta blob surgery per registri misti (già in commit skill §Isolamento index p.6 — riusata 3× senza delta); guardie push su commit altrui (già in §Sessioni parallele); voti Laya feat/fix/docs (calibrazione nel loop `laya_outcome`, non regola da file); fonte unica consumers.list (già canone 1.13.14/1.13.15 + AGENTS.md); esito push consumer (già ESITO HT-014 nel CHANGELOG root, 702aeb6).
- **Evidenza:** HAL `174c5e0`→`4af90d3`→`702aeb6` (remoto verificato via MCP GitHub); 12 push `ls-remote`==HEAD locale; gDrive_ops `Repository not found` (remote `carlo/gDrive_ops` inesistente); brainbeez HEAD mosso (44069e7≠23b286c), InnerCircle ahead=7, liberating.it ahead=2 → skip corretti; probe `printf` negativa; test push-auth 6/6.
- **Dove:** `agents/a-agentzero/learn/references/tool-pitfalls.md` (§Push HTTPS, §Parametri numerici, §Replay/stale), `ToDo.md` (HT-016), learn 1.8.2→1.8.3 (`SKILL.md` + `CHANGELOG.md`).

## 2026-11-20 — /learn ! catena side-car Auto Ontology (HT-013 · AO-1/1.1/2) → HAL

### HAL

- **Cosa:** consolidati 6 apprendimenti della catena `auto-ontology-mcp`: (1) `todo_flush` appiattisce le voci chiuse multi-bullet sul solo titolo → Esito in riga (formato HT-010); (2) una guardia non deve asserire sul backlog volatile (assert 4 di `check-ontology-bc-boundary.sh` tornato RED dopo il flush → inasprito su sede slice); (3) lo smoke di boot MCP va fatto con comando **e** env esatti della entry (senza env: 35 tool di default; con: 13 `answer` — match baseline KPI-1); (4) `router.py choice --json` non emette `request_hash` → voti di calibrazione esprimibili solo via tool MCP (2ª occorrenza, famiglia `auto_vote_routing` learn 1.6.19); (5) deviazione di path per sudo non interattivo: registrarla con procedura di ripristino (→ pin file), non subirla; (6) pin di runtime side-car (clone fuori bundle, `references/*-source.md` con blocco PIN) ≠ corpus vendor da distillare (`agents/vendor/`) — da precisare in `l1-from-proto.md`. Escluso (anti-grasso): la race del batch parallelo — già §Tool call paralleli in tool-pitfalls; conferma, non voce nuova.
- **Evidenza:** CHANGELOG riga 108 spogliata dei 4 sub-bullet dal flush (Esito re-inlineato a mano); guardia RED post-flush → GREEN con assert 5 su slice; doppio handshake stdio 35 vs 13 tool (righe `ao-2-boot-smoke`/`ao-2-env-verify` di agent-progress); `routing` S1 → ABSTAIN su tutte e 6 le voci (gate k=4: classificazione a System 2 — esito onesto, non sostituito).
- **Stato:** registro interino in `docs/apprendimenti-auto-ontology-2026-11-20.md`; riversamento nei target canonici (tool-pitfalls §nuova «Registri condivisi», estensione del bullet `auto_vote_routing` di learn 1.6.19 per la 4, l1-from-proto per la 6) **rinviato a `HT-015`** — i target canonici sono sporchi di WIP parallelo (stessa causa di HT-012) e il gate «≥2 sessioni» di tool-pitfalls è soddisfatto solo per la famiglia (4). Nessun bump learn deep (non toccato in questo giro).
- **Ambito:** HAL. **Destinazione:** docs (fatto) + `./ToDo.md` `HT-015` (fatto) + skill learn deep (via HT-015).

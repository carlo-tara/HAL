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

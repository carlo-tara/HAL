# Mappa residui — HAL

Backlog rinfrescabile (≠ Progress append-only). Igiene: `/todo`.

Delta 2026-10-28 da Kimi docs «Dynamically Loaded Tools» (platform.kimi.ai): 6 voci sotto.

Delta 2026-10-28 da QwenCloud docs «Multi-turn conversations» (docs.qwencloud.com/developer-guides/run-and-scale/multi-turn): 5 voci sotto.

Delta 2026-10-28 da QwenCloud docs «Context cache» (docs.qwencloud.com/developer-guides/run-and-scale/context-cache): 7 voci sotto. Vincoli trasversali da rispettare: prefisso ≥1024 token, lookback ≤20 content block dal marker, max 4 marker/request, validità explicit/session 5 min con reset on hit, cache isolata per account e per modello, implicit non disattivabile; nessun warm-up finto su batch (Laya resta sulla sua `lru_cache`: prompt sotto soglia).

Delta 2026-10-28 da QwenCloud docs «Connection reuse and pooling» (docs.qwencloud.com/developer-guides/run-and-scale/connection-pooling): 7 voci sotto. Non applicabili: WebSocket/TTS object pooling (HAL non usa API realtime); il «pool size ≤ QPS limit» è già coperto da `LayaCallBudget`; il circuit breaker/fallback esiste già in `gateway_core.py`.

Delta 2026-10-28 da QwenCloud docs «Async task management» (docs.qwencloud.com/developer-guides/run-and-scale/async-task-management): 6 voci sotto. Vincoli trasversali: stati terminali del task model sono 6 (`PENDING`/`RUNNING`/`SUCCEEDED`/`FAILED`/`CANCELED`/`UNKNOWN`), solo `PENDING` è cancellabile, retention metadati+URL risultati 24h per la Task API (30 giorni per la Batch), endpoint di gestione (query/list/cancel) condivisi a 20 QPS per account.

Delta 2026-10-28 da QwenCloud docs «Streaming output» (docs.qwencloud.com/developer-guides/run-and-scale/streaming): 4 voci sotto. Non applicabili: endpoint regionali `ap-southeast-1.maas.qwencloudapi.com` e SDK DashScope (HAL transita da OrcaRouter in modalità OpenAI-compatibile); la nota «Web frontend `ReadableStream` + `TextDecoderStream`» riguarda il client, non il gateway.

## P0

- [ ] Includere dichiarazioni tool/skill nella chiave Cache L1 `#bug` · P0 · Gateway Core
  - Perché utile: `normalize_prompt`/`compute_cache_key` in `gateway_core.py` hashano solo il campo `content`; due richieste con stesso testo ma tool set diverso condividono la chiave → falso hit con risposta potenzialmente errata.
  - Acceptance: unit test in `tests/` con due richieste stesso testo / tool diversi produce chiavi diverse; `make test-unit` verde.

## P1

- [ ] Chiave Cache L1 a due livelli: prefix stabile + suffix append-only `#feature` · P1 · Gateway Core
  - Perché utile: oggi la chiave è esatta sull'intera richiesta: ogni append (skill iniettata, nuovo turno) invalida tutta la voce; un hash di «prefix stabile» (system + tool core + primi turni) più suffix consente riuso parziale come il prefix caching Kimi.
  - Acceptance: append di messaggio/dichiarazione su conversazione già chiave non invalida la parte di prefix; test dedicato + aggiornamento `docs/07_cache_l1.md`.

- [ ] Catalogo skill compatto con System 1 (Laya) come tool-search `#feature` · P1 · System 1 (Laya) + Agent Platform
  - Perché utile: ~37 descrizioni complete esposte a ogni prompt = Tool Definition Bloat (token, scelte errate di tool); Laya `routing`/`noul` è già un `search_tools`: esporre solo nome + keyword e caricare il bundle completo su domanda.
  - Acceptance: `router.py routing` restituisce il sottoinsieme skill da keyword tag; catalogo `.agents/skills/` ridotto a riga «keywords»; riduzione token misurata in `benchmark/`.

- [ ] Regola di protocollo append-only per dichiarazioni iniettate `#docs` · P1 · Agent Platform
  - Perché utile: doc Kimi: mai modificare dichiarazioni già iniettate a metà conversazione (invalida il prefix cache e il tool decade); le versioni aggiornate si accodano. Da codificare in `a-agentzero`.
  - Acceptance: regola presente in `agents/a-agentzero/AGENT-PROTOCOL.md`; nessuna modifica in-place di skill iniettata on-during-session.

- [ ] ContextManager multi-turn nel Gateway Core: troncamento, rolling summary, retrieval `#feature` · P1 · Gateway Core
  - Perché utile: doc QwenCloud: l'API è stateless e il client deve mantenere l'array `messages` applicando tre strategie (tenere gli ultimi N turni, rolling summary a soglia ~70% del contesto, retrieval vettoriale on-demand). Oggi `SystemTwoEngine.execute(task, text)` è single-shot (riceve un `str`, nessuna rappresentazione di conversazione); `docs/15_enforcement_budget.md` pone il trigger sulla compattazione ma le strategie non sono implementate.
  - Acceptance: modulo `ContextManager` che accetta `messages` e restituisce un array entro `max_context_tokens` del profilo applicando troncamento/summary/retrieval; unit test per le tre strategie in `tests/`; `make test-unit` verde.

- [ ] Regola di protocollo: mai reinserire `reasoning_content` nella history `#docs` · P1 · Agent Platform
  - Perché utile: doc QwenCloud sui thinking model: quando si aggiorna l'array `messages` va trattenuto solo il campo `content`, ignorando `reasoning_content`; HAL instrada verso modelli thinking (`qwen/qwen3.8-flash`, `qwen3.7-flash`) ma nel codice e negli agenti non esiste alcuna gestione del campo: reinserire il ragionamento in context spreca token e degrada le risposte.
  - Acceptance: regola presente in `agents/a-agentzero/AGENT-PROTOCOL.md`; percorso di ricostruzione history (futuro `ContextManager` incluso) che filtra via `reasoning_content`; unit test dedicato.

- [ ] Regola di protocollo ordering static-first: mai contenuto volatile in testa al prompt `#docs` · P1 · Agent Platform + Gateway Core
  - Perché utile: doc QwenCloud: l'implicit cache matcha il prefisso byte-per-byte, quindi «static content at the beginning, variable content at the end». Per HAL: system prompt agente → tool descriptions → file di contesto → storico conversazione → domanda attuale. Contenuto volatile in testa (timestamp, nonce, `session_id` nel prompt) azzera ogni hit su ogni turno. Complementare alle voci «Chiave Cache L1 a due livelli» e «System prompt come instructions». Nota: `normalize_prompt` (lowercase + rimozione timestamp) va usato solo per la chiave Redis L1, mai sul testo inviato: normalizzare i messaggi distrugge il match di prefisso lato provider.
  - Acceptance: regola di ordering e divieto di normalizzazione sul body inviato in `agents/a-agentzero/AGENT-PROTOCOL.md` + nota in `docs/07_cache_l1.md`; contratto dei backend System 2 che fissa l'ordine dei blocchi.

- [ ] Telemetria `cached_tokens` e `cache_creation_input_tokens` nei runner e nei gate `#feature` · P1 · Benchmark
  - Perché utile: `benchmark/runner/benchmark_models.py` estrae da `usage` solo `prompt_tokens`/`completion_tokens`/`total` (più i campi Gemini) e `generate_orcarouter_report.py` legge `prompt_tokens_details.cached_tokens` trattandolo come eccezione «Claude-specific»; il doc QwenCloud espone gli stessi campi su tutti i path cache-abilitati. Senza parsing uniforme il beneficio di cache è invisibile e `SystemEvaluationEngine` non può confrontare i modelli su costo effettivo invece che nominale.
  - Acceptance: `cached_tokens` e `cache_creation_input_tokens` persistiti su tutti i path provider in `system2_metrics.py` e nei report; KPI hit-rate % e costo effettivo per richiesta; dimensione disponibile nei gate di evaluation; unit test con fixture `usage` contenente i campi.

- [ ] Retry su Laya con exponential backoff e jitter `#feature` · P1 · System 1 (Laya)
  - Perché utile: doc QwenCloud §Production checklist: «Retry logic with exponential backoff for transient failures». In `laya_service.py::_call` (L82-86) il retry su `Timeout`/`ConnectionError` esegue `continue` in un loop stretto, senza alcuna attesa: se Laya è degradata il gateway la martella e amplifica l'incidente invece di smorzarlo. Il `LayaCallBudget` limita il _numero_ di tentativi ma non ne distanzia il _timing_.
  - Acceptance: attesa esponenziale (base ~0.2–0.5 s) con jitter tra i tentativi nel `_call`, sempre entro il budget esistente; unit test con clock fake che asserisce tentativi distanziati e nessun retry oltre il budget; `make test-unit` verde.

- [ ] HTTPAdapter con pool dimensionato sulla `_session` Laya `#feature` · P1 · System 1 (Laya)
  - Perché utile: doc QwenCloud §HTTP connection reuse: il pool va calibrato sul carico concorrente (tabella Java `connectionPoolSize`/`maximumAsyncRequests`; Python `TCPConnector(limit, limit_per_host)`). Oggi `_session = requests.Session()` usa il default urllib3 (10 connessioni per host) senza `HTTPAdapter` montato: con `batch_score`/`batch_routing` o esecuzioni parallele si generano connessioni extra e pool-overflow silenziosi, e il reuse ratio (>95% target del doc) non è garantito sotto picco.
  - Acceptance: `pool_connections`/`pool_maxsize` configurabili via env con default documentato e coerente col massimo di chiamate batch concorrenti; retry di trasporto (`urllib3.Retry`) disattivato o esplicitamente allineato al budget applicativo per non sommare due forme di retry; unit test.

- [ ] Timeout disaccoppiati connect/read/pool sulle chiamate Laya `#feature` · P1 · System 1 (Laya)
  - Perché utile: doc QwenCloud §parametri: `connectTimeout` corto distinto da `readTimeout` (e idle timeout per evitare riconnessioni frequenti). In `laya_service.py` un solo `LAYA_TIMEOUT=5.0` copre l'intera operazione: un hang in connessione consuma lo stesso budget di una lettura lenta, e il `pool_timeout` implicito può far attendere su connessione libera più del previsto.
  - Acceptance: tupla `(connect_timeout, read_timeout)` passata a `Session.post` con env dedicate (es. `LAYA_CONNECT_TIMEOUT`, default 1–2 s per servizio locale) e `pool_timeout` esplicito; unit test sul parsing dei timeout.

- [ ] Polling a backoff esponenziale con stati terminali completi `#bug` · P1 · Skill illustrator (a-design) + Gateway Core
  - Perché utile: il doc condanna esplicitamente il polling a intervallo fisso («Naive fixed-interval polling wastes API calls and may hit rate limits»); `poll_synthesis_task` in `.agents/skills/a-design/illustrator/scripts/generate-image.py` usa intervallo fisso 8s, timeout 120s e tratta come terminali solo `SUCCEEDED`/`FAILED`: `CANCELED` e `UNKNOWN` (task id scaduto/non interrogabile) continuano a girare fino al timeout sprecando chiamate contro il limite condiviso di 20 QPS. Tabella doc per modaltà: immagine 3s iniziali ×1.5 con cap 15s e timeout 2min, video 15s ×1.5 cap 60s timeout 5min, ASR 5s ×1.5 (varia con la durata audio).
  - Acceptance: `poll_synthesis_task` accetta intervalli per modaltà e applica `min(interval * 1.5, max_interval)`; `UNKNOWN`/`CANCELED` sollevano subito come terminali; unit test con `http_json` mockato che verifica la sequenza di intervalli e l'uscita immediata sui due stati; `make test-unit` verde.

- [ ] Idempotenza di submit: registro task_id anti-duplicato `#feature` · P1 · Gateway Core
  - Perché utile: ogni POST crea un nuovo task anche con parametri identici e il doc impone di «track task IDs to avoid duplicate work and unnecessary cost»; HAL ha cache L1 a chiave di contenuto sulle risposte (`compute_content_based_cache_key`) ma nessun dedup sulle sottomissioni asincrone: un retry di submit fallito (rete, switching tra provider in `ProviderResolverWithBreaker`) può ri-creare lo stesso task pagandolo due volte.
  - Acceptance: piccolo registro (memoria/Redis, riuso della chiave `cache:v1:...` come idempotency key) che mappa richiesta → `task_id` in-flight; submit identico entro la finestra non crea un nuovo task e restituisce il `task_id` esistente; unit test con doppia submit; `make test-unit` verde.

## P2

- [ ] Capability flag per-modelli per tool loading dinamico `#feature` · P2 · Gateway Core
  - Perché utile: l'iniezione dinamica è supportata solo da kimi-k3/k3.1-pro (altri modelli: `tokenization failed`) e un messaggio `system` con `tools` non deve avere `content` (400); senza gate nel resolver, il routing verso modelli OrcaRouter non supportanti rompe il payload.
  - Acceptance: flag `dynamic_tools`/`prefix_caching` nei profili in `global_config.py` + validazione gateway che rifiuta `system`+`tools`+`content`; unit test.

- [ ] Registry tool session-scoped append-only (carry-forward) `#feature` · P2 · Gateway Core
  - Perché utile: le dichiarazioni caricate vanno trasportate invariate nelle richieste successive, altrimenti il tool non è invocabile e il prefix si destabilizza; serve un registry per sessione derivato da `derive_session_id`, non una ricomposizione per-request.
  - Acceptance: registry restituisce il medesimo tool set (stabile, solo append) tra turni consecutivi; test unitario dedicato.

- [ ] Metrica benchmark token/richiesta vs skill dichiarate `#spike` · P2 · Benchmark
  - Perché utile: serve evidenza del risparmio: baseline di prompt token in funzione del numero di tool/skill dichiarate giustifica le voci su catalogo e Cache L1.
  - Acceptance: run in `system2_metrics` registra `prompt_tokens` e conteggio dichiarazioni; report con curva token-vs-dimensione-catalogo.

- [ ] System prompt come `instructions`, fuori dal transcript append-only `#feature` · P2 · Gateway Core
  - Perché utile: doc QwenCloud: passare il system prompt via `instructions` e non come item, per non perderlo alla scadenza degli item e tenerlo separato dalla history; in HAL `normalize_prompt` appiattisce i messaggi perdendo i ruoli (causa anche del falso hit P0) e il system finisce sia nell'hash sia nel body trattenuto; separarlo stabilizza il prefix della Cache L1 e si allinea al context cache dei provider.
  - Acceptance: `normalize_prompt`/`compute_content_based_cache_key` ricevono system e transcript separati con ruolo esplicito; il system non entra nel transcript append-only; unit test con stesso transcript / system diverso → chiavi diverse.

- [ ] Capability flag `context_cache` nei `SYSTEM_TWO_PROFILES` `#feature` · P2 · Gateway Core
  - Perché utile: doc QwenCloud §cost control: il context cache è automatico (zero codice) sui modelli Qwen-Max/Plus/Flash/Coder; i profili in `global_config.py` preferiscono già `qwen/qwen3.8-flash` ma senza flag che segnali i modelli cacheabili, e quindi il layout del prefix stabile e la selezione modello per costo non possono essere guidati. Si accompagna ai flag `dynamic_tools`/`prefix_caching` già richiesti nella voce P2 Kimi.
  - Acceptance: flag `context_cache` nei profili/modelli di `global_config.py`; il resolver lo considera per i profili cost-oriented; unit test.

- [ ] Astrazione conversation lato gateway (alternativa locale a `previous_response_id`) `#spike` · P2 · Gateway Core
  - Perché utile: doc QwenCloud offre sessioni server-side (Responses `previous_response_id`, Conversations `conversation`) ma sono Qwen-specific e non drop-in su OrcaRouter; le lezioni da portare in HAL sono tre: parametri di richiesta mutuamente esclusivi (da validare alla frontiera), item con scadenza 7 giorni (la copia locale resta la fonte di verità, già imposto dal vincolo ZDR), `instructions` separate dalla history. Spike per valutare se HAL necessiti un `conversation_id` e message array session-scoped oltre al `derive_session_id` attuale.
  - Acceptance: documento spike in `docs/` con decisione adotta/rifiuta e mappatura delle tre lezioni; in caso di adozione, apertura voce feature con acceptance own.

- [ ] Supporto marker `cache_control` (explicit cache) a due strati sui blocchi stabili `#feature` · P2 · Gateway Core
  - Perché utile: doc QwenCloud: fino a 4 marker `{"type":"ephemeral"}` per request partizionano il prompt per frequenza di riuso; a due strati — system prompt agente (marker 1) + file di contesto (marker 2) — la variazione di un file invalida solo il secondo blocco e non il primo. Candidato naturale: il flusso segmentato della knowledge runner (estrazione/traduzione capitoli: 3+ richieste con lungo prefisso condiviso, ognuna sopra i 1024 token minimi). Dipende dalla regola ordering static-first (P1).
  - Acceptance: contratto dei backend System 2 accetta marker per blocco; il builder applica i guardrail 1024 token e ≤20 content block di lookback (altrimenti omette il marker); verifica hit via `cached_tokens` in risposta; unit test.

- [ ] Merge dei messaggi tool consecutivi same-role nel message builder `#feature` · P2 · Gateway Core
  - Perché utile: doc QwenCloud §«Optimize message structure for parallel tool calls»: un messaggio `tool` per ogni risultato parallelo fa crescere i content block oltre la finestra di lookback di 20 dal marker → cache miss. Il loop di esecuzione HAL deve fondere i risultati same-role dello stesso turno in un solo messaggio con più content block; stabilizza anche la ricostruzione del transcript per la Cache L1.
  - Acceptance: builder/`ContextManager` produce un messaggio `tool` con N block per N risultati dello stesso turno; fixture con tool calls parallele in `tests/`.

- [ ] Costo di refill cache nel failover e nel fallback `#feature` · P2 · Gateway Core
  - Perché utile: FAQ QwenCloud: la cache è isolata per modello oltre che per account. Quando `ProviderResolverWithBreaker` o il `fallback_used` di `SystemTwoEngine` cambiano modello a sessione in corso, il prefisso riparte da zero e la ricreazione costa 125%: il costo del failover non è solo latenza ma anche «cache burn», da riflettere nei modelli di costo del breaker e nei gate di rollback di `SystemEvaluationEngine`.
  - Acceptance: metrica/evento che marca il cambio modello a sessione invariata e il costo di creazione atteso; nota in `docs/19_circuit_breaker` (o equivalente) sul sovrapprezzo; unit test sul percorso fallback.

- [ ] Prezzi cache effettivi da tabella per modello/regione, non costanti `#feature` · P2 · Benchmark
  - Perché utile: doc QwenCloud §billing: `qwen3.8-flash` e `qwen3.8-max` non rispettano i rapporti 10%/20% e 125% (variano per regione). `orcarouter/qwen/qwen3.8-flash` è già nell'allowlist di `global_config.py`: stime di costo basate su rapporti fissi darebbero classifiche errate sui profili cost-oriented.
  - Acceptance: tabella prezzi con `cache_hit_ratio` e `cache_creation_ratio` per modello/regione (default documentato quando manca); i report derivano i costi dai `cached_tokens` misurati, non dal listino nominale; test con fixture a rapporti alterati.

- [ ] Spike: session cache `x-dashscope-session-cache` via OrcaRouter/DashScope `#spike` · P2 · Gateway Core
  - Perché utile: doc QwenCloud: l'header `x-dashscope-session-cache: enable` (Responses API + `previous_response_id`) demanda la cache multi-turno al server con billing explicit (10% on hit) senza gestione manuale dei marker; HAL ha già un `derive_session_id` deterministico che mappa bene sul concetto di sessione. OrcaRouter è un aggregatore: va verificato se inoltra header e marker `cache_control` o se resta solo l'implicit; inoltre explicit e implicit sono mutualmente esclusivi su Chat Completions/DashScope/Anthropic-compatibile.
  - Acceptance: documento spike in `docs/` con esito del forwarding (header/marker) e scelta dell'ingresso (implicit+ordering vs explicit vs session); la decisione alimenta le voci su marker explicit e «Astrazione conversation lato gateway».

- [ ] Regola System 1 task-vs-batch per workload ad alto volume `#feature` · P2 · System 1 (Laya)
  - Perché utile: il doc distingue due pattern asincroni — Task API (media, secondi/minuti, retention 24h) e Batch API (testi/embedding ad alto volume, sconto 50%, JSONL fino a 50.000 richieste / 500 MB, finestra 24h configurabile a 336h, retention 30 giorni); HAL ha job di testo bulk una-tantum — `cmd_distill` in a-knowledge (stub in attesa di integrazione OrcaRouter) e replay in `benchmark/` — che convenirebbero in batch. La scelta è una decisione discreta a basso costo cognitivo, perfetta per `router.py choice` con criteri volume/latenza; nella presente sessione Laya ha abstenuto (servizio non raggiungibile) quindi la regola va codificata e la sua esecuzione dipende da S1 disponibile.
  - Acceptance: regola di scelta (criteri: n. richieste, latency budget, retention risultato) documentata in un `docs/` e collegata ai job bulk; nota `Batch API −50%` nello stub `cmd_distill` di `.agents/skills/a-knowledge/scripts/extract.py` come opzione oltre la soglia di volume.

- [ ] Successo parziale nei task multi-output: iterare choices con `finish_reason` `#bug` · P2 · Skill illustrator (a-design)
  - Perché utile: con `n>1` il task è marcato `SUCCEEDED` se almeno un output è generato e il doc prescrive di iterare `choices` verificando `finish_reason`; `poll_synthesis_task` restituisce solo `results[0]["url"]` e `extract_multimodal_image_urls` scorre le choices senza controllare `finish_reason`: un troncamento silenzioso 4→2 immagini non viene segnalato e output parziali possono essere accettati senza avviso.
  - Acceptance: estrazione di tutti gli URL con `finish_reason == "stop"` e segnalazione degli output saltati (warning su stderr e campo `partial` nell'output JSON dello script); unit test con payload misto stop/non-stop.

- [ ] Budget di polling per gli endpoint di gestione task (20 QPS) `#feature` · P2 · Gateway Core
  - Perché utile: query, list e cancel condividono 20 QPS per account e il doc prescrive di batchare i check di stato quando i task concorrenti sono molti, con `Throttling.RateQuota` come segnale di ridurre la frequenza/aumentare l'intervallo; HAL ha il `CircuitBreaker` per i fallimenti e il token budget per Laya (`LayaCallBudget`) ma nessun budget di frequenza sui poll LLM: molti polling paralleli (più skill/media) possono saturare il limite; il pattern di `LayaCallBudget` in `system1_preflight.py` è riutilizzabile lato task.
  - Acceptance: rate-limit/token bucket per le status check dei task (batching dei poll concorrenti e incremento intervallo su 429/`Throttling.RateQuota`); unit test con N poll concorrenti che resta sotto il budget simulato.

- [ ] Regola di protocollo: persistere i risultati entro la retention del provider `#docs` · P2 · Agent Platform
  - Perché utile: metadati del task e URL dei risultati (immagini, video) restano disponibili solo 24 ore (batch: 30 giorni) e poi vengono cancellati; l'illustrator scarica subito dopo il successo, ma non esiste una regola generale per agenti/skill che producono artefatti asincroni: «Download results immediately — always save results to persistent storage»; lo stato `UNKNOWN` su query è il sintomo a valle di una retention saltata.
  - Acceptance: regola in `agents/a-agentzero/AGENT-PROTOCOL.md` (submit → poll terminale → persist immediato; mai conservare solo URL del provider); rimando in `docs/05_retention_redaction.md` per la distinzione tra retention HAL (body 30g/metadati 12 mesi) e retention del provider (24h/30g).

- [ ] Teardown della `_session` (close / context manager di run) `#feature` · P2 · System 1 (Laya)
  - Perché utile: doc QwenCloud §Best practices + checklist: «Use `with` statements to manage the Session lifecycle» e «Graceful shutdown calls `pool.shutdown()`». La `_session` modulare di `laya_service.py` non viene mai chiusa: nei processi batch (benchmark, `batch_*`) le connessioni restano aperte fino al termine del processo.
  - Acceptance: metodo `close()` (o context manager di run) sul servizio che rilascia l'adapter; i runner batch lo invocano nel `finally`; unit test.

- [ ] `verify` configurabile con CA bundle invece di `verify=False` fisso `#feature` · P2 · System 1 (Laya)
  - Perché utile: doc QwenCloud §parametri Python: «SSL certificate validation for HTTPS connections» tra i parametri del connettore. HAL disabilita la verifica TLS e sopprime l'`InsecureRequestWarning` per tutti gli ambienti, anche quando `laya.local` potrebbe avere una CA self-signed dedicata esportabile.
  - Acceptance: env `LAYA_CA_BUNDLE` (o `LAYA_TLS_VERIFY`) che, se impostata, passa il percorso CA a `Session.post`; `verify=False` solo in fallback esplicito con nota in `docs/`; unit test con fixture env.

- [ ] Client riusato negli script skill (a-knowledge, a-seozoom, illustrator) `#feature` · P2 · Agent Platform
  - Perché utile: doc QwenCloud §HTTP connection reuse: riuso della stessa Session su chiamate multiple. `agents/a-knowledge/scripts/extract.py` crea un nuovo `httpx.Client` a ogni invocazione (`cmd_check`, `route_chapter_laya`, quest'ultimo senza `close()` → leak); `agents/a-seozoom/scripts/cf_analytics_export.py` usa `requests.post` nudo (una TCP+TLS handshake per riga esportata); `agents/a-design/illustrator/scripts/generate-image.py` riapre una connessione a ogni poll con `urllib.request.urlopen`. Il pattern corretto esiste già in `benchmark/runner/benchmark_models.py` (un `httpx.Client` passato nel `with` e riusato).
  - Acceptance: un client/sessione per run passato tra le funzioni (o `with` attorno al loop di polling) nei tre script; nessun `httpx.Client` istanziato dentro funzioni invocate in loop; verifica manuale con run locale.

- [ ] Metrica connection reuse nella telemetria HAL `#spike` · P2 · Benchmark + Gateway Core
  - Perché utile: doc QwenCloud §Performance monitoring fissa target «connection reuse ratio > 95%» e «pool utilization 60–80% al picco». HAL registra esiti logici (cache hit/miss, abstention, fallback) ma non ha equivalenti locali: non può dire se il pooling della `_session` stia funzionando o se sotto carico nascano connessioni nuove.
  - Acceptance: spike in `scripts/bench_hot_paths.py` (o evento log) che conti richieste vs connessioni nuove dai pool stats urllib3; soglia di attenzione documentata; decisione se portare la metrica nei gate di `SystemEvaluationEngine`.

- [ ] Percorso di esecuzione streaming System 2 (SSE) per eliminare il timeout strutturale delle generazioni lunghe `#feature` · P1 · Gateway Core
  - Perché utile: tutti i percorsi HAL chiamano l'upstream con `stream: false` (payload in `benchmark/scripts/run_orcarouter_comparison.py` e `retry_hal_cells.py`; `SystemTwoEngine.execute` single-shot). L'evidenza interna è già pagata: i 504 «al vecchio timeout upstream di 60 s», definiti in `generate_orcarouter_report.py` «la differenza strutturale più rilevante» (Opus diretto ~99 s). QwenCloud FAQ: lo streaming elimina il timeout end-to-end della richiesta e «streaming does not affect response quality». Extra: `stream_options={"include_usage": true}` produce l'usage reale nell'ultimo chunk (OpenAI-compat); il formato DashScope restituisce l'usage a ogni chunk, abilitando l'early-stop a budget superato sul gating esistente (`scripts/token_budget.py`, `tests/test_runner_token_gating.py`).
  - Acceptance: un backend registrato via `SystemTwoEngine.register_backend` ricostruisce un `SystemTwoResponse` dallo stream: accumulo di `delta.content`, gestione del chunk finale senza `choices` ma con `usage`, terminazione alla sentinella `data: [DONE]`; unit test con stream SSE mock in `tests/`; `make test-unit` verde.

- [ ] Capability flag `streaming_only` per-modelli con validazione alla frontiera `#feature` · P2 · Gateway Core
  - Perché utile: doc §Notes: Qwen3 open-source, QwQ, QVQ, Qwen3.5-Omni e Qwen3-Omni-Flash supportano **solo** streaming — le chiamate non-streaming «falliscono o restituiscono contenuto vuoto». `resolve_model_for_profile` in `global_config.py` ammette già `orcarouter/qwen/qwen3.8-flash`: un routing su modello streaming-only con backend `stream: false` sarebbe un fallimento silenzioso (200 vuoto) anziché errore esplicito, la classe peggiore per un gateway. Stesso pattern delle voci flag `dynamic_tools`/`prefix_caching`/`context_cache`.
  - Acceptance: flag `streaming_only` nei profili/modelli di `global_config.py`; il resolver o il validatore di frontiera forza `stream=True` (o rifiuta con errore esplicito e motivato) quando il modello selezionato ha il flag; unit test che asserisce la modalità imposta.

- [ ] Accumulo dei delta streaming per `tool_calls` e JSON Mode prima del parsing `#feature` · P2 · Gateway Core
  - Perché utile: doc §Streaming with tool calls: gli argomenti arrivano come stringhe JSON parziali in `tool_calls[i].function.arguments`, da concatenare per `index` e passare a `json.loads` solo a stream terminato; con thinking mode il flusso emette tre fasi (token di thinking → delta tool → risposta finale). Corollario §FAQ JSON Mode: con `response_format: {"type":"json_object"}` + `stream` solo l'output concatenato è JSON valido — quindi in Cache L1 va messa la risposta completa concatenata, non i chunk (si aggancia alla voce P0 dichiarazioni/tool).
  - Acceptance: helper di accumulo (`dict` per `tc.index`, parsing solo a fine stream) usato dal backend streaming; unit test con fixture che frammenta gli argomenti di due tool call parallele su ≥3 chunk; nessuna invocazione di parsing su chunk singolo.

- [ ] Vincoli deployment SSE del serving documentati nel serving spec (proxy buffering, pool, fd) `#docs` · P2 · Gateway Core
  - Perché utile: doc §Notes: senza `proxy_buffering off` su Nginx gli eventi SSE vengono bufferizzati e lo streaming si manifesta come rallentamento percepito, vanificando il beneficio sui timeout; ad alta concorrenza vanno dimensionati i pool di connessione e monitorati i file descriptor. Il layer di serving HAL che espone `/chat/completions` (contexto `hal_system2`, `benchmark/README.md`) deve portare questi vincoli prima di abilitare il percorso streaming.
  - Acceptance: nota con `proxy_buffering off`, dimensionamento pool/fd e sentinella `data: [DONE]` come contratto di terminazione in `docs/23_serving_speculativo.md` (o nuovo `docs/` dedicato) e referenziata dalla voce streaming P1.

## Già fatto

_(Buffer pre-flush in formato Keep a Changelog: sotto `### Added`, `### Changed`, `### Fixed` o `### Removed`; `/todo` lo svuota nel CHANGELOG.)_

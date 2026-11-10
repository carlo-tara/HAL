---
name: laya
version: 1.10.1
description: >-
  Reason why: senza un modello System 1 veloce e a basso costo per routing, scelte discrete, scoring euristico, stima di confidenza e chiarezza del contesto, l'agente spreca ragionamento su decisioni preliminari. Interfaccia per Laya System 1: routing di categorie, choice tra opzioni, score euristico di rischio o aderenza, confidence 0-100%, context 0-100%, noul. Invocabile via CLI python3 router.py, modulo Python router o come tool MCP in Zed (mcp_laya.py).
---

# Laya — System 1 Service

Skill per l'interazione con **Laya**, il modello **System 1** integrato in HAL.

## Architettura Cognitiva HAL

HAL adotta una separazione rigorosa a due livelli:

1. **System 1 (Laya)**:
   - Modello veloce, reattivo, a basso costo e ad alta efficienza.
   - Compiti: categorizzazione iniziale, instradamento (routing), scelta discreta tra percorsi equivalenti (choice), attribuzione di punteggio euristico (score), pre-elaborazione (noul).
   - Invocazione: via CLI (`python3 router.py ...` o `HAL/router.py`) o importando `router` in Python.

2. **System 2 (Agente / Active Reasoning Model)**:
   - Modello di ragionamento ad alta capacità (es. Gemini / Claude / GPT) attivo in Zed / Cursor.
   - Compiti: pianificazione strategica, comprensione profonda del codice, scrittura e modifica file, refactoring, esecuzione test, verifica semantica.

---

## Quando consultare Laya (System 1)

L'agente deve consultare Laya ogni volta che si presenta un compito preliminare di:

- **Triage e Routing**: assegnare un file, una richiesta o un problema a una categoria/rotta (`python3 router.py routing "..." --routes ...`).
- **Scelta discreta**: scegliere tra un set definito di opzioni o strategie operative (`python3 router.py choice "..." --options ...`).
- **Valutazione di rischio o aderenza**: ottenere uno score 0-1 rispetto a un criterio specifico (`python3 router.py score "..." --criteria ...`).
- **Valutazione di confidenza**: stimare la confidenza (0-100%) di una risposta a un quesito o dato (`python3 router.py confidence "..."`).
- **Valutazione del contesto**: stimare la chiarezza e completezza (0-100%) del contesto fornito (`python3 router.py context "..."`).
- **Pre-filtro**: ridurre opzioni prima di una pianificazione approfondita di System 2.

## Quando NON usare Laya (riservato a System 2)

- Modifica, generazione o refactoring del codice.
- Creazione o manipolazione di file nel workspace.
- Esecuzione ed interpretazione di test suite o verifiche deterministiche (`make test-unit`, `check-parity`, ecc.).
- Decisioni architetturali vincolanti che richiedono piena coerenza di contesto.

---

## Tabella di delega — cosa può chiudere System 1

Derivata dalla telemetria 2026-10-11→30 (`laya_calls`, esiti calibrati, benchmark S1/S2 su coding/math/reasoning/source/translation). Costo S1: 0 € (GPU locale), ~4,5 ms in cache / ~1 s in inferenza, contro decine di secondi di System 2.

**✅ Verde — delega con esecuzione diretta**
- `noul` / pre-filter di intent sulle richieste grezze degli agenti (189/189 outcome `correct`; cache ~90% a 4,5 ms).
- Choice binaria/ternaria (k≤3) con `margin ≥ 0.5`.
- Preflight di workflow: proposta task_family/contract, normalizzazione, attachment filtering (Strategy D) — family_confidence 0,97–0,9999 su coding/translation.
- Ripetizioni in cache di verdetti già visti (sub-5 ms, zero token).

**⚠️ Giallo — solo con gate, mai diretto al primo pass**
- Choice 4–5 opzioni: diretto solo con ensemble `top1 ≥ 0.8`; altrimenti `accept_with_caution` + check deterministico a valle.
- Stime `confidence`/`context`: campioni di esito ancora esigui — segnale debole, mai prova.

**❌ Rosso — resta su System 2**
- Routing su etichette tecniche italiane con ≥5 rotte: 48% dei verdetti sotto `confidence` 0,3 e input troncati nel 33% dei casi.
- `score`/rischio: non discriminativo (bypass documentato `NON_DISCRIMINATIVE_TASKS`).
- Matematica e ragionamento numerico: preflight conf 0,062.
- Per contratto: codice, file, test, decisioni architetturali vincolanti.

## Interfaccia CLI

L'interfaccia principale da terminale è `python3 router.py`:

```bash
# 1. Routing
python3 router.py routing "<testo>" --routes "<rotta1>, <rotta2>, <rotta3>"
# con output JSON:
python3 router.py routing "<testo>" --routes "<rotta1>, <rotta2>" --json

# 2. Scelta discreta (Choice)
python3 router.py choice "<prompt o domanda>" --options "<opzione1>, <opzione2>"
python3 router.py choice "<prompt>" --options "<opzione1>, <opzione2>" --json
# routing/choice --json espone il gate: margin, top1_prob, recommendation, passes, request_hash

# 3. Score euristico
python3 router.py score "<testo da valutare>" --criteria "<criterio>"
python3 router.py score "<testo>" --criteria "<criterio>" --json

# 4. Confidenza (0-100%)
python3 router.py confidence "<testo o domanda>"
python3 router.py confidence "<testo o domanda>" --json

# 5. Contesto (0-100%)
python3 router.py context "<testo o contesto>"
python3 router.py context "<testo o contesto>" --json

# 6. Noul
python3 router.py noul "<testo>"
```

## Uso via Zed MCP tool

Oltre alla CLI, Laya è esposta in Zed come **context server MCP**: `mcp_laya.py` (server JSON-RPC stdio senza dipendenze, wrapper di `laya_service.py` per i task su `/predict` e di `POST /systemone` per `noul`). Setup idempotente in `~/.config/zed/settings.json` via `python3 scripts/setup_zed_mcp.py` (parser JSONC-aware, backup one-shot `settings.json.bak-laya`).

- **Endpoint**: sempre DNS `laya.local` (env `LAYA_URL`, default nel codice), mai IP nudi.
- **Tool**: `laya_routing`, `laya_choice`, `laya_score`, `laya_confidence`, `laya_context`, `laya_noul`, `laya_outcome`, `laya_health`.
- **Esito decisioni** (`laya_routing` / `laya_choice`): `selected`, `margin`, `probabilities` e `recommendation` — `system1_direct` | `accept_with_caution` | `escalate_system2`. L'escalation (Strategy C) è decisione dell'agente System 2 che chiama: il tool non consulta mai L2 internamente.
- **`laya_noul`**: path GPU canonico `POST /systemone` `{task_type,text,params}`; budget proprio `LAYA_NOUL_TIMEOUT` (default 15 s vs media ~2 s; picchi 3–30 s da GPU contesa = eccezioni → su timeout retry una volta, poi escalate). Restituisce anche `request_hash` per la calibrazione via `/outcome`.
- **Calibrazione**: `laya_routing`/`laya_choice` (via eco `request_hash` ora presente anche su `/predict`) e `laya_noul` restituiscono `request_hash`; `laya_outcome` registra il verdetto `correct|incorrect` (+ `correction` opzionale) **oppure** il voto cieco `expected` (rv8: il server calcola `correct|incorrect` dal confronto con la scelta archiviata ed è mutuamente esclusivo con `outcome`, `400` su conflitto) su `POST /outcome` con Bearer. Il server salta le righe cache-hit e non sovrascrive righe già votate: una inferenza = un voto. Unica eccezione (T-33B98, gate steward risolto con ok esplicito 2026-11-09): il voto-a-verità-esterna `source='commit'` emesso dal protocollo `/commit` dopo commit riuscito sostituisce al più una volta un voto di autorità minore (implicit_s2/explicit/legacy), mai un altro commit. Per `laya_routing` la verità esterna è il file/bersaglio realmente modificato dopo la decisione: voto cieco `laya_outcome(expected=<target>)` sull'eco `request_hash`.
- **Gate k-aware (rv7 c1, revoca v1.7.0; inversione T-73140, ok PO 2026-11-09)**: con k≥4 `system1_direct` **e** `accept_with_caution` non sono mai emessi — System 1 non è un decisore su quelle famiglie: ordina (campo `shortlist` top-2 con probabilità, `laya_gate.top_shortlist`) e la selezione finale è sempre System 2; `selected`/`choice` restano per compatibilità come testa deprecata della shortlist. `laya_routing`/`laya_choice` forzano il secondo pass (`fresh=true`, istruzioni canoniche ⇒ `request_hash` norm identico) e lo dichiarano in `notes` con `flipped` se i due pass divergono. `LAYA_FAMILY_ESCALATION_OVERRIDES` (liste di famiglie, lettura env live) forza `escalate_system2` senza toccare codice.
- **Voto implicito System 2**: l'escalation di `smart_choice`/`smart_route` (CLI/gateway) registra il verdetto L2 come outcome sulla riga del primo pass via `/outcome` (`LAYA_IMPLICIT_VOTES=0` disattiva).
- **Strategy B al confine**: >5 opzioni → errore con hint di raggruppamento; 5 opzioni → truncation diversificata a 4 con nota; label >30 caratteri → warning.
- **Campi rv7/rv8 nel payload**: `degraded_context` (true quando `usage.truncated`/`state_tokens_dropped` — verdetto computato su contesto ridotto), `calibrated_confidence` (accuracy empirica per famiglia×banda dalla tabella di `make telemetry-report ARGS=--write-table`, `LAYA_CALIBRATION_TABLE`; `null` se tabella assente o voti insufficienti — la grezza resta nel campo `margin`/`probabilities`), `flipped` (solo a 2 pass), `shortlist` (k≥4: top-2 ordinata, campo autoritativo per S2 — T-73140). Le risposte cache-hit del servizio espongono `retried`; i corpi freschi riportano il `model` richiesto (rv8 f2).
- **Igiene stdio**: stdout trasporta solo frame JSON-RPC; i warning di `laya_service` vanno su stderr. Su errore di qualsiasi tool, chiamare `laya_health` prima di dichiarare disservizio (Diagnosi ABSTAIN).
- **Gate**: `make mcp-test` (unit tool + setup JSONC + contratto di questa sezione); suite completa del servizio con `make test`.

## Best Practices per Agenti (Ottimizzazione L1)

Per massimizzare la confidenza e l'efficacia di Laya, la skill `smart_choice` implementa automaticamente le seguenti strategie:

### Strategy A — Multi-question Anchoring

Le decisioni complesse vengono ancorate a una domanda di categorizzazione preliminare nello stesso payload.

**Pattern:**

```bash
python3 router.py routing "<testo>" --routes "<rotta1>, <rotta2>"
# Prima di System 2, verificare:
python3 router.py confidence "<testo categorizzato>"
```

**Telemetria:** `python3 scripts/token_budget.py log s1_call` dopo ogni routing.

### Strategy B — Semantic Pacing

Evitare più di 5 opzioni e usare descrizioni di criteri con alta distanza semantica.

**Regole:**

- Max 5 opzioni per chiamata `choice` / `routing`.
- Se le opzioni sono > 5, raggrupparle semanticamente prima di chiamare Laya.
- Usare etichette brevi (< 30 caratteri) per ogni opzione.

**Telemetria:** `python3 scripts/token_budget.py log attachment_filter <original_count> <summary_length>` quando si troncano liste.

### Strategy C — Gate k-aware (top1_prob / margin)

La telemetria (8.091 chiamate `laya_calls`, 2026-10-11→30; estesa rv7 a n=94 voti family) falsifica la `confidence` entropica come soglia: il gate corretto è il **margine top-1/top-2** di `probabilities`; a k≥4 il margine stesso non separa più (37% anche a margin≥0,6) → il cap blocca `system1_direct` del tutto (rv7 c1).

| Opzioni | Diretto richiede | Se non diretto |
|---|---|---|
| 2–3 | `margin ≥ 0.5` (`LAYA_FAST_MARGIN`) | self-consistency (seconda passata con ordine invertito, vettori mediati); ensemble `margin < 0.15` → escalate |
| 4–5 | mai `system1_direct` con k≥4, a prescindere da top1 (rv7 c1: l'eccezione `top1 ≥ 0.8` è revocata — decision-family 37% anche a margin≥0,6) | self-consistency forzata (pass2 con `fresh=true` sul `request_hash` canonico); verdetto ≤ `accept_with_caution` |
| Routing | `margin ≥ 0.6` (`LAYA_ROUTE_FAST`); con k≥4 mai direct (rv7 c1) | banda `≥ 0.4` self-consistency (pass2 `fresh=true`), poi `escalate_system2` |

- I tool MCP applicano già il gate: `recommendation` non emette `system1_direct` su primo pass k≥4 a massa dispersa; il payload espone `margin`, `probabilities` e `thresholds.direct_min_top1`.
- **Sorgente canonico del gate**: soglie e helper (`verdict_directly_acceptable`, `decision_recommendation`) vivono in `laya_gate.py`; il gateway (`hal_gateway/laya_service.py`) lo importa via symlink, quindi CLI, tool MCP e gateway condividono per costruzione le stesse soglie.
- **Sorgente canonico del protocollo choice** (rv9): `laya_protocol.py` possiede il testo del formato opzioni/completion — decoro `**choice**` (`CHOICE_DECORATION`), trim-set del matcher derivato (`OPTION_TRIM_CHARS`), `extract_completion_text`/`match_option`/`format_predict_as_text`/`systemone_result`; engine (`laya_service.py`) e layer HTTP (`server.py`) delegano via re-export: shape e parsing non possono più divergere per convenzione.
- CLI `--json` su `routing`/`choice` espone `margin`, `top1_prob`, `recommendation`, `passes`, `request_hash`: usa quelli, non la `confidence`, per il branch.
- **Voto implicito**: quando il percorso CLI/gateway escala a System 2 e L2 risponde, il suo verdetto viene registrato come outcome calibrato (`POST /outcome`: `correct` se concorde, `incorrect`+`correction` se no) sulla riga d'inferenza del primo pass. Disattivabile con `LAYA_IMPLICIT_VOTES=0`. L2 è configurabile via `SYSTEM2_URL`/`SYSTEM2_MODEL`/`SYSTEM2_API_KEY`; `_read_completion` + `_extract_completion_text` tollerano JSON e SSE fermandosi al terminatore del flusso (`[DONE]`/`finish_reason`): l'orchestratore locale (:8910) può tenere aperta la connessione anche dopo la fine della risposta, quindi non usare mai `response.read()` intero. Se L2 non risponde, nessun voto: comportamento atteso, non disservizio.

**Pattern:**

```bash
rec=$(python3 router.py choice "<testo>" --options "a,b,c" --json | grep -oP '"recommendation":\s*"\K[^"]+')
case "$rec" in
    system1_direct)     # verdetto usato così com'è ;;
    accept_with_caution) # accettato ma verificato con un check deterministico a valle ;;
    escalate_system2)   # decisione passa a System 2 ;;
esac
```

**Telemetria:** `python3 scripts/token_budget.py log s1_call` o `s2_call` in base al branch.

### Strategy D — Attachment Filtering

Liste lunghe di allegati o file vengono riassunte (es. "15x .JPG") per ridurre il rumore testuale.

**Regole:**

- Non elencare mai più di 5 elementi nello stesso payload.
- Riassumere: "N x .estensione" per gruppi omogenei.
- Mantenire solo i nomi rilevanti per la decisione corrente.

**Telemetria:** `python3 scripts/token_budget.py log attachment_filter <original_count> <summary_length>`.

---

### Middleware di sistema

Laya include middleware che:

- **Validano il payload** segnalando pattern a bassa confidenza (troppe opzioni).
- **Migliorano il prompt** chiamando System 2 se l'input è ambiguo, troppo corto o "caricato".

Se eseguito all'interno di script o runtime Python in HAL:

```python
from router import handle_choice, handle_routing, handle_score, handle_confidence, handle_context, handle_noul

scelta = handle_choice("strategia", ["opt1", "opt2"])
rotta = handle_routing("richiesta", ["docs", "agents", "infra"])
punteggio = handle_score("snippet", "rischio_regressione")
conf = handle_confidence("quanti abitanti ha Milano?")
ctx = handle_context("richiesta utente con dettagli...")
```

---

## Diagnosi rapida — ABSTAIN / GPU

- Prima di dichiarare «servizio non raggiungibile»: verificare path canonico `/var/www/hal_system1/router.py` (il vecchio `/var/www/HAL` è morto), `GET http://127.0.0.1:8091/health`, `docker ps --filter name=laya-gpu`.
- Righe `log.sqlite` con `error_message` `[Errno 32] Broken pipe` su `/systemone`: il client ha mollato per primo (timeout troppo basso vs inferenza GPU), non disservizio. Budget client ≥ p99 della funzione più lenta (`noul`: ~2 s media, picchi 3–30 s; hal_system2 `LAYA_TIMEOUT=3`).
- Check GPU a 4 livelli: env `LAYA_DEVICE=cuda`; boot log `laya ready device=cuda` (nessun `falling back to cpu`); `/health` con `cuda.available=true` e `allocated_gb>0` (tensor nel processo server); util `nvidia-smi` >0% sotto carico.
- `LAYA_K2_CPU` (default `0`): seam backend rv9 — con `1` le domande binarie k=2 sono deviate su CPU (GPU riservata a k≥3 e model load). Finché il gate umano non ha fatto benchmark + parity ≥20 casi il flag resta `0` = comportamento invariato; con `1` e backend CPU non inizializzato la richiesta risponde `500 {"error": "cpu backend not initialized…"}`: segnale atteso di gate, non disservizio — lato client trattalo come escalate.
- `/health` con `device: "cpu"` = fallback attivo dopo carico CUDA fallito (`load_router` in `server.py`): indagare con `docker logs laya-gpu`.
- **Contratto endpoint**: `/v1/predict` (richiede `Authorization: Bearer`) accetta solo nativo `{state,questions}` o shorthand `{text}` (→ intent-only); i campi `{task,routes,options,criteria}` sono lì ignorati → `invalid_*` NON è disservizio. Il task endpoint canonico è `POST /systemone` `{task_type,text,params}` (localhost, senza auth) → `{"result":{choice,confidence,probabilities},"request_hash"}`. Client HAL referenziale: `/var/www/hal_system1/laya_service.py` (nativo `{state:{notes,language},questions}` + atteso pesato per lo score).
- **`score` by-pass**: `NON_DISCRIMINATIVE_TASKS` risponde `{"bypass":true,"reason":"score_not_discriminative"}` (misurato: distribuzione identica per testi benigni/iniettivi/harmful) → astensione documentata, mai fabricare punteggi.
- **Runtime container**: `laya-gpu` gira **Python 3.10.12** (`docker exec laya-gpu python3 --version`) — nei fix dei warning lint non introdurre `datetime.UTC` (3.11+): usare l'alias `_UTC = datetime.timezone.utc` con `# noqa: UP017` su riga singola; `removesuffix()` (3.9+) e' ammesso.
- **Log canonico**: `/var/www/hal_system1/log.sqlite`; in HAL `/var/www/laya/log.sqlite` è una directory vuota (sqlite3 «unable to open database file» ≠ DB corrotto).
- Verdetti con `confidence < 0.3` → escalation System 2 (Strategy C); su etichette tecniche italiane il routing può essere inaffidabile (sonde 2026-10-29: conf 0.02–0.63) — non usare verdetti a bassa confidenza come prova.

# Benchmark System 1 / System 2 — handoff da hal_system2

Specchio operativo del runner benchmark di **HAL System 2**.
Sorgente canonica del codice: `/var/www/hal_system2` (`app/benchmark_models.py`,
`app/system2_metrics.py`, `config/benchmark-*.json`, `scripts/generate_benchmark_report.py`,
`docker-compose.benchmark.yml`). Ogni modifica al runner va fatta nel progetto canonico e
poi risincronizzata qui; questa cartella serve da base di esecuzione e archivio storico
per hal_gateway.

## Struttura

| Percorso                               | Contenuto                                                                                 |
| -------------------------------------- | ----------------------------------------------------------------------------------------- |
| `runner/`                              | Copia dei moduli `benchmark_models.py` + `system2_metrics.py` (pacchetto eseguibile)      |
| `config/`                              | `benchmark-models.json` (catalogo modelli) e `benchmark-prompts.json` (5 test)            |
| `scripts/generate_benchmark_report.py` | Generatore `report.htm` (D3.js), anche in modalità `--confronto`                          |
| `docker-compose.benchmark.yml`         | Compose di riferimento (build dal contesto hal_system2)                                   |
| `history/`                             | Storico run: cartelle `yyyymmdd_id` + baseline `results.json` + `system2_metrics.sqlite3` |

## Convenzioni (obbligatorie)

- Cartella di run: `yyyymmdd_id` (es. `20261019_1`). `--run-dir` rifiuta cartelle esistenti.
- File per risultato: `NN_<test>_<model>.json` (es. `01_ragionamento_logico_qwen2.5_1.5b.json`);
  il nome include il modello. Output `.htm` del test `programmazione` (Sudoku) accanto al JSON.
- Tutte le run di uno stesso confronto vanno raccolte in un'unica cartella.

## Prerequisiti

- **Ollama** attivo su `http://127.0.0.1:11434` con i modelli del catalogo
  (attuale: `phi3:mini`, `qwen2.5:1.5b`, `llama3.2:3b`, `llama3.2:1b`).
- **Laya (System 1)** attivo su `http://127.0.0.1:8091` per run con `--system1`.
- Variabili d'ambiente (o `--env-file`): `OLLAMA_BASE_URL`, `OLLAMA_API_KEY`,
  `GOOGLE_API_KEY`/`LLM_API_KEY` (provider google), `LAYA_URL`, `LAYA_API_KEY`,
  `LAYA_TIMEOUT`, `LAYA_MIN_CONFIDENCE`, `LAYA_MODEL`, `BENCHMARK_TIMEOUT_SECONDS`,
  `SYSTEM2_METRICS_DB_PATH`.

## Lanciare una nuova run

### Modalità A — dal progetto canonico (consigliata)

```bash
cd /var/www/hal_system2
python3 -m app.benchmark_models \
  --run-dir events/benchmarks/20261019_2 \
  --output events/benchmarks/20261019_2/results.json \
  --system1 \
  --provider ollama \
  --metrics-db events/benchmarks/system2_metrics.sqlite3
```

### Modalità B — da questa cartella (mirror standalone)

```bash
cd /var/www/hal_gateway/benchmark
python3 -m runner.benchmark_models \
  --models config/benchmark-models.json \
  --prompts config/benchmark-prompts.json \
  --run-dir history/20261019_2 \
  --output history/20261019_2/results.json \
  --system1 \
  --provider ollama \
  --metrics-db history/system2_metrics.sqlite3
```

Nota: `--env-file` di default punta alla `.env` nella root del runner; qui passa
`--env-file /var/www/hal_gateway/.env` (oppure esporta le variabili).

### Filtri utili

- `--model phi3:mini` (ripetibile) — esegue solo i modelli indicati.
- `--prompt ragionamento_logico` (ripetibile) — esegue solo i test indicati.
- `--timeout 600` — timeout HTTP per operazione.
- `--refresh-models [--providers ollama google]` — aggiorna solo il catalogo.

### Via Docker (compose di riferimento)

Il file `docker-compose.benchmark.yml` replica quello di hal_system2: fa `build: .`
dal contesto hal_system2 (serve il suo `Dockerfile`) e monta `./config`, `./docs`,
`./events/benchmarks`. Per lanciare:

```bash
cd /var/www/hal_system2
docker compose -f docker-compose.benchmark.yml run --rm benchmark \
  -- --run-dir /app/events/benchmarks/20261019_2 --output /app/events/benchmarks/20261019_2/results.json --system1 --provider ollama
```

## Vincoli operativi

- `--run-dir` deve non esistere; `--output` deve trovarsi direttamente dentro `--run-dir`.
- `--cooldown SECONDI` mette una pausa tra un modello e il successivo (default 0, nessuna pausa dopo l'ultimo): una sola cartella di run, quindi il generatore funziona senza aggregazione manuale. Le run storiche fino a `20261020_2` usavano invece una run per modello con `sleep` (generatore su cartella piatta: non legge le sottocartelle).
- Per lanciare in background usare `setsid` (un `nohup ... &` lanciato dalla shell del tool termina con la shell).
- Generatore, runner e metriche esistono in due copie: la sorgente è `hal_system2`, il gateway è un mirror. `bash benchmark/scripts/sync_hal_system2.sh check` verifica (exit 1 se divergono), `apply` copia canonico → gateway. Modificare sempre prima `hal_system2`.
- I test del runner stanno in `hal_system2/tests/test_benchmark_models.py`; nel gateway c'è solo una guardia (`tests/test_runner_token_gating.py`). Le run lanciate da `hal_system2` usano la copia di `hal_system2`.
- In `source_chunks` l'assemblaggio è locale quando meccanico (`assemble_segments_locally`: traduzione concatenata, segmento unico, estrazione JSON con segmenti validi unita in un array); altrimenti resta la chiamata al modello. Il tetto opzionale per segmento è `--segment-max-tokens`. La copia del gateway è un mirror: la logica canonica è in `hal_system2/app/`.
- I test `estrazione_json` e `sintesi_traduzione` leggono `docs/Pensieri_lenti_e_veloci.epub`, presente in `hal_system2/docs/` e assente in `benchmark/docs/`. Con la Modalità B serve un symlink temporaneo `benchmark/docs` → `/var/www/hal_system2/docs`: va rimosso a fine run e non committato; senza, il runner si ferma all'avvio con `File non trovato`.
- Lo strumento di scrittura del progetto accetta solo percorsi in `hal_gateway`: le modifiche a `hal_system2` vanno fatte via terminale.

## Telemetria (token per stage)

La telemetria viva è `hal_system2/events/benchmarks/system2_metrics.sqlite3` (la copia in `history/` è un'istantanea più vecchia). Aprirla in sola lettura, ad esempio `sqlite3.connect("file:<path>?mode=ro", uri=True)`.

- Tabella `system2_workflow_events`: `run_id` è un UUID, non il nome della run; per datare le run usare `timestamp`.
- Gli eventi `system1` (`preflight_laya`) non hanno token; i token sono solo negli stage `system2` (`segmento_N`, `assemblaggio_finale`, `risposta_finale`).
- `--timeout` (default 600 s) vale per **singola chiamata HTTP**; `seconds` nei JSON di test è la durata dell'intero workflow, quindi può superare il timeout (es. 1172 s = stage riusciti + 600 s dello stage in timeout).
- Gli stage in errore (timeout) non registrano token, quindi il costo dei retry non è misurabile da qui.
- `System2Metrics.get_token_breakdown(run_id=None)` restituisce token per categoria (segmenti, assemblaggio, risposta singola) e `wasted_tokens`: token spesi da stage riusciti in workflow che poi hanno avuto uno stage fallito (output scartato).

## Report e confronti

```bash
cd /var/www/hal_gateway/benchmark
python3 scripts/generate_benchmark_report.py history/20261019_2 \
  --confronto history/20261017_2
```

Scrive `report.htm` dentro la cartella della run (grafici D3.js: token, tempi, qualità;
con `--confronto` mostra i delta rispetto alla baseline nominata dalla cartella).

## Storico incluso in `history/`

| Cartella                                 | Contenuto                                                                                                                                                                                                                                                                                                                                                                                                                                             | Stato                                     |
| ---------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------- |
| `results.json` (root)                    | Baseline storica completa: 7 modelli × 5 test = 35 risultati, senza middleware                                                                                                                                                                                                                                                                                                                                                                        | completa                                  |
| `20261017_all/`                          | Run baseline 7 modelli × 5 test (senza `--system1`), con `report.htm`                                                                                                                                                                                                                                                                                                                                                                                 | completa                                  |
| `20261017_2/`                            | Run middleware System1/System2 **versione vecchia**, 7 modelli × 5 test, con `report.htm`                                                                                                                                                                                                                                                                                                                                                             | completa                                  |
| `20261019_1/`                            | Run gating **nuovo** (task-aware + telemetria SQLite), 4 modelli Ollama rimasti; interrotta a 8/20 (`status: running`). `report.htm` rigenerato con `--confronto 20261017_2`                                                                                                                                                                                                                                                                          | **incompleta**                            |
| `20261020_1/`                            | Run gating **nuovo** con Laya su **GPU**, pausa 300 s tra le run (una per modello), 4 modelli × 5 test: 19/20 ok, 1 timeout su `qwen2.5:1.5b`. Report con executive summary e confronto con `20261019_3`. Layout: sottocartelle per modello + copia piatta dei JSON per test (il generatore non legge le sottocartelle)                                                                                                                               | completa, con 1 errore                    |
| `20261020_2/`                            | Ripetizione di `phi3:mini` e `llama3.2:3b` con le stesse condizioni di `20261020_1` (Laya su GPU, pausa 300 s): 9/10 ok, 1 timeout su `phi3:mini` (`estrazione_json`). Report con executive summary e confronto con `20261020_1`. Layout come sopra                                                                                                                                                                                                   | completa, con 1 errore                    |
| `20261019_3/`                            | Run gating **nuovo** con Laya su CPU e cooldown, una run per modello (`phi3_mini`, `qwen2_5_1_5b`, `llama3_2_3b`, `llama3_2_1b`): 19/20 ok, 2 timeout su `qwen2.5:1.5b`. `report.htm` con executive summary e confronto con `20261017_2`                                                                                                                                                                                                              | completa, con 2 errori                    |
| `20261021_1/`                            | Run gating **nuovo** con Laya su **GPU**, pausa 180 s (`--cooldown 180`), 4 modelli × 5 test: 19/20 ok, 1 timeout su `qwen2.5:1.5b` (`sintesi_traduzione`). Report con executive summary e confronto con `20261020_1`. Una sola cartella piatta, senza sottocartelle                                                                                                                                                                                  | completa, con 1 errore                    |
| `20261021_2/`                            | Prova mirata: `qwen2.5:1.5b` su `sintesi_traduzione` con `--timeout 1200` (una chiamata, pausa 180 s non applicabile): ok in 211,8 s, 8.919 token, qualità 1/2. Report con executive summary che confronta le sette run complete                                                                                                                                                                                                                      | completa                                  |
| `20261023_6/`                            | Run nativa middleware, mirror sincronizzato, 2 modelli × 2 test; diagnostica pre-fix: traduzioni single-pass senza fonte (369/334 token, `min_chars` fallito); phi3 estrazione in timeout; llama estrazione 21.099 token con `assemblaggio_finale`. Include log e report vs `20261023_5`                                                                                                                                                              | diagnostica, non valida                   |
| `20261023_7/`                            | Run nativa post-fix, 2 modelli × 2 test; 3/4 ok, phi3 estrazione in timeout. Entrambe le traduzioni passano `min_chars: 7500` (phi3 15.941 caratteri, 9.053 token; llama 12.887 caratteri, 7.893 token). Report e log; confronto vs `20261023_5`                                                                                                                                                                                                      | parziale, 1 timeout                       |
| `20261023_8/`                            | Run con prompt `estrazione_json_semplificato` (5 pagine, JSON rigido `{capitolo, riassunto}`): **assemblaggio locale CONFERMATO** su phi3 (`finish_reason: local_assembly`, tutti i 5 segmenti JSON valido, qualità 2/2). Phi3: 17.169 token (seg2=5.806, seg3=6.959 — output molto lungo); Llama: 7.258 token (0,79× baseline). Sintesi_traduzione phi3: **timeout 3600s** (critico; baseline 790s). Llama traduzione: 5.219 token (1,01× baseline). | assemblaggio locale confermato, 1 timeout |
| `system2_metrics.sqlite3`                | Telemetria System1/System2 delle run con `--system1`                                                                                                                                                                                                                                                                                                                                                                                                  | —                                         |
| `cloudflare-workers-ai-free-models.json` | Catalogo modelli Cloudflare (non referenziato dal runner)                                                                                                                                                                                                                                                                                                                                                                                             | archivio                                  |

### Lettura dei risultati

- `status: ok` ≠ risposta corretta: la qualità è una rubrica euristica (max 30 controlli).
- Confronti validi solo per coppie `(modello, test)` appaiate.
- Esito ad oggi: il nuovo gating riduce token (~−53%) e tempi (~−46%) vs il middleware
  vecchio, qualità ~piatta; resta sopra la baseline `20261017_all` per costo.
  La run `20261019_3` (4×5, una run per modello) conferma il miglioramento su phi3, llama3.2:3b e llama3.2:1b, ma resta sotto la baseline su phi3 e llama3.2:1b; vedi l'executive summary nel report.
- Confronto `20261023_7` vs baseline full-ctx `20261023_5` (`compare_tokens.py`): llama3.2:1b 14.305 → 29.815 token (2,08×) sulle due coppie; phi3:mini 7.656 → 9.053 (1,18×) sulla sola traduzione valida. Phi3 `estrazione_json` escluso per timeout. In `sintesi_traduzione` entrambe le risposte superano `min_chars: 7500`; la run conferma la traduzione, non l'assemblaggio locale perché il gate sceglie `single_pass`. In `estrazione_json` llama usa `assemblaggio_finale` via modello, non `assemblaggio_locale`; l'effetto dell'assemblaggio locale resta da misurare.

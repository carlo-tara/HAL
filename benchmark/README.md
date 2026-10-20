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
- Non esiste un'opzione di cooldown tra modelli. Per la pausa si usa una run per modello (`--model`), con `sleep` tra una run e l'altra; ogni run ha la sua cartella, quindi il generatore va eseguito su una cartella piatta con i JSON per-test (il generatore non legge le sottocartelle).
- Per lanciare in background usare `setsid` (un `nohup ... &` lanciato dalla shell del tool termina con la shell).
- `scripts/generate_benchmark_report.py` esiste in due copie (`benchmark/scripts/` e `hal_system2/scripts/`): modificarle insieme e verificare con `diff`.
- I test `estrazione_json` e `sintesi_traduzione` leggono `docs/Pensieri_lenti_e_veloci.epub`, presente in `hal_system2/docs/` e assente in `benchmark/docs/`.
- Lo strumento di scrittura del progetto accetta solo percorsi in `hal_gateway`: le modifiche a `hal_system2` vanno fatte via terminale.

## Report e confronti

```bash
cd /var/www/hal_gateway/benchmark
python3 scripts/generate_benchmark_report.py history/20261019_2 \
  --confronto history/20261017_2
```

Scrive `report.htm` dentro la cartella della run (grafici D3.js: token, tempi, qualità;
con `--confronto` mostra i delta rispetto alla baseline nominata dalla cartella).

## Storico incluso in `history/`

| Cartella                                 | Contenuto                                                                                                                                                                                                                                | Stato                  |
| ---------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------- |
| `results.json` (root)                    | Baseline storica completa: 7 modelli × 5 test = 35 risultati, senza middleware                                                                                                                                                           | completa               |
| `20261017_all/`                          | Run baseline 7 modelli × 5 test (senza `--system1`), con `report.htm`                                                                                                                                                                    | completa               |
| `20261017_2/`                            | Run middleware System1/System2 **versione vecchia**, 7 modelli × 5 test, con `report.htm`                                                                                                                                                | completa               |
| `20261019_1/`                            | Run gating **nuovo** (task-aware + telemetria SQLite), 4 modelli Ollama rimasti; interrotta a 8/20 (`status: running`). `report.htm` rigenerato con `--confronto 20261017_2`                                                             | **incompleta**         |
| `20261019_3/`                            | Run gating **nuovo** con Laya su CPU e cooldown, una run per modello (`phi3_mini`, `qwen2_5_1_5b`, `llama3_2_3b`, `llama3_2_1b`): 19/20 ok, 2 timeout su `qwen2.5:1.5b`. `report.htm` con executive summary e confronto con `20261017_2` | completa, con 2 errori |
| `system2_metrics.sqlite3`                | Telemetria System1/System2 delle run con `--system1`                                                                                                                                                                                     | —                      |
| `cloudflare-workers-ai-free-models.json` | Catalogo modelli Cloudflare (non referenziato dal runner)                                                                                                                                                                                | archivio               |

### Lettura dei risultati

- `status: ok` ≠ risposta corretta: la qualità è una rubrica euristica (max 30 controlli).
- Confronti validi solo per coppie `(modello, test)` appaiate.
- Esito ad oggi: il nuovo gating riduce token (~−53%) e tempi (~−46%) vs il middleware
  vecchio, qualità ~piatta; resta sopra la baseline `20261017_all` per costo.
  La run `20261019_3` (4×5, una run per modello) conferma il miglioramento su phi3, llama3.2:3b e llama3.2:1b, ma resta sotto la baseline su phi3 e llama3.2:1b; vedi l'executive summary nel report.

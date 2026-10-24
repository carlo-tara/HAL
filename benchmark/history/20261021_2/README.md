# Benchmark 20261021_2 — OrcaRouter diretto vs HAL System2

## Modelli testati

| #   | Modello        | Slug OrcaRouter      |
| --- | -------------- | -------------------- |
| 1   | Qwen 3.7 Flash | `qwen/qwen3.7-flash` |
| 2   | Qwen 3.8 Flash | `qwen/qwen3.8-flash` |
| 3   | GPT-6 Luna     | `openai/gpt-6-luna`  |

> **Claude Haiku escluso (23/10)**: `anthropic/claude-haiku-5.5` non esiste nel catalogo
> OrcaRouter (`404 model_not_found`, suggerimento `claude-haiku-4.5`); il sostituto
> `anthropic/claude-haiku-4.5` è rimasto `503 upstream_unavailable` per tutta la finestra
> di run su entrambi i percorsi. Voce rimossa dal config (cartella `excluded`),
> da ri-testare quando l'upstream Anthropic torna disponibile.

## Percorsi confrontati

1. **OrcaRouter diretto** — `POST https://api.orcarouter.ai/v1/chat/completions` con la chiave OrcaRouter, senza layer HAL.
2. **HAL System2** — `POST http://127.0.0.1:8910/v1/chat/completions` (servizio `hal_system2` locale): preflight Laya, routing e telemetria HAL, poi inoltro a OrcaRouter con la stessa chiave.

Stesso messaggio utente, stessa temperatura (0.6), `stream: false`, `Cache-Control: no-cache` su entrambi i percorsi.

## Metriche raccolte

- **Qualità**: rubriche euristiche da `config/benchmark-prompts.json` (17 check totali per modello).
- **Velocità**: tempo end-to-end per chiamata in secondi.
- **Consumo token**: input, output e totali riportati dal provider.

## Prerequisiti

1. Chiave OrcaRouter in `/var/www/hal_system2/.env` (`ORCAROUTER_API_KEY`).
2. Servizio HAL System2 attivo su `127.0.0.1:8910` (endpoint `/v1/chat/completions`).
3. EPUB sorgente in `/var/www/hal_system2/docs/Pensieri_lenti_e_veloci.epub`.

## Esecuzione

```bash
cd /var/www/hal_gateway
python3 benchmark/scripts/run_orcarouter_comparison.py \
  --run-dir benchmark/history/20261021_2/run \
  --models-file benchmark/config/benchmark-models-20261021_2.json \
  --cooldown 180
```

Ordine alternato per modello (HAL→diretto, diretto→HAL), pausa 180 s tra le run.
3 modelli × 2 percorsi × 5 prompt = 30 richieste (40 con Haiku nella run originale 22/10).

## Generazione report

```bash
python3 benchmark/scripts/generate_comparison_report.py benchmark/history/20261021_2/run_merged --run-id 20261021_2
```

Produce `report.htm` (esecutivo + grafici, autonomo) nella cartella della run.
`REPORT.md` in questa cartella è la versione markdown con executive summary dettagliato.

## Retry celle HAL (23/10)

Le 4 celle HAL fallite con `504` al vecchio timeout upstream di 60 s sono state rilanciate
dopo aver reso il timeout configurabile (`HAL_UPSTREAM_TIMEOUT_SECONDS=600`, rebuild
immagine + restart container):

```bash
python3 benchmark/scripts/retry_hal_cells.py \
  --run-dir benchmark/history/20261021_2/run_retry_hal \
  --source benchmark/history/20261021_2/run/results.json
python3 benchmark/scripts/merge_retry_20261021_2.py \
  --run benchmark/history/20261021_2/run \
  --retry benchmark/history/20261021_2/run_retry_hal \
  --out benchmark/history/20261021_2/run_merged
```

Risultato: 4/4 ok (111–423 s), matrice fusa 30/30 `completed` (Haiku escluso, celle
sostituite con traccia `superseded_error`).

## Struttura

```
benchmark/history/20261021_2/
├── run/                    ← run originale 22/10 (26/40: 4 celle 504, 10 Haiku 503) + report.htm
├── run_retry_hal/          ← retry 23/10 delle 4 celle 504 (4/4 ok) + results.json
├── run_merged/             ← matrice finale 30/30 (Haiku escluso) + report.htm  ← REPORT di riferimento
├── run.log / run_retry_hal.log
├── REPORT.md               ← report con executive summary (matrice completa)
├── README.md               ← questo file
└── orcarouter_direct/      ← tentativo preliminare del 2026-10-22 fallito (404 slug errati), conservato per storia
```

## Note

- Temperatura fissa: 0.6, stream: false, Cache-Control: no-cache.
- Pausa tra le run: 180 s. Timeout client: 900 s.
- Il timeout upstream di HAL è configurabile: `HAL_UPSTREAM_TIMEOUT_SECONDS` in `/var/www/hal_system2/.env` (default 600 s dal 23/10, via `timeout_seconds` in `config/providers.yaml`). Durante questa run era 60 s hardcoded: i 4 `504` HAL sono di questo. Richiede rebuild immagine + restart container dopo la modifica.
- Gli ID dei prompt provengono da `config/benchmark-prompts.json` (ragionamento_logico, matematica, programmazione, estrazione_json, sintesi_traduzione).
- Lo status `wrong_model_served` può essere un falso positivo: OrcaRouter restituisce lo slug invece dell'ID catalogo; il runner normalizza già il valore.
- Errori `403 access_denied: token cycle spend limit reached` indicano esaurimento credito OrcaRouter (già accaduto nella run 20261021_8).

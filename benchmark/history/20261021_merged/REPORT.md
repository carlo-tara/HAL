# Confronto hal_system2 vs OrcaRouter diretto — 20261021_8

Versione con executive summary e grafici: [`report.htm`](report.htm) (autonoma, senza dipendenze esterne). Rigenerabile con `python3 benchmark/scripts/generate_orcarouter_report.py benchmark/history/20261021_8`.

**Esito: benchmark incompleto.** Solo 3 run su 8 hanno prodotto output valido.
Dalla quinta run in poi OrcaRouter ha risposto `403 access_denied: token cycle spend limit reached,
resets at 2026-10-26T00:00:00Z`. Le 25 richieste successive (Opus via HAL, GPT-6 Luna ×2,
GPT-6.1 Sol ×2) non hanno prodotto output e sono marcate `not_executed_spend_limit`.
Le richieste via HAL falliscono con `502 upstream_http provider_status 403`: dato che HAL inoltra a
OrcaRouter con la stessa chiave, la causa è il medesimo limite (inferenza, non verificata sul server HAL).

## Metodo

- Stessi 5 prompt e rubriche di `config/benchmark-prompts.json`; EPUB da `/var/www/hal_system2/docs/`.
- Stesso messaggio utente su entrambi i percorsi, `temperature` 0.6, `stream: false`, `Cache-Control: no-cache`.
- Percorsi: `hal_system2` (`http://127.0.0.1:8910/v1`, con preflight Laya, routing e telemetria) e
  `orcarouter_direct` (`https://api.orcarouter.ai/v1`).
- Ordine alternato per modello (HAL→diretto, diretto→HAL), 180 s tra ogni run (pause rispettate).
- **Percorso HAL = singola chiamata `/v1/chat/completions`**, non il workflow `source_chunks` del runner
  Ollama/Google. Non è stato confrontato Zed UI (non pilotabile da qui).
- Lo status `wrong_model_served` iniziale era un falso positivo: OrcaRouter restituisce lo slug
  (`claude-sonnet-5-5`) invece dell'ID catalogo. Corretto a posteriori in `results.json`;
  il runner contiene già la normalizzazione.

## Risultati validi

| Modello            | Percorso          | Prompt ok | Qualità rubriche | Tempo (solo ok) | Note                                                                                                 |
| ------------------ | ----------------- | --------- | ---------------- | --------------- | ---------------------------------------------------------------------------------------------------- |
| claude-sonnet-5.5  | hal_system2       | 4/5       | 11/11 sui 4 ok   | 110,96 s        | `programmazione`: 504 "Upstream provider timed out" a 60,0 s                                         |
| claude-sonnet-5.5  | orcarouter_direct | 5/5       | 17/17            | 167,51 s        | `programmazione` 76,2 s, 6/6                                                                         |
| claude-opus-5.5    | orcarouter_direct | 5/5       | 14/17            | 230,60 s        | `programmazione` 5/6 con 8192 token (probabile troncamento); `sintesi_traduzione` 0/2 con 1530 token |
| claude-opus-5.5    | hal_system2       | —         | —                | —               | non eseguito (limite di spesa)                                                                       |
| openai/gpt-6-luna  | entrambi          | —         | —                | —               | non eseguito (limite di spesa)                                                                       |
| openai/gpt-6.1-sol | entrambi          | —         | —                | —               | non eseguito (limite di spesa)                                                                       |

## Lettura

- Sonnet 5.5, prompt appaiati su 4 test: HAL è più lento su 3 prompt su 4 (HAL 9,1/5,3/42,2/54,3 s vs diretto 7,2/7,2/36,9/40,0 s,
  circa +22 % in totale); con una sola misura per cella lo scarto per singolo prompt è poco affidabile.
  Qualità identica (11/11 rubriche su entrambi i percorsi).
- Differenza strutturale rilevata: HAL ha un timeout upstream di 60 s (`httpx.AsyncClient(timeout=60.0)` in
  `app/providers/openai_compatible.py`) e ha fatto fallire il Sudoku, che direttamente richiede ~76 s.
  Anche Opus (99 s sul Sudoku) fallirebbe verosimilmente via HAL.
- Con n=1 per cella e temperatura 0.6 le differenze di token (es. 770 vs 444 sul primo prompt) sono rumore
  di campionamento, non effetto del percorso.
- **Nessun confronto è possibile per GPT-6 Luna e GPT-6.1 Sol**, né per Opus via HAL.

## Per completare

Dopo il ripristino del credito/limite sulla chiave OrcaRouter (reset previsto 2026-10-26 00:00 UTC),
rilanciare le sole run mancanti in una nuova cartella; le 3 run valide qui sopra restano riutilizzabili.
Stima: 5 run, ~4 pause da 180 s, circa 25–35 minuti.

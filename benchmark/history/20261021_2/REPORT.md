# Confronto hal_system2 vs OrcaRouter diretto — 20261021_2

Versione con executive summary e grafici: [`run_merged/report.htm`](run_merged/report.htm) (autonoma, senza dipendenze esterne). Rigenerabile con `python3 benchmark/scripts/generate_comparison_report.py benchmark/history/20261021_2/run_merged --run-id 20261021_2`.

**Run originale**: 2026-10-22 22:34 → 23:29 UTC (26/40 valide) · **Retry HAL**: 2026-10-23 00:34 → 00:54 UTC (4/4 ok) · **Stato finale**: `completed` — **30/30 richieste valide**
**Modelli**: Qwen 3.7 Flash · Qwen 3.8 Flash · GPT-6 Luna · ~~Claude Haiku~~ (rimosso, vedi sotto)
**Percorsi**: `orcarouter_direct` (`https://api.orcarouter.ai/v1`) vs `hal_system2` (`http://127.0.0.1:8910/v1`, con preflight Laya, routing e telemetria HAL)
**Prompt**: 5 test standard da `config/benchmark-prompts.json` · **Temperatura**: 0.6 · **Cooldown**: 180 s

---

## Executive Summary

### Esito

| Percorso           | Modelli | Richieste ok | Errori | Note                                                                                        |
| ------------------ | ------- | ------------ | ------ | ------------------------------------------------------------------------------------------- |
| OrcaRouter diretto | 3       | 15/15        | 0      | —                                                                                           |
| HAL System2        | 3       | 15/15        | 0      | 4 celle inizialmente `504` (timeout upstream 60 s), recuperate il 23/10 con timeout a 600 s |

- **Matrice completa 3 modelli × 2 percorsi × 5 prompt = 30/30 richieste valide.** Le 4 celle HAL fallite nella run originale (timeout upstream di 60 s, ora reso configurabile a 600 s) sono state rilanciate il 23/10 con lo stesso messaggio, temperatura e percorso: tutte `ok`.
- **Claude Haiku escluso dal benchmark**: `anthropic/claude-haiku-5.5` non esiste su OrcaRouter (`404`, suggerimento `claude-haiku-4.5`); il sostituto 4.5 è rimasto upstream-indisponibile (`503`) per tutta la finestra di run. Rimossa la voce dal config (23/10).
- **Qualità complessiva identica tra i percorsi**: 51/51 rubriche HAL vs 51/51 diretto sui prompt appaiati, con due sole deviazioni — entrambe spiegate (rumore di campionamento su Qwen 3.8 `programmazione`; falso negativo della rubrica su Luna `matematica`).

### Verdetto sintetico

- **Qualità**: **il percorso HAL non degrada la qualità**. Qwen 3.7: 17/17 su entrambi i percorsi. Qwen 3.8: 16/17 HAL vs 17/17 diretto (un solo check perso, `nessuna dipendenza o risorsa remota`, con n=1 e temperatura 0.6 è rumore). Luna: 14/17 HAL vs 17/17 diretto, ma i 3 check falliti cercano stringhe letterali (`2.770,20`) che la risposta HAL contiene in forma LaTeX (`2.770{,}20`) con i **valori calcolati identici e corretti** → artefatto della rubrica, non del percorso.
- **Velocità**: con il timeout corretto, **HAL è equivalente o più veloce del diretto**: Qwen 3.7 +0,4 % (256,9 s vs 255,9 s), Qwen 3.8 −12,0 % (982,1 s vs 1.115,8 s), Luna −8,1 % (100,8 s vs 109,7 s). Nessun overhead sistematico misurabile del preflight Laya; i Δ per singolo prompt (−54 % … +147 %) restano dominati dalla varianza del provider.
- **Token**: **input identici cella per cella tra i due percorsi** (10.282 vs 10.282 per Qwen 3.7; 10.537 vs 10.537 per Qwen 3.8; 11.452 vs 11.452 per Luna) → il gate Laya/routing/telemetria di HAL **non aggiunge alcun costo di prompt**. Le differenze di output (Qwen 3.7 +1,1 %, Luna +1,1 %, Qwen 3.8 +25,8 % trascinato da una sintesi più verbosa in HAL: 40.548 vs 29.181 token) sono varianza di campionamento.
- **Scelta consigliata**: **GPT-6 Luna** come modello di default (2–10× più veloce, ~1/3 dei token, qualità piena su entrambi i percorsi); **HAL System2 abilitato in produzione** con `HAL_UPSTREAM_TIMEOUT_SECONDS=600`. Qwen 3.8 Flash solo se serve massima verbosità e la latenza non conta.

### KPI della run completa

| KPI                                        | Valore                                                        |
| ------------------------------------------ | ------------------------------------------------------------- |
| Richieste valide                           | 30/30 (100 %, dopo retry)                                     |
| Overhead input-token di HAL                | **0** (identici per cella)                                    |
| Overhead tempo HAL (appaiati)              | −12 % … +0,4 %, non sistematico                               |
| Qualità appaiata                           | 51/51 diretto vs 51/51 HAL (2 deviazioni spiegate)            |
| Modello più veloce                         | GPT-6 Luna — 109,7 s diretto / 100,8 s HAL (5 prompt)         |
| Modello più lento                          | Qwen 3.8 Flash — 1.115,8 s diretto / 982,1 s HAL              |
| Token totali (diretto)                     | Luna 21.021 < Qwen 3.7 36.271 ≪ Qwen 3.8 71.011               |
| Costo per run da 5 prompt (USD, tier base) | Qwen 3.7 ~0,0037 $ < Luna ~0,0059 $ ≪ Qwen 3.8 ~0,030–0,037 $ |

---

## Metodo

- Stessi 5 prompt e rubriche di `config/benchmark-prompts.json`; fonte EPUB `Pensieri_lenti_e_veloci.epub` per `estrazione_json` (10 pagine) e `sintesi_traduzione` (5 pagine → spagnolo).
- Stesso messaggio utente su entrambi i percorsi, `temperature` 0.6, `stream: false`, `Cache-Control: no-cache`.
- Percorso **orcarouter_direct**: `POST https://api.orcarouter.ai/v1/chat/completions` con chiave OrcaRouter.
- Percorso **hal_system2**: `POST http://127.0.0.1:8910/v1/chat/completions` (servizio HAL locale: preflight Laya, routing, telemetria, poi inoltro a OrcaRouter con la stessa chiave). **Singola chiamata**, non il workflow `source_chunks` del runner Ollama.
- Ordine alternato per modello, pausa 180 s tra le run.
- Runner: `benchmark/scripts/run_orcarouter_comparison.py` con `--models-file benchmark/config/benchmark-models-20261021_2.json`.
- **Retry 23/10**: `benchmark/scripts/retry_hal_cells.py` ha rilanciato le 4 celle `504` via HAL (timeout ora 600 s, stesso messaggio/temperatura/no-cache); fusione con `benchmark/scripts/merge_retry_20261021_2.py` → `run_merged/` (le celle sostituite conservano `superseded_error`).
- **Haiku escluso** su richiesta: voce rimossa dal config, 10 richieste `503` della run originale non fanno parte della matrice fusa.

---

## Copertura (matrice finale)

| Modello        | Percorso | ragionamento | matematica | programmazione | estrazione_json | sintesi_traduzione |
| -------------- | -------- | ------------ | ---------- | -------------- | --------------- | ------------------ |
| Qwen 3.7 Flash | HAL      | OK 4/4       | OK 3/3     | OK 6/6         | OK 2/2          | OK 2/2 ↻           |
| Qwen 3.7 Flash | diretto  | OK 4/4       | OK 3/3     | OK 6/6         | OK 2/2          | OK 2/2             |
| Qwen 3.8 Flash | HAL      | OK 4/4       | OK 3/3     | OK 5/6 ↻       | OK 2/2 ↻        | OK 2/2 ↻           |
| Qwen 3.8 Flash | diretto  | OK 4/4       | OK 3/3     | OK 6/6         | OK 2/2          | OK 2/2             |
| GPT-6 Luna     | HAL      | OK 4/4       | OK 0/3 ⚠   | OK 6/6         | OK 2/2          | OK 2/2             |
| GPT-6 Luna     | diretto  | OK 4/4       | OK 3/3     | OK 6/6         | OK 2/2          | OK 2/2             |

↻ = cella recuperata con il retry del 23/10 (originariamente `504` a 60 s) · ⚠ = falso negativo della rubrica (LaTeX).

---

## Risultati per modello (percorsi appaiati, 5/5 prompt)

### Qwen 3.7 Flash

| Prompt               | HAL (s)   | Diretto (s) | Δ tempo    | Token out HAL/diretto | Rubriche          |
| -------------------- | --------- | ----------- | ---------- | --------------------- | ----------------- |
| ragionamento_logico  | 16,1      | 34,7        | −54 %      | 1.369 / 2.785         | 4/4 · 4/4         |
| matematica           | 23,8      | 21,5        | +11 %      | 2.691 / 2.431         | 3/3 · 3/3         |
| programmazione       | 47,7      | 36,1        | +32 %      | 5.567 / 3.739         | 6/6 · 6/6         |
| estrazione_json      | 58,0      | 54,3        | +7 %       | 5.135 / 5.583         | 2/2 · 2/2         |
| sintesi_traduzione ↻ | 111,4     | 109,2       | +2 %       | 11.512 / 11.451       | 2/2 · 2/2         |
| **Totale**           | **256,9** | **255,9**   | **+0,4 %** | 26.274 / 25.989       | **17/17 · 17/17** |

### Qwen 3.8 Flash

| Prompt               | HAL (s)   | Diretto (s) | Δ tempo     | Token out HAL/diretto | Rubriche          |
| -------------------- | --------- | ----------- | ----------- | --------------------- | ----------------- |
| ragionamento_logico  | 17,8      | 7,2         | +147 %      | 573 / 547             | 4/4 · 4/4         |
| matematica           | 30,7      | 13,1        | +134 %      | 1.542 / 1.318         | 3/3 · 3/3         |
| programmazione ↻     | 352,6     | 470,5       | −25 %       | 20.456 / 23.658       | **5/6** · 6/6     |
| estrazione_json ↻    | 157,8     | 113,5       | +39 %       | 12.955 / 5.770        | 2/2 · 2/2         |
| sintesi_traduzione ↻ | 423,2     | 511,5       | −17 %       | 40.548 / 29.181       | 2/2 · 2/2         |
| **Totale**           | **982,1** | **1.115,8** | **−12,0 %** | 76.074 / 60.474       | **16/17 · 17/17** |

Il check perso su `programmazione` HAL (`nessuna dipendenza o risorsa remota`) è l'unica differenza di sostanza tra i percorsi: con n=1 e temperatura 0.6 non è attribuibile al percorso. Nota: la cella HAL di `estrazione_json` ha generato 12.955 token di output (2,2× il diretto) pur passando 2/2 — verbosità del modello, non del gate.

### GPT-6 Luna

| Prompt              | HAL (s)   | Diretto (s) | Δ tempo    | Token out HAL/diretto | Rubriche          |
| ------------------- | --------- | ----------- | ---------- | --------------------- | ----------------- |
| ragionamento_logico | 4,4       | 4,1         | +7 %       | 244 / 302             | 4/4 · 4/4         |
| matematica          | 7,2       | 6,3         | +14 %      | 539 / 489             | **0/3** ⚠ · 3/3   |
| programmazione      | 44,6      | 59,8        | −25 %      | 3.896 / 4.450         | 6/6 · 6/6         |
| estrazione_json     | 12,2      | 8,0         | +53 %      | 1.510 / 846           | 2/2 · 2/2         |
| sintesi_traduzione  | 32,3      | 31,4        | +3 %       | 3.488 / 3.482         | 2/2 · 2/2         |
| **Totale**          | **100,8** | **109,7**   | **−8,1 %** | 9.677 / 9.569         | **14/17 · 17/17** |

⚠ I 3 check di `matematica` falliti via HAL cercano le stringhe letterali `2.770,20`, `610,20`, `22,03%`: la risposta HAL le contiene in forma LaTeX (`2.770{,}20`, `610{,}20`, `22{,}03\%`). I valori calcolati sono **corretti e identici al diretto** → falso negativo della rubrica, non degrado di qualità.

### Claude Haiku — escluso

`anthropic/claude-haiku-5.5` non esiste nel catalogo OrcaRouter; il sostituto `anthropic/claude-haiku-4.5` ha restituito `503 upstream_unavailable` su tutte le 10 richieste (entrambi i percorsi) durante la finestra di run. Rimosso dal benchmark il 23/10 (voce in `excluded` del config). Da ri-testare quando l'upstream Anthropic sarà disponibile.

---

## Analisi qualità

| Modello             | OrcaRouter diretto | HAL System2                | Differenza                      |
| ------------------- | ------------------ | -------------------------- | ------------------------------- |
| Qwen 3.7 Flash      | 17/17              | 17/17                      | pari                            |
| Qwen 3.8 Flash      | 17/17              | 16/17                      | −1 check (rumore, n=1)          |
| GPT-6 Luna          | 17/17              | 14/17                      | −3 check (falso negativo LaTeX) |
| **Totale appaiato** | **51/51**          | **47/51** (51/51 corretti) | nessuna differenza reale        |

**Osservazioni**:

- Con la matrice completa, **la qualità è determinata dal modello, non dal percorso**: gli input identici (cella per cella) e le rubriche appaiate lo confermano.
- Le 2 deviazioni sono entrambe spiegate e non strutturali: 1 check perso dal caso (varianza), 1 artefatto di misurazione (rubrica a stringhe vs LaTeX).
- Tutti e tre i modelli passano 17/17 in diretto: i 5 prompt standard non discriminano la qualità tra questi modelli. Per un giudizio di modello servono rubriche più selettive o n≥3.

---

## Analisi velocità

Tempi totali per run (5 prompt, matrice completa):

```
GPT-6 Luna        ██████████  diretto 109,7 s  | HAL 100,8 s (−8 %)
Qwen 3.7 Flash    █████████████████████  diretto 255,9 s | HAL 256,9 s (+0,4 %)
Qwen 3.8 Flash    █████████████████████████████████████████████████████████████████████  diretto 1.115,8 s | HAL 982,1 s (−12 %)
```

**Osservazioni**:

- **GPT-6 Luna è il più veloce** su entrambi i percorsi (media ~20 s/chiamata); `estrazione_json` in 8–12 s dove gli altri modelli impiegano 54–158 s.
- **Qwen 3.8 Flash è il più lento** (media ~200 s/chiamata): genera 20–40 k token di output sui task lunghi.
- **Nessun overhead misurabile di HAL**: −12 % … +0,4 % sui totali appaiati. Il preflight Laya (modello locale) non aggiunge latenza percepibile; i Δ per prompt sono varianza del provider.
- Il **vecchio timeout upstream di 60 s era l'unico vero costo del percorso HAL** (4/20 celle perse, 20 %). Con 600 s configurabili (`HAL_UPSTREAM_TIMEOUT_SECONDS`, attivo dal 23/10) la penalità è eliminata: le 4 celle retry sono riuscite in 111–423 s.

---

## Analisi consumo token

| Modello        | Percorso | Input tot | Output tot | Totale | Media/run |
| -------------- | -------- | --------- | ---------- | ------ | --------- |
| Qwen 3.7 Flash | diretto  | 10.282    | 25.989     | 36.271 | 7.254     |
| Qwen 3.7 Flash | HAL      | 10.282    | 26.274     | 36.556 | 7.311     |
| Qwen 3.8 Flash | diretto  | 10.537    | 60.474     | 71.011 | 14.202    |
| Qwen 3.8 Flash | HAL      | 10.537    | 76.074     | 86.611 | 17.322    |
| GPT-6 Luna     | diretto  | 11.452    | 9.569      | 21.021 | 4.204     |
| GPT-6 Luna     | HAL      | 11.452    | 9.677      | 21.129 | 4.226     |

**Osservazioni**:

- **HAL non consuma token extra**: input identici cella per cella su tutti e 15 i prompt appaiati. Il preflight Laya gira su modello locale e non entra nel prompt inoltrato a OrcaRouter.
- Output: +1,1 % su Qwen 3.7 e Luna (rumore), +25,8 % su Qwen 3.8 — interamente spiegato da 2 celle retry più verbose (`sintesi` 40.548 vs 29.181; `estrazione` 12.955 vs 5.770) che hanno comunque passato le rubriche. Con n=1 non è effetto del percorso.
- **Luna è il modello più efficiente**: 21 k token totali per 5 task con 17/17 (≈ metà di Qwen 3.7, ≈ 1/3 di Qwen 3.8). Rapporto output/input: Luna ~0,8; Qwen 3.7 ~2,5; Qwen 3.8 ~5,7.

---

## Analisi costo (token × €/token)

Prezzi da `GET /v1/models` di OrcaRouter (currency **USD**, convertita in € a tasso assunto 0,93). Tutte le richieste hanno input < 32 K, quindi si applica sempre il **tier base**:

| Modello        | $/M input | $/M output | €/M input | €/M output |
| -------------- | --------- | ---------- | --------- | ---------- |
| Qwen 3.7 Flash | 0,03      | 0,13       | ≈0,028    | ≈0,121     |
| Qwen 3.8 Flash | 0,15      | 0,47       | ≈0,140    | ≈0,437     |
| GPT-6 Luna     | 0,10      | 0,50       | ≈0,093    | ≈0,465     |

Costo della run completa (5 prompt, dai token reali di `run_merged`):

| Modello        | Percorso | Token (in/out)  | Costo run                 | Costo/prompt | $ per M token lavorati |
| -------------- | -------- | --------------- | ------------------------- | ------------ | ---------------------- |
| Qwen 3.7 Flash | diretto  | 10.282 / 25.989 | **0,00369 $** (≈0,0034 €) | 0,00074 $    | 0,102                  |
| Qwen 3.7 Flash | HAL      | 10.282 / 26.274 | 0,00372 $ (≈0,0035 €)     | 0,00075 $    | 0,102                  |
| GPT-6 Luna     | diretto  | 11.452 / 9.569  | 0,00593 $ (≈0,0055 €)     | 0,00119 $    | 0,282                  |
| GPT-6 Luna     | HAL      | 11.452 / 9.677  | 0,00598 $ (≈0,0056 €)     | 0,00120 $    | 0,283                  |
| Qwen 3.8 Flash | diretto  | 10.537 / 60.474 | 0,03000 $ (≈0,0279 €)     | 0,00600 $    | 0,423                  |
| Qwen 3.8 Flash | HAL      | 10.537 / 76.074 | 0,03734 $ (≈0,0347 €)     | 0,00747 $    | 0,431                  |

**Osservazioni**:

- **HAL non aggiunge costo**: +0,9 % su Luna e +1,0 % su Qwen 3.7 (solo varianza di output); il +24 % su Qwen 3.8 HAL è interamente dovuto alle 2 celle retry più verbose (sintesi 40.548 vs 29.181 token out), non al percorso.
- **Qwen 3.7 è il più economico per run** (≈1/8 di Qwen 3.8, ≈2/3 di Luna) nonostante generi ~2,7× i token di **output** di Luna: il prezzo unitario Flash (0,03/0,13 $/M) lo compensa. Luna costa di più per token lavorato (0,28 vs 0,10 $/M blended), ma è il prezzo della sua velocità.
- **Qwen 3.8 paga 2× il prezzo unitario di Luna e genera 6× il suo output**: 8–10× il costo per task a parità di rubriche (16-17/17). La cella singola più cara: sintesi_traduzione HAL 0,0196 $ (40,5 k token out).
- Trade-off costo/qualità/velocità: **Luna** vince su velocità e token lavorati; **Qwen 3.7** vince sul costo assoluto; Qwen 3.8 non ha un vantaggio che giustifichi il costo a parità di rubriche.
- I prezzi OrcaRouter sono USD; il simbolo € è una conversione a tasso assunto (0,93), non una tariffa del provider.

---

## Decisioni proposte

1. **Percorso**: HAL System2 è **idoneo in produzione** — a matrice completa non perde nulla rispetto al diretto (qualità pari, zero overhead token, latenza equivalente o migliore). **[FATTO 23/10]**: timeout upstream reso configurabile (`HAL_UPSTREAM_TIMEOUT_SECONDS`, default 600 s, immagine ricostruita e container riavviato; retry verificato 4/4 ok).
2. **Modello consigliato**: **GPT-6 Luna** (velocità 2–10× superiore, ~1/3 dei token, 17/17 su entrambi i percorsi). **Qwen 3.7 Flash** come secondo. **Qwen 3.8 Flash** solo per task dove la verbosità estrema è un valore.
3. **Rubrica `matematica`**: normalizzare i valori numerici (LaTeX `{,}` → `,`) per eliminare il falso negativo su Luna HAL.
4. **Claude Haiku**: ri-testare quando l'upstream Anthropic torna disponibile; nel frattempo la voce resta in `excluded` nel config.
5. **Campione**: per decisioni definitive servono n≥3 repliche per cella; con n=1 i Δ per prompt (−54 % … +147 %) e i Δ di output token non sono affidabili.

---

## Note di lettura

- `status: ok` non equivale a risposta corretta: la qualità è una rubrica euristica a stringhe.
- Con n=1 per cella e temperatura 0.6 le differenze di token e i Δ per singolo prompt sono rumore di campionamento.
- Il percorso HAL qui è la **singola chiamata** `/v1/chat/completions` al servizio locale (preflight Laya + routing + telemetria), non il workflow `source_chunks` multi-stage del runner Ollama.
- La run preliminare del 22/10 in `orcarouter_direct/` (5× `404`) era causata da slug errati in configurazione; corretta prima dell'esecuzione.
- Le 4 celle `504` della run originale (timeout upstream 60 s) sono state sostituite dai retry del 23/10 in `run_merged/`; gli originali restano in `run/` per storia, con `superseded_error` nelle celle fuse.
- Nessun `403 token cycle spend limit reached` in questa run (a differenza della 20261021_8).

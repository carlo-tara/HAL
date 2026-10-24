# Benchmark 20261021_2 — OrcaRouter diretto vs HAL System2

**Data**: 2026-10-22  
**Modelli**: Qwen 3.7 Flash · Qwen 3.8 Flash · Claude Haiku 5.5 · GPT-6 Luna  
**Percorsi**: OrcaRouter diretto (`orcarouter_direct`) vs HAL System2 (`hal_system2`)  
**Prompt**: 5 test standard (ragionamento_logico, matematica, programmazione, estrazione_json, sintesi_traduzione)  
**Temperatura**: 0.6 · **Timeout**: 600 s · **Cooldown**: 180 s  

---

## Executive Summary

> **Nota**: questo template va compilato dopo l'esecuzione dei benchmark. Le sezioni seguenti descrivono la struttura attesa e i criteri di valutazione.

### Panoramica esito

| Percorso | Modelli completati | Prompt totali | Successi | Errori | Tempo medio/chiamata |
|----------|-------------------|---------------|----------|--------|---------------------|
| OrcaRouter diretto | _da compilare_ | _da compilare_ | _da compilare_ | _da compilare_ | _da compilare_ |
| HAL System2 | _da compilare_ | _da compilare_ | _da compilare_ | _da compilare_ | _da compilare_ |

### Verdetto sintetico

- **Qualità**: _[compilare dopo aver analizzato le rubriche]_
- **Velocità**: _[compilare confrontando i tempi per modello]_
- **Token**: _[compilare confrontando input/output/total per percorso]_
- **Scelta consigliata**: _[compilare in base ai risultati]_

---

## Metodo

- Stessi 5 prompt e rubriche di `config/benchmark-prompts.json`.
- Stesso messaggio utente su entrambi i percorsi, `temperature` 0.6, `stream: false`, `Cache-Control: no-cache`.
- Percorso **OrcaRouter diretto**: chiamata singola `/v1/chat/completions` a `https://api.orcarouter.ai/v1`.
- Percorso **HAL System2**: stessa chiamata ma attraverso il gate Laya/System 1 (preflight task-aware) + telemetria SQLite.
- Ordine alternato per modello, pausa 180 s tra ogni run.
- Qualità valutata con rubriche euristiche (max 17 check per modello nei test completi).

---

## Risultati per modello

### Qwen 3.7 Flash

| Prompt | OrcaRouter diretto | HAL System2 | Differenza tempo |
|--------|-------------------|-------------|-----------------|
| ragionamento_logico | _tempo / token / qualità_ | _tempo / token / qualità_ | _%_ |
| matematica | _tempo / token / qualità_ | _tempo / token / qualità_ | _%_ |
| programmazione | _tempo / token / qualità_ | _tempo / token / qualità_ | _%_ |
| estrazione_json | _tempo / token / qualità_ | _tempo / token / qualità_ | _%_ |
| sintesi_traduzione | _tempo / token / qualità_ | _tempo / token / qualità_ | _%_ |

**Media qualità**: OrcaRouter _/5_ · HAL _/5_  
**Media tempo**: OrcaRouter _s_ · HAL _s_ (+_%_)  
**Media token**: OrcaRouter _in/out_ · HAL _in/out_ (+_%_)

### Qwen 3.8 Flash

_[stessa struttura di Qwen 3.7 Flash]_

### Claude Haiku 5.5

_[stessa struttura di Qwen 3.7 Flash]_

### GPT-6 Luna

_[stessa struttura di Qwen 3.7 Flash]_

---

## Analisi qualità

Tabella riepilogativa qualità per modello (checks superati / disponibili):

| Modello | OrcaRouter diretto | HAL System2 | Differenza |
|---------|-------------------|-------------|------------|
| Qwen 3.7 Flash | _da compilare_ | _da compilare_ | _±_ |
| Qwen 3.8 Flash | _da compilare_ | _da compilare_ | _±_ |
| Claude Haiku 5.5 | _da compilare_ | _da compilare_ | _±_ |
| GPT-6 Luna | _da compilare_ | _da compilare_ | _±_ |

**Osservazioni**:
- _[compilare: quali modelli hanno perso check, su quali prompt, motivi probabili]_
- _[compilare: pattern ricorrenti tra i due percorsi]_

---

## Analisi velocità

Grafico barre tempi medi per modello (solo chiamate ok):

```
Qwen 3.7 Flash    ████████████ OrcaRouter  XX.Xs  ████ HAL XX.Xs (+XX%)
Qwen 3.8 Flash    ████████████████ OrcaRouter  XX.Xs  ████ HAL XX.Xs (+XX%)
Claude Haiku 5.5  ████████ OrcaRouter  XX.Xs  ████████ HAL XX.Xs (+XX%)
GPT-6 Luna        ████████████████████ OrcaRouter  XX.Xs  ████ HAL XX.Xs (+XX%)
```

**Osservazioni**:
- _[compilare: quale percorso è più lento e di quanto]_
- _[compilare: differenze significative per singolo modello]_
- _[compilare: eventuali timeout o errori di timeout]_

---

## Analisi consumo token

Tabella token medi per modello:

| Modello | Percorso | Input avg | Output avg | Total avg |
|---------|----------|-----------|------------|-----------|
| Qwen 3.7 Flash | OrcaRouter | _X_ | _Y_ | _Z_ |
| Qwen 3.7 Flash | HAL | _X_ | _Y_ | _Z_ |
| Qwen 3.8 Flash | OrcaRouter | _X_ | _Y_ | _Z_ |
| Qwen 3.8 Flash | HAL | _X_ | _Y_ | _Z_ |
| Claude Haiku 5.5 | OrcaRouter | _X_ | _Y_ | _Z_ |
| Claude Haiku 5.5 | HAL | _X_ | _Y_ | _Z_ |
| GPT-6 Luna | OrcaRouter | _X_ | _Y_ | _Z_ |
| GPT-6 Luna | HAL | _X_ | _Y_ | _Z_ |

**Osservazioni**:
- _[compilare: HAL System2 usa più token per il preflight Laya?]_
- _[compilare: differenze di output tokens tra i due percorsi]_
- _[compilare: rapporto costo/qualità per ciascun modello]_

---

## Decisioni proposte

1. **Qualità**: _[compilare: le differenze sono significative o rumore di campionamento?]_
2. **Velocità**: _[compilare: il overhead di HAL System2 è accettabile?]_
3. **Token**: _[compilare: il consumo extra di HAL System2 giustifica i benefici?]_
4. **Modello consigliato**: _[compilare: quale modello offre il miglior trade-off]_
5. **Percorso consigliato**: _[compilare: diretto o HAL System2?]_

---

## Note di lettura

- `status: ok` non equivale a risposta corretta: la qualità è una rubrica euristica.
- Con n=1 per cella e temperatura 0.6 le differenze di token sono rumore di campionamento.
- Le pause di 180 s tra i modelli possono influenzare la latenza percepita.
- Lo status `wrong_model_served` può essere un falso positivo: OrcaRouter restituisce lo slug invece dell'ID catalogo.
- Eventuali errori `403 access_denied: token cycle spend limit reached` indicano esaurimento credito OrcaRouter.

# 25 — Scelta Task API vs Batch API per workload ad alto volume (System 1)

Regola discreta a basso costo cognitivo, destinata a `router.py choice`
(System 1 Laya) quando il servizio è disponibile; eseguita a mano (System 2)
finché la chiamata non è cablata nel job. Fonte: QwenCloud docs
«Async task management» (2026-10-28), voci `gateway_core` Task API e replay
`benchmark/`.

## Criteri di scelta

| Criterio | Task API | Batch API |
| -------- | -------- | --------- |
| Numero richieste | 1–poche, interattive | alto volume (> ~500 righe JSONL, fino a 50.000 / 500 MB) |
| Latency budget | secondi/minuti, esito serve subito | finestra 24h (configurabile fino a 336h), esito differito |
| Retention risultato | metadati+URL 24h | metadati+URL 30 giorni |
| Costo | prezzo standard | sconto ~50% |
| Modalità | multimodale (immagine/video), poll con backoff per modality | testi/embedding |

## Mappatura HAL (job bulk una-tantum)

- `cmd_distill` in `agents/a-knowledge/scripts/extract.py`: distillazione
  capitolo-per-capitolo, 3+ richieste con prefisso lungo per libro → **candidato
  Batch** oltre la soglia di volume ( JSONL, esito in 24h, −50% ); sotto soglia
  resta Task API. Lo stub porta la nota in linea.
- Replay `benchmark/`: suite di prompt ripetuti non interattiva → **Batch**;
  i runner di warm-up restano Task API (esito serve nel run).
- Vincolo sempre valido (regola protocollo § contesto, dichiarazioni, cache):
  submit → poll terminale → persist immediato; mai conservare solo l'URL del
  provider (retention 24h/30g). La scelta del pattern non cambia la persistenza.

## invocazione System 1

`python3 router.py choice "job: <n richieste>, latency budget: <X>, risultato
serve entro: <window>" --options "task-api,batch-api"` — con `ABSTAIN` (S1 non
disponibile) decide la tabella qui sopra (System 2), senza retry.

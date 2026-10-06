# 19 — Circuit breaker sui provider + session_id corretto per conversazioni parallele

**Priorità:** P1 · **SCAMPER:** — · **Costo runtime:** <1 ms (state machine in memoria per provider; chiave session derivata) · **Impatto:** 🛡 niente stalli su provider degradati; prerequisito della cache (07)

---

## Perché

Due problemi operativi non affrontati dalla spec. Primo: il session_id deterministico da
(api_key, conversation), ma come viene derivato conversation non è detto; due chat parallele con
la stessa chiave rischiano di condividere sessione (cache avvelenata, stato Redis mescolato).
Secondo: nessun circuit breaker sui provider, un provider lento ma non morto (timeout parziali,
429 intermittenti) può tenere in stallo ogni request che lo tocca. L analogo biologico: la
noradrenalina disattiva i circuiti costosi quando l organismo è in crisi, il sistema smette di
insistere sulla via che non paga.

## Cosa

1. **session_id**: derivazione esplicita e documentata — hash(api_key, workspace_path,
   conversation_title o id conversazione Zed se disponibile), con test di non collisione.
2. **Circuit breaker** per provider: stato chiuso → aperto dopo N errori consecutivi o tasso
   errore sopra soglia in finestra; aperto = skip diretto alla catena di fallback per X secondi;
   semi-aperto = una request di prova.

## Come

1. Specifica della derivazione session_id in session.py + test: due conversazioni parallele
   → due session_id distinti; stessa conversazione riaperta → stesso id.
2. Breaker in system2 (state in Redis, coerente col resto dello stato): soglie da providers.yaml
   (`breaker: {failure_threshold: 5, window_s: 60, open_s: 30}`).
3. Il breaker interagisce col fallback chain esistente: provider aperto = rimosso dalla risoluzione.
4. Metriche: stato dei breaker in dashboard, conteggio fallback per provider.
5. Il breaker conta anche i timeout lenti: latenza p95 sopra soglia per finestra = mezzo fallimento
   (degradazione, non solo morte).

---

### Verifica di successo
Test: provider mock lento → richieste smistate al fallback entro una finestra.
Test: due chat parallele in Zed → cache e stato non mescolati.

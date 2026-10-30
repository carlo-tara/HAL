# 23 — Serving speculativo: bozza servita mentre il grande completa (estensione di 16)

**Priorità:** P2 · **SCAMPER:** R (Reverse) · **Costo runtime:** +1 token-unità concorrente sulle request attivate (la chiamata grande avviene comunque nel piano) · **Impatto:** ⏱ massimo sulla latenza percepita; ⚠️ solo dopo 03+13

---

## Perché

L inversione completa dell attesa: invece di rispondere dopo il grande, si risponde
durante. La biologia non lo fa in modo consapevole, ma la percezione predittiva sì: il cervello
consegna una percezione e la corregge continuamente con l arrivo di evidenza migliore. Il costo
è quello della discordanza: se la bozza e il grande concordano, si è raddoppiata solo la velocità;
se discordano, si paga la chiamata grande che c era comunque nel piano, più l attrito cognitivo
della correzione. Il gruppo ombra (03) misura esattamente questo tasso di discordanza, da lì
la decisione se attivare lo speculativo su un bucket.

## Cosa

Variante a costo pieno dello urgency (16): non si aspetta il superamento del budget,
la bozza parte immediatamente per tutto il traffico dei bucket dove il log mostra alta
concordanza bozza/grande; il grande lavora comunque e la correzione arriva solo se rilevante
(verifica Laya di disaccordo).

## Come

1. Prerequisiti duri: gruppo ombra attivo (03), tasso di discordanza per bucket stabile e
   basso (<20%), urgency già funzionante (16).
2. Attivazione per bucket via config diff, come 11 e 13, mai globale al lancio.
3. Il SSE consegna bozza → eventuale delta: se il grande conferma, un evento di conferma silenzioso;
   se corregge, delta con spiegazione minima.
4. Misura dell attrito: tasso di retry/edit dell utente dopo una bozza poi corretta, se sale,
   il bucket esce dallo speculativo.
5. Interazione col metabolico (20): sotto stress lo speculativo si spegne per primo.

---

## Vincoli di deployment SSE del serving (voce P1 streaming, ToDo 2026-10-28)

Il percorso streaming System 2 (`streaming_backend.py`, registrato via
`SystemTwoEngine.register_backend`) richiede che il layer di serving che espone
`/chat/completions` rispetti questi vincoli, altrimenti lo streaming si manifesta
come rallentamento percepito e vanifica il beneficio sui timeout:

1. **`proxy_buffering off`** (Nginx) sulla rotta SSE: senza di esso gli eventi
   vengono bufferizzati dal proxy e il client riceve l'intera risposta in un
   blocco solo alla fine (peggio: con timeout proxy, il 504 torna).
2. **Contratto di terminazione**: il flusso si chiude solo alla sentinella
   `data: [DONE]` del backend; il proxy non deve inventare chiusure intermedie
   (nessuna `gzip on` sul stream, `chunked_transfer_encoding on`).
3. **Pool e fd dimensionati sulla concorrenza**: ogni conversazione streaming
   tiene aperta una connessione end-to-end finché la generazione non finisce;
   con N utenze concorrenti servono `worker_connections`/fd ≥ N più margine
   (monitorare `ss -s` e i fd di processo sotto picco; target reuse ratio >95%
   sui pool outbound lato gateway).
4. **Nessun timeout short-read sotto la sentinella**: il timeout end-to-end non
   si applica più al primo byte; il read timeout va tarato sull'inter-chunk
   (es. 60 s), non sulla generazione totale (le generazioni lunghe Opus ~99 s
   motivate dal report OrcaRouter).

Questi vincoli sono prerequisito all'abilitazione del path streaming in
produzione (bucket per bucket, come da regola 2 del serving speculativo sopra).

---

### Verifica di successo

Latenza percepita mediamente ≥2x migliore sui bucket attivati. Tasso di retry post-correzione
entro soglia. Attivazione e disattivazione di bucket documentate nel log delle config.

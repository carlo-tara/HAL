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

### Verifica di successo
Latenza percepita mediamente ≥2x migliore sui bucket attivati. Tasso di retry post-correzione
entro soglia. Attivazione e disattivazione di bucket documentate nel log delle config.

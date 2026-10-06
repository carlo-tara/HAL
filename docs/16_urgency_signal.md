# 16 — Urgency signal: sotto deadline si serve la bozza, il grande completa in background

**Priorità:** P1 · **SCAMPER:** M+R (Modify+Reverse) · **Costo runtime:** +1 chiamata concorrente sul 10-20% del traffico (bozza poi scartata) · **Impatto:** ⏱ latenza percepita dimezzata; ⚠️ attivare solo con urgenza misurata alta

---

## Perché

Il drift-diffusion model (Ratcliff): la soglia di decisione è regolata da urgenza e posta
in gioco — alta posta = soglia alta (più accuratezza, più tempo); deadline vicina = soglia bassa
(veloce e sporco). Il cervello sotto deadline non perfeziona la risposta, degrada la soglia e
risponde col meglio disponibile. L utente che aspetta da 20 secondi ha già scontato la qualità:
meglio una bozza buona ora che una risposta perfetta tra un minuto. Il `latency_budget_ms: 8000`
dichiarato ma non enforced ottiene qui il suo meccanismo.

## Cosa

Se il tempo atteso del percorso completo supera il budget del profilo:
1. si genera e serve subito la bozza (modello piccolo o cache L2)
2. nel frattempo il modello grande completa in background
3. a completamento: se la risposta definitiva differisce in modo rilevante (verifica Laya, 33 ms),
   viene consegnata come aggiornamento; altrimenti la bozza resta
Sotto il budget: comportamento normale, zero costo aggiuntivo.

## Come

1. Stima del tempo atteso: latenza media per bucket (dal log) del percorso scelto vs budget YAML.
2. Attivazione condizionata: urgenza misurata alta (budget superato) E confidence della bozza
   sopra soglia di decenza — altrimenti si aspetta normalmente (la bozza ridicola sotto deadline
   è peggio dell attesa).
3. Consegna: SSE supporta aggiornamenti; Zed vede prima bozza poi eventuale correzione.
4. Controllo del costo: la chiamata concorrente grande avviene comunque (era nel piano), quindi
   il costo extra è zero nel caso di scarto — è la stessa chiamata anticipata.
5. Estensione (23): serving speculativo puro quando il log mostra alta concordanza bozza/grande.

---

### Verifica di successo
Latenza percepita (primo token utile) ridotta ≥40% sulle request attivate. Tasso di
correzione post-bozza visibile e <30% (altrimenti la soglia di decenza è troppo bassa).

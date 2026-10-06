# 05 — Retention e redaction del volume eventi dal giorno 1

**Priorità:** P0 · **SCAMPER:** E (Eliminate — eliminare il rischio, non il log) · **Costo runtime:** ~1 ms/evento in scrittura (filtro redaction); rotazione automatizzata · **Impatto:** 🛡 il log contiene segreti, chiavi e codice reale: compliance prima dei dati, non dopo

---

## Perché

La regola operativa 'body logging fin dal giorno 1' è corretta (OrcaRouter è ZDR: la copia
locale è l'unica), ma il documento non dice per quanto tempo, con quali filtri e con quali
controlli d'accesso. Zed scrive codice reale: nei body finiscono token API, chiavi private,
eventualmente dati personali e codice aziendale. Un volume Docker non cifrato, senza retention,
senza redaction è un data breach in attesa — e per di più è il dataset di training del futuro
sistema esperto: i segreti nel log diventano parte del training set.

## Cosa

- **Redaction in scrittura**: pattern noti (API key, Bearer token, chiavi SSH/PEM, password,
  email) oscurati prima dell'append
- **Classificazione PII** via preset Laya (costo già pagato dall'architettura)
- **Retention differenziata**: body grezzo 30 giorni; eventi compattati (senza body) 12 mesi
- **Cifratura a riposo** del volume e del backup
- **Accesso**: solo expert (read-only, dentro il container), mai montato altrove

## Come

1. Denylist regex in `event_writer`/`events.py` (chiavi OpenAI/AWS/GitHub, Bearer, PEM block)
   → sostituzione con placeholder tipizzato `{{secret:openai}}` (il tipo aiuta il tuning delle regole).
2. Preset Laya `pii_scan` sul body (batch col guardrail, 0 costo marginale) → flag `pii_detected`
   nell'evento; se true, body cifrato separatamente e retention più corta.
3. Rotazione JSONL giornaliera (già prevista) + job di purge: delete body oltre 30 gg, mantieni metadati.
4. Volume events cifrato (filesystem o sidecar); backup cifrato con chiave separata.
5. Test: inviare un body con API key finta e verificare che nel JSONL compaia solo il placeholder.

---

### Verifica di successo
Test redaction: 0 segreti noti nei log. Retention: purge automatico funzionante.
Volume cifrato verificato. Documentato nel README operativo.

# 07 — Cache L1 esatta: hash normalizzato, invalidazione per file, TTL per classe, prefisso session

**Priorità:** P0 · **SCAMPER:** C+M+P (Combine+Modify+Put to other use) · **Costo runtime:** 1 GET Redis (~1 ms) per request; ~10 MB RAM per 10k entry · **Impatto:** 💰 40-60% del traffico IDE ripetitivo servito a ~0 token

---

## Perché

L'80% delle chiamate da IDE è ripetitivo: stesso file, stesso errore, stessa domanda
riformulata. Il principio del minimo sforzo di Kahneman ha la sua controparte ingegneristica:
non ricalcolare ciò che è già stato calcolato. Ma una cache ingenua (hash esatto del messaggio)
fa peggio di niente: miss continui per riformulazioni e hit avvelenati su codice cambiato.
La regola del libro sul fluency è pertinente: una risposta servita troppo facilmente deve comunque
essere quella giusta — la cache va validata, non solo trovata.

## Cosa

Cache Redis a chiave composita:

    cache:v1:{session_id}:{use_case}:{hash(normalizzazione(messages))}:{hash(files_rilevanti)}

con TTL per classe (code-tdd corto: il codice cambia in fretta; writing lungo; analyze medio)
e invalidazione alla modifica dei file dichiarati rilevanti dal contesto.

## Come

1. Normalizzazione: lowercase, strip whitespace, path relativi canonizzati, rimozione
   timestamp casuali — poi SHA-256 della serializzazione canonica.
2. Dipendenze file: context-opt conosce quali file sono nel contesto → il loro hash entra nella
   chiave; un fix su `bar.py` non invalida la cache di `foo.py`.
3. TTL in `use-cases/*.yaml` (`cache_ttl_s`), default: code-tdd 300 s, analyze 3600 s, writing 86400 s.
4. Streaming: la risposta cachata viene re-streamata SSE a blocchi (Zed non nota differenza).
5. Hit rate per use_case in dashboard; provenance (`cache_hit: true`) negli eventi.
6. Edge case: se `has_tools`, la cache vale solo per la prima risposta del turn (i tool cambiano stato).

---

### Verifica di successo
Hit rate >40% entro due settimane su traffico reale. Nessuna risposta stale servita dopo
modifica file (test: modifica file, verifica miss).

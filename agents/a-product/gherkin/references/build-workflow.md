# Build workflow (`/build`)

Zoom su **un** Feature/flusso (Core Job o capability) da seeds + inventory.

## Checklist

1. **Scope** — job/seeds/PRD slice indicati dal PO (o inferiti da gap)
2. **Inventory** — UI + IO del solo flusso in scope ([ui-interaction-inventory.md](ui-interaction-inventory.md), [external-io-catalog.md](external-io-catalog.md))
3. **Cluster file** — 1 `.feature` per il flusso; più Scenario OK; `Rule:` per boundary/exception
4. **Happy / journey** — ≥1 `@journey` se il flusso è un Core Job (o nota waiver)
5. **Map seeds/needs** — tag `@seed-ssNN` `@need-nNN`
6. **Map UI/IO** — ogni controllo/IO → Scenario o waiver
7. **Indipendenza** — Given auto-contenuto; no ordine di run
8. **Draft** — mostra in chat; `/export` solo dopo conferma PO
9. **README** — aggiorna coverage + inventory rows per il file

## Anti-pattern

- Scaricare tutto il prodotto in un unico file "god feature"
- Creare un file per ogni Scenario singolo (vietato come regola obbligatoria)
- Saltare inventory perché "i seed bastano"

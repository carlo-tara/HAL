---
name: aggregate-root
kind: competency
version: 1.0.0
description: >-
  Aggregate Root DDD: mutazioni stato solo tramite radice aggregato. Test Red
  non mutano entità figlie direttamente.
---

# Competenza L1 — aggregate-root

Guardiano integrità: non aggirare regole di business manipolando entità figlie.

## Regola tassativa

1. **Mutazioni stato** solo tramite metodi pubblici dell'**Aggregate Root**
2. Entità figlie: incapsulate; setter privati o readonly verso l'esterno
3. **Vietato** query/update dirette su tabelle/collezioni figlie che bypassano la root

## Fase RED (test)

- Non testare mutazione diretta di child entity
- Esercita comportamento via API della root: `order.addLine(...)`, `order.confirm()`

## Fase GREEN (implementazione)

- Incapsula figli nel aggregate
- Invarianti verificati nella root prima di persistenza

## Esempio

| Corretto | Errato |
|----------|--------|
| `order.addInvoiceLine(line)` | `line.quantity = 5` su entity figlia |
| `shipment.dispatch()` | UPDATE diretto su `shipment_items` |

## Quando applicare

- `/red` e `/green` su entità con figli (Order/Line, Shipment/Package, …)
- `/refactor` se invarianti sparsi su figli

## Anti-pattern

- Anemic domain model con logica solo su service che muta DTO piatti
- Repository che espone update granulare su child senza root

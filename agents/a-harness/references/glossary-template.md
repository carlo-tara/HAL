# Glossario dominio (template)

Documento **vivo**. Termini qui definiti sono obbligatori in codice e test (`ubiquitous-language`).

## Istruzioni

- Un concetto = una voce = un termine canonico (EN o IT, coerente col codebase)
- Aggiungi sinonimi **vietati** esplicitamente
- Aggiorna con `/steward` o PO quando il dominio evolve

---

## Entità

| Termine canonico | Definizione | Sinonimi vietati |
|------------------|-------------|------------------|
| {Customer} | {Chi paga / account titolare} | User, Client |
| {Invoice} | {Documento fiscale emesso} | Bill, Receipt |

## Verbi / azioni

| Termine canonico | Definizione | Sinonimi vietati |
|------------------|-------------|------------------|
| {Confirm} | {Transizione stato X→Y} | Validate, Approve (se distinti nel dominio) |

## Eventi (opz.)

| Evento | Payload minimo | Emesso da |
|--------|----------------|-----------|
| {InvoiceIssued} | invoiceId, customerId | Billing |

## Note

- {Convenzioni naming file/classi}
- {Bounded context owner per termine ambiguo}

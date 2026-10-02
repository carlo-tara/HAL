# Bounded contexts (template)

Mappa confini del sistema. Ogni `/slice` dichiara quale context è attivo.

## Context map

| Context | Path modulo | Responsabilità | Integrazioni |
|---------|-------------|----------------|--------------|
| {Billing} | `src/modules/billing/` | Fatturazione, pagamenti | → {Shipping} via `OrderPaid` event |
| {Shipping} | `src/modules/shipping/` | Spedizioni, tracking | ← Billing |

## Regole

1. **Nessun import diretto** tra colonne Path modulo
2. Integrazioni solo via colonna Integrazioni (eventi o port pubblici)
3. Shared kernel (se esiste): documentare path e owner

## Eventi di dominio pubblici

| Evento | Publisher | Subscribers | Schema |
|--------|-----------|-------------|--------|
| {OrderPaid} | Billing | Shipping | `{ orderId, paidAt }` |

## Port pubblici (alternativa a eventi)

| Port | Context | Consumatori |
|------|---------|-------------|
| `{BillingQueries.getInvoice}` | Billing | Reporting (read-only) |

## Waiver temporanei

| Waiver | Motivo | Scadenza |
|--------|--------|----------|
| — | — | — |

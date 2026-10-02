---
name: anti-corruption-layer
kind: competency
version: 1.0.0
description: >-
  ACL DDD: core domain mai esposto a payload HTTP/DB/API esterne. Adapter obbligatori
  ai confini. Fase GREEN tipica.
---

# Competenza L1 — anti-corruption-layer (ACL)

Protezione del nucleo: traduci e filtra **prima** che i dati entrino nel dominio.

## Regola tassativa

Il **core domain** non deve conoscere:

- shape JSON di API esterne
- schema tabelle DB (ORM entity leakage)
- header/cookie HTTP
- tipi del client SDK terzo

## Azione (fase GREEN)

Ogni integrazione esterna richiede:

1. **Adapter** al confine (infrastructure layer)
2. **DTO/domain type** interno mappato esplicitamente
3. Unit test dominio **senza** rete/DB (mock adapter)

## Esempio errore

```typescript
// VIETATO — JSON API nel service dominio
async createOrder(payload: StripeCheckoutSession) { ... }
```

## Esempio corretto

```typescript
// ACL al confine
class PaymentGatewayAdapter {
  toPaymentIntent(session: ExternalSession): PaymentIntent { ... }
}
```

## Quando applicare

- `/green` su boundary HTTP, DB, message queue, file system
- `/refactor` se leakage rilevato

## Anti-pattern

- Pass-through response HTTP al dominio
- Entity ORM usata come domain entity
- Test dominio che richiedono DB reale per logica pura

---
name: sustainable-pace
kind: competency
version: 1.2.0
description: >-
  Anti review-fatigue e anti context-bloat: niente PR/review/done finché make ready-for-review ≠ 0.
  Slice medium discrete, quiet test default, rate limiting orario E2E; PR-as-proof.
---

# Competenza L1 — sustainable-pace

Protegge la risorsa scarsa: **attenzione umana**. L'agente non sommerge di revisioni imperfette.

## Regola suprema (sempre attiva)

**Non hai autorizzazione** di:

- richiedere revisione umana
- aprire Pull Request
- dichiarare lavoro finito

finché:

```bash
make ready-for-review
```

non restituisce exit code **0**.

Post-gate: l'umano valida **intent** («è quello che volevamo?»), non esecuzione meccanica — vedi [pr-proof-checklist.md](../../references/pr-proof-checklist.md).

## Slice medium discrete

| Troppo largo           | Troppo stretto    | Sweet spot                                          |
| ---------------------- | ----------------- | --------------------------------------------------- |
| «refactor auth module» | «rename variable» | «add rate limit su /api/X usando pattern in /api/Y» |

`/slice` deve includere: acceptance criteria, pattern di riferimento, file ≤4, effort (fast|thorough).

## PR / diff budget

- Preferire **&lt;400 LOC** netti per handoff
- Oltre → spezza slice (policy On Ready = warn/fail)

## Tiny slices e commit

- Un micro-lotto logico per slice
- Commit dopo ogni slice con `/ready` verde (o checkpoint intermedio se concordato)
- Messaggio: **perché** architetturale

```
feat(billing): add InvoiceLine validation

Why: enforce aggregate invariant before persistence;
tests red-first on duplicate line IDs per glossary term InvoiceLine.
```

## `/ready`

1. Esegui `make ready-for-review` (run **fresco** post-diff; vedi [pr-proof-checklist.md](../../references/pr-proof-checklist.md) § Proof del gate)
2. Se exit ≠ 0 → autocorreggi; **non** notificare umano
3. Checklist [pr-proof-checklist.md](../../references/pr-proof-checklist.md)
4. Se exit = 0 → riepilogo audit + handoff **intent** (Reasoning alto)
5. **Converge** (Spec Kit): se il contratto/slice ha gap ancora aperti rispetto al codice, proponi un **nuovo** `/slice` — non dichiarare “done” sul residuo né allargare lo slice chiuso

## Quiet test execution & E2E rate limiting

Protezione del focus cognitivo e prevenzione del context exhaustion:

- **Test compatti nel gate:** le verifiche meccaniche (`make test-unit`, `make test-quiet`) non devono inquinare la chat con cascate di test verdi; l'agente osserva solo `full GREEN` o i dettagli del fallimento `RED`.
- **E2E Throttling sostenibile:** i test browser end-to-end non devono essere rieseguiti compulsivamente a ogni micro-step; la Platform API differisce esecuzioni ripetute entro l'ora per evitare saturazione di risorse e collisioni concorrenti.

## Anti-pattern

- PR con linter rosso "per feedback presto"
- Accumulo multi-slice senza test verdi
- Commit message solo "fix" / "update" senza perché
- **Lazy delete** — placeholder `// ... existing code ...` che cancella codice → fail ready
- Shadow code — nessuno può spiegare l'intent in 2 frasi
- Parallel agents su slice non scoped (default = un `/cycle` alla volta)
- Dichiarare `ready=0` da log Gate OK **stale** (slice precedente) o da `make | tail` senza `MAKE_EXIT` osservato
- Patchare un **track concurrent** (assert/path di un altro agente) per far passare il gate — canone `steward`: wait + retry

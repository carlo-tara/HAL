# Handoff da a-gherkin → a-harness

Pipeline: **personas → JTBD → Gherkin → implementazione TDD**.

## Quando handoff

- Esiste almeno uno `.feature` con scenario implementabile
- US/AC ratificati (PO o waiver documentato in `features/README.md`)

## Prompt handoff (da a-gherkin o umano)

```
@a-harness /cycle per {nome-flusso}.

Contratto: .cursor/product/features/{file}.feature — scenario "{nome}".
Bounded context: {Context} ({path modulo}).
Rispetta docs/glossary.md e docs/bounded-contexts.md.
Non chiedermi attenzione finché make ready-for-review non è verde.
```

## Mapping Gherkin → test codice

| Gherkin | Test codice (RED) |
|---------|-------------------|
| Scenario title | Nome test descrittivo (termine glossario) |
| Given | Fixture / setup via aggregate root o ACL |
| When | Azione su API pubblica dominio |
| Then | Assertion comportamento osservabile |

Non tradurre 1:1 step Gherkin in selettori UI nel unit test — per UI/E2E usa `test-e2e` in slice dedicato.

## Ambiguità

Se scenario contraddice glossario o bounded context:

1. **Non** indebolire il test
2. Segnala e invoca `a-gherkin` `/refine`
3. Se gap product → `a-po`

In Plan (`/slice`), tratta questo come **analyze** Spec Kit: allineamento contratto ↔ glossario ↔ BC prima di `/red` — [github-spec-kit-source.md](github-spec-kit-source.md).

## Riferimento upstream

Handoff inverso (gherkin → dev generico): `a-gherkin/references/handoff-to-dev.md` — a-harness **specializza** con ciclo R/G/R e gate Makefile.

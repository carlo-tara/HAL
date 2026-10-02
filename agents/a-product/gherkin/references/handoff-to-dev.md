# Handoff implementazione — a-harness

Dopo export Gherkin, delega a **a-harness** (non un coding agent generico).

```
@a-harness /cycle per {flusso}.

Contratto: .cursor/product/features/{file}.feature — scenario "{nome}".
Bounded context: {Context} ({path modulo}).
Rispetta docs/glossary.md e docs/bounded-contexts.md.
Tratta i .feature come contratto comportamentale.
Usa interazioni semantiche (ruolo, label, testo visibile) — non selettori CSS fragili in unit test.
Se uno scenario è ambiguo o contraddice personas/jtbd, non indebolire il test:
segnala e invoca a-gherkin /refine (e upstream se serve).
Non chiedermi attenzione finché make ready-for-review non è verde.
```

Dettaglio mapping Gherkin → TDD: [`a-harness/references/handoff-from-gherkin.md`](../../a-harness/references/handoff-from-gherkin.md).

Vedi selector-strategy.md per E2E. @edge-infra / @security-infra possono restare pending senza harness.

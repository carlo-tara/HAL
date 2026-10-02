---
name: bdd-security-performance
kind: competency
version: 1.0.0
extends-version: 1.0.0
description: >-
  Cataloghi e regole per scenari Gherkin di sicurezza e performance osservabili.
  Usare con /secure e /perf in a-gherkin.
---

# Competenza L1 — bdd-security-performance

Sicurezza e performance entrano in Gherkin solo come **comportamento osservabile**.

**Reference:** [security-catalog.md](references/security-catalog.md) · [performance-catalog.md](references/performance-catalog.md) · [scope-rules.md](references/scope-rules.md)

## Principi

1. Niente “il sistema è sicuro” senza esito verificabile
2. Niente assert su ms/CPU/SLA inventati
3. Scope PO/jtbd/PRD; anti-invention
4. Tag `@security` / `@performance` (+ sotto-tag)
5. Classificare product vs `@security-infra` / pending harness

## Skill collegate

- `/secure` — famiglie security-catalog
- `/perf` — famiglie performance-catalog

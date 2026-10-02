---
name: gherkin
parent: a-product
version: 1.1.16
description: >-
  Reason why: senza scenari su cosa deve succedere (e fallire), prodotto e sviluppo non hanno un accordo chiaro da verificare. QA Lead / BDD Spec integrato in a-product: suite Gherkin da jtbd seeds, inventory UI/IO, journey E2E, expand edge, /cover, add-scenario da NL, /secure e /perf. Da usare per creare o validare file .feature e definire le acceptance prima dell'handoff ad a-harness.
---

# gherkin — BDD Spec & Edge Cases

Skill di prodotto per contratto comportamentale `.feature`. Competenza integrata di **a-product**.

Competenze interne: **bdd-security-performance**.

---

## Prerequisito

`jtbd.md` con scenario_seeds (o seed equivalenti dal PO).

Discovery: `.cursor/product/` → `.claude/product/` → `product/`. Output: `features/*.feature` + `features/README.md`.

---

## Principi BDD

1. Comportamento/intento, non DOM (`#id`, coordinate)
2. Then dichiarativi; When in linguaggio utente
3. Scenari **indipendenti** (Given ricostruisce stato); journey via `@journey` non ordine di run
4. Selettori semantici nella guida per il coding agent, non nei passi Gherkin

---

## Comandi (slash)

| Invocazione | Obiettivo |
| ----------- | --------- |
| `/triage` | Feature valide? → validate/refine/expand/cover/add-scenario/secure/perf/none |
| `/create` | Suite iniziale da jtbd + inventory UI/IO |
| `/build` | Un Feature/flusso da seeds (+ inventory del flusso) |
| `/cover` | Inventory UI/IO → scenari mancanti da mockup/PRD/binding |
| `/add-scenario` | Scenari aggiuntivi da NL |
| `/expand` | Edge da happy path + cataloghi UI/IO |
| `/secure` | BDD sicurezza (competenza bdd-security-performance) |
| `/perf` | BDD performance percepita |
| `/validate` | Coverage seeds/needs/journey **+** UI **+** IO |
| `/refine` | Dopo jtbd/UI change |
| `/lint` | Qualità Gherkin |
| `/gap` | Report-only |
| `/show` | Read-only |
| `/export` | Scrive features dopo conferma PO |

---

## Handoff implementazione

Delega ad **`a-harness`** (`/cycle`, TDD).

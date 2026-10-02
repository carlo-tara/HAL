---
name: evidence-probe
kind: competency
version: 1.0.0
description: >-
  Mappa assunzioni (VUBF / 8 cat new), Impact×Risk, PoL probe, red-team
  kill-assumptions. Solo L1 (a-po).
---

# Competenza L1 — evidence-probe (a-po)

Decide **cosa validare** e **come**, al costo minimo di apprendimento. Non sostituisce experiment design engineering; produce piano evidenza e kill criteria.

---

## Quando applicare

- `/validate` dopo shape, o pre-build su bet rischiosa
- Red-team di PRD/roadmap/strategy prima di commit
- Dopo OST: trasformare experiment hints in probe concreti
- Dopo Lean Canvas: input tipico = **riskiest boxes** (stress-test canvas)
- Market risk → può richiamare `market-public-data`

## Quando NON applicare

- Nessuna ipotesi chiara → prima `problem-framing`
- Serve suite BDD → handoff `a-gherkin` dopo slice
- “Impress the exec with a prototype” non è validation

---

## Workflow

### 1 — Extract assumptions

**Existing product (VUBF):** Value | Usability | Business viability | Feasibility

**New product — estendi a 8:** + Ethics | Go-to-Market | Strategy & objectives | Team

Prospettive: PM / Design / Eng (devil’s advocate).

### 2 — Prioritize (Impact × Risk)

- High impact + high uncertainty → test now
- High impact + low risk → proceed / monitor
- Low impact + high risk → reject or defer
- Low + low → defer

### 3 — Choose probe (PoL flavors)

| Flavor | Core question | Typical horizon |
|--------|---------------|-----------------|
| Feasibility check | Can we build it? | 1–2 days |
| Task-focused test | Can users complete the job? | 2–5 days |
| Narrative prototype | Does the story earn buy-in? | 1–3 days |
| Synthetic / desk data | Can we model without prod risk? | 2–4 days |
| Skin-in-the-game probe | Will it survive real contact? | 2–3 days |

Golden rule: *cheapest probe that tells the harshest truth.*

### 4 — Red-team mode (optional)

Per 3–5 load-bearing claims:

- Claim (steelman) → **Fails if** (falsifiable)
- Evidence to get this week
- **Kill criterion**
- Cheapest test
- Rank by impact × likelihood wrong × cheapness to test

Non inventare debolezze; dichiara cosa è già ben ragionato.

### 5 — Checkpoint

“Quali 1–3 assumption testare questa settimana?”

---

## Regole ferree

1. Hypothesis esplicita prima del metodo
2. Success / invalidate metric per ogni test
3. Mai inventare risultati di experiment
4. Pre-mortem launch (Tigers / Paper Tigers / Elephants) solo se esplicitamente richiesto o fase launch

---

## Anti-pattern

- Scegliere il tool comodo (Figma/code) invece del rischio
- Lista rischi generica senza fail condition
- Validare opinion al posto di behavior

---

## Output della fase

- Assumption table: assumption | category | impact | evidence | priority
- Top probes: method | metric | threshold | owner/timing
- Red-team block (se usato)
- Next: `/prioritize`, `/market-data`, o handoff specialist

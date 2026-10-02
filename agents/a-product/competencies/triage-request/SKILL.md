---
name: triage-request
kind: competency
version: 1.0.1
description: >-
  Decodifica richieste in ingresso (literal ask vs outcome) e triage batch
  di feature request per temi e allineamento strategico. Solo L1 (a-po).
---

# Competenza L1 — triage-request (a-po)

Trasforma Slack/email/mandate o pile di feature request in **outcome chiaro**, contesto di potere/stake, e next artifact — senza costruire ciò che il cliente ha chiesto alla lettera.

---

## Quando applicare

- `/intake` o `/triage` su messaggio carico, escalation, “mandate” da stakeholder
- Batch di richieste clienti/support/sales da categorizzare
- Scope unclear all’avvio → preferisci questa competenza prima di framing
- Brief **feature-only** da orchestra `a-product` / facade `a-b2b` (anti–Build Trap) → `/triage` qui

## Quando NON applicare

- Già c’è un problem statement confermato → passa a `problem-framing`
- Serve job map / personas → delega `a-jtbd` / `a-personas`
- Lista lead da arricchire → `a-enrichment` (non qui)

---

## Workflow

```
1. Accetta input (testo, CSV, file) — non ri-chiedere ciò che è già nel brief/L2
2. Separa: literal ask | job/outcome sottostante | sender power/stake | urgenza percepita
3. Se batch: cluster per temi; conta frequenza; allineamento High/Med/Low/None vs goal/OKR
4. Per tema o richiesta top: Impact, strategic fit, effort T-shirt, risk if ignored, revenue signal
5. Output + checkpoint: “quali 1–3 temi/outcome portare a framing?”
```

Usa `po-interviewer`: 1–2 Q/turno se mancano goal, stage, segmenti da pesare.

---

## Regole ferree

1. **Opportunities/problems, non feature list** — non lasciare che i clienti disegnino la soluzione
2. Etichetta `evidence` vs `hypothesis`
3. Non inventare ICP, volumi, o “tutti i clienti vogliono X”
4. Next artifact esplicito: brief, framing, validate, o delega

---

## Anti-pattern

- Rispondere subito “ok lo mettiamo in sprint”
- Mediare ranking senza goal strategici
- Confondere frequenza richiesta con Opportunity Score

---

## Output della fase

- **Literal ask** vs **outcome**
- **Sender / stake** (1 riga)
- Tabella temi (se batch): tema | count | alignment | priority hint
- **Next actions** + checkpoint per `problem-framing` o `/shape`

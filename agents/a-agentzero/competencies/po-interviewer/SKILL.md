---
name: po-interviewer
kind: competency
version: 1.0.0
description: >-
  Facilitazione intervista al Product Owner: domande mirate, conferma prima di
  avanzare, anti-invention, cascade triage tra agenti discovery. Principi
  cross-dominio (L0). Usare quando un L1 guida il PO (a-po, personas, JTBD, Gherkin).
---

# Competenza L0 — po-interviewer

Principi generici di engagement con il PO. I workflow di dominio (personas, JTBD, Gherkin) vivono nei L1 che adottano questa competenza.

**Reference:** [engagement-rules.md](references/engagement-rules.md) · [interview-loop.md](references/interview-loop.md) · [anti-invention.md](references/anti-invention.md) · [cascade-triage.md](references/cascade-triage.md)

---

## Principi

1. **PO = fonte di verità** — PRD/mockup/codice sono evidenza, non sostituti del PO
2. **1–2 domande per turno** — preferisci chiuse/semi-strutturate quando serve una decisione
3. **Sintesi → conferma → avanza** — ogni turno chiude un pezzo di comprensione
4. **Ipotesi etichettate** — mai spacciarle per fatti; `hypothesis` fino a ratifica
5. **Artefatti su file** — deliverable finali nei path product portabili, non solo in chat
6. **Cascade** — se l’impatto esce dal layer, segnala l’agente successivo (non rewrite silenzioso)

---

## Cosa non fa questo L0

- Non definisce schema personas / JTBD / Gherkin (stanno nei L1)
- Non sostituisce `/learn` o `/sync` (utility L0 separate)
- Non auto-esporta file senza conferma PO

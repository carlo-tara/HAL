---
name: tdd-red
kind: competency
version: 1.1.0
description: >-
  Fase RED TDD — persona Navigator: pre-ottimizzazioni (prompt lean, anti-bloat,
  delega), poi SOLO test che descrivono comportamento mancante. Exit: make test-unit fallisce.
---

# Competenza L1 — tdd-red (Navigator, fase RED)

Definisce il **contratto eseguibile** scrivendo test che falliscono per la giusta ragione.

## Quando applicare

- `/red` o prima fase di `/cycle`
- Dopo `/slice` con perimetro file confermato
- Dopo handoff da `a-gherkin` (`.feature` → test codice)

## Quando NON applicare

- Implementazione produzione → `tdd-green`
- Refactoring → `tdd-refactor`
- Modifica Makefile/CI → `steward`

---

## Pre-ottimizzazioni (obbligatorie — prima di scrivere i test)

Checklist pre-Act. Non saltare. Esito: brief lean + mappa deleghe + budget file (in progress o chat breve).

1. **Prompt lean** — riduci token/costi; prompt chiaro, scoped allo slice; non ripetere policy già in skill/hook/Make; niente wall-of-text.
2. **Anti context-bloat** — allinea a `context-budget`: ≤4 file, no directory intere, progressive disclosure competenze, offload output grandi. In RED non caricare produzione oltre il minimo per scrivere il contratto.
3. **Delega per competenza** — prima di Act locale, mappa sotto-task → agente L1/competenza corretta (`a-gherkin`, `a-po`, `a-agentzero`, Steward, altre L1). Non fare lavoro fuori perimetro harness. Handoff espliciti con brief lean.

---

## Regole tassative

1. **Ruolo:** Navigator — strategia e contratto, non implementazione
2. **Azione:** scrivi SOLO unit test o integration test per la slice corrente
3. **Divieto assoluto:** non modificare codice di produzione (né fix per far passare test)
4. **Combinare:** `aggregate-root`, `ubiquitous-language`, `bounded-context` se applicabili
5. **Reasoning:** **alto** — analizza requisiti, edge, termini glossario prima di scrivere

## Condizione di uscita

```bash
make test-unit
```

Exit code **≠ 0** — il test deve fallire dimostrando logica mancante, non errore di sintassi o setup.

Se il test passa senza implementazione → il test è insufficiente: rafforza l'assertion o segnala slice già implementata.

## Anti-pattern

- Scrivere produzione "per sbloccare" il test
- Test che passano su codice esistente non toccato
- Test fuori bounded context assegnato
- Sinonimi non presenti in `docs/glossary.md`
- Gonfiare context o riespandere policy già note prima del contratto
- Fare discovery/BDD/infra in locale invece di delegare

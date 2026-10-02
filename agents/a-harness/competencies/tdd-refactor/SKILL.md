---
name: tdd-refactor
kind: competency
version: 1.0.0
description: >-
  Fase REFACTOR TDD: pulizia sotto rete di test verdi. Duplicazioni reali, rename,
  rimozione zavorra, allineamento glossario. Reasoning alto (verifica).
---

# Competenza L1 — tdd-refactor (Navigator + Driver)

Paga debito tecnico **localizzato** mantenendo comportamento invariato.

## Quando applicare

- `/refactor` o terza fase di `/cycle`
- GREEN completato con test + pre-commit verdi

## Quando NON applicare

- Test rossi → torna a GREEN o RED
- Nuova funzionalità → nuovo `/slice` + `/red`

---

## Regole

1. **Ruolo:** Navigator per analisi duplicazioni; Driver per modifiche
2. **Duplicazioni REALI only** — non astrarre duplicazioni ipotetiche future
3. **Rimozione zavorra:** codice commentato, log dead, harness morto, import inutili
4. **Linguaggio ubiquo:** rename per allineamento a `docs/glossary.md`
5. **Surface area:** preferisci rimuovere codice vs aggiungerne
6. **Reasoning:** **alto** — verifica impatto architetturale prima di ogni rename strutturale

## Condizione di uscita

```bash
make test-unit
```

(o suite più ampia se definita in L2) — exit **0**, comportamento invariato.

## Anti-pattern

- Cambiare behavior sotto copertura "refactor"
- Introduire nuove astrazioni non motivate da duplicazione misurabile
- Lasciare sinonimi rispetto al glossario

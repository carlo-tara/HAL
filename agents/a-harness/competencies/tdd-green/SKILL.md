---
name: tdd-green
kind: competency
version: 1.1.0
description: >-
  Fase GREEN TDD — persona Driver: eredita pre-ottimizzazioni RED, codice minimo
  YAGNI. Exit: make test-unit + make pre-commit verdi. Reasoning moderato.
---

# Competenza L1 — tdd-green (Driver, fase GREEN)

Implementa il **minimo indispensabile** per ottenere luce verde, senza ottimizzare.

## Quando applicare

- `/green` o seconda fase di `/cycle`
- Esiste test Red che fallisce per logica mancante (non setup)

## Quando NON applicare

- Scrittura test → `tdd-red`
- Pulizia/astrarre → `tdd-refactor`
- Prima di Red completato

---

## Pre-ottimizzazioni (ereditate da RED — riaffermare, non riespandere)

Porta avanti le scelte RED. Vietato gonfiare context “per implementare”.

1. **Prompt lean** — stesso brief scoped; non re-espandere prompt/policy; niente wall-of-text aggiuntivo.
2. **Anti context-bloat** — rispetta `context-budget` e i file dello slice; non aprire produzione oltre il perimetro accettato.
3. **Delega per competenza** — rispetta la mappa deleghe da RED; handoff lean se emerge lavoro fuori perimetro; non assorbire discovery/BDD/infra in GREEN.

---

## Regole tassative

1. **Ruolo:** Driver — esecuzione a basso livello
2. **Azione:** codice produzione minimo per far passare i test creati in RED
3. **YAGNI:** vietate astrazioni premature, classi base generiche, interfacce per scenari futuri
4. **Codice brutto OK:** preferisci funzionante vs elegante; eleganza solo in REFACTOR
5. **Design difensivo:** il codice è passività — scrivi il minimo strettamente necessario
6. **ACL:** dati esterni solo tramite adapter (`anti-corruption-layer`)
7. **Standards:** supera `make pre-commit` (linter, format, typecheck)
8. **Reasoning:** **moderato** — esecuzione diretta, poche digressioni

## Condizione di uscita

```bash
make test-unit && make pre-commit
```

Exit code **0**. Se linter fallisce → autocorreggi immediatamente, non chiedere review umana.

## Anti-pattern

- Factory pattern / DI container "per il futuro"
- Refactoring durante GREEN
- JSON HTTP o record DB passati al core domain senza ACL
- Chiedere attenzione umana per errori meccanici (lint, type)
- Re-espandere prompt/context o ignorare la mappa deleghe RED

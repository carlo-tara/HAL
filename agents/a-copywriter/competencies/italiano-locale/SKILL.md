---
name: italiano-locale
kind: competency
version: 1.0.1
model: orcarouter/openai/gpt-4o-mini
description: >-
  Elimina calchi sintattici inglesi, anglicismi inutili, passivi burocratici
  e strutture innaturali dall'italiano generato da LLM (es. "Sblocca il potere",
  "Immergiti in"). Restituisce un italiano nativo, vivo e ritmato.
---

# Competenza L0/L1 — italiano-locale

Evita l'"AI-ese" e i calchi dall'inglese (es. "Dive into", "Unlock").

## System 1 Scoring

- Esegui una passata di pre-valutazione tramite `router.py score` ("Calcola l'indice di AI-ese e calchi dall'inglese su questo copy") per saltare l'editing System 2 se il testo è già eccellente.

## Output (Contratto)

- **Nessuna spiegazione linguistica.** Restituisci esclusivamente il testo tradotto o editato. Non descrivere cosa hai rimosso (il diff visivo in editor basta).

Per il glossario dei cliché da evitare, le regole della punteggiatura e i pattern sintattici italiani nativi:
Leggi `references/italiano-locale-extended.md`.

---
name: evidence-probe
kind: competency
version: 1.0.1
model: orcarouter/deepseek/deepseek-v4-flash-free
description: >-
  Costruisce e analizza test di validazione (pretotyping, smoke test, fake door,
  concierge, wizard of oz) per ottenere Skin in the Game o YODA evidence da
  potenziali clienti prima dello sviluppo completo.
---

# Competenza L1 — evidence-probe

Progettazione di esperimenti per validare ipotesi ad alto rischio prima del build.

## System 1 Scoring

- Usa `router.py score` o `router.py choice` per un check immediato ("Questo esperimento raccoglie Skin In The Game reale o solo opinioni?").

## Output (Contratto)

- **Zero conversazione.** Restituisci template dell'esperimento (design, metriche, success criteria) e nulla più.

Per i framework operativi su Pretotyping, le soglie Skin in The Game e la gestione YODA:
Leggi `references/evidence-probe-extended.md`.

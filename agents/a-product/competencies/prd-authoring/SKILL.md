---
name: prd-authoring
kind: competency
version: 1.1.0
description: >-
  Scrive, struttura e revisiona Product Requirements Documents (PRD).
  Usa framework 1-Pager, definisce il Problem Space, vincoli tecnici e success metrics.
---

# Competenza L1 — prd-authoring

Competenza L1 per la gestione e stesura di Product Requirements Documents (PRD).

**Caricamento Dinamico & System 1:**

- Usa `router.py score` per validare rapidamente l'aderenza di un draft PRD rispetto ai vincoli di progetto a costo zero, prima di procedere a revisione logica.
- Usa `router.py choice` per identificare il miglior framework strutturale del documento.

## Output (Contratto)

- **Zero saluti o preamboli.** Nessuna spiegazione discorsiva sul "perché" il PRD è strutturato in un certo modo.
- Ritorna solo il Markdown compilato o il changelog.
- Mantieni tabelle compatte per le requirements.

Per il template completo del 1-Pager, i formati di spec, checklist di validazione PRD e guide di discovery:
Leggi `references/prd-extended.md`.

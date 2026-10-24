---
name: switch-interview
kind: competency
version: 1.1.0
description: >-
  Prepara, conduce (simulazione) e analizza JTBD Switch Interviews.
  Mappa le 4 forze (Push, Pull, Anxiety, Habit) e la Timeline del cliente
  (First Thought, Passive Looking, Active Looking, Deciding, Consuming).
---

# Competenza L1 — switch-interview (JTBD)

Esecuzione tecnica e analisi di Jobs To Be Done (JTBD) Switch Interviews.

## Pre-filtro

- Usa `router.py routing` sulle trascrizioni grezze d'intervista per smistare citazioni tra Push/Pull/Anxiety/Habit. Esegui il chunking per non intasare l'LLM Reasoning.

## Output (Contratto)

- **Zero verbosità narrativa.** Restituisci la Timeline e le 4 Forze in formato strutturato Markdown/Json.

Per le tecniche d'intervista (Police Interrogator, The Documentary), i pattern d'estrazione e i trigger:
Leggi `references/switch-interview-extended.md`.

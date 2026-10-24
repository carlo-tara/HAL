---
name: todo
kind: competency
version: 1.3.0
description: >-
  Gestisce la Mappa residui ./ToDo.md: scrivere Attività chiare, ordinare priorità,
  riconoscere ed eliminare completate, chiarire con ubiquitous-language e
  bounded-context (perché utili), risolvere ambiguità/duplicazioni/conflitti,
  taggare (feature, bug, techdebt, uiux…), flush «Già fatto» → ./CHANGELOG.md
  (Keep a Changelog). Lean summary ≤200 token + handoff-todo.json via
  prompt-builder. Use when ./ToDo.md is created or modified, when the user
  invokes /todo, or residual backlog needs triage.
---

# Competenza L1 — todo (Mappa residui)

Custode operativo di **`./ToDo.md`** (root repo). Backlog **rinfrescabile** — ≠ Progress (`agent-progress.md`, Capture append-only) e ≠ Slice accettato.

## Pipeline (`/todo`) e System 1

1. **Flush Deterministico CLI:** Usa `python3 agents/a-agentzero/scripts/agent-todo.py flush` per svuotare le voci `[x]` (con le sotto-voci) e la sezione «Già fatto» dal `ToDo.md` a `CHANGELOG.md` in formato Keep a Changelog (bug → Fixed, feature → Added, altri → Changed) senza l'LLM.
2. **Lean summary:** Usa `scripts/harness-prompt-builder.sh render` per caricare ≤200 token di titoli aperti P0/P1. Non leggere MAI il ToDo o il Changelog intero.
3. **Prune/Risolvi/Tag:** Operazioni mirate sul delta passato dallo script.

## Output (Contratto)

- **Zero verbosità, nessun preambolo, nessun riepilogo discorsivo.**
- Restituisci il nuovo blocco per `ToDo.md` o aggiorna `handoff-todo.json`.
- Restituisci sintesi `[N] Aperte, [M] Flushate in CHANGELOG` in una sola riga.

Per i dettagli su tagging, formato "Perché utile/Acceptance", regole CHANGELOG e mapping:
Leggi `references/todo-extended.md`.

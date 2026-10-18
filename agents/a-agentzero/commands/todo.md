---
model: orcarouter/deepseek/deepseek-v4-flash-free
---

# Mappa residui (L0)

## Objective

Eseguire l'igiene di **`./ToDo.md`** (root del repo attivo): inventario, prune, chiarisci, priorità, tag, flush obbligatorio di tutte le voci presenti nella sezione «Già fatto» verso `./CHANGELOG.md` ad ogni invocazione. Non avviare `/slice` né Act su Attività.

## Process

1. **Flush CLI Deterministico:** Esegui `python3 agents/a-agentzero/scripts/agent-todo.py flush` (o equivalente di progetto) prima dell'analisi LLM per spostare le voci chiuse `[x]` e svuotare "Già fatto" su `CHANGELOG.md` a costo zero.
2. **Lean summary** — dopo il flush deterministico, brief ≤200 token via `bash scripts/harness-prompt-builder.sh render` (titoli P0/P1, non file intero nel prompt modello).
3. Carica **a-harness** e la competenza **`todo`** (`a-harness/competencies/todo/SKILL.md` o `~/.agents/skills/a-harness/competencies/todo/SKILL.md`).
4. Esegui la pipeline `/todo` documentata lì (ordinamento priorità, prune, chiarisci - no flush LLM).
5. **Handoff** — `product/state/handoff-todo.json` (`handoff-write todo --field summary='…'`).
6. Non duplicare qui le regole di formato/tag/flush — restano nella competenza.

## Expected output

- **Nessun testo narrativo, convenevoli o riepilogo.**
- `handoff-todo.json` aggiornato.
- Sintesi numerica (una riga): `[N] Aperte, [M] Flushate in CHANGELOG`.
- Stop. Nessuna stampa a video dell'intero file modificato.

## Usage

```
/todo
```

## Notes

- Baseline L0: `a-agentzero/commands/todo.md`.
- Override progetto: `{repo}/.agents/commands/todo.md` se presente.
- Tool: `scripts/harness-prompt-builder.sh` + `handoff-todo.json`.
- Modello preferito OrcaRouter: `deepseek-v4-flash-free`; se non raggiungibile → default editor.
- Canone operativo: competenza `todo` sotto **a-harness** (non ridocumentare la pipeline in questo file).

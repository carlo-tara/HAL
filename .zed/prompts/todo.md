# Mappa residui (L0)

## Objective

Eseguire l'igiene di **`./ToDo.md`** (root del repo attivo): inventario, prune, chiarisci, priorità, tag, flush obbligatorio di tutte le voci presenti nella sezione «Già fatto» verso `./CHANGELOG.md` ad ogni invocazione. Non avviare `/slice` né Act su Attività.

## Process

1. **Lean summary** — dopo lettura ToDo, brief ≤200 token via `bash scripts/harness-prompt-builder.sh render` (titoli P0/P1, non file intero nel prompt modello).
2. Carica **a-harness** e la competenza **`todo`** (`a-harness/competencies/todo/SKILL.md` o `~/.agents/skills/a-harness/competencies/todo/SKILL.md`).
3. Esegui la pipeline `/todo` documentata lì (pass completo **deterministico**, una sola riscrittura coerente a fine pass).
4. **Handoff** — `.cursor/product/handoff-todo.json` (`handoff-write todo --field summary='…'`).
5. Non duplicare qui le regole di formato/tag/flush — restano nella competenza.

## Expected output

- `./ToDo.md` conforme (P0/P1/P2 / Già fatto)
- Eventuale append a `./CHANGELOG.md` Unreleased se c'era flush
- `handoff-todo.json` + sintesi breve: aperte vs flushate

## Usage

```
/todo
```

## Notes

- Baseline L0: `a-agentzero/commands/todo.md` (pubblicata da `/sync !` in `~/.cursor/commands/`).
- Override progetto: `{repo}/.cursor/commands/todo.md` se presente.
- Tool: `scripts/harness-prompt-builder.sh` + `handoff-todo.json`.
- Modello preferito OrcaRouter: `deepseek-v4-flash-free`; se non raggiungibile → default Cursor.
- Canone operativo: competenza `todo` sotto **a-harness** (non ridocumentare la pipeline in questo file).

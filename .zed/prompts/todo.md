# Mappa residui (L0)

## Objective

Eseguire l'igiene di **`./ToDo.md`** (root del repo attivo): inventario, prune, chiarisci, priorità, tag, flush obbligatorio di tutte le voci presenti nella sezione «Già fatto» verso `./CHANGELOG.md` ad ogni invocazione **su master** (post-land, transazione di consolidamento). Non avviare `/slice` né Act su Attività.

## Process

1. **Flush CLI Deterministico (transazione di master):** Esegui `python3 /var/www/hal_gateway/agents/a-agentzero/scripts/agent-todo.py flush` (o equivalente di progetto) prima dell'analisi LLM per spostare le voci chiuse `[x]` e svuotare "Già fatto" su `CHANGELOG.md` a costo zero. Il flush è consolidamento: solo su `master`/`main` checkout pulito, idealmente post-land (su slice il tool rifiuta — le `[x]` restano nel ToDo di branch e le trasporta il merge; `--force` per eccezioni umane); scrive sotto il flock cooperativo `agent-commit.lock` condiviso con commit/land. **Contratto di appiattimento:** del corpo di una voce sopravvivono solo il titolo e il figlio `- Esito:` — i report lunghi non vanno nel corpo del ToDo, nascono dove sopravvivono (nota datata in `docs/` di progetto o equivalente) e nel ToDo ci lasciano un puntatore. **Chiusura della transazione:** un flush riuscito su master si chiude nello stesso turno con `git add ToDo.md CHANGELOG.md && git commit` (un'unica invocazione) + `git push`; le prove dei gate `#human` (mhtml/JSON) vanno tracciate nel turno che le produce — mai lasciare un `[x]` flushato e non committato nel worktree.
2. **Lean summary** — dopo il flush deterministico, brief ≤200 token via `bash scripts/harness-prompt-builder.sh render` (titoli P0/P1, non file intero nel prompt modello).
3. Carica **a-harness** e la competenza **`todo`** (`/var/www/hal_gateway/agents/a-harness/competencies/todo/SKILL.md` o skill globale `~/.agents/skills`).
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
- Canone operativo: competenza `todo` sotto **a-harness** (non ridocumentare la pipeline in questo file).

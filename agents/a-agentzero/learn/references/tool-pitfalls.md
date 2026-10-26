# /learn — pitfall tool Zed (HAL)

Pattern validati in ≥2 sessioni. Consultare prima di ripetere tentativi a vuoto.

## Parametri numerici respinti come stringhe

- `read_file` con `start_line`/`end_line` e `terminal` con `timeout_ms` possono fallire con `invalid type: string, expected u32/u64` anche con valori numerici → non insistere: per i range usare `sed -n '<A>,<B>p' <file>` via terminal; per `terminal` omettere `timeout_ms` (il default basta per comandi brevi).
- Evidenza: sessione `/graph -y` Gate 5/6 (2026-10-26, 3 occorrenze) e sessione graph-cycle-sync-todo (2026-10-21, `product/session-learnings.md` § "Tool pitfalls Zed editor").

## Batch `edit_file` non atomico

- Se un edit del batch non combacia, la chiamata si interrompe: gli edit **prima** sono applicati, quelli **dopo** no → dopo un failure, rileggere il file e riapplicare solo i mancanti con il testo esatto corrente.
- Un formatter/reflow tra un turno e l'altro può spezzare liste YAML/Markdown (es. `tests: [a, b]` su più righe) e far fallire `old_text` multiriga → preferire ancore a riga singola o rileggere sempre prima di un nuovo batch.
- Evidenza: `product/state/work-graph.md` (2026-10-26, batch interrotto all'indice 1 con YAML riflow; listini `tests:` multiriga).

## Assenze da verificare prima di ToDo/claim

- Prima di asserire che uno script o un riferimento manca, `grep -r` sul repo: il claim «il comando graph referenzia `agents/scripts/harness-graph.py` mancante» (2026-10-26) era infondato — il comando usa solo `scripts/harness-prompt-builder.sh`.
- Routing System 1: se `python3 router.py routing` risponde `ABSTAIN`, non forzare retry — decide la tabella Destinazione di `learn-guidelines.md` (System 2), come da fallback documentato dal router stesso.

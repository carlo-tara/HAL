---
name: review
version: 1.0.1
description: Command review for HAL workspace.
---

# Code review (L0)

## Objective

Revisione manuale (checklist) del diff o dell'area indicata nel **repository corrente**.

## Process

1. **Diff-tiering e pre-filtraggio:**
   - Inizia con `git status -s` e `git diff --stat`.
   - Seleziona solo i file modificati di logica o testo (salta lock, map, minified).
   - Se il diff totale > 150 righe, ispeziona un path alla volta. Non riversare mai il diff totale nel contesto.
   - Traccia: `python3 scripts/token_budget.py log diff_read <lines>`.
2. **Chunk-based Scoring (System 1):**
   - Frammenta il diff in chunk <= 80 righe.
   - Per ogni chunk: `python3 router.py score "<chunk>" --criteria "Rischio di regressione o bug"`.
   - Se score < 0.5: skip del chunk (nessun finding significativo).
   - Solo chunk con score alto → System 2 per analisi approfondita.
   - Traccia: `python3 scripts/token_budget.py log chunk_score <score> <threshold>`.
3. **Lazy-load:**
   - Se devi leggere file non modificati per contesto: usa `start_line`/`end_line`.
   - Mai leggere file interi se > 100 righe.
   - Traccia: `python3 scripts/token_budget.py log lazy_load <path> <lines_read> <total_lines>`.
4. **Funzionalità**: il comportamento corrisponde al task? Edge case evidenti?
5. **Qualità**: chiarezza, gestioni errore, duplicazioni evitabili nel solo scope del diff.
6. **Test**: copertura adeguata o gap da segnalare; non richiedere suite assenti dal repo.
7. **Documentazione**: contratti pubblici / README / docs aggiornati se il diff li richiede.
8. **Sicurezza**: niente segreti hardcoded; `.env` non tracciato; input esterni validati dove pertinente.
9. Se presenti skill HAL nel diff: frontmatter `version` / `extends-version`, protocollo, niente indebolimento sicurezza L0.
10. Output: report in chat; file review persistente **solo se** l'utente lo chiede (es. `docs/reviews/`).

## Checklist

- [ ] Correttezza rispetto al task
- [ ] Sicurezza (segreti, auth, path sensibili)
- [ ] Test / verifiche adeguate o gap espliciti
- [ ] Doc allineata se necessario
- [ ] Nessun scope creep nel diff

## Expected output

- **Nessun preambolo narrativo o convenevoli.**
- Lista finding compatta (severità, file:riga, suggerimento).
- Se il diff è perfetto, rispondi solo "Nessun finding (OK)." senza spiegazioni aggiuntive.
- Max 500 token output. Se necessario, scrivere dettagli in file esterni.

## Telemetria

```bash
python3 scripts/token_budget.py init
python3 scripts/token_budget.py log s1_call
python3 scripts/token_budget.py log diff_read 120
python3 scripts/token_budget.py log chunk_score 0.6 0.5
python3 scripts/token_budget.py log output 200
python3 scripts/token_budget.py report
```

## Usage

```
/review
/review path/to/area
```

## Notes

- Baseline L0: `a-agentzero/commands/review.md` (pubblicata da `/sync !`).
- Override progetto: `{repo}/.agents/commands/review.md` se presente.
- Non confondere con `/test` (esecuzione automatica) se il progetto lo definisce.
- Per miglioramenti proattivi usare `/improve`.

---
model: orcarouter/deepseek/deepseek-v4-flash
model-fallback: cursor-default
---

# Code review (L0)

## Objective

Revisione manuale (checklist) del diff o dell'area indicata nel **repository corrente**.

## Process

1. **Funzionalità**: il comportamento corrisponde al task? Edge case evidenti?
2. **Qualità**: chiarezza, gestioni errore, duplicazioni evitabili nel solo scope del diff.
3. **Test**: copertura adeguata o gap da segnalare; non richiedere suite assenti dal repo.
4. **Documentazione**: contratti pubblici / README / docs aggiornati se il diff li richiede.
5. **Sicurezza**: niente segreti hardcoded; `.env` non tracciato; input esterni validati dove pertinente.
6. Se presenti skill HAL nel diff: frontmatter `version` / `extends-version`, protocollo, niente indebolimento sicurezza L0.
7. Output: report in chat; file review persistente **solo se** l'utente lo chiede (es. `docs/reviews/`).

## Checklist

- [ ] Correttezza rispetto al task
- [ ] Sicurezza (segreti, auth, path sensibili)
- [ ] Test / verifiche adeguate o gap espliciti
- [ ] Doc allineata se necessario
- [ ] Nessun scope creep nel diff

## Expected output

- Lista finding (blocker / nice-to-have)
- Suggerimenti concreti (file + idea fix)
- Opzionale: path del file review se creato

## Usage

```
/review
/review path/to/area
```

## Notes

- Baseline L0: `a-agentzero/commands/review.md` (pubblicata da `/sync !`).
- Override progetto: `{repo}/.cursor/commands/review.md` se presente.
- Non confondere con `/test` (esecuzione automatica) se il progetto lo definisce.
- Per miglioramenti proattivi usare `/improve`.

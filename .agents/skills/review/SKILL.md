---
name: review
version: 1.0.0
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
2. **Funzionalità**: il comportamento corrisponde al task? Edge case evidenti?
3. **Qualità**: chiarezza, gestioni errore, duplicazioni evitabili nel solo scope del diff.
4. **Test**: copertura adeguata o gap da segnalare; non richiedere suite assenti dal repo.
5. **Documentazione**: contratti pubblici / README / docs aggiornati se il diff li richiede.
6. **Sicurezza**: niente segreti hardcoded; `.env` non tracciato; input esterni validati dove pertinente.
7. Se presenti skill HAL nel diff: frontmatter `version` / `extends-version`, protocollo, niente indebolimento sicurezza L0.
8. Output: report in chat; file review persistente **solo se** l'utente lo chiede (es. `docs/reviews/`).

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

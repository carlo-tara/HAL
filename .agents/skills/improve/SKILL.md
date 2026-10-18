---
name: improve
version: 1.0.0
description: Command improve for HAL workspace.
---

# Miglioramenti (L0)

## Objective

Analizzare e proporre (o applicare con approvazione) miglioramenti mirati al codice o alle skill del **repository corrente**, senza refactor gratuiti.

## Process

1. **Diff-tiering e pre-filtraggio (Evitare context dumping):**
   - Esegui `git status -s` e `git diff --stat` per avere una panoramica.
   - Escludi lockfile, file autogenerati o vendor.
   - Leggi il diff completo solo se <= 150 righe, altrimenti leggi `git diff` limitato ai soli path rilevanti.
2. **Scoring Euristico (System 1):** Usa `python3 router.py score "<chunk>" --criteria "Opportunità di refactoring a basso rischio e alto impatto"` per filtrare le proposte senza consumare token di ragionamento LLM. Procedi con System 2 solo se lo score è alto.
3. **Qualità** (solo per le aree con score System 1 positivo):
   - Duplicazioni evitabili, nomi chiari, percorsi d'errore gestiti
   - Coerenza con convenzioni del repo (`README`, linter, skill L2)
   - Performance o DX solo se evidenti e a basso rischio
4. **Sicurezza**: niente segreti in codice; credenziali solo da `.env` del progetto.
5. Dopo modifiche sostanziali: eseguire le verifiche tipiche del repo (test, build, lint) se disponibili.
6. Evitare di "pulire" file non toccati dal task.
7. Se si modificano skill agenti: bump `version` + CHANGELOG e, se serve, `/sync` / `/version`.

## Checklist

- [ ] Miglioramenti pertinenti al task corrente
- [ ] Nessun refactor di massa non richiesto
- [ ] Verifiche post-edit eseguite o motivate
- [ ] Nessun path hardcoded a progetti non correlati
- [ ] Nessun segreto introdotto

## Expected output

- **Nessun preambolo narrativo o riepilogo.**
- Tabella compatta: `| File | Riga | Difetto | Fix proposto |`
- Se applicati: diff stringente e stato `make test` (una riga).

## Usage

```
/improve
```

## Notes

- Baseline L0: `a-agentzero/commands/improve.md` (pubblicata da `/sync !`).
- Override progetto: `{repo}/.agents/commands/improve.md` se presente.
- Per revisione mirata al diff usare `/review`.

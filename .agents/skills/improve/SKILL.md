---
name: improve
version: 1.2.1
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
   - Traccia: `python3 scripts/token_budget.py log diff_read <lines>`.
2. **Chunk-based Scoring (System 1):**
   - Frammenta l'input in chunk <= 80 righe prima di valutare.
   - Per ogni chunk: `python3 router.py score "<chunk>" --criteria "Opportunità di refactoring a basso rischio e alto impatto"`.
   - Se lo score è sotto threshold (0.5): scarta il chunk senza System 2.
   - Solo i chunk con score alto passano a System 2.
   - Traccia: `python3 scripts/token_budget.py log chunk_score <score> <threshold>`.
3. **Lazy-load:**
   - Prima di `read_file`: stimare la dimensione del file.
   - Se > 100 righe, usare `start_line` / `end_line` per leggere solo le sezioni rilevanti.
   - Mai leggere file interi se non strettamente necessario.
   - Traccia: `python3 scripts/token_budget.py log lazy_load <path> <lines_read> <total_lines>`.
4. **Qualità** (solo per le aree con score System 1 positivo):
   - Duplicazioni evitabili, nomi chiari, percorsi d'errore gestiti
   - Coerenza con convenzioni del repo (`README`, linter, skill L2)
   - Performance o DX solo se evidenti e a basso rischio
5. **Sicurezza**: niente segreti in codice; credenziali solo da `.env` del progetto.
6. Dopo modifiche sostanziali: eseguire le verifiche tipiche del repo (test, build, lint) se disponibili.
7. Evitare di "pulire" file non toccati dal task.
8. Se si modificano skill agenti: bump `version` + CHANGELOG e, se serve, `/sync` / `/version`.

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
- Max 500 token output. Se necessario, scrivere dettagli in file esterni.

## Telemetria

```bash
python3 scripts/token_budget.py init            # una volta all'avvio
python3 scripts/token_budget.py log s1_call     # ogni chiamata Laya
python3 scripts/token_budget.py log s2_call     # ogni reasoning System 2
python3 scripts/token_budget.py log output 350  # output generato
python3 scripts/token_budget.py report          # report finale (JSONL: events/token-budget.jsonl)
```

## Usage

```
/improve
```

## Notes

- Baseline L0: `a-agentzero/commands/improve.md` (pubblicata da `/sync !`).
- Override progetto: `{repo}/.agents/commands/improve.md` se presente.
- Per revisione mirata al diff usare `/review`.

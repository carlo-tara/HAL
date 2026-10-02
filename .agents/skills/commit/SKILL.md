---
name: commit
version: 1.0.0
description: Command commit for HAL workspace.
---

# Pre-commit (L0)

## Objective

Verificare che le modifiche siano pronte per il commit nel **repository corrente** e proporre messaggio e comando `git`. Non eseguire il commit a meno che l'utente non lo chieda esplicitamente.

## Process

1. Dalla **root del repository** attivo:
   - `git status` e `git diff` (staged + unstaged)
   - Identificare area toccata (src, docs, test, config, skill, …)
2. **Segreti**: niente `.env`, credenziali, token, chiavi API nei file tracciati.
3. **Verifiche contestuali** (solo se esistono e sono pertinenti al diff):
   - script/test documentati in `README.md`, `package.json`, `Makefile`, `CONTRIBUTING.md`
   - lint/test del linguaggio in uso
   - doc operativa se cambiano contratti pubblici
4. Se il repo ha skill agenti HAL: allineamento `version` / `extends-version` / `CHANGELOG` se il diff tocca skill (vedi anche `/version`, `/sync`).
5. Generare messaggio di commit (conventional) e comando `git add` / `git commit` suggerito.

## Checklist

- [ ] Diff compreso; scope del commit chiaro
- [ ] Nessun segreto nel commit
- [ ] Test/verifiche rilevanti eseguiti o motivati se saltati
- [ ] Doc aggiornata se cambiano contratti o workflow
- [ ] Messaggio conventional coerente col diff

## Commit message (conventional)

Esempi:

- `feat:` nuova funzionalità
- `fix:` correzione bug
- `docs:` solo documentazione
- `chore:` tooling, dipendenze, config
- `refactor:` ristrutturazione senza cambio comportamento

Messaggio in **frasi complete**, lingua coerente col resto del repo.

## Expected output

- Esito verifiche eseguite
- Checklist sintetica
- Messaggio commit proposto + `git add …` e `git commit -m "…"`

## Usage

```
/commit
```

## Notes

- Baseline L0: `a-agentzero/commands/commit.md` (pubblicata da `/sync !` in `~/.cursor/commands/`).
- Override progetto: `{repo}/.cursor/commands/commit.md` se presente.
- Per snapshot stato repo usare `/snapshot` se disponibile nel progetto.

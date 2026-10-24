---

# Pre-commit (L0)

## Objective

Verificare che le modifiche siano pronte per il commit nel **repository corrente** e proporre messaggio e comando `git`. Non eseguire il commit a meno che l'utente non lo chieda esplicitamente.

## Process

1. **Diff-tiering (System 1 & pre-filtraggio):**
   - Esegui `git status -s` e `git diff --stat`.
   - Se il diff totale > 150 righe, ispeziona solo i chunk o file modificati rilevanti (escludendo vendor, lockfile, asset autogenerati).
   - Usa `python3 router.py choice "Scegli il prefisso conventional commit per queste modifiche" --options feat fix docs chore refactor` per determinare il tipo a costo zero token.
2. Dalla **root del repository** attivo:
   - Identificare area toccata (src, docs, test, config, skill, …) in base all'output precedente.
3. **Segreti**: niente `.env`, credenziali, token, chiavi API nei file tracciati.
4. **Verifiche contestuali** (solo se esistono e sono pertinenti al diff):
   - script/test documentati in `README.md`, `package.json`, `Makefile`, `CONTRIBUTING.md`
   - lint/test del linguaggio in uso
   - doc operativa se cambiano contratti pubblici
5. Se il repo ha skill agenti HAL: allineamento `version` / `extends-version` / `CHANGELOG` se il diff tocca skill (vedi anche `/version`, `/sync`).
6. Generare messaggio di commit (conventional) e comando `git add` / `git commit` suggerito.

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

- **Nessun preambolo o saluto.**
- **Nessuna ripetizione** della checklist statica.
- Esito test verificati (una riga).
- Blocco di codice con messaggio commit + `git add …` e `git commit -m "…"` pronto al copia-incolla.

## Usage

```
/commit
```

## Notes

- Baseline L0: `a-agentzero/commands/commit.md`.
- Override progetto: `{repo}/.agents/commands/commit.md` se presente.
- Per snapshot stato repo usare `/snapshot` se disponibile nel progetto.

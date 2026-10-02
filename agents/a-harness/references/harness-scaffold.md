# Harness scaffold — bootstrap su repo greenfield

Workflow per portare un progetto consumer sotto Meta-Harness.

Profiles: [bootstrap-profiles.md](bootstrap-profiles.md)

## Prerequisiti

- Repo con codice applicativo (o greenfield post-PRD/Gherkin)
- Stack test/lint identificabile

## Checklist `/bootstrap`

```
Task Progress:
- [ ] 0. Scegliere profile minimal | standard
- [ ] 1. Creare L2 `.cursor/skills/harness-{progetto}/SKILL.md` da extension-template
- [ ] 2. Copiare/adattare Makefile da makefile-template.mk (CI-first)
- [ ] 3. (standard) docs/glossary.md + docs/bounded-contexts.md
- [ ] 4. Creare agent-progress (+ opz. session-learnings, freeze) da template
- [ ] 5. Verificare make test-unit, make pre-commit
- [ ] 6. Raggiungere make ready-for-review
- [ ] 7. (Opz.) hooks da cursor-hooks-recipe.md
- [ ] 8. (Opz.) Mirror competenze in .cursor/rules/
- [ ] 9. `/steward` audit iniziale + harness changelog
```

## Ordine consigliato

1. **Makefile prima** — senza gate test non scalare autonomia
2. **Glossario + bounded contexts** (standard) — prima del primo `/cycle`
3. **Progress file** — session_id da subito
4. **Primo slice** — medium discrete da un `.feature`

## Mirror `.cursor/rules/` (opzionale)

| File L2 | Competenza sorgente |
|---------|---------------------|
| `.cursor/rules/tdd-red.mdc` | `tdd-red` |
| `.cursor/rules/tdd-green.mdc` | `tdd-green` |
| `.cursor/rules/tdd-refactor.mdc` | `tdd-refactor` |
| `.cursor/rules/steward.mdc` | `steward` |

Non duplicare corpus intero — link a `@a-harness` + delta L2.

## Anti-pattern bootstrap

- Iniziare `/cycle` senza Makefile
- Glossario vuoto su dominio non banale
- `ready-for-review` che non esegue realmente pre-commit
- Autonomia multi-slice con stub eterni

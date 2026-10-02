---
model: orcarouter/openai/gpt-4o-mini
model-fallback: cursor-default
---

# Documentazione (L0)

## Objective

Aggiornare la documentazione operativa del **repository corrente** dopo cambiamenti significativi a codice, config, workflow o API pubbliche.

## Fonti di verità (discovery)

Cerca in ordine ciò che esiste nel repo:

| Cosa | Dove tipico |
|------|-------------|
| Panoramica | `README.md` |
| Doc operativa | `docs/` |
| Changelog | `CHANGELOG.md` (root o per pacchetto) |
| Skill agenti L2 | `.cursor/skills/*/SKILL.md` |
| Brand / tono | `.cursor/brands/*.md` |
| Protocollo HAL (se AF) | `a-agentzero/AGENT-PROTOCOL.md` |

Adatta l'elenco al progetto: non inventare file assenti.

## Process

1. Leggere `git log` recente e diff se il task riguarda una release o un cambiamento specifico.
2. Allineare `README.md` e doc in `docs/` a:
   - quick start reale
   - comandi build/test/deploy verificati
   - link alle fonti di dettaglio (niente duplicazione enciclopedica)
3. Aggiornare tracker/changelog di progetto solo se già in uso.
4. Non documentare segreti (API key, token, path con credenziali).
5. Se toccate skill agenti: verificare coerenza con `/version` e CHANGELOG della skill.

## Checklist

- [ ] README / docs allineati al comportamento attuale
- [ ] Comandi in doc verificati (eseguiti o controllati)
- [ ] Nessun segreto in chiaro
- [ ] Nessuna doc orfana o contraddittoria introdotta

## Expected output

- Elenco file documentazione toccati
- Breve riepilogo in chat di cosa è stato documentato
- Suggerimento commit `docs:` se l'utente chiede commit

## Usage

```
/document
/document deploy
/document API
```

## Notes

- Baseline L0: `a-agentzero/commands/document.md` (pubblicata da `/sync !`).
- Override progetto: `{repo}/.cursor/commands/document.md` se presente.
- Per versioning formale usare `/version`; per deploy agenti `/sync`.

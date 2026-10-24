---
name: document
version: 1.0.0
description: Command document for HAL workspace.
---

---

# Documentazione (L0)

## Objective

Aggiornare la documentazione operativa del **repository corrente** dopo cambiamenti significativi a codice, config, workflow o API pubbliche.

## Fonti di verità (discovery)

Cerca in ordine ciò che esiste nel repo:

| Cosa                   | Dove tipico                           |
| ---------------------- | ------------------------------------- |
| Panoramica             | `README.md`                           |
| Doc operativa          | `docs/`                               |
| Changelog              | `CHANGELOG.md` (root o per pacchetto) |
| Skill agenti L2        | `.agents/skills/*/SKILL.md`           |
| Brand / tono           | `docs/brands/*.md`                    |
| Protocollo HAL (se AF) | `a-agentzero/AGENT-PROTOCOL.md`       |

Adatta l'elenco al progetto: non inventare file assenti.

## Process

1. **Routing Documentale (System 1):** Usa `python3 router.py routing "[argomento] o diff" --routes README docs CHANGELOG skill` per determinare quale sezione documentale aggiornare a costo zero.
2. Leggere `git log` recente e diff (usando la pre-selezione System 1) se il task riguarda una release.
3. Allineare i file scelti dal triage a:
   - quick start reale
   - comandi build/test/deploy verificati
   - link alle fonti di dettaglio (niente duplicazione enciclopedica)
4. Aggiornare tracker/changelog di progetto solo se già in uso.
5. Non documentare segreti (API key, token, path con credenziali).
6. Se toccate skill agenti: verificare coerenza con `/version` e CHANGELOG della skill.

## Checklist

- [ ] README / docs allineati al comportamento attuale
- [ ] Comandi in doc verificati (eseguiti o controllati)
- [ ] Nessun segreto in chiaro
- [ ] Nessuna doc orfana o contraddittoria introdotta

## Expected output

- **Nessun preambolo narrativo né saluti.**
- Elenco puntato sintetico dei file aggiornati.
- Comando `git commit -m "docs: ..."` (solo se richiesto dall'utente).

## Usage

```
/document
/document deploy
/document API
```

## Notes

- Baseline L0: `a-agentzero/commands/document.md` (pubblicata da `/sync !`).
- Override progetto: `{repo}/.agents/commands/document.md` se presente.
- Per versioning formale usare `/version`; per deploy agenti `/sync`.

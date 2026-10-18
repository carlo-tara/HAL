---
name: sync
version: 1.1.5
model: orcarouter/deepseek/deepseek-v4-flash
description: >-
  Sincronizza agenti HAL L0/L1 (deploy) e comandi Cursor L0 ereditabili; verifica
  allineamento versioni; analizza L2 per generalizzazione (/sync <). Usa quando
  chiede /sync, /sync ?, /sync !, /sync < o promuovere pattern.
---

# /sync — sincronizzazione agenti (L0)

Skill utility di **a-agentzero**. Pubblica agenti e comandi in `~/.cursor`, riporta lo stato versioni, analizza le skill L2 per proporne la promozione.

**Reference:**

- [agent-versioning.md](../references/agent-versioning.md)
- [sync-guidelines.md](references/sync-guidelines.md) (workflow dettagliati, comandi CLI e format output)

---

## Invocazione

| Comando   | Modalità                                                                                    |
| --------- | ------------------------------------------------------------------------------------------- |
| `/sync ?` | **Report** — `--dry-run`, mostra STALE e stato comandi. Nessuna scrittura                   |
| `/sync !` | **Deploy** — esegue deploy-all, symlink comandi, e report finale                            |
| `/sync <` | **Generalizza** — analizza skill L2 e propone DUP/promozione (nessuna scrittura automatica) |
| `/sync`   | Mostra sintassi                                                                             |

---

## Workflow `?` e `!`

```
Task Progress:
- [ ] 1. Esegui `bash agents/a-agentzero/scripts/sync-agents.sh [--dry-run] [--only-stale] [--projects ...]`
- [ ] 2. Se STALE, chiedi all'utente per sync selettivo ([sync:safe] vs [sync:review]).
- [ ] 3. Emetti report tabellare.
```

---

## Workflow `<` (Generalizza)

```
Task Progress:
- [ ] 1. Identifica i progetti L2 (argomenti path o fallback su discovery `/var/www/`).
- [ ] 2. Esegui lo script `python3 agents/a-agentzero/scripts/l2-analyzer.py` per estrarre duplicati programmaticamente senza consumare token di lettura.
- [ ] 3. Identifica duplicati rispetto a padri (DUP) o pattern comuni (NEED-N).
- [ ] 4. Emetti report per l'umano; nessuna scrittura su file.
```

Per dettaglio logica e output, usa `sync-guidelines.md`.

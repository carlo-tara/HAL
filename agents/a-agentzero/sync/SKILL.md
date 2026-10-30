---
name: sync
version: 1.2.1
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

## Notes

- **Mirror dei comandi L0**: `.agents/skills/<cmd>/SKILL.md` e `.zed/prompts/<cmd>.md` sono generati da `agents/a-agentzero/commands/<cmd>.md` (link-workspace-skills.sh): contenuto e `version` vivono nel canonico, le modifiche al mirror sono annullate da `/sync !` (caso graph 1.0.3, 2026-10-30). Se dopo il deploy un mirror risulta sporco di contenuto vecchio, il canonico è indietro: bumpa il canonico e rilancia il link.
- `sync` (come `learn`) è una skill utility canonica in `agents/a-agentzero/<nome>/`, pubblicata in `.agents/skills/<nome>` **via symlink**: lì l'edit del canonico è diretto e non c'è rigenerazione. La regola del mirror vale solo per i comandi L0 in `a-agentzero/commands/` (graph, todo, slice, cycle, version, document, commit, review, improve).


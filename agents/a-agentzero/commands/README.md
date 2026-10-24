# Comandi L0 (baseline ereditabile)

Sorgente canonica dei comandi condivisi: `version`, `document`, `review`, `improve`, `commit`, `todo`, `slice`, `cycle`, `graph`.

| Livello                        | Path                                                    | Ruolo                                                         |
| ------------------------------ | ------------------------------------------------------- | ------------------------------------------------------------- |
| **L0 (canone)**                | `a-agentzero/commands/*.md`                             | Baseline generica                                             |
| **Workspace (skills/prompts)** | `.agents/commands/`, `.agents/skills/`, `.zed/prompts/` | Symlink generati da `agents/scripts/link-workspace-skills.sh` |
| **Progetto**                   | `{repo}/.agents/commands/`                              | Override: se presente, vince sul comando standard             |

## Pubblicazione

```bash
# Via sync (canale ufficiale)
bash a-agentzero/scripts/sync-agents.sh          # deploy + report
bash a-agentzero/scripts/sync-agents.sh --dry-run # solo report (anche stato comandi)

# Equivalente: deploy L0 include i symlink comandi
bash a-agentzero/deploy.sh
```

`/sync ?` e `/sync !` riportano lo stato dei symlink (`OK` / `MISSING` / `DRIFT`).  
Con `--projects DIR`: per ogni repo, `override` vs `inherit` sui nomi L0.

## Override di progetto

Non copiare i file L0 in ogni repo. Crea `{repo}/.agents/commands/{nome}.md` solo se serve un workflow specifico (test locali, path, checklist dominio).

## Scope

Questi **nove** comandi sono L0. Altri slash (`snapshot`, `test`, comandi dominio) restano locali al progetto o ad altri canali.

| Comando    | Ruolo breve                             |
| ---------- | --------------------------------------- |
| `version`  | Semver / CHANGELOG skill                |
| `document` | Documentazione                          |
| `review`   | Review codice/skill                     |
| `improve`  | Miglioramenti mirati                    |
| `commit`   | Pre-commit / messaggio                  |
| `todo`     | Igiene `./ToDo.md` (→ a-harness `todo`) |
| `slice`    | Plan slice (→ a-harness)                |
| `cycle`    | Skeleton RGR (→ a-harness)              |

- `graph` | Work Graph / Loop (→ a-harness `graph`) |

## Override di progetto

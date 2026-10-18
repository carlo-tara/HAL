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

| Comando    | Ruolo breve                             | Modello preferito        |
| ---------- | --------------------------------------- | ------------------------ |
| `version`  | Semver / CHANGELOG skill                | `deepseek-v4-flash-free` |
| `document` | Documentazione                          | `gpt-4o-mini`            |
| `review`   | Review codice/skill                     | `deepseek-v4-flash`      |
| `improve`  | Miglioramenti mirati                    | `deepseek-v4-flash`      |
| `commit`   | Pre-commit / messaggio                  | `gpt-4o-mini`            |
| `todo`     | Igiene `./ToDo.md` (→ a-harness `todo`) | `deepseek-v4-flash-free` |
| `slice`    | Plan slice (→ a-harness)                | `deepseek-v4-flash`      |
| `cycle`    | Skeleton RGR (→ a-harness)              | `deepseek-v4-flash`      |
| `graph`    | Work Graph / Loop (→ a-harness `graph`) | `deepseek-v4-flash`      |

## Modello LLM preferito

Ogni comando L0 dichiara in frontmatter:

```yaml
model: orcarouter/…
```

Se il modello OrcaRouter non è raggiungibile o configurato, usare il **modello di default** attivo nell'editor.

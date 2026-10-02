# Comandi Cursor L0 (baseline ereditabile)

Sorgente canonica dei slash command condivisi: `version`, `document`, `review`, `improve`, `commit`, `todo`, `slice`, `cycle`, `graph`.

| Livello | Path | Ruolo |
|---------|------|-------|
| **L0 (canone)** | `a-agentzero/commands/*.md` | Baseline generica |
| **User (deploy)** | `~/.cursor/commands/` | Symlink pubblicati da **`/sync !`** via `deploy.sh` |
| **Progetto** | `{repo}/.cursor/commands/` | Override: se presente, vince sul comando user |

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

Non copiare i file L0 in ogni repo. Crea `{repo}/.cursor/commands/{nome}.md` solo se serve un workflow specifico (test locali, path, checklist dominio).

## Scope

Questi **nove** comandi sono L0. Altri slash (`snapshot`, `test`, comandi dominio) restano locali al progetto o ad altri canali.

| Comando | Ruolo breve | Modello preferito |
|---------|-------------|-------------------|
| `version` | Semver / CHANGELOG skill | `deepseek-v4-flash-free` |
| `document` | Documentazione | `gpt-4o-mini` |
| `review` | Review codice/skill | `deepseek-v4-flash` |
| `improve` | Miglioramenti mirati | `deepseek-v4-flash` |
| `commit` | Pre-commit / messaggio | `gpt-4o-mini` |
| `todo` | Igiene `./ToDo.md` (→ a-harness `todo`) | `deepseek-v4-flash-free` |
| `slice` | Plan slice (→ a-harness) | `deepseek-v4-flash` |
| `cycle` | Skeleton RGR (→ a-harness) | `deepseek-v4-flash` |
| `graph` | Work Graph / Loop (→ a-harness `graph`) | `deepseek-v4-flash` |

## Modello LLM preferito

Ogni comando L0 dichiara in frontmatter:

```yaml
model: orcarouter/…
model-fallback: cursor-default
```

Se il modello OrcaRouter non è raggiungibile/configurato in Cursor, usare il **modello di default** dell'IDE. Contratto: `.cursor/product/contracts/check-orcarouter-command-models.sh`.

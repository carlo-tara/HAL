---
version: 1.0.1
---

# /sync — sincronizzazione agenti (L0)

## Objective

Esporre la sincronizzazione HAL come comando L0 a tutti gli effetti: `?` report, `!` deploy, `<` generalizza. Il canone operativo (workflow, script, formati di output, tool MCP equivalenti) resta la skill utility `a-agentzero/sync/` con versione e CHANGELOG proprî — qui vive solo la superficie d'invocazione. Non avviare `/sync !` senza conferma quando tocca stati condivisi.

## Process

1. **Carica il canone:** `read /var/www/hal_gateway/agents/a-agentzero/sync/SKILL.md` (il deep skill nel bundle; la skill globale `~/.agents/skills/sync` è il wrapper generato da questo file — nessun mirror locale in `.agents/skills/`).
2. **Instrada l'argomento:**
   - `?` → `bash /var/www/hal_gateway/agents/a-agentzero/scripts/sync-agents.sh --dry-run [--only-stale] [--projects <consumer>...]`
   - `!` → `bash /var/www/hal_gateway/agents/a-agentzero/scripts/sync-agents.sh` — solo da hal_gateway: la «Guardia HAL» di `link-workspace-skills.sh` rifiuta l'esecuzione da mount consumer.
   - `<` → `python3 /var/www/hal_gateway/agents/a-agentzero/scripts/l2-analyzer.py` (sola lettura, nessuna scrittura automatica)
   - senza argomento → mostra questa invocazione.
3. **Dettagli di workflow e formati** (e i tool MCP `sync_report`, `sync_deploy`, `l2_analyze` che delegano gli stessi script): `references/sync-guidelines.md` dentro la skill canone.
4. Esegui quanto documentato lì; non reinventare la pipeline qui.

## Expected output

- `?`: tabella STALE/comandi, zero scritture. `!`: esito deploy-all (link + publish globali) + report catene. `<`: candidati DUP/NEED-N senza modifiche su file.

## Usage

```
/sync ? | ! | <
```

## Notes

- Baseline L0: `a-agentzero/commands/sync.md`. Canone operativo: skill utility `a-agentzero/sync/SKILL.md`.
- Il wrapper generato (prompt/skill globale) è invocabile anche dal modello; la skill deep conserva le proprie flag di invocazione.
- Override progetto: `{repo}/.agents/commands/sync.md` se presente (skill locale omonima ha priorità sulla globale).

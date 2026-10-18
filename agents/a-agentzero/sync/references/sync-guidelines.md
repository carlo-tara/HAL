# /sync — Guide Operative

## Comandi Shell
```bash
# Report-only
bash agents/a-agentzero/scripts/sync-agents.sh --dry-run
# Deploy L0+L1+comandi + report
bash agents/a-agentzero/scripts/sync-agents.sh
# Include progetti consumer
bash agents/a-agentzero/scripts/sync-agents.sh --projects /path/a
# Catena singola
bash agents/a-agentzero/scripts/agent-version.sh chain <SKILL.md>
```

## Workflow `/sync !` (Deploy)
- Esegui `sync-agents.sh` (include deploy comandi L0 in ~/.cursor/commands).
- Se nessuna STALE: report OK.
- Se STALE: proponi sync selettivo. [sync:safe] = solo bump `extends-version` e `version` patch figlio. [sync:review] = adatta delta prima di bump.

## Workflow `/sync <` (Generalizza)
- Analisi **sola lettura**. Non modifica `extends-version` automaticamente.
- Risolvi progetti da path, cwd, o discovery in `/var/www/`.
- Inventario `.cursor/skills/*/SKILL.md`.
- Carica padri e confronta voci: DUP | L1 | L0 | L2 | NEED-N.
- Cross-progetto: pattern ripetuti in >=2 progetti hanno priorità di promozione.
- Emetti report e attendi conferma utente.

## Formato Output `/sync ? / !`
```markdown
# /sync — Sincronizzazione agenti
## Deploy
[eseguito | saltato]
## Comandi L0
| Comando | Stato |
|---------|-------|
| version | OK / MISSING / DRIFT |
## Catene
| Agente | Version | Extends | Stato |
|--------|---------|---------|-------|
| ... | ... | ... | OK / STALE |
```

## Formato Output `/sync <`
```markdown
# /sync < — Generalizzazione
## Progetti analizzati
## Candidati
### 1. [DUP|L0] Titolo
- **Cosa:** ...
- **Perché:** ...
```

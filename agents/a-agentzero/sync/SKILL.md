---
name: sync
version: 1.1.3
model: orcarouter/deepseek/deepseek-v4-flash
model-fallback: cursor-default
description: >-
  Sincronizza agenti HAL L0/L1 (deploy in ~/.cursor) e comandi Cursor L0
  ereditabili; verifica allineamento versioni; analizza L2 per generalizzazione
  L1/L0 (/sync <). Usa quando l'utente chiede /sync, /sync ?, /sync !, /sync <,
  deploy-all, STALE extends-version, o promuovere pattern da L2.
---

# /sync — sincronizzazione agenti (L0)

Skill utility di **a-agentzero**. Pubblica L0/L1 in `~/.cursor` (skill, agents, **comandi**), riporta lo stato sync selettivo (versioni / CHANGELOG pending), e analizza skill L2 per candidati di generalizzazione verso L1/L0.

**Reference:** [agent-versioning.md](../references/agent-versioning.md) · [l2-generalization.md](references/l2-generalization.md) · script [sync-agents.sh](../scripts/sync-agents.sh) · [agent-version.sh](../scripts/agent-version.sh) · comandi [commands/](../commands/)

---

## Invocazione

| Input utente | Modalità |
|--------------|----------|
| `/sync ?` | **Report** — catene versioni + stato comandi L0 (equivalente `--dry-run`); nessuna scrittura |
| `/sync !` | **Deploy + report** — esegue `deploy-all.sh` (skill/agents/comandi) poi report L1 (e L2 se indicati progetti) |
| `/sync <` | **Generalizza** — analizza skill L2 nei progetti; propone promozione a L1/L0 o taglio DUP; **nessuna scrittura** |
| `/sync` senza suffisso | Mostra sintassi e chiedi `?`, `!` o `<` |

Il suffisso (`?`, `!`, `<`) ha priorità su eventuale testo aggiuntivo.

Testo aggiuntivo: path progetti consumer, es. `/sync ! /path/to/project`, `/sync < /path/a /path/b`.

---

## Cosa fa

| Passo | `?` | `!` | `<` |
|-------|-----|-----|-----|
| `bash agents/deploy-all.sh` | no | sì | no |
| Symlink comandi L0 → `~/.cursor/commands/` | no (solo report) | sì (via `a-agentzero/deploy.sh`) | no |
| Report comandi L0 (`OK` / `MISSING` / `DRIFT`) | sì | sì | no |
| `agent-version.sh chain` su ogni L1 | sì | sì | opz. (contesto) |
| `pending` se STALE | sì | sì | no |
| Scan L2 + override comandi in `--projects` | se indicati | se indicati | **obbligatorio** (path o cwd) |
| Analisi promozione L2→L1/L0 | no | no | **sì** |

**Non** modifica automaticamente `extends-version` o CHANGELOG dei figli: il sync selettivo resta guidato (vedi sotto).  
**Non** applica da solo le promozioni di `/sync <`: solo report; conferma utente prima di edit L1/L0.  
**Non** copia comandi nei repo consumer: ereditarietà = user-level; override solo se `{repo}/.cursor/commands/{nome}.md` esiste.

---

## Comandi shell (canone)

Dalla macchina host (`?` / `!` — non usati da `<`):

```bash
# Report-only (tutti L1 + stato comandi L0)
bash /var/www/HAL/agents/a-agentzero/scripts/sync-agents.sh --dry-run

# Deploy L0+L1+comandi + report
bash /var/www/HAL/agents/a-agentzero/scripts/sync-agents.sh

# Include skill L2 e override comandi in uno o più progetti consumer
bash /var/www/HAL/agents/a-agentzero/scripts/sync-agents.sh \
  --projects /path/to/project-a /path/to/project-b

# Solo report + L2
bash /var/www/HAL/agents/a-agentzero/scripts/sync-agents.sh --dry-run \
  --projects /path/to/project
```

Equivalente diretto deploy:

```bash
bash /var/www/HAL/agents/deploy-all.sh
```

Singola catena / pending:

```bash
bash /var/www/HAL/agents/a-agentzero/scripts/agent-version.sh chain <SKILL.md>
bash /var/www/HAL/agents/a-agentzero/scripts/agent-version.sh pending <SKILL.md>
```

---

## Workflow agente

### `/sync ?`

```
Task Progress:
- [ ] 1. Esegui sync-agents.sh --dry-run [--projects …]
- [ ] 2. Elenca catene STALE (L1 e L2)
- [ ] 3. Per ogni STALE: mostra pending CHANGELOG (già nello script)
- [ ] 4. Verifica report comandi L0 (MISSING/DRIFT → consiglia /sync !)
- [ ] 5. Report: cosa aggiornare (extends-version / delta) senza modificare file
```

### `/sync !`

```
Task Progress:
- [ ] 1. Esegui sync-agents.sh [--projects …]  # include deploy-all + comandi L0
- [ ] 2. Conferma comandi L0 OK in ~/.cursor/commands/
- [ ] 3. Se nessuna STALE → conferma OK
- [ ] 4. Se STALE → proponi sync selettivo per ogni figlio:
        - [sync:safe]: aggiorna solo extends-version + bump patch figlio
        - [sync:safe] su soli comandi/deploy L0: idem, nessun delta body L1
        - [sync:review|breaking]: adatta delta L2/L1 prima di bump
- [ ] 5. Non bumpare extends-version senza leggere voci [sync:breaking]
- [ ] 6. Dopo modifiche: riesegui chain / sync-agents.sh --dry-run
```

**L2 meta-repo (HAL):** `sync-agents.sh` senza `--projects` riporta solo catene L1. Anche se «Nessuna STALE», verifica L2 in-repo:

```bash
bash a-agentzero/scripts/agent-version.sh chain .cursor/skills/harness-agentfactory/SKILL.md
# oppure: make version-chains
```

L2 consumer: `--projects /path/…` oppure `make sync-consumer-stale`.

Workflow dettagliato: [agent-versioning.md](../references/agent-versioning.md) § Sync selettivo.

### `/sync <`

Analisi **sola lettura**. Criteri: [references/l2-generalization.md](references/l2-generalization.md).

**Default meta-repo (HAL):** se non passi path e il cwd è HAL, inventario L2 in-repo (`.cursor/skills/`) **più** i consumer noti con skill sotto `/var/www/*/./.cursor/skills/` (discovery non vuota → non chiedere). Path espliciti dopo `/sync <` restano prioritari. Se 0 path, cwd non è consumer né HAL, e discovery vuota → chiedi.

```
Task Progress:
- [ ] 1. Risolvi progetti — path dopo `/sync <`, oppure workspace; se cwd = HAL → L2 AF + consumer noti `/var/www` (vedi sopra); altrimenti cwd consumer; altrimenti chiedi
- [ ] 2. Inventario L2 — ogni `.cursor/skills/*/SKILL.md` con extends: a-* (o legacy); annota role:
- [ ] 3. Carica padri — L1 (e competenze) + L0 per confronto; non duplicare lettura inutile
- [ ] 4. Classifica voci — DUP | L1 | L0 | L2 | NEED-N (vedi l2-generalization.md)
- [ ] 5. Cross-progetto — se ≥2 path, evidenzia pattern ripetuti (priorità promozione)
- [ ] 6. Emetti report nel formato sotto — zero scrittura su disco
- [ ] 7. Prossimo passo — chiedi conferma prima di edit L1/L0; non invocare /sync ! da solo
```

Filtro opzionale: `/sync < solo copywriter` o `/sync < /path — solo DUP` limita dominio o classe.

---

## Formato output

### `?` / `!`

```markdown
# /sync — Sincronizzazione agenti

## Deploy
[eseguito | saltato (--dry-run / ?)]

## Comandi L0
| Comando | Stato |
|---------|-------|
| version / document / review / improve / commit | OK / MISSING / DRIFT |

## Catene
| Agente | Version | Extends | Stato |
|--------|---------|---------|-------|
| … | … | … | OK / STALE |

## Azioni consigliate
- [ ] …
```

### `<`

```markdown
# /sync < — Generalizzazione L2 → L1 / L0

## Progetti analizzati
- `/path/a` — N skill L2
- `/path/b` — …

## Sintesi
[1–2 frasi: debito DUP vs candidati promozione]

## Candidati (per priorità)

### 1. [DUP|L0|L1|NEED-N|L2] — Titolo breve
- **Dove:** `repo/.cursor/skills/…/SKILL.md` § sezione
- **Cosa:** [enunciato operativo]
- **Perché:** [già in padre / ≥2 progetti / protocollo / …]
- **Target proposto:** `a-{dominio}/…` o `a-agentzero/…` o «taglia L2»
- **Evidenza:** [citazione corta o path parallelo in altro repo]

[Ripeti]

## Resta L2 (inventario breve)
- … (solo se utile; non dilungarsi)

## Escluso
- path/.env/brand corpus / one-off

## Prossimo passo
Conferma le voci da applicare (edit L1/L0 + snellimento L2), oppure riesegui con filtro.
Non eseguito: deploy, bump extends-version, scrittura file.
```

---

## Limiti

- Non sincronizza repo git remoti (`git pull` / push) — solo symlink Cursor + report versioni
- Skill L2 e override comandi (`?`/`!`) solo se passi path progetto (`--projects` o argomenti dopo `/sync`)
- `/sync <` richiede almeno un progetto risolvibile (argomenti, cwd consumer, **oppure** cwd HAL con discovery consumer)
- Credenziali e `.env` non toccati
- I nove comandi L0 non sovrascrivono override di progetto già presenti
- `/sync <` non promuove automaticamente: report only

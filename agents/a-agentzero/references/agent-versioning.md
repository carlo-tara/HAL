# Versionamento agenti e sync selettivo

Specifica operativa per versioni semver, CHANGELOG e allineamento padre↔figlio nella gerarchia L0 → L1 → L2.

**Protocollo formale:** [AGENT-PROTOCOL.md](../AGENT-PROTOCOL.md) § Versionamento.

---

## Campi frontmatter

| Campo | L0 | L1 | L2 |
|-------|----|----|-----|
| `version` | obbligatorio | obbligatorio | obbligatorio |
| `extends` | — | `a-agentzero` | `a-{dominio}` |
| `extends-version` | — | versione L0 integrata | versione L1 integrata |
| `model` / `model-fallback` | legacy, non usati dal formato skill condiviso | legacy, non usati dal formato skill condiviso | legacy, non usati dal formato skill condiviso |

Zed e Cursor caricano le skill dal formato Agent Skills (`name`, `description`, workflow e risorse). Le chiavi `model` importate dal vecchio frontmatter non selezionano il modello dell'agente. L'esecuzione usa il default System 2 di HAL, `SystemTwoEngine.ACTIVE_MODEL_NAME`; i subagent Cursor ereditano il modello padre (default `inherit`). Non assegnare un modello diverso a una skill o a un subagent.

**No L1→L1:** un L1 non dichiara `extends:` verso un altro L1 (la catena lo etichetterebbe L2). Per ingresso alias / retrocompatibilità usa **Facade L1** (stesso `extends: a-agentzero`, body thin che punta al canone peer — es. `a-b2b` → `a-product` § Profilo B2B).

Esempio L1:

```yaml
---
name: a-copywriter
extends: a-agentzero
version: 1.0.0
extends-version: 1.0.0
description: >-
  ...
---
```

Esempio L2:

```yaml
---
name: copywriter-esempio
extends: a-copywriter
version: 1.0.0
extends-version: 1.0.0
description: >-
  ...
---
```

### Regola indipendenza

- Ogni agente incrementa **solo la propria** `version` quando cambia il **proprio** artefatto.
- Modificare un figlio **non** incrementa la versione del padre.
- Modificare il padre **non** incrementa automaticamente i figli: restano alla loro `version`; `extends-version` segnala se sono indietro.

---

## Semver per livello

| Bump | Quando |
|------|--------|
| **patch** | Typo, chiarimenti, fix non comportamentali |
| **minor** | Nuove capability, checklist o reference retrocompatibili |
| **major** | Breaking change per i figli (workflow rimosso, override obbligatorio, cambio path canonico) |

Un bump **minor** nel padre di solito **non** richiede bump **major** nel figlio, salvo conflitti espliciti nel delta L2.

---

## CHANGELOG

- Un `CHANGELOG.md` per ogni agente (L0, L1, L2).
- Utility nested con `version` propria (es. `learn/`, `sync/`): `CHANGELOG.md` co-located nella cartella utility; il bump non richiede di per sé bump del padre L0.
- Formato [Keep a Changelog](https://keepachangelog.com/it/IT/1.1.0/) + [Semantic Versioning](https://semver.org/lang/it/).
- Template: [changelog-template.md](changelog-template.md).

### Tag sync nelle voci

Ogni voce destinata ai figli deve indicare l'impatto sul sync:

| Tag | Significato | Azione figlio |
|-----|-------------|---------------|
| `[sync:safe]` | Retrocompatibile; nessuna modifica al delta L2 richiesta | Opzionale: aggiorna solo `extends-version` |
| `[sync:review]` | Potrebbe richiedere adattamento del delta L2 | Leggi e valuta applicabilità |
| `[sync:breaking]` | Richiede modifica esplicita del figlio | Adatta delta L2 prima di aggiornare `extends-version` |

**Infrastruttura L0 (comandi Cursor, deploy, script sync):** voci `[sync:safe]` su `commands/`, symlink `~/.cursor/commands/`, o report in `sync-agents.sh` **non** richiedono modifica al body delle skill L1 — basta allineare `extends-version` (+ bump patch figlio + CHANGELOG). I comandi ereditabili arrivano già via `/sync !` / `deploy.sh`.

Esempio voce padre:

```markdown
## [1.1.0] - 2026-07-15

### Added
- Checklist meta GEO in pre-consegna [sync:safe]

### Changed
- Rinominato path export SEO da `seo-data/` a `seo/` [sync:breaking]
```

---

## Sync selettivo (workflow)

Usare quando `extends-version` del figlio < `version` del padre diretto.

```
Task Progress:
- [ ] 1. Report — esegui `scripts/agent-version.sh pending <SKILL.md>`
- [ ] 2. Leggi — CHANGELOG padre dalle voci > extends-version
- [ ] 3. Classifica — ogni voce: applica / ignora / adatta delta L2
- [ ] 4. Applica — modifica solo il delta L2 (path, override, regole locali)
- [ ] 5. Allinea — imposta extends-version = version corrente del padre
- [ ] 6. Bump — incrementa version del figlio + voce CHANGELOG figlio
```

### L1 ← L0 (es. a-copywriter ← a-agentzero)

1. Leggi `a-agentzero/CHANGELOG.md` dalle voci > `extends-version` in `a-copywriter/SKILL.md`.
2. Integra nel L1 solo ciò che riguarda protocollo/workflow dominio (es. nuova checklist comune → aggiungi in checklist L1 se non già coperta).
3. **Competenze:** se le voci pending sono moduli `kind: competency` non pertinenti al dominio del figlio, **non** adottarli: allinea solo `extends-version` (adozione opt-in; vedi AGENT-PROTOCOL § Competenze). Se il L1 le adotta, copia/estendi sotto `competencies/{id}/` e bump minor.
4. **Comandi / deploy L0:** se le voci pending riguardano solo `commands/` o tooling sync/deploy (`[sync:safe]`), non toccare il body L1 — solo `extends-version` + patch.
5. Aggiorna `extends-version` in `a-copywriter/SKILL.md` alla `version` attuale di L0.
6. Bump `version` L1 (patch se solo allineamento; minor se adotti capability L0).

### L2 ← L1 (es. copywriter-progetto ← a-copywriter)

1. Leggi `a-copywriter/CHANGELOG.md` dalle voci > `extends-version` del figlio.
2. **Non** copiare intere sezioni L1 nel figlio — eredità via `extends:`.
3. Applica solo voci `[sync:breaking]` o `[sync:review]` che impattano path/override locali.
4. Voci `[sync:safe]`: aggiorna `extends-version` senza modificare il body se il delta resta valido.
5. Bump `version` L2 + voce CHANGELOG (es. «Allineato a a-copywriter 1.2.0: aggiornato path export»).
6. **Companion** — se esiste `.cursor/agents/{nome}.md` per questa skill: allinea `extends-version`, path `competencies/`, riferimenti allo SKILL L2 (vedi § Companion).

---

## Companion (`.cursor/agents/`)

Dopo ogni sync o bump rilevante di una skill L2 (o L1 deployata come subagent di progetto):

| Check | Azione |
|-------|--------|
| Companion assente ma subagent usato | Crea da template agente L1 / progetto |
| `extends-version` divergete dalla skill | Allinea al valore skill |
| Path competenze / SKILL rinominati | Aggiorna link nel companion |
| Solo `[sync:safe]` senza path change | Bump `extends-version` nel companion se dichiarato |

Non lasciare companion con istruzioni legacy dopo un rename di competenze L1.

---

## Verifica all'avvio

Ogni agente, dopo aver caricato la catena `extends:`:

1. Confronta `extends-version` con `version` del padre diretto.
2. Se **stale** (figlio indietro): segnala all'utente sync disponibile; non bloccare il task salvo `[sync:breaking]` noto.
3. Comando rapido: `bash agents/a-agentzero/scripts/agent-version.sh chain .cursor/skills/{dominio}-{progetto}/SKILL.md`

---

## Anti-pattern

- Copiare intere sezioni del padre nel figlio invece di usare `extends:`
- Incrementare la versione del padre quando cambia solo un figlio
- Omettere `extends-version` in L1/L2
- Omettere tag `[sync:*]` su voci CHANGELOG che impattano i figli
- Bumpare `extends-version` senza leggere le voci `[sync:breaking]`

---

## Competenze modulari (versionamento)

Le competenze (`kind: competency`) hanno semver **indipendente** dall'agente host e dalla stessa competenza agli altri livelli.

| Livello | Path | `extends-version` punta a |
|---------|------|---------------------------|
| L0 | `a-agentzero/competencies/{id}/` | — (opzionale: non tutte le competenze hanno L0) |
| L1 | `a-{dominio}/competencies/{id}/` | `version` L0 stessa id **se esiste**; altrimenti omettere |
| L2 | `{repo}/.cursor/skills/{figlio}/competencies/{id}/` | `version` L1 stessa id |

Regole:

- Bump della competenza quando cambia il **proprio** SKILL/references/CHANGELOG
- Sync: leggi CHANGELOG del livello inferiore > `extends-version`, applica delta, allinea `extends-version`
- Tag `[sync:*]` anche sulle voci CHANGELOG delle competenze se impattano i livelli superiori
- Check: `bash a-agentzero/scripts/agent-version.sh competency-chain <path-SKILL-competenza>`
- Baseline L0 di una competenza **non** obbliga ogni L1 ad adottarla (opt-in per dominio)
- **Non** spostare `scripts/` o JSON runtime sotto `competencies/` solo per simmetria documentale
- **Non** confondere file dati progetto (brand, illustration-styles, brief) con moduli competenza

Check manuale (senza script): confronta frontmatter `version` / `extends-version` di L0, L1 e L2 per la stessa `name` (id).

---

## Script di supporto

[`scripts/agent-version.sh`](../scripts/agent-version.sh):

| Comando | Descrizione |
|---------|-------------|
| `show <path>` | Mostra `version` e `extends-version` di un agente o competenza |
| `chain <SKILL.md>` | Catena agente L2→L1→L0 con flag STALE |
| `competency-chain <SKILL.md>` | Catena stessa competenza L0/L1/L2 con flag STALE |
| `pending <SKILL.md>` | Voci CHANGELOG padre non ancora integrate |

Il sync resta guidato dall'agente; lo script fornisce report oggettivo.

**Sync globale (deploy + tutte le catene L1):** skill [`sync/SKILL.md`](../sync/SKILL.md) e script [`sync-agents.sh`](../scripts/sync-agents.sh) (`/sync ?` / `/sync !`).  
**Generalizzazione L2→L1/L0 (solo report):** `/sync <` — [`l2-generalization.md`](../sync/references/l2-generalization.md).

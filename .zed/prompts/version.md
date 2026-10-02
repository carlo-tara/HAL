# /version <tipo> — Incremento versione file e documenti modificati (L0)

## Obiettivo

Il comando `/version` (es. `/version patch`, `/version minor`, `/version major`) individua tutti i file e documenti modificati rispetto alla versione precedente (o tracciati in Git / changelog) e ne incrementa la versione in modo coordinato, mantenendo allineati frontmatter, manifest e changelog secondo lo standard HAL.

---

## Modi d'uso

```bash
/version patch          # Incremento patch (fix, chiarimenti, micro-modifiche)
/version minor          # Incremento minor (nuove sezioni, capability)
/version major          # Incremento major (breaking changes strutturali)
/version                # Mostra lo stato delle versioni dei file modificati
```

---

## Processo operativo

1. **Rilevamento file modificati:**
   Esegue un controllo sui file modificati nel working tree (tramite `git status` o confrontando con l'ultimo tag/commit stabile), focalizzandosi su:
   - Skill e manifest di agenti (`SKILL.md` con campo `version: X.Y.Z`).
   - Documentazione e registri (`CHANGELOG.md`, `ToDo.md`, file sotto `docs/` o `.cursor/product/`).
   - Configurazione di progetto o manifesti (`catalog.json`, `package.json`, ecc.).

2. **Calcolo del bump:**
   - **Patch (`x.y.Z+1`):** correzioni, aggiornamenti testuali, fix minori, allineamenti documentali.
   - **Minor (`x.Y+1.0`):** aggiunta di nuove sezioni operative, nuove competenze o comandi senza rompere i contratti esistenti.
   - **Major (`X+1.0.0`):** modifiche strutturali ai protocolli, ai contratti di interazione o ai bounded context.

3. **Applicazione:**
   - Aggiorna il campo `version:` nel frontmatter YAML dei file `SKILL.md` toccati.
   - Aggiunge una voce sotto `## [Unreleased]` o nella sezione attiva del `CHANGELOG.md` del file o del modulo.
   - Preserva la gerarchia e non tocca file non modificati o non tracciati.

4. **Verifica post-bump:**
   - Per gli agenti HAL, verifica la catena di versione e lo stato con gli script di supporto:
     ```bash
     bash agents/a-agentzero/scripts/agent-version.sh chain <SKILL.md>
     ```
   - Esegue la sincronizzazione o il report finale.

---

## Regole di coerenza

- **Delta only:** non modificare la versione di file che non hanno subito modifiche effettive nella sessione o nel diff corrente.
- **Isolamento L0/L1/L2:** non incrementare la versione di `a-agentzero` (L0) per modifiche locali confinate in skill L2 o documentazione di progetto consumer.
- **Tracciabilità:** ogni bump deve essere accompagnato da una riga nel changelog pertinente (es. `CHANGELOG.md` del modulo o registro di sessione).

---

## Riferimenti

- [agent-versioning.md](../../references/agent-versioning.md) — Semver e CHANGELOG HAL.
- [sync/SKILL.md](../../../sync/SKILL.md) — Sincronizzazione e deploy dei comandi L0.

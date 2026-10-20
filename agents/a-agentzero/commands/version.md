---
model: orcarouter/deepseek/deepseek-v4-flash-free
version: 1.3.0
---

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
   - Documentazione e registri (`CHANGELOG.md`, `ToDo.md`, file sotto `docs/` o `product/state/`).
   - Configurazione di progetto o manifesti (`catalog.json`, `package.json`, ecc.).

2. **Calcolo del bump (System 1):**
   Se il livello (patch/minor/major) non è fornito, usa la CLI System 1 per deciderlo senza token generativi:
   `python3 router.py choice "In base a queste modifiche [sintesi], quale bump applicare?" --options patch minor major`
   - **Patch:** correzioni, aggiornamenti testuali, fix minori.
   - **Minor:** aggiunte senza rompere contratti.
   - **Major:** modifiche strutturali o breaking changes.

3. **Applicazione (Deterministica):**
   Usa lo script CLI senza modificare a mano frontmatter e changelog:
   `bash agents/a-agentzero/scripts/agent-version.sh bump <patch|minor|major> <file>`
   Questo calcola e applica l'incremento preservando la gerarchia YAML e appendendo al CHANGELOG.

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

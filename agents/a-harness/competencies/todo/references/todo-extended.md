
Esegui in ordine; riscrivi i file solo a fine pass (scritture coerenti). Passo 1–8 = **pipeline deterministica** (ordine fisso).

1. **Inventario** — leggi `./ToDo.md` (se assente: crea scheletro minimo sotto); elenca Attività aperte vs completate
2. **Lean brief** — `harness-prompt-builder.sh render` (≤200 token; titoli P0/P1)
3. **Prune** — riconosci ed elimina (o sposta in «Già fatto» se utile anti-rework) le Attività completate / stale già in HEAD / obsolete
4. **Chiarisci** — Attività vaghe → riscrivi; UL/BC **solo se serve**; aggiungi **perché è utile** (outcome / friction / gate)
5. **Risolvi** — ambiguità, duplicazioni, conflitti (merge, split, o kill con nota breve)
6. **Tag** — assegna ≥1 tag ordinabile
7. **Priorità** — ordina le aperte P0 → P1 → P2 (e track paralleli se multi-agente)
8. **Flush CHANGELOG** — per ogni voce in **«Già fatto»** non ancora registrata: append in `./CHANGELOG.md` (vedi sotto); poi rimuovi le voci flushate da «Già fatto» (sezione vuota o assente OK)
9. **Scrivi** — format conforme su `./ToDo.md` (+ `./CHANGELOG.md` se flush) + `handoff-todo.json`; niente segreti

## Formato Attività

```markdown
- [ ] Titolo chiaro `#tag` · P0|P1|P2 · BC opz.
  - Perché utile: …
  - Acceptance: …
```

| Campo | Regola |
|-------|--------|
| Titolo | Un outcome verificabile; termini da `docs/glossary.md` |
| Tag | Almeno uno (vedi sotto) |
| Priorità | P0 sblocca gate/HEAD; P1 wave/slice candidato; P2 housekeeping |
| Perché utile | Friction, gate, evidence in progress, o valore business — non “nice to have” vuoto |
| Acceptance | Criterio falsificabile; se manca → chiarisci prima di promuovere a `/slice` |

## Tag (ordinabili)

| Tag | Uso |
|-----|-----|
| `feature` | Capacità nuova |
| `bug` | Difetto riproducibile |
| `techdebt` | Debito / potatura / freeze |
| `uiux` | Layout, a11y, shell UI |
| `docs` | Manuali, glossario, BC map |
| `infra` | Makefile, CI, hooks, sync |
| `spike` | Esplorazione time-boxed |

Altri tag solo se già nel glossario o dichiarati in L2; non inventare sinonimi per lo stesso concetto.

## Flush «Già fatto» → `./CHANGELOG.md`

Target **unico** per Attività della Mappa residui: **`./CHANGELOG.md`** (root del repo attivo).

| Caso | Azione |
|------|--------|
| File assente | Crea scheletro Keep a Changelog (titolo + `## [Unreleased]` + sezioni vuote tipiche) |
| File presente | Append sotto `## [Unreleased]` nella sottosezione corretta |
| Solo fabbrica AF (Makefile/hooks/rules) e L2 punta a `docs/harness-CHANGELOG.md` | Opzionale: stesso stile lì **invece** del root, se il progetto lo documenta — default resta `./CHANGELOG.md` |

**Non** scrivere Attività ToDo nei `CHANGELOG.md` degli agenti (`a-*/`, L2 skill): quelli restano ownership di `/version` + bump skill.

### Mapping tag → sezione Keep a Changelog

| Tag Attività | Sezione |
|--------------|---------|
| `feature` | `### Added` |
| `bug` | `### Fixed` |
| `docs` / `infra` / `techdebt` / `uiux` / `spike` | `### Changed` |
| rimozione esplicita / deprecazione | `### Removed` o `### Deprecated` (solo se chiaro dal titolo) |

Se più tag: priorità `bug` > `feature` > altri → una sola sezione.

### Stile bullet (consono)

- Una riga: outcome al passato prossimo / fatto compiuto, italiano chiaro (allineato al CHANGELOG del repo)
- Niente `- [x]`, niente `P0|P1|P2`, niente «Perché utile» / Acceptance
- Conserva hash commit / versione già nel titolo se presenti (es. `` `7a74469` ``, `a-product 1.2.0`)
- Prefisso tag opzionale solo se aiuta la scansione: `` `#feature` `` non obbligatorio
- **Dedup:** non aggiungere se in `## [Unreleased]` (o ultima release) esiste già una riga con stesso commit hash o titolo sostanzialmente uguale
- Dopo append riuscito: **elimina** la voce da «Già fatto» (anti doppio flush)

Esempio trasformazione:

```markdown
# Da ToDo «Già fatto»
- [x] Escaping the Build Trap → a-product Fasi 1–4 … `a-product` 1.2.0 / `7a74469` `#feature`

# A CHANGELOG.md
## [Unreleased]

### Added
- Escaping the Build Trap → a-product (anti–Build Trap, Product Kata light) — `a-product` 1.2.0 (`7a74469`)
```

## Delega semantic layer

| Gap | Competenza | Azione |
|-----|------------|--------|
| Nome / sinonimo dubbio | `ubiquitous-language` | Leggi/aggiorna glossario **prima** di rinominare Attività |
| Confini / owner path | `bounded-context` | Dichiara BC; no silo; Fit-to-whole sulla mappa |

## Sezioni file

| Sezione | Ruolo |
|---------|--------|
| P0 | Sblocca gate / HEAD |
| P1 | Candidati `/slice` con acceptance |
| P2 | Housekeeping |
| Track paralleli | Altri agenti/BC — non Act sul track sbagliato |
| Già fatto | Buffer breve pre-flush CHANGELOG; dopo flush vuoto o assente |

## Anti-pattern

- Trattare `./ToDo.md` come Progress o come Slice accettato
- Attività senza tag, priorità o “perché utile”
- Sinonimi fuori glossario; mix IT/EN per la stessa entità
- Duplicati lasciati “per dopo”; conflitti non risolti
- Hook/freeze o Act automatico sulle Attività senza `/slice`
- Dump grezzo checkbox ToDo nel CHANGELOG; bump version inventati; scrivere nei CHANGELOG agenti da `/todo`
- Lasciare «Già fatto» pieno dopo flush riuscito (doppia fonte di verità)
- Dump `ToDo.md` intero nel prompt modello invece di summary ≤200 token + `handoff-todo.json`

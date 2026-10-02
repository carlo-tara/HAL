# Changelog — a-agentzero

## [Unreleased]

## [1.8.0] - 2026-10-02

### Added
- Ottimizzazioni avanzate di System 1 (Laya): caching in-memory `@lru_cache` (maxsize=128) e HTTP session pooling persistente (`requests.Session`) in `laya_service.py` [sync:safe]

## [1.7.1] - 2026-10-02

### Added
- Layer cognitivo System 1 (Laya) in `a-agentzero`: definizione formale del protocollo di routing globale (`router.py routing` / `triage`), pre-filtro (`noul`) e scoring euristico (`score`) obbligatori prima di invocare il ragionamento System 2 [sync:safe]

## [1.7.0] - 2026-10-02

### Added
- Zed editor integration: workspace settings (`.zed/settings.json`), automatic prompt mapping (`.zed/prompts/`), and command-to-skill packaging in `.agents/skills/` for seamless multi-editor support (Cursor ⇄ Zed) [sync:safe]
- Automatic frontmatter stripping for Zed prompts and skills via `agents/scripts/link-workspace-skills.sh` [sync:safe]

## [1.6.15] - 2026-09-18

### Changed
- L0 `/graph` `/slice` `/cycle` `/todo`: lean brief via `harness-prompt-builder` + `handoff-*.json` [sync:safe]

### Added
- Appreso da sessione: selezione modelli OrcaRouter (costo a parità; no image-gen come LLM) in agent-versioning [sync:safe]
- Comandi L0: frontmatter `model` + `model-fallback: cursor-default` (OrcaRouter; fallback Cursor default) [sync:safe]
- Comando L0 `/todo` (Mappa residui → competenza a-harness `todo`; modello `deepseek-v4-flash-free`) [sync:safe]
- Comandi L0 `/slice`, `/cycle`, `/graph` (→ a-harness; modello `deepseek-v4-flash`) [sync:safe]

## [1.6.14] - 2026-09-17

### Added
- Frontmatter `model: orcarouter/deepseek/deepseek-v4-flash-free` + `model-fallback: cursor-default` (OrcaRouter preferred; Cursor default se non raggiungibile) [sync:safe]

## [1.6.13] - 2026-09-15

### Changed
- Appreso da sessione: `/learn !` può scrivere `./ToDo.md` e docs locali (se necessario) — sintesi § Apprendimento [sync:safe]

## [1.6.12] - 2026-09-15

### Changed
- Deleghe: `a-b2b` = facade B2B; canone orchestra in `a-product` § Profilo B2B [sync:review]

## [1.6.11] - 2026-09-15

### Added
- Registry L1 `a-product` (orchestratore peer multi-step); Deleghe + agents + PROTOCOL [sync:safe]

## [1.6.10] - 2026-09-15

### Changed
- Appreso da sessione: Reason why in description + regole di ingaggio subagent [sync:safe]


## [1.6.9] - 2026-09-15

### Added
- Appreso da sessione: Comunicazione all'utente — scelte e ragionamenti in italiano chiaro, gergo tecnico minimo (prose verso l'umano) [sync:safe]

## [1.6.8] - 2026-09-15

### Added
- Appreso da sessione: mappa residui permanente → `./ToDo.md` in root repo (≠ progress append-only) [sync:safe]

## [1.6.7] - 2026-09-15

### Changed
- Appreso da sessione: manutenzione registry → allineare § Deleghe + `agents/a-agentzero.md` nello stesso slice; no PageSpeed su L1 seozoom [sync:safe]

## [1.6.6] - 2026-09-15

### Changed
- Deleghe L1 complete (13) + CWV/PageSpeed solo L2; companion `agents/a-agentzero.md` tabella/scaffold/perimetro allineati [sync:safe]
- Description L0: reason-why esplicita (protocollo/sync/sicurezza condivisi) [sync:safe]

## [1.6.5] - 2026-09-15

### Changed
- Appreso/ottimizza: registry L1 completo + legacy po/harness/uiux/enrichment [sync:safe]

## [1.6.4] - 2026-09-08

### Changed
- Scaffold § Git: commit staged-only quando UI elenca file ma index vuoto (lista autoritativa + `-f` se gitignored) [sync:safe]

## [1.6.3] - 2026-08-17

### Changed
- Scaffold: sezione Git per tracciare skill L2 (`git add -f`) quando `.cursor/` è in `.gitignore` [sync:safe]

## [1.6.2] - 2026-08-15

### Changed
- Appreso da sessione: `l1-from-proto` — CC BY-NC-SA / non-commercial = distillazione + attribution only, no redistribuzione pack [sync:safe]

## [1.6.1] - 2026-08-15

### Added
- Registry L1 `a-po`, `a-enrichment`: discovery file dati + elenco L1 [sync:safe]

## [1.6.0] - 2026-08-13

### Changed
- Registry L1 `a-b2b`: deploy-all, sync-agents, discovery, naming L2 `b2b-*` [sync:safe]

## [1.5.8] - 2026-08-13

### Changed
- `humanizer` L0 1.1.0: principio Never inject (togliere/affilare, non aggiungere voice/fatti) [sync:review]

## [1.5.7] - 2026-08-13

### Changed
- Appreso da sessione: `l1-from-proto` — multi-corpus, no-SPDX, override conflitti, no runtime-upstream; `docs/operativo` Ship L1 (anche bump) con tree sporco [sync:safe]

## [1.5.6] - 2026-08-07

### Added
- L1 `a-charts`: registry deploy/sync, discovery `.cursor/chart-styles/`, deleghe, naming L2 `charts-*` [sync:safe]

## [1.5.5] - 2026-08-03

### Changed
- `tono-di-voce` L0 1.0.2: voice-as-brand (brand file opzionale se skill voice è unica fonte) [sync:review]

## [1.5.4] - 2026-08-03

### Added
- `/sync <`: analisi L2 per generalizzazione L1/L0 (report only); reference `sync/references/l2-generalization.md`; sync skill 1.1.0 [sync:safe]

## [1.5.3] - 2026-08-03

### Added
- Multi-figlio L2: `role:` / `primary:`, risoluzione task→ruolo (AGENT-PROTOCOL) [sync:review]
- Agent companion sync dopo L2←L1 (extension-scaffold, agent-versioning) [sync:review]
- Template deleghe sibling + conflitto voice vs SEO (extension-template) [sync:safe]
- `/learn`: anti-grasso L2, promozione ≥2 progetti, brand vs voice skill [sync:review]
- L0 `tono-di-voce` 1.0.1: brand file vs skill voice [sync:review]

## [1.5.2] - 2026-07-28

### Changed
- Appreso da sessione: `l1-from-proto` esteso a corpus skill esterni (vendor gitignored + pin + update; adozione opt-in; no dump) [sync:safe]

## [1.5.1] - 2026-07-27

### Changed
- Appreso da sessione: `[sync:safe]` su comandi/deploy L0 → L1 allinea solo `extends-version` (nessun delta body) in `agent-versioning.md` + `sync/SKILL.md` [sync:safe]

## [1.5.0] - 2026-07-27

### Added
- Comandi Cursor L0 ereditabili in `commands/` (`version`, `document`, `review`, `improve`, `commit`) pubblicati in `~/.cursor/commands/` via deploy/`/sync !` [sync:safe]
- Report stato comandi L0 (`OK`/`MISSING`/`DRIFT`) e override vs inherit in `scripts/sync-agents.sh` [sync:safe]

## [1.4.1] - 2026-07-27

### Added
- Appreso da sessione: regola authorship L1 da proto-prompt (critica/estensione, non copia) in `references/l1-from-proto.md` [sync:safe]

## [1.4.0] - 2026-07-27

### Added
- Competenza L0 `po-interviewer` (engagement PO, anti-invention, cascade triage discovery) [sync:review]
- Discovery file dati per L1 `a-personas`, `a-jtbd`, `a-gherkin` (path product portabili) [sync:review]
- Target `/learn` per pipeline discovery in `consolidation-targets.md` [sync:safe]

## [1.3.1] - 2026-07-27

### Changed
- Appreso da sessione: file dati ≠ competenze; esempi L1-only SEO + illustrazioni; lista competenze a-illustrator in adozione opt-in [sync:safe]

## [1.3.0] - 2026-07-27

### Added
- Release minor protocollo competenze: L0 opzionale, asset operativi fuori da competencies, riuso cross-dominio on-demand, adozione opt-in (regole già in 1.2.1–1.2.2) [sync:safe]

## [1.2.2] - 2026-07-27

### Changed
- Appreso da sessione: baseline L0 competenze opzionale; asset operativi fuori da competencies; riuso cross-dominio on-demand [sync:safe]

## [1.2.1] - 2026-07-27

### Changed
- Appreso da sessione: adozione competenze opt-in per dominio; sync L1←L0 senza copiare moduli non pertinenti [sync:safe]

## [1.2.0] - 2026-07-27

### Added
- Competenze modulari path-based L0→L1→L2 (`kind: competency`): protocollo, risoluzione runtime, versionamento indipendente per id [sync:review]
- Baseline L0: `competencies/tono-di-voce`, `competencies/humanizer`, `competencies/italiano-locale` [sync:review]
- Script `agent-version.sh competency-chain` per confrontare versioni stessa competenza [sync:safe]
- Note in `agent-versioning.md` e `extension-scaffold.md` su override competenze L2 [sync:review]

## [1.1.2] - 2026-07-16

### Added
- Skill L0 [sync/SKILL.md](sync/SKILL.md): `/sync ?` (report) e `/sync !` (deploy-all + report versioni) [sync:safe]
- Script [scripts/sync-agents.sh](scripts/sync-agents.sh) e comando Cursor `.cursor/commands/sync.md` [sync:safe]
- Deploy: symlink top-level `~/.cursor/skills/sync` (come `learn`) [sync:safe]

## [1.1.1] - 2026-07-13

### Changed
- `learn/references/consolidation-targets.md`: target generici AgentFactory + pattern consumer, rimossi riferimenti a progetti specifici [sync:safe]

## [1.1.0] - 2026-07-13

### Added
- Skill L0 [learn/SKILL.md](learn/SKILL.md): `/learn ?` (riflessione sessione) e `/learn !` (consolidamento in skill) [sync:safe]
- Reference [learn/references/consolidation-targets.md](learn/references/consolidation-targets.md) [sync:safe]
- Sezione Apprendimento da sessione in SKILL.md e AGENT-PROTOCOL.md [sync:safe]

## [1.0.0] - 2026-07-13

### Added
- Versionamento semver e protocollo sync selettivo [sync:safe]
- Campo `version` nel frontmatter L0
- Reference [agent-versioning.md](references/agent-versioning.md) e script `scripts/agent-version.sh` [sync:safe]
- Sezione Versionamento in [AGENT-PROTOCOL.md](AGENT-PROTOCOL.md) [sync:safe]

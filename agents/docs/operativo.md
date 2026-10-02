# HAL — guida operativa

Documentazione di lavoro per sviluppo, deploy e versionamento degli agenti L0/L1. Per la specifica formale vedi [`a-agentzero/AGENT-PROTOCOL.md`](../a-agentzero/AGENT-PROTOCOL.md).

**RGR:** ogni update ad agenti/skill segue Red→Green→Refactor — [`AGENTS.md`](../AGENTS.md). Gate: `make ready-for-review` (Platform API in `Makefile`; mapping in [`project-skills/harness-agentfactory/SKILL.md`](../project-skills/harness-agentfactory/SKILL.md)).

---

## Platform API (Make)

Lista L1 unica in `Makefile` / `a-agentzero/scripts/sync-agents.sh` — non duplicare `for d in a-…` in docs/comandi.

| Target | Uso |
|--------|-----|
| `make pre-commit` | `bash -n` + `frontmatter-all` + shellcheck + md-links |
| `make test-unit` | `version-chains` + `sync-agents.sh --dry-run` |
| `make ready-for-review` | standards + test + `ready-proof` |
| `make install-git-hooks` | hook locale → `make pre-commit` |
| `make sync-consumer-stale` | report STALE L2 consumer (lista in script) |

Changelog fabbrica: [`harness-CHANGELOG.md`](harness-CHANGELOG.md). Playbook DUP L2: [`playbook-l2-dup-cut.md`](playbook-l2-dup-cut.md).

---

## Deploy

### Deploy completo

```bash
cd /var/www/HAL/agents
bash deploy-all.sh
# equivalente con report versioni:
bash a-agentzero/scripts/sync-agents.sh
```

Effetto:

| Origine | Destinazione |
|---------|--------------|
| `a-agentzero/` | `~/.agents/skills/a-agentzero` + `~/.cursor/agents/a-agentzero.md` |
| `a-agentzero/learn/` | `~/.agents/skills/learn` |
| `a-agentzero/sync/` | `~/.agents/skills/sync` |
| `a-{dominio}/` | `~/.agents/skills/a-{dominio}` + `~/.cursor/agents/a-{dominio}.md` |

Ogni `a-*/deploy.sh` crea symlink (`ln -sfn`); non copia file.

### Quando ridistribuire

Dopo ogni modifica a `SKILL.md`, `CHANGELOG.md`, reference o script referenziati dalle skill L0/L1:

```bash
bash deploy-all.sh
# oppure:
bash a-agentzero/scripts/sync-agents.sh
```

In chat: `/sync !` (deploy + report) · `/sync ?` (solo report).

### Ship L1 con working tree sporco

Appreso da sessione (a-charts; riaffermato su a-seozoom 1.5.0): se HAL ha WIP misto (altri L1, registry L0, sync, README bulk) **non** mescolare tutto in un unico commit — vale per **nuovo L1** e per **bump/distillazione** di un L1 esistente.

1. **Commit 1 — agente:** solo `a-{dominio}/` (SKILL, competenze, `deploy.sh`, companion, template, CHANGELOG) + asset strettamente legati (es. `vendor/README.md`, `.cursor/commands/update-*-repo.md`, righe `vendor/` in `.gitignore`). Deploy locale: `bash a-{dominio}/deploy.sh` (Cursor + Claude).
2. **Commit 2 — registry:** quando il tree è pulito o in un PR dedicato — `deploy-all.sh`, `a-agentzero/scripts/sync-agents.sh`, discovery/deleghe in `a-agentzero/SKILL.md` + `AGENT-PROTOCOL.md`, riga in `README.md` / questa guida.
3. Non stageare file L0/L1 non correlati solo perché «toccati nello stesso working tree».
4. Non includere un `README.md` “bulk” se il diff mescola altri agenti: aggiorna la riga versioni nel commit registry, oppure un commit README dedicato.

Finché manca il commit registry, l’agente resta usabile via `deploy.sh` diretto; `deploy-all.sh` remoto lo includerà al passo 2.

---

## Versionamento

Ogni agente ha semver **indipendente** e un `CHANGELOG.md` nella propria directory.

### Comandi

```bash
# Report tutte le catene L1←L0 (no deploy)
bash a-agentzero/scripts/sync-agents.sh --dry-run

# Con skill L2 di progetti consumer
bash a-agentzero/scripts/sync-agents.sh --dry-run --projects /path/to/project

# Catena singola (flag STALE se extends-version indietro)
bash a-agentzero/scripts/agent-version.sh chain a-copywriter/SKILL.md

# Catena competenza (stessa id L0/L1/L2)
bash a-agentzero/scripts/agent-version.sh competency-chain a-copywriter/competencies/humanizer/SKILL.md

# Delta CHANGELOG padre non integrato
bash a-agentzero/scripts/agent-version.sh pending a-copywriter/SKILL.md

# Versione singola
bash a-agentzero/scripts/agent-version.sh show a-seozoom/
```

### Competenze modulari

Oltre a `extends:` (un solo padre), gli agenti possono dichiarare moduli in `competencies/{id}/` risolti **L0 → L1 → L2** se esistono. Specifica: [`AGENT-PROTOCOL.md`](../a-agentzero/AGENT-PROTOCOL.md) § Competenze modulari.

| Regola | Dettaglio |
|--------|-----------|
| Baseline L0 | **Opzionale** — copy ha L0 (`tono-di-voce`, `humanizer`, `italiano-locale`); discovery ha L0 `po-interviewer`; SEO e illustrazioni sono **solo L1** |
| Asset operativi | `scripts/` e JSON/runtime restano sotto l'agente (es. `a-seozoom/references/export-manifest.json`), non obbligatoriamente in `competencies/` |
| File dati | `.cursor/brands/`, `.cursor/illustration-styles/`, brief SEO, `.cursor/product/` (discovery), … restano **dati progetto**, non moduli competenza |
| Adozione | Opt-in per dominio; al sync L1←L0 non copiare moduli non pertinenti |
| Cross-dominio | Carico on-demand (es. SEO → `tono-di-voce` in scrittura title/meta); altrimenti delega all'agente L1 |

| Dominio | Id competenze L1 | Baseline L0 |
|---------|------------------|-------------|
| a-copywriter | `tono-di-voce`, `humanizer`, `italiano-locale` | sì |
| a-seozoom | `seo-import`, `metriche-analisi`, `onpage-seo`, `geo-citabilita`, `seo-audit`, `schema-markup`, `programmatic-seo`, `site-architecture`, `hreflang-i18n`, `topic-cluster` | no |
| a-illustrator | `stile-visivo`, `prompt-composizione`, `preview-render`, `qa-artefatti` | no |
| a-wordpress | — (non ancora modularizzato) | — |
| a-personas | `po-interviewer` | sì (L0) |
| a-jtbd | `po-interviewer`, `switch-interview` | sì (`po-interviewer`); `switch-interview` L1-only |
| a-gherkin | `po-interviewer`, `bdd-security-performance` | sì (`po-interviewer`); `bdd-*` L1-only |
| a-charts | `scelta-tipo`, `leggibilita`, `implementazione`, `qa-grafici` | no |
| a-b2b | — (facade → a-product § Profilo B2B; deleghe a-po / a-enrichment / discovery / copy) | — |
| a-product | — (orchestra multi-step + § Profilo B2B; thin; no authoring PRD) | — |
| a-po | `po-interviewer`, `triage-request`, `problem-framing`, `lean-canvas`, `prd-authoring`, `positioning-offer`, `evidence-probe`, `slice-prioritization`, `growth-loops`, `market-public-data` | sì (`po-interviewer`); resto L1-only |
| a-enrichment | — (pattern + references; handoff a-copywriter) | — |
| a-harness | TDD/DDD/Steward competencies (vedi `a-harness/competencies/`) | no |
| a-uiux | `static-stack`, `accessibility`, `editorial-layout` | no |

Override L2: `{progetto}/.cursor/skills/{figlio}/competencies/{id}/SKILL.md` (solo delta). Check: `agent-version.sh competency-chain <path>`.

### Workflow release L1 (sync da L0)

1. `pending` sul figlio → leggi voci con tag `[sync:safe|review|breaking]`
2. Applica solo il delta necessario in `SKILL.md` / reference
3. Aggiorna `extends-version` alla versione L0 integrata
4. Bump `version` del figlio (di solito patch; minor se adotti capability)
5. Voce in `CHANGELOG.md` del figlio
6. `deploy-all.sh` o `sync-agents.sh`

Specifica: [`a-agentzero/references/agent-versioning.md`](../a-agentzero/references/agent-versioning.md)  
Skill sync: [`a-agentzero/sync/SKILL.md`](../a-agentzero/sync/SKILL.md)  
Template changelog: [`a-agentzero/references/changelog-template.md`](../a-agentzero/references/changelog-template.md)

### Versioni attuali

**Non mantenere tabelle snapshot qui** (shadow-doc). Fonte live:

```bash
make version-chains
# oppure
bash a-agentzero/scripts/sync-agents.sh --dry-run
```

L2 fabbrica: `.cursor/skills/harness-agentfactory/` (oggi **1.1.0**, `extends` a-harness). STALE L2 consumer ≠ debito fabbrica — `make sync-consumer-stale`.

Pipeline discovery: [`docs/discovery-pipeline.md`](discovery-pipeline.md). Export Claude stand-alone: `bash scripts/export-discovery-claude.sh`.

**Product orchestra:** `a-product` applica anti–**Build Trap** (Outcome / Success signal prima degli Output) e **Product Kata** light; ingresso B2B via facade `a-b2b`. Map: `a-product/references/escaping-build-trap-map.md`.

---

## Scaffold skill L2 (progetto consumer)

Le skill figlie **non** stanno in HAL. Si creano nel repo del sito/blog/WP.

### Workflow sintetico

1. Nel repo consumer: `mkdir -p .cursor/skills/{dominio}-{slug}`
2. Copia `agents/a-{dominio}/extension-template.md` → `SKILL.md`
3. Compila `extends: a-{dominio}`, `version`, `extends-version` (versione L1 corrente)
4. Aggiungi delta: path contenuti, brand, regole locali
5. Crea file dati se mancanti:

| Dominio | File dati |
|---------|-----------|
| copywriter | `.cursor/brands/{slug}.md` |
| illustrator | `.cursor/illustration-styles/{slug}.md` |
| seozoom | `seo/export-manifest.json`, brief in skill L2; se ricerca interna → playbook L2 (`pagefind-*.md`) + canone L1 `competencies/geo-citabilita/references/ricerca-on-site-seo-geo.md` |
| wordpress | `.cursor/wordpress/{slug}.md` |
| personas / jtbd / gherkin | `.cursor/product/` (fallback `.claude/product/`, `product/`) — `prd.md`, `mockup/`, `personas.md`, `jtbd.md`, `features/` |
| charts | `.cursor/chart-styles/{slug}.md` |
| b2b | L2 `b2b-*` + path enrichment / ICP in skill (vedi `a-b2b/extension-template.md`; canone = `a-product` § Profilo B2B) |
| product | L2 `product-*` + path product (vedi `a-product/extension-template.md`) |
| po | L2 `po-*` + `.cursor/product/` (vedi `a-po/extension-template.md`) |
| enrichment | L2 `enrichment-*` o path da `b2b-*` (vedi `a-enrichment/extension-template.md`) |
| harness | L2 `harness-{progetto}` (vedi `a-harness/extension-template.md`) |
| uiux | L2 `uiux-*` / legacy `uiux-designer` → preferire `extends: a-uiux` (vedi `a-uiux/extension-template.md`); playbook DUP [`playbook-l2-dup-cut.md`](playbook-l2-dup-cut.md) |

6. Opzionale: override competenze in `.cursor/skills/{figlio}/competencies/{id}/SKILL.md` (solo delta; vedi `extension-template.md` del dominio)
7. `CHANGELOG.md` figlio da template L0

Guida completa: [`a-agentzero/references/extension-scaffold.md`](../a-agentzero/references/extension-scaffold.md)

**a-seozoom / a-illustrator / a-copywriter L2:** i template includono `competencies:` e stub override. Path/script/comandi consumer solo in L2. Non hardcodare nomi di siti nel canone L1.

### Naming consigliato

`{dominio}-{slug}` — es. `copywriter-esempio`, `seozoom-miosito`, `wordpress-cliente`, `personas-etf`, `jtbd-etf`, `gherkin-etf`, `charts-dashboard`, `b2b-explorer`, `product-progetto`, `po-prodotto`, `enrichment-prodotto`, `harness-wtp`, `uiux-liberating`.

---

## Verifica e test

```bash
# Gate salute (catene L0/L1/L2 + sync dry-run) — lista L1 = Makefile / sync-agents.sh
make test-unit

# Solo catene versioni (fail on STALE)
make version-chains

# Quality pack (bash -n, frontmatter, shellcheck, md-links)
make pre-commit

# Python (se toccati script seozoom)
python3 -m py_compile a-seozoom/scripts/seozoom_lib.py a-seozoom/scripts/dashboard_extract.py
```

HAL non ha una suite unittest centralizzata. I test dei siti consumer restano nei rispettivi repository.

---

## Configurazione locale HAL

### `.cursor/` in questo repo

| Path | Contenuto |
|------|-----------|
| `.cursor/brands/agentfactory.md` | Tono e lessico per copy su HAL |
| `.cursor/commands/` | Override slash AF (`/commit`, `/document`, `/sync`, `/version`, …) |
| `.cursor/plans/` | Piani storici (es. protocollo versionamento) |

Baseline L0 condivisa: [`a-agentzero/commands/`](../a-agentzero/commands/) → `~/.cursor/commands/` via `/sync !`. In conflitto vince l'override in `.cursor/commands/`.

Non includere skill L2 consumer né `illustration-styles` importati da altri progetti.

### `.env`

File locale per test (credenziali image API, SeoZoom, ecc.). **Non** tracciato in git. Gli script `a-seozoom` leggono il `.env` del **progetto consumer**, non quello di HAL, quando eseguiti con `--project-root`.

---

## Apprendimento da sessione (`/learn`)

| Invocazione | Effetto |
|-------------|---------|
| `/learn ?` | Report apprendimenti chat corrente; zero scrittura |
| `/learn !` | Consolida in L2 / brand / rules; **se necessario** Attività in `./ToDo.md` e/o docs locali |

Skill: [`a-agentzero/learn/SKILL.md`](../a-agentzero/learn/SKILL.md)  
Target consolidamento: [`a-agentzero/learn/references/consolidation-targets.md`](../a-agentzero/learn/references/consolidation-targets.md)

---

## Sync agenti (`/sync`)

| Invocazione | Effetto |
|-------------|---------|
| `/sync ?` | Report catene L1←L0 (e L2 se path progetto) + stato comandi L0; nessun deploy |
| `/sync !` | `deploy-all.sh` (skill, agents, `~/.cursor/commands/`) + report; sync selettivo guidato |
| `/sync <` | Analisi L2→L1/L0 (DUP / promozione); **solo report**. Su cwd HAL: L2 in-repo + consumer noti `/var/www/*/./.cursor/skills/` — vedi sync skill § `/sync <` e [`l2-generalization.md`](../a-agentzero/sync/references/l2-generalization.md) |

```bash
bash a-agentzero/scripts/sync-agents.sh
bash a-agentzero/scripts/sync-agents.sh --dry-run
bash a-agentzero/scripts/sync-agents.sh --projects /path/to/project
```

Skill: [`a-agentzero/sync/SKILL.md`](../a-agentzero/sync/SKILL.md)  
Comandi L0: [`a-agentzero/commands/`](../a-agentzero/commands/)

---

## Snapshot

Per handoff o debug versioni:

```bash
mkdir -p docs/snapshots
# Raccogli output sync-agents.sh --dry-run + git status
# Scrivi docs/snapshots/SNAPSHOT_YYYY-MM-DD_HH-mm.md
```

Vedi anche slash command `/snapshot` in `.cursor/commands/snapshot.md`.

---

## Riferimenti rapidi agenti L1

| Agente | Skill | Subagent | Template L2 |
|--------|-------|----------|-------------|
| Copy | `a-copywriter/SKILL.md` | `agents/a-copywriter.md` | `extension-template.md` |
| Illustrazioni | `a-illustrator/SKILL.md` | `agents/a-illustrator.md` | `extension-template.md` |
| SEO/GEO | `a-seozoom/SKILL.md` | `agents/a-seozoom.md` | `extension-template.md` |
| WordPress | `a-wordpress/SKILL.md` | `agents/a-wordpress.md` | `extension-template.md` |
| Personas | `a-personas/SKILL.md` | `agents/a-personas.md` | `extension-template.md` |
| JTBD | `a-jtbd/SKILL.md` | `agents/a-jtbd.md` | `extension-template.md` |
| Gherkin | `a-gherkin/SKILL.md` | `agents/a-gherkin.md` | `extension-template.md` |
| Charts | `a-charts/SKILL.md` | `agents/a-charts.md` | `extension-template.md` |
| B2B (facade) | `a-b2b/SKILL.md` | `agents/a-b2b.md` | `extension-template.md` |
| Product (orchestra) | `a-product/SKILL.md` | `agents/a-product.md` | `extension-template.md` |
| PO / Product shape | `a-po/SKILL.md` | `agents/a-po.md` | `extension-template.md` |
| Enrichment | `a-enrichment/SKILL.md` | `agents/a-enrichment.md` | `extension-template.md` |
| Harness | `a-harness/SKILL.md` | `agents/a-harness.md` | `extension-template.md` |
| UI/UX | `a-uiux/SKILL.md` | `agents/a-uiux.md` | `extension-template.md` |

### Discovery (a-personas / a-jtbd / a-gherkin)

| Path | Contenuto |
|------|-----------|
| Guida pipeline | [`docs/discovery-pipeline.md`](discovery-pipeline.md) |
| L0 `po-interviewer` | [`a-agentzero/competencies/po-interviewer/`](../a-agentzero/competencies/po-interviewer/) |
| L1 `bdd-security-performance` | `a-gherkin/competencies/bdd-security-performance/` (`/secure`, `/perf`) |
| Product path | `.cursor/product/` → `.claude/product/` → `product/` |
| Export Claude pack | `scripts/export-discovery-claude.sh` → `dist/claude-discovery-agents-*.zip` |
| Authorship da proto | [`a-agentzero/references/l1-from-proto.md`](../a-agentzero/references/l1-from-proto.md) |

### Copy (a-copywriter)

| Path | Contenuto |
|------|-----------|
| `competencies/tono-di-voce/` | Voce brand, inclusività, voice-as-brand |
| `competencies/humanizer/` | Anti-AI, loop, editing |
| `competencies/italiano-locale/` | Purismo, italiano vivo, forbici strutturali |
| `publication-types.md` | Template tipi pubblicazione + workflow JSON-first |

Baseline L0 in `a-agentzero/competencies/` per le stesse id.

### Illustrazioni (a-illustrator)

| Path | Contenuto |
|------|-----------|
| `competencies/stile-visivo/` | Onboarding, style file, coerenza |
| `competencies/prompt-composizione/` | Formula prompt (+ `references/prompt-style.md`) |
| `competencies/preview-render/` | Anteprime → render |
| `competencies/qa-artefatti/` | Checklist artefatti AI, no-fill firme |
| `references/api-providers.md` | `.env` / Qwen (asset orchestratore) |
| `scripts/generate-image.py` | Generazione API |

Style file progetto: `.cursor/illustration-styles/` (dati, non competenze).

### Charts (a-charts) / B2B / Product / PO / Enrichment

| Agente | Path utili |
|--------|------------|
| a-charts | `competencies/{scelta-tipo,leggibilita,implementazione,qa-grafici}/` · style `.cursor/chart-styles/` |
| a-product | orchestra multi-step + § **Profilo B2B** · anti–**Build Trap** (Outcome vs Output) + Product Kata light · L2 `product-*` |
| a-b2b | facade B2B → a-product § Profilo B2B · stesso gate Outcome · `references/delegation-playbook.md` · L2 `b2b-*` |
| a-po | `competencies/{triage-request,problem-framing,lean-canvas,prd-authoring,positioning-offer,evidence-probe,slice-prioritization,growth-loops,market-public-data}/` · `po-interviewer` · `scripts/fetch-istat-sdmx.sh` · L2 `po-*` · data `.cursor/product/data/` · lean-canvas datati · `prd.md` |
| a-enrichment | `references/{enrichment-gates,domain-enrichment-workflow,lead-research-output}.md` · L2 `enrichment-*` |

### Reference SEO/GEO (a-seozoom)

| File | Contenuto |
|------|-----------|
| [`competencies/metriche-analisi/references/metriche-seozoom.md`](../a-seozoom/competencies/metriche-analisi/references/metriche-seozoom.md) | ZO, ZS, ZT, ZA, KO, KD — glossario; fonte `dashboard/{domain}_metriche.json` |
| [`references/dashboard-widgets.json`](../a-seozoom/references/dashboard-widgets.json) | Mapping widget panoramica → API AJAX / JS globals |
| [`competencies/geo-citabilita/references/ricerca-on-site-seo-geo.md`](../a-seozoom/competencies/geo-citabilita/references/ricerca-on-site-seo-geo.md) | Ricerca interna allineata a SEO/GEO (canone L1; playbook in L2) |
| [`competencies/seo-import/references/ui-navigation.md`](../a-seozoom/competencies/seo-import/references/ui-navigation.md) | Endpoint API SeoZoom + panoramica progetto |

Competenze L1: `seo-import`, `metriche-analisi`, `onpage-seo`, `geo-citabilita`, `seo-audit`, `schema-markup`, `programmatic-seo`, `site-architecture`, `hreflang-i18n`, `topic-cluster`. Export dashboard: `seo/YYMMDD/seozoom/dashboard/` (default in `seozoom_export.py`; `--skip-dashboard` per saltarlo). Playwright-only: no `SEOZOOM_API_KEY` / apiv2 come percorso primario.

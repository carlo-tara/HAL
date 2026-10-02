# Changelog — a-seozoom

## [Unreleased]

## [1.8.12] - 2026-09-18

### Changed
- Sync padre: extends-version a-agentzero → 1.6.15 (lean L0 cmds) [sync:safe]



## [1.8.11] - 2026-09-17

### Added
- Sezione **Estensioni L2**: pattern sibling `role: data` + `role: editorial` (pointer Multi-figlio + l2-generalization) [sync:safe]

## [1.8.10] - 2026-09-17

### Added
- Frontmatter `model: orcarouter/deepseek/deepseek-v4-flash-free` + `model-fallback: cursor-default` (OrcaRouter preferred; Cursor default se non raggiungibile) [sync:safe]
- Sync L0 a-agentzero `extends-version: 1.6.14` (preferred model frontmatter) [sync:safe]

## [1.8.9] - 2026-09-15

### Changed
- Sync L0 a-agentzero `extends-version: 1.6.13` (/learn ! ToDo+docs pointer) [sync:safe]


## [1.8.8] - 2026-09-15

### Changed
- Sync L0 a-agentzero `extends-version: 1.6.12` (a-product § Profilo B2B / a-b2b facade) [sync:safe]

## [1.8.7] - 2026-09-15

### Changed
- Sync L0 a-agentzero `extends-version: 1.6.11` (registry a-product) [sync:safe]


## [1.8.6] - 2026-09-15

### Changed
- Appreso da sessione: Reason why in description + regole di ingaggio subagent [sync:safe]


## [1.8.5] - 2026-09-15

### Added
- `metriche-analisi` **1.0.5**: contratto confronto batch (JSON+delta, `(kw,url)`, no overwrite scorecard) + mid-lag EARLY± / segnali deboli ≠ OK — promuosso da `/sync <` liberating.it [sync:review]

## [1.8.4] - 2026-09-15

### Added
- `seo_import_all`: `usable` su SeoZoom FAILED (`missing_critical=[]` + dashboard OK); GTM soft-fail 403/env (slice 2) [sync:safe]

## [1.8.3] - 2026-09-15

### Fixed
- `seo_import_all`: summary SeoZoom da JSON validate multi-riga (niente più Detail `}`); cella MD sanitizzata; FAILED stampa `summary` [sync:safe]

## [1.8.2] - 2026-09-08

### Changed
- Sync L0 a-agentzero `extends-version: 1.6.4` (scaffold commit staged-only) [sync:safe]

## [1.8.1] - 2026-09-07

### Changed
- Competenza `google-ads` **1.1.1**: RSA/LP allineati a 5 Copy Blocks (a-copywriter) [sync:safe]

## [1.8.0] - 2026-09-07

### Changed
- Competenza `google-ads` **1.1.0**: `ops-analysis.md` (6 procedure ricorrenti CPA/spreco/anomalie/scenari + packaging metodo≠dati) [sync:review]

## [1.7.0] - 2026-09-05

### Added
- Competenza `google-ads` 1.0.0: Search / PMax / Shopping (struttura, tracking, budget, feed) distillata da itallstartedwithaidea/agent-skills `skills/google-ads/` (MIT) [sync:review]
- Pin `references/google-ads-agent-skills-source.md`, script `update-google-ads-agent-skills-repo.sh`, comando `/update-google-ads-agent-skills-repo` [sync:safe]

## [1.6.2] - 2026-08-15

### Changed
- Sync L0 1.6.3 (`extends-version: 1.6.3`): git-track L2 sotto `.gitignore` [sync:safe]


## [1.6.1] - 2026-08-15

### Changed
- Sync L0 1.6.2 (`extends-version: 1.6.2`): registry a-po/a-enrichment + l1-from-proto CC BY-NC-SA distill-only [sync:safe]

## [1.6.0] - 2026-08-13

### Changed
- `gmc_export.py`: issue item-level da Merchant API `productStatus.itemLevelIssues` (rimossa Content API `productstatuses`); mapping prodotti su `product_attributes`; niente fallback silenzioso a Content API in mode `merchant` [sync:safe]
- Sync L0 1.6.0 (`extends-version: 1.6.0`): registry `a-b2b` [sync:safe]

## [1.5.1] - 2026-08-13

### Changed
- Sync L0 1.5.7–1.5.8 (`extends-version: 1.5.8`): `l1-from-proto` [sync:safe]; humanizer Never inject ereditato in scrittura on-page/tone — nessun delta body L1 [sync:review]

## [1.5.0] - 2026-08-13

### Added
- Upstream dual: `claude-seo` (MIT) + Labat `SEO-GEO-AEO-Skill` (no SPDX, metodologia lean) — pin, script update, comandi Cursor [sync:review]
- Competenze `hreflang-i18n` 1.0.0 e `topic-cluster` 1.0.0 [sync:review]

### Changed
- `schema-markup` 1.1.0: rich result retired (FAQ/HowTo/…) vs vocabulary [sync:review]
- `geo-citabilita` 1.2.0: GEO≠AEO, llms.txt evidence, checklist Labat riscritta [sync:review]
- `seo-audit` 1.1.0: finding falsificabili, Effort×Impact, Quick/Full batch, drift [sync:review]
- `onpage-seo` 1.0.3 / `metriche-analisi` 1.0.4: ponti AEO e topic-cluster [sync:review]
- Template L2 `extends-version` → 1.5.0 [sync:safe]

## [1.4.7] - 2026-08-13

### Changed
- `/sync <` liberating.it: promuove NEED-N — `metriche-analisi` 1.0.3 (guardrail batch + fuori perimetro), `seo-import` 1.0.3 (CF API live), `onpage-seo` 1.0.2, `site-architecture` 1.0.1 (alias SERP) [sync:review]

## [1.4.6] - 2026-08-07

### Changed
- Sync L0 1.5.6: L1 `a-charts` registry/discovery → solo extends-version [sync:safe]

## [1.4.5] - 2026-08-04

### Changed
- `metriche-analisi` 1.0.2: pass low-KO (KO <=55 + Pos 4-20) con gate owner/intent in canone `metriche-seozoom.md` [sync:review]

## [1.4.4] - 2026-08-03

### Changed
- Sync L0 1.5.5 (voice-as-brand) → extends-version [sync:safe]
- `seo-import` 1.0.2: FAILED usabile, retry timeout, batch misto competitor [sync:review]
- `metriche-analisi` 1.0.1: validazione post-batch (no 24h, ranking≠owner, Δ storici) [sync:review]

## [1.4.3] - 2026-08-03

### Changed
- Sync L0 1.5.4: `/sync <` generalizzazione L2 → solo extends-version [sync:safe]

## [1.4.2] - 2026-08-03

### Changed
- Sync L0 1.5.3: multi-figlio / companion / learn → solo extends-version [sync:safe]
- `onpage-seo` 1.0.1: keyword CSV ≠ copy; voice vince su stuffing [sync:review]
- `seo-import` 1.0.1: latest batch + manifest check [sync:review]

## [1.4.1] - 2026-07-28

### Changed
- Sync L0 1.5.2: `l1-from-proto` corpus skill esterni (vendor+pin) → solo extends-version [sync:safe]

## [1.4.0] - 2026-07-28

### Added
- Competenze distillate da [marketingskills](https://github.com/coreyhaines31/marketingskills) (MIT): `seo-audit`, `schema-markup`, `programmatic-seo`, `site-architecture` [sync:review]
- `geo-citabilita` 1.1.0: pilastri AEO/GEO, audit citabilità, Google vs multi-engine [sync:review]
- Pin upstream + mapping: [references/marketingskills-source.md](references/marketingskills-source.md); clone `vendor/marketingskills/`; script `scripts/update-marketing-repo.sh`; comando `.cursor/commands/update-marketing-repo.md` [sync:safe]

## [1.3.5] - 2026-07-27

### Changed
- Sync L0 1.5.1: `[sync:safe]` comandi/deploy → solo extends-version [sync:safe]

## [1.3.4] - 2026-07-27

### Changed
- Sync L0 1.5.0: comandi Cursor L0 ereditabili (`commands/`) [sync:safe]

## [1.3.3] - 2026-07-27

### Changed
- Sync L0 1.4.1: `po-interviewer`/discovery opt-in (non adottato); regola authorship proto [sync:safe]

## [1.3.2] - 2026-07-27

### Changed
- Sync L0 1.3.1: file dati ≠ competenze [sync:safe]

## [1.3.1] - 2026-07-27

### Changed
- Sync L0 1.3.0: protocollo competenze (L0 opzionale, asset fuori, cross-dominio) [sync:safe]

## [1.3.0] - 2026-07-27

### Added
- Competenze modulari L1: `seo-import`, `metriche-analisi`, `onpage-seo`, `geo-citabilita` [sync:review]
- Orchestratore SKILL.md + agent: lettura selettiva, frontmatter `competencies:` [sync:review]
- Template L2: directory `competencies/{id}/` per override [sync:review]
- `onpage-seo`: riuso competenza copy `tono-di-voce` in scrittura title/meta/FAQ [sync:review]

### Changed
- Sync L0 1.2.1; `extends-version: 1.2.1` [sync:safe]
- Reference markdown migrati sotto `competencies/*/references/` [sync:breaking]
- Asset script restano in `references/` (`export-manifest.json`, `dashboard-widgets.json`, `ui-selectors.json`) [sync:safe]

**Mapping reference → competenza:**

| Ex path | Nuovo path |
|---------|------------|
| `references/ui-navigation.md` | `competencies/seo-import/references/` |
| `references/url-to-filename.md` | `competencies/seo-import/references/` |
| `references/metriche-seozoom.md` | `competencies/metriche-analisi/references/` |
| `references/ricerca-on-site-seo-geo.md` | `competencies/geo-citabilita/references/` |

## [1.2.1] - 2026-07-27

### Changed
- Sync L0 1.2.0: protocollo competenze modulari (opt-in; copy resta su a-copywriter) [sync:safe]

## [1.2.0] - 2026-07-17

### Added
- Supporto `SEOZOOM_PROJECT_COMPETITOR`: export di un secondo progetto SeoZoom in `seo/YYMMDD/seozoom-competitor/` (globals + dashboard; per-URL skip di default) [sync:review]
- Helper `competitor_project_from_env`, `detect_project_domain`, `export_filenames_for_domain`, `manifest_with_domain` in `seozoom_lib.py`
- Funzione riusabile `export_project()` in `seozoom_export.py`; flag CLI `--skip-competitor-project` (export + import massivo)
- Documentazione confronto metriche nostro vs competitor project in `references/metriche-seozoom.md` (distinto da `{domain}_competitor.csv`)

### Changed
- Path batch: sottocartella `seozoom-competitor` in `batch_paths.SUBDIRS` e manifest template [sync:review]

## [1.1.3] - 2026-07-16

### Changed
- Sync L0 1.1.2: skill `/sync` (deploy + report versioni) [sync:safe]

## [1.1.2] - 2026-07-16

### Added
- Appreso da sessione: invariante Playwright-only per export SeoZoom progetto (no `SEOZOOM_API_KEY` / apiv2 come percorso primario) [sync:safe]

## [1.1.1] - 2026-07-15

### Added

- Credenziali `.env` e documentazione import per **Google Merchant Center** (`GMC_*`) e **Google Ads** (`GOOGLE_ADS_*`) [sync:safe]
- Script `gmc_export.py`, `google_ads_export.py` integrati in `seo_import_all.py` e `analytics_export_all.py` [sync:safe]
- Troubleshooting L1: developer token Test, `LOGIN_CUSTOMER_ID`, Centro API MCC, OAuth Testing [sync:safe]

### Changed

- Tabella fonti dati, workflow import e prerequisiti `.env` allineati a GMC/Google Ads [sync:safe]

## [1.1.0] - 2026-07-15

### Added
- Export panoramica progetto SeoZoom in `seozoom/dashboard/` (metriche ZA/ZT/ZS/ZO, andamento dominio, distribuzione keyword, andamento annuale, backlink, previsione traffico, keyword monitorate/progetto, pagine competitor, idee articoli)
- `scripts/dashboard_extract.py`, metodi dashboard su `SeoZoomClient`, mapper timeseries/metriche in `csv_mappers.py`
- `scripts/probe_dashboard_capture.py` e mapping [references/dashboard-widgets.json](references/dashboard-widgets.json)
- Flag `--skip-dashboard` su `seozoom_export.py` / `seo_import_all.py`
- Validazione e sezione report per file dashboard (non critical)

### Changed
- Fonte metriche sito: priorita `dashboard/{domain}_metriche.json` vs sola UI [sync:safe]
- Documentazione SKILL, agent, metriche-seozoom, ui-navigation [sync:safe]

## [1.0.8] - 2026-07-14

### Added
- Appreso da sessione (sito consumer): canone L1 ricerca on-site da insight SEO/GEO (`references/ricerca-on-site-seo-geo.md`); sezione SKILL, agent, extension-template [sync:safe]

### Changed
- Reference ricerca on-site: esempi path L2 generici (`seozoom-{slug}`), senza nomi siti consumer [sync:safe]

## [1.0.7] - 2026-07-13

### Changed
- Sync L0 1.1.1: sezione Apprendimento da sessione [sync:safe]
- Script export: `--project-root` default = cwd; rimossi path hardcoded a siti consumer [sync:safe]
- Manifest fallback e `url-to-filename.md` con dominio `example.it` generico [sync:safe]
- Tabella esempi L2 resa generica (`seozoom-{slug}`) [sync:safe]

## [1.0.6] - 2026-07-13

### Added
- Workflow analisi «Come migliorare la ZA»; eccezione ZT vs ZA (metriche sito tutte basse, ZO minima); colonna ZA in tabella file CSV [sync:safe]

## [1.0.5] - 2026-07-13

### Added
- Appreso da sessione Batch 11 (export L1): workflow batch PagesWithPotential + sanity check; soglia GSC CTR; pattern FAQ/JSON-LD e ricerca on-site; sezione SKILL batch [sync:safe]

## [1.0.4] - 2026-07-13

### Added
- Appreso da sessione: fonte UI vs CSV per ZA/ZT/ZS/ZO; § ZT vs ZA; workflow diagnosi ZT-ZA; colonna `za` in competitor.csv; tabella CSV con colonna ZT; eccezione UI in SKILL e agent [sync:safe]

## [1.0.3] - 2026-07-13

### Added
- Appreso da sessione: canone L1 agent readiness per GEO (Content Signals `ai-train=no`, Link verso indice curato, no `api-catalog` per JSON UI, DNS-AID dipendente da DS registrar, Markdown Cloudflare Free accettabile) [sync:safe]

## [1.0.2] - 2026-07-13

### Added
- Appreso da sessione: workflow analisi «Come migliorare la ZS»; matrice leve ZO vs ZS; soglie `Var`; anti-pattern ZS; file CSV Cannibalization/PagesWithTrafficDown/MainPages [sync:safe]

## [1.0.1] - 2026-07-13

### Added
- Appreso da sessione: glossario ZO/KO/KD/ZA in `references/metriche-seozoom.md`; workflow analisi «Come migliorare la ZO»; regola striking distance vs ContentGap [sync:safe]

## [1.0.0] - 2026-07-13

### Added
- Baseline iniziale — import massivo SeoZoom/GSC/GA4/GTM/Cloudflare, analisi SEO/GEO
- Campi `version` e `extends-version: 1.0.0` (allineato a a-agentzero 1.0.0) [sync:safe]

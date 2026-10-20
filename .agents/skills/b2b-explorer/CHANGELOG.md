# Changelog — b2b-explorer (L2)

## [Unreleased]

### Changed

- 1.2.2 → **1.2.3** — Rimossi riferimenti a Cursor: `.cursor/product/` → `product/`, `.cursor/rules/` → `docs/rules/`, `.cursorrules` rimosso da layout repo `[sync:safe]`
- 1.2.1 → **1.2.2** — Appreso da sessione: riconciliazione alias Company Key / Customer 360, allineamento `primary_domain` al sito corporate verificato e clearing domini freemail/privacy (`simplelogin`, `gmx.us`, ecc.) `[sync:safe]`

- 1.1.50 → **1.1.51** — Runtime B2B usa solo PostgreSQL di produzione (`PGDATABASE_URI_PROD`); DB locale confinato ai test `[sync:safe]`

- 1.1.49 → **1.1.50** — Sync padre: extends-version a-b2b 2.2.0 → 2.2.1 `[sync:safe]`
- 1.1.48 → **1.1.49** — Skill L1 canonical HAL Gateway collegata via `.agents/skills`; `extends-version` a-b2b 2.1.2→2.2.0; WTP L2 resta autorità per guardrail/path `[sync:safe]`
- 1.1.47 → **1.1.48** — Extract ICP hard: `export:icp-list` → `icp-6-50-chiasso-3h.*` (6–50 ∩ LO+PI+ER+VE/~3h); legacy `export:icp-list:legacy-chiasso-2h`; `MAX_H_CHIASSO_3H` + preferred `bacino_chiasso` `[sync:safe]`
- 1.1.46 → **1.1.47** — Hard guardrails PO ok: ICP **6–50** ∩ bacino Chiasso **~3h**; capacity **3+3**/sett; GTM **4 bucket** (advocacy/nicchie/tiepidi/freddi); description + AGENTS/README allineati; 6–20/≤2h/70/30 → storico `[sync:safe]`
- 1.1.45 → **1.1.46** — LeadMagic company LinkedIn+domain → PG upsert (`enrich:companies:leadmagic-*`); helpers `leadmagic-company-pg` `[sync:safe]`
- 1.1.44 → **1.1.45** — Appreso da sessione: LeadMagic domain no-org + checkpoint clusters; Apollo last3m merge; P.IVA `icp_*` a scala master; gap LinkedIn→PG vs `enrich-companies-leadmagic.js` / Apollo checkpoint `[sync:safe]`
- 1.1.43 → **1.1.44** — Sync selettivo padre `a-b2b` 2.0.6→**2.1.2**: facade → `a-product` § Profilo B2B; Cascata GTM puntatore aggiornato `[sync:review]` + pin L0 `[sync:safe]`
- 1.1.42 → **1.1.43** — Appreso da sessione: minuta > Gemini summary; GTM anticipato → `proposta-delta-prd-*` (PRD Stable intatto); drift GTM set 2026 (6–50/~3h/3+3) documentato senza auto-expand hard L2 `[sync:safe]`
- 1.1.41 → **1.1.42** — `/sync <` DUP#2: enrichment runbook → puntatore `b2b-enrichment-run.mdc`; skill = path + ICP/buyer `[sync:safe]`
- 1.1.40 → **1.1.41** — Sync selettivo padre `a-b2b` 2.0.5→**2.0.6** (Reason why + regole subagent) `[sync:safe]`
- 1.1.39 → **1.1.40** — Appreso da sessione: live score3 = PG+Mongo (non PG-only); `WTP_EXPLORER_SCORE3_LIMIT` `[sync:safe]`
- 1.1.38 → **1.1.39** — Explorer UI live da `GET /api/wtp/explorer/score3-clusters` (PG+Mongo); standalone/viz file non SoT runtime `[sync:safe]`
- Master enrichment build → Postgres `enrichment.*` (`build:enrichment` / alias `build:sqlite`); SoT `DATABASE_URL` invece di `.shared/b2b/enrichment.sqlite`. [sync:safe]

## [1.1.38] — 2026-09-12

### Changed

- Sync selettivo: `extends-version` 2.0.4 → 2.0.5 (`a-b2b` Non-goals/freeze greppabile) [sync:safe]

## [1.1.37] — 2026-09-11

### Added

- Appreso da sessione: `enrich:icp-buyers` (ranking owner→CEO→C-level→Director; LTV Mongo via user ObjectId; P.IVA footer; ReportAziende ATECO/utile/fatturato); freemail → scrape sul sito; anti-pattern rebuild che droppa `leadmagic_linkedin` su companies. [sync:safe]

## [1.1.36] — 2026-09-09

### Added

- Appreso da sessione: anti-pattern XLSX lookalike vs export senza ingest; caveat delta ICP senza `enriched_at`; dotenv quiet per CLI JSON; lib `icp-export-filter` + test. [sync:safe]

## [1.1.35] — 2026-09-09

### Added

- SoT master `.shared/b2b/enrichment.sqlite` nelle specs pilota; seed lookalike `ingest:lookalike-geo`; extract ICP `export:icp-list` (full / `--since-last`). [sync:safe]

## [1.1.34] — 2026-09-09

### Added

- Appreso da sessione: Sync Jira = lista nel PRD (no ticket in delta); anti-pattern no collasso a 2 livelli / no survey prequalifica fuori WB-45 / no naming ETF inventato (solo ok PO). [sync:safe]

## [1.1.33] — 2026-09-09

### Changed

- PRD fonte viva → `PRD_b2b_v1-0-1.md` (v1.0.1): WB-45 landing interattiva, WB-46 naming ETF, AC WB-27/25/43; riservati `WB-41`…`WB-46`; cleanup riferimenti vivi `JS-*`. [sync:safe]

## [1.1.32] — 2026-09-09

### Changed

- PRD fonte viva rinominato: `01-requisiti/PRD_b2b_v1-0-0.md` (ex `PRD_moneysurfers-b2b-pmi_v0.9.md`). [sync:safe]

## [1.1.31] — 2026-09-09

### Added

- Enforce commit enrichment: gitignore su cluster/cohort/checkpoint JSON in `.shared/b2b/`; README + rule — sqlite sì se aggiornato, JSON hand-off no. [sync:safe]

## [1.1.30] — 2026-09-08

### Added

- Appreso da sessione: git enrichment — commitare `enrichment.sqlite` se aggiornato; non tracciare di default cluster/cohort/checkpoint JSON; attenzione size GitHub >50MB. [sync:safe]

## [1.1.29] — 2026-09-08

### Added

- Appreso da sessione: segmento `priorsignups` (`--until`/`--out` + `enrich:priorsignups:apollo`); preservare partial Apollo su crediti insufficienti; non ingestare cluster JSON vuoti/failed; `APOLLO_CREDITS_REMAINING` default ≠ saldo API. Rule + README aggiornati. [sync:safe]

## [1.1.28] — 2026-09-08

### Added

- Rule `docs/rules/b2b-enrichment-run.mdc` + README fasi: `--since` se manca corpmails; HS senza `--trigger`; doppie metriche post-`build:sqlite`. [sync:safe]

## [1.1.27] — 2026-09-08

### Added

- Appreso da sessione: run enrichment — `npm install` se manca dotenv; export `--since` senza corpmails; HS read-only (no `--trigger`); Apollo solo HS-miss; post-fase `build:sqlite` + metriche `recognized` vs `clienti_enriched_*`; anti-pattern rebuild parziale che droppa provider assenti dai JSON. [sync:safe]

## [1.1.26] — 2026-09-08

### Changed

- Sync selettivo `a-b2b` 2.0.4: `extends-version: 2.0.4` (padre solo `[sync:safe]` L0). [sync:safe]

## [1.1.25] — 2026-09-08

### Added

- Appreso da sessione: ordine obbligatorio delta PRD (AC WB-42→24→26 prima di nuove JS; no nuove epiche; WB-43/44 riservate) + rule `docs/rules/b2b-prd-delta.mdc` su `01-requisiti/**`. [sync:safe]

## [1.1.24] — 2026-09-08

### Added

- Appreso da sessione: delta PRD minimo (AC prima, JS solo per gap outcome); spine WB-42 (A/B/C, SLA firma ≤7gg); pack WB-24 + info generiche; SLA avvio ≤15gg / OQ IT; WB-43 campagna nov (Marketing/P2) vs contratti WB-30; WB-44 step 2 a 6 mesi; riservati `WB-41`…`WB-44`; anti-pattern no JS HubSpot/provvigioni/training sales. [sync:safe]

## [1.1.23] — 2026-09-03

### Added

- Appreso da sessione: Owner _Product Owner_ (flusso vendite WB-42); igiene Backlog/OQ (no done/ko/già in Jira; no OQ risolte). [sync:safe]

## [1.1.22] — 2026-09-03

### Added

- Appreso da sessione: anti-pattern no tabella mapping ID nel PRD; configuratore→WB-12, flusso vendite→WB-13; analisi solvibilità/visure dentro WB-24. [sync:safe]

## [1.1.21] — 2026-09-03

### Changed

- Mappa dipendenze JS fuori dal PRD: `01-requisiti/dipendenze-job-stories.md`; rimossa tabella allineamento ID Jira dal PRD. [sync:safe]

## [1.1.20] — 2026-09-03

### Changed

- PRD v0.9.2: story `WB-41`/`WB-42` riservate finché create in Jira (sync per titolo). [sync:safe]

## [1.1.19] — 2026-09-03

### Changed

- Appreso da sessione: priorità JS per **Cost of Delay** (fasi fondazioni → commerciale → deal/erogazione → scala); rimandi `WB-xx — Titolo` anche in AC/DoD/backlog. [sync:safe]

## [1.1.18] — 2026-09-03

### Changed

- Appreso da sessione: sync PRD↔Jira per titolo/riepilogo; campo **Dipende da** (`WB-xx — Titolo`) + mappa dipendenze PRD. [sync:safe]

## [1.1.17] — 2026-09-03

### Changed

- Appreso da sessione: ID PRD epiche/Job Story = chiavi Jira `WB-*` (`00-docs/Jira.csv`); mapping storici `JS-*`/`EPIC-*` nel PRD. [sync:safe]

## [1.1.16] — 2026-09-03

### Changed

- Appreso da sessione: metadata JS `Owner` + `Persona` (codice+titolo); POV cliente P1/P2/P4/P5 da JS-B02; Owner = ruoli stabili; titoli processuali; epic B2/B4 naming + plain language anti-gergo; PRD unica fonte. [sync:safe]

## [1.1.15] — 2026-09-02

### Removed

- Eliminato mirror `prd_js_v0.9.md`: PRD v0.9 è unica fonte viva per Job Stories. [sync:safe]

## [1.1.14] — 2026-09-02

### Changed

- PRD v0.9.1: epiche Blocco B riallineate a **5 outcome** lungo funnel processo ripetibile (B1 offerta → B2 pipeline → B3 deal pronto → B4 erogazione → B5 scala); ex B6/B7/B8 assorbite. JS invariate. [sync:safe]

## [1.1.13] — 2026-09-02

### Added

- Appreso da sessione: PRD v0.9 con Job Stories (`JS-*`) + **Ruolo (ownership)**; path fonte viva `01-requisiti/PRD_moneysurfers-b2b-pmi_v0.9.md`; mirror `prd_js_v0.9.md`; EPIC-B8 (JS-B20–B22); welfare layer formazione vs piattaforma full. [sync:safe]

### Changed

- Allineamento listino operativo: tre livelli modulari L1/L2/L3 (Base/Premium superati). [sync:safe]

## [1.1.12] — 2026-08-20

### Changed

- Path inventario SOM: `projects/b2b-piccoleimprese/` (non `wtp/projects/…`). [sync:safe]

## [1.1.11] — 2026-08-20

### Changed

- Sync selettivo `a-b2b` 2.0.3: cascata GTM e formato PRD → rimandi L1; `extends-version: 2.0.3`. [sync:review]

## [1.1.10] — 2026-08-18

### Changed

- Appreso da sessione: codice app in `wtp/`; in root solo `data/` e `.shared`. [sync:safe]

## [1.1.9] — 2026-08-17

### Changed

- Appreso da sessione: skill/agenti portati in WTP App; working dir `/var/www/WTP_App`; dati `.shared/b2b/`; env solo root; URL `/explorer/b2b/`. [sync:safe]
- Guardrail allineati a listino Enrico (Base/Premium forfait+€/pax; Spread out; 5–6 close). [sync:safe]

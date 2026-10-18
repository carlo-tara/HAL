# Changelog — harness-wtp (L2)

## [Unreleased]

### Changed

- 1.1.2 → **1.1.3** — Appreso da sessione: Cost control OpenAPI Risk; `/IT-negativita` strictly on-demand (includeNegativity: true, bottone UI); Company 360 lazy risk solo su tab #rischi (no prefetch su renderShell); fetch incrementale existingSources riutilizza Start/Advanced senza ri-addebiti `[sync:safe]`

- 1.1.1 → **1.1.2** — Appreso da sessione: quiet test runner default per backend e Platform API con log esteso rotante settimanale in `logs/test-YYYY-WW.log` (in `.gitignore`), throttling 1h e lockfile PID per `test-e2e`; sync padre `extends-version: 1.7.4` `[sync:safe]`
- 1.1.0 → **1.1.1** — Appreso da sessione: node-pg-migrate dry-run check (no comando status), fallback su pg Node per script Python senza driver di sistema PEP 668 e risoluzione .env assoluta da `__file__` `[sync:safe]`

- 1.0.98 → **1.0.99** — Appreso da sessione: verifica snapshot index isolato per WIP misto, preservazione working tree/formatting e assert AppBar da manifest con release contract aggiornato `[sync:safe]`

- 1.0.97 → **1.0.98** — Gate integration operativo (manifest partizionato); browser BDD Playwright su UI Auth con API doubles; coverage frontend nativa Node, limiti espliciti in README `[sync:safe]`

- 1.0.96 → **1.0.97** — Runtime locale/B2B punta solo a PostgreSQL produzione; Compose PostgreSQL confinato ai test `[sync:safe]`

- 1.0.95 → **1.0.96** — Sync padre: extends-version a-harness 1.7.2 → 1.7.3 `[sync:safe]`
- 1.0.94 → **1.0.95** — Appreso da sessione: sync massivo enrichment su Railway (PGDATABASE_URI_PROD) via data-only pg_dump/psql; Customer 360 Mongo Atlas secureConnect timeout `[sync:safe]`
- 1.0.93 → **1.0.94** — Skill base a-harness HAL Gateway collegata; `extends-version` 1.5.10→1.7.2 `[sync:safe]`
- 1.0.92 → **1.0.93** — Appreso da sessione: home-chat SQL cache `home_chat_sql:*`; force-table+`totalCount`; Customer decisore incl. Manager (no demote champion); UI scroll 50 `[sync:safe]`
- 1.0.91 → **1.0.92** — Appreso da sessione: Company 360 curated packs (bandi ACL+API+tab); DATE PG → ISO in `mapRow` ACL `[sync:safe]`
- 1.0.90 → **1.0.91** — Appreso da sessione: host nginx `/api/customer`→`:3000`; home-chat no recent-50 silenzioso; Contact Owner PG + ignore `HubSpot owner <id>`; parity 360 no Risk su persona `[sync:safe]`
- 1.0.89 → **1.0.90** — Appreso da sessione: Compose `api` bake-only (no mount BE) → `build` + `--force-recreate` per patch `src/wtp/backend` `[sync:safe]`
- 1.0.88 → **1.0.89** — Appreso da sessione: FE fetch JSON fail-soft (HTML/`<!DOCTYPE` ≠ JSON); route API nuove → restart `api` `[sync:safe]`
- 1.0.87 → **1.0.88** — Appreso da sessione: FE PDF continuo + titoli H2 export; puntatore carta light `wtp-ux-ui` `[sync:safe]`
- 1.0.86 → **1.0.87** — Appreso da sessione: FE PDF continuo via File→Esporta PDF; classic-script = vendor globals + `WtpDomToPdfBlob`; multi-tab = reveal all panels `[sync:safe]`
- 1.0.85 → **1.0.86** — Compose: shell `LLM_PROVIDER` batte `.env` (es. `cursor#qwen`) `[sync:safe]`
- 1.0.84 → **1.0.85** — OpenAPI `OPENAPI_SANDBOX=1` → `resolveOpenApiBases` test.risk/test.company `[sync:safe]`
- 1.0.83 → **1.0.84** — Appreso da sessione: chat→`./ToDo.md` Attività; chiudere track paralleli → backlog flat `[sync:safe]`
- 1.0.82 → **1.0.83** — Appreso da sessione: `build:prompts` da seed + COPY `seed` in Docker/Railway; D3 locale vendor (no CDN) `[sync:safe]`
- 1.0.81 → **1.0.82** — Appreso da sessione: scheda Liste = session fallback + no latch suggerimenti; redirect legacy preserva query `[sync:safe]`
- 1.0.80 → **1.0.81** — Appreso da sessione: Postgres locale `wtp` vs `wtp_test` vs Railway; shell `DATABASE_URL` batte `.env` in Compose; SMTP no-op/preload in test; dump PG18→PG16 `[sync:safe]`
- 1.0.79 → **1.0.80** — Appreso da sessione: Customer query `?jobId=`/`listId`; job routes = restore come `GET /jobs`; config seed≠`data/`; `/graph -y` hygiene tip `[sync:safe]`
- 1.0.78 → **1.0.79** — Appreso da sessione: `/todo` Inventario ricalcola HEAD + origin da git (no snapshot stale) `[sync:safe]`

## [1.0.75] - 2026-09-15

### Changed

- Sync padre: extends-version a-harness → 1.5.1 + soft DUP proof-gate/diff-tab → rimandi L1 [sync:safe]

### Changed

- 1.0.73 → **1.0.74** — Sync padre `a-harness` **1.3.1**; track concurrent + dual-alias → L1; delta assert WTP `[sync:safe]`
- 1.0.72 → **1.0.73** — Sync selettivo padre `a-harness` 1.2.9→**1.3.0**; Note gate alto/medio → puntatori L1 (delta WTP resta) `[sync:safe]`
- 1.0.71 → **1.0.72** — soft DUP: § Temi UI → puntatore `wtp-ux-ui` + `surferdark.css` (no hex/path DS) `[sync:safe]`
- 1.0.70 → **1.0.71** — `/sync <` DUP#1: SurferDark CSS gate → puntatore `wtp-ux-ui` checklist #12 `[sync:safe]`
- 1.0.69 → **1.0.70** — Sync selettivo padre `a-harness` 1.2.8→**1.2.9** (Reason why + regole subagent) `[sync:safe]`
- 1.0.68 → **1.0.69** — Appreso da sessione: accept MS range ⊆ grafo hub (espandi avanti); Act ready≠commit; post-accept refresh ToDo; freeze lag ≠ SoT next Act `[sync:safe]`
- 1.0.67 → **1.0.68** — Sync selettivo padre `a-harness` 1.2.7→**1.2.8** + puntatore path `./ToDo.md` (canone L0/L1) `[sync:safe]`
- 1.0.66 → **1.0.67** — Sync selettivo padre `a-harness` 1.2.5→**1.2.7** (`/accept` default Plan; `/cycle` ≠ accept) `[sync:safe]`
- 1.0.65 → **1.0.66** — Appreso da sessione: Diff-tab index vuoto + path unstaged ≠ HEAD → no `git add` silenzioso, segnala re-stage `[sync:safe]`
- 1.0.64 → **1.0.65** — Appreso da sessione: SurferDark≠Lists wait/retry; soft dual-alias su token opt-in GREEN `[sync:safe]`
- 1.0.63 → **1.0.64** — Appreso da sessione: MS≠SurferDark wait/retry; hub FCIS post-port se D1 no-op; commit MS = grafo `require` loadable; `.lock` file ≠ held `[sync:safe]`
- 1.0.62 → **1.0.63** — Appreso da sessione: SurferDark CSS gate suite-wide soft style + `ruleBody` anti-discendenti + print `:has` scope `[sync:safe]`
- 1.0.61 → **1.0.62** — Appreso da sessione: D1 probe `:param`↔`{param}` + multi-router; boundary regex anti-falso-positivo; C-hub port compositi + pure locale Enrichment; staged-only index vuoto `[sync:safe]`
- 1.0.59 → **1.0.60** — Appreso da sessione: L3 process live da `bcServiceRegistry`+nginxStrangler; D1 probe prima del RED; C-hub residui + `commercialExecutiveSummaryPort` `[sync:safe]`
- 1.0.58 → **1.0.59** — Appreso da sessione: SurferDark CSS gate — assert Explorer tollerano assenza `<style>` page-local `[sync:safe]`
- 1.0.57 → **1.0.58** — Appreso da sessione: OAS↔runtime = implementare path canone; «procedi» su v1 completo = solo residual debt; seed ICP no `activityStatus` inventato; 502 `apiErrorBody` `[sync:safe]`
- 1.0.56 → **1.0.57** — Risk: client OpenAPI reale (`openApiRiskClient` + Bearer env); no sandbox/`openApiAuth` inventati; slim `/score` + seed ICP in README tip `[sync:safe]`
- 1.0.55 → **1.0.56** — Appreso da sessione: integrità slice multi-agente pre-gate; `profileLibRoot` = clone reale (no `WTP_REPO_ROOT` sandbox); restore env nei test `[sync:safe]`
- 1.0.54 → 1.0.55 — Appreso da sessione: Steward smell → ri-verifica HEAD/WIP prima del RED (no slice su finding stale) `[sync:safe]`
- 1.0.53 → 1.0.54 — SurferDark wave2: shim `enrico.css` removed; CSS SoT only `surferdark.css` `[sync:safe]`
- 1.0.52 → 1.0.53 — Appreso da sessione: rename CSS SurferDark = no blanket replace su assert `doesNotMatch` legacy `[sync:safe]`
- 1.0.51 → 1.0.52 — SurferDark SoT `surferdark.css` (shim `enrico.css`); gate `surferdarkAppbarCss.test.js`; migration step 6 Done `[sync:safe]`
- 1.0.50 → 1.0.51 — Appreso da sessione: ladder Lists `list_rows` strangler + ACL artifactStore puro; flag `listsStoredInListRows`; «prosegui»=rung successivo `[sync:safe]`
- 1.0.49 → 1.0.50 — Appreso da sessione: no `| tail` sul gate (MAKE_EXIT); hard-close fase + `mongoDbPort`; edit chirurgico routes; «procedi»=Act `[sync:safe]`
- 1.0.48 → 1.0.49 — Appreso da sessione: i18n SoT `src/auth/locales` only; `wtpStaticRoot` no `dist/`; no FastAPI big-bang; no `wtp-runs`/archive scripts in repo `[sync:safe]`
- 1.0.47 → 1.0.48 — Appreso da sessione: Diff-tab post-cycle = solo residuo proprio (no WIP concurrent); Customer cache → `lists/customerPerfCachePort` (non Integrations) `[sync:safe]`
- 1.0.46 → 1.0.47 — Appreso da sessione: «procedi Bn» HEAD vs WIP; ports B1–B2 Customer/Commercial; scorecard Prossimo; docs/stage; `wantsHtml` product shells `[sync:safe]`
- 1.0.45 → 1.0.46 — Appreso da sessione: node-pg-migrate numbering/checkOrder; no backfill sotto numero già run; remediazione rename + allinea `pgmigrations`; Railway boot = migrate critical path `[sync:safe]`
- 1.0.44 → 1.0.45 — Appreso da sessione: doppio flock gate; no Gate OK stale; port boundary source-level; `WTP_REPO_ROOT` temp+profile lib; Railway data-seed restore; mega mid-edit retry; «accetto»→Act; B# disambiguato con path/port `[sync:safe]`
- 1.0.43 → 1.0.44 — Appreso da sessione: Docker `env_file` → `--force-recreate`; OpenAPI sandbox hosts + OAuth mint vs Bearer; Risk smoke in-container `[sync:safe]`
- 1.0.42 → 1.0.43 — Layout: prodotto Company 360 (`src/company/`, `/company/`, `/api/company/*`); invarianti + catalogo `[sync:safe]`
- 1.0.41 → 1.0.42 — Appreso da sessione: diff-tab commit solo stage (+ push); rename-first 100% per taglio BC `[sync:safe]`
- 1.0.40 → 1.0.41 — Appreso da sessione: Explorer `explorerRoutes` shell-only; anti-circular `scripts/`↔`src/explorer` (modulo terziario per costanti) `[sync:safe]`
- 1.0.39 → 1.0.40 — Appreso da sessione: gate esclusivo multi-agente; no `pg_terminate` mid-suite; make/flock da root; isolamento prima del fix; progress solo con `MAKE_EXIT:0` `[sync:safe]`
- 1.0.38 → 1.0.39 — Appreso da sessione: Liste=consumatore scheda (SoT Customer 360 `/customer/<UID>`); redirect legacy `customer.html` OK; checklist deploy COPY+nginx; flake PG retry `[sync:safe]`
- 1.0.37 → 1.0.38 — Appreso da sessione: ladder BE ports/FCIS; enrichmentStore PG SoT; `resetPoolForTests`→`end()`; llmCompletionPort + quota ACL; Integrations perfCache/webhook FCIS; SPA version assert `[sync:safe]`
- 1.0.36 → 1.0.37 — Appreso da sessione: Auth ≠ Profile (no shim `/api/auth` settings); Profile test = preload BE; decoupling `*FromPg` no require Profile `[sync:safe]`
- 1.0.35 → 1.0.36 — Customer 360 deploy: Docker COPY `src/customer/`; nginx Railway proxy `/customer/` `/risk/` `/profile/`; layout L2 include customer `[sync:safe]`
- 1.0.34 → 1.0.35 — Docs: scheda SoT Customer 360 `/customer/`; temp LLM default **0.1**; note legacy `customer.html` `[sync:safe]`
- 1.0.33 → 1.0.34 — Appreso da sessione: scheda Liste SoT `customer.html` (≠ redirect `/customer/`); gate contract CSS SurferDark in test-unit auth `[sync:safe]`
- 1.0.32 → 1.0.33 — BC Profile (`src/profile/`): UI `/profile/`, API `/api/profile`, ACL PG `*FromPg`; test-unit include profile `[sync:safe]`
- 1.0.30 → 1.0.31 — Puntatore `docs/backend-decomposition.md` (mappa BE → microservizi, slice FCIS/ACL) `[sync:safe]`
- 1.0.29 → 1.0.30 — Appreso da sessione: view artefatti `/api/wtp/view/:jobId/:file` + unwrap envelope; FE no import CJS `shared/` (mirror ESM in `frontend/lib/`); cookie preview host-bound `[sync:safe]`
- 1.0.28 → 1.0.29 — `make verify-pg-vs-sqlite` + one-shot `migrate:sqlite-*` / config-seed; SQLite disco = archivio vs `DATABASE_URL` `[sync:safe]`
- 1.0.27 → 1.0.28 — Appreso da sessione: SurferDark (ex Enrico); Docker non mountare tutto `src/auth`; preview `127.0.0.1`; Input Liste = scaffold vanilla + payload Zod `[sync:safe]`
- 1.0.26 → 1.0.27 — Appreso: Postgres Docker = solo `wtp_test`; app SoT = Railway `DATABASE_URL`; `make migrate-app` vs `make migrate` `[sync:safe]`
- 1.0.25 → 1.0.26 — Appreso da sessione: Railway Postgres privato vs TCP pubblico + `uselibpqcompat`; Explorer `Cannot GET` = static miss; `WTP_REPO_ROOT=/app` in immagine `[sync:safe]`
- 1.0.24 → 1.0.25 — Frontend Liste: test glob `lib/*` + `js/*`; dead-code scan root `frontend/lib` (ex `frontend/src`) `[sync:safe]`
- 1.0.22 → 1.0.23 — Appreso da sessione: Enrico = chrome suite (anche Explorer B2B); `check-secrets` script deve essere tracked `[sync:safe]`

## [1.0.22] — 2026-09-12

### Changed

- Appreso da sessione: suite Sales Coach vs prodotti; product catalog SoT; SPA path unici; LLM orcarouter/temp 0.6 + usage history `[sync:safe]`

## [1.0.21] — 2026-09-12

### Added

- Appreso da sessione / steward: `make check-secrets` → `scripts/harness-secrets-scan.js` (low-noise, fuori ready-for-review) `[sync:safe]`

### Changed

- Active learnings compact ≤10 (A1–A10); Steward notes aggiornate su audits secrets `[sync:safe]`

## [1.0.20] — 2026-09-12

### Changed

- Appreso da sessione: audit trail sync selettivo (pre-ottim = padre; DevSecOps Make opzionale); fix newline Steward notes `[sync:safe]`

## [1.0.19] — 2026-09-12

### Changed

- Sync selettivo: `extends-version` 1.1.8 → 1.2.5 (`a-harness`: Spec Kit, semantic layer, workflow context, DevSecOps/SAST, pre-ottimizzazioni TDD) [sync:safe]
- Review 1.2.0: puntatore esplicito pre-ottimizzazioni RED/GREEN al padre; description snellita (no riesporre ciclo TDD) [sync:review]
- Nota L1 `consumer-platform-hygiene` DevSecOps opzionale non ancora wired in Make WTP [sync:safe]

## [1.0.18] — 2026-09-12

### Changed

- `check-cursor-whitelist` documentato con `git check-ignore --no-index`; registry `wtp-ux-ui` / `wtp-brand-voice` [sync:safe]

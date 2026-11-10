---
name: b2b-explorer-ui-ux
extends: a-copywriter
version: 1.0.33
extends-version: 1.7.5
description: >-
  Microcopy/UX e delta chrome per l’explorer Cluster B2B score3 (`/explorer/b2b/`):
  entrypoint, pattern STRATEGY_GUIDE; canone pattern guida/chrome → L1 `uiux` § Pattern guida, classi WTP → `wtp-ux-ui` § Explorer help & guide.
---

# B2B Explorer — UI/UX microcopy

Skill figlia di `a-copywriter`. Governa microcopy della dashboard score3 **e** delta chrome explorer; non usa `publication-types` JSON-first (newsletter/promo) né **5 Copy Blocks** / landing Pain→Promise→Proof (`references/five-copy-blocks.md` L1) — fuori scope di questa UI. Anti-AI guide → competenza **humanizer** L1. Copy Sales Coach (`.po`, prompt LLM) → `a-copywriter-wtp`. Token / menubar / shell SurferDark → `wtp-ux-ui` (non ridocumentare qui); pattern guida/chrome generici → L1 `uiux` § Pattern guida (non ridocumentare qui).

## Purpose

Rendere le guide e i testi della dashboard **più leggibili e operativi** per il team commerciale, senza perdere la semantica dei cluster (codici e clusterId rimangono invariati). Microcopy: canone L1 `a-copywriter` § Microcopy UI/dashboard. Chrome suite: pattern canone L1 `uiux` § Pattern guida, classi `wtp-ux-ui`.

## File entrypoint (invarianti)

Working directory: `/var/www/WTP_App`.

- **URL autenticato:** `/explorer/b2b/` (stessa sessione magic-link di Sales Coach).
- **Entry point ufficiale:** `src/explorer/b2b/b2b-score3-clusters.html` (template live; servito da `explorerRoutes`).
- **Dati live:** `GET /api/wtp/explorer/score3-clusters` — assemble da Postgres `enrichment.*` + acquisti Mongo (nessuna generazione intermedia obbligatoria).
- **Non SoT prodotto:** `b2b_explorer.html` (standalone gitignored, opzionale/legacy) e `.shared/b2b/viz/b2b-score3-clusters-data.json` (export batch opzionale via `cluster-b2b-score3.js`).
- Edit UI sul template; non serve rigenerare uno standalone per vedere i cluster in produzione/dev autenticato.
- Non ripristinare il nome legacy `b2b-score3-clusters-standalone.html`.

## Chrome suite (delta explorer)

SoT chrome/token/menubar/radius/focus: **`wtp-ux-ui`**. Qui solo override prodotto:

- **Implementazione:** template `b2b-score3-clusters.html` + `src/explorer/b2b/wtp-app-chrome.js` (wrap `/auth/js/chrome.js`); modello testabile `scripts/lib/b2bAppChromeModel.js` (`npm run test:app-chrome`).
- **Brand AppBar (LOCK):** `.appbar-brand` = **Sales Coach** (`ListsWtpTitle`); `.appbar-version` = semver UI. Non «Explorer B2B» / «Cluster» nello slot brand.
- **Meta dataset:** contatori / “generato…” sotto `</header>` (`#header-meta` / `.page-dataset-meta`), non dentro `.appbar-title`.
- **File:** `Stampa…` + `Esporta CSV` (utenti filtrati della tabella corrente).
- **Prodotti:** parity con `src/wtp/shared/wtpProductCatalog.js` (`listWtpProducts()`); non inventare href/label locali.
- **Preferiti:** `localStorage` key `wtp-b2b-explorer-favorites-v1` (vista: strategia / filtro / ricerca); **non** condividere IndexedDB Preferiti di Liste WTP.
- **i18n:** locale suite da `src/auth/locales/{it,en}.po` (serviti anche come `/auth/locales/`).
- **Destra AppBar:** email da `/api/auth/me` + link Profilo → `/wtp/`.
- **Layout denso:** tab secondarie **Panoramica | Grafici | Utenti**; KPI compatti; strategie a chip; un solo lavoro per tab. Click su barra/heatmap che applica filtro → apre tab Utenti.
- **Edit UI:** solo template (+ `wtp-app-chrome.js`) + regenerate (vedi entrypoint sopra).

## Principi (non negoziabili)

Canone L1 `a-copywriter` § Microcopy UI/dashboard. Delta explorer: **codici cluster invariati** (`1_playbook_b2b`, `decisore_light_hot`, …); HTML minimo (`<strong>`/`<em>` solo se serve).

## Pattern UI & copy

### Guide grafiche (CHART_HELP / template help)

Canone pattern in L1 `uiux` § «Pattern guida & chrome comuni (shell)» («come leggere» = 1 riga con interazione chiave; legenda = cosa rappresenta la vista + come si filtra). Qui vive solo il **contenuto** dei testi.

### Strategy guide (STRATEGY_GUIDE 1..8b)

- Ogni voce:
  - `purpose`: 1 frase chiara sul significato operativo della strategia
  - `howToRead`: 1 frase su cosa separa il grafico (assunti/lettura)
  - `commercialUse`: 1 frase su come usarla in pratica
  - `relatesTo`: 1 riga con relazioni in elenco breve (es. “2 canale · 4 timing · 7 priorità · 8a/8b script”)

## Empty state e guide collassabili

Canone pattern in L1 `uiux` § «Pattern guida & chrome comuni (shell)»; classi WTP in `wtp-ux-ui` § Explorer help & guide: `detail-hint` con azione «Clicca una riga…»; `<details>`/`<summary>` chiusi di default per la performance percepita. Qui contano solo le classi del template `b2b-score3-clusters.html`.

## Footer assunzioni

- Footer “Assunzioni & limiti” in 2 frasi:
  - cosa sono i dati (coorte live PG + Mongo) e come si leggono le 9 strategie parallele
  - regole di esclusione/aggregazione (es. `@moneysurfers.com`, oltre 15 isole → “altri”)
- In chiusura: puntare all’API `GET /api/wtp/explorer/score3-clusters` (non al comando batch standalone).

## Quick QA (per revisione copy)

L1 microcopy UI/dashboard. Qui: cluster codes invariati; `CHART_HELP` / `STRATEGY_GUIDE` dicono _cosa fare_ (click/filter).

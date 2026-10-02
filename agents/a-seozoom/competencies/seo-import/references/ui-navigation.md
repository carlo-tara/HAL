# SeoZoom UI — sznew.seozoom.it (Liberating.it)

Ricognizione UI per agente a-seozoom. Aggiornato: 2026-07-06.

## Login

| Step | URL / selettore |
|------|-----------------|
| Login page | `https://sznew.seozoom.it/login/` |
| Email | `input[placeholder="Email o Username"]` |
| Password | `input[placeholder="Password"]` |
| Submit | `button:has-text("ACCEDI")` (headed) o `LOGIN` (headless) |
| Cookie | `#CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll` / `Accetta tutti` |

## Progetto

| Campo | Valore Liberating.it |
|-------|----------------------|
| Nome UI | `Liberating.it` |
| Project ID (`pid`) | `167592` |
| Domain ID (`DomainID`) | `90098587` |
| URL progetto | `https://sznew.seozoom.it/project/view/167592` |

Variabili JS globali sulla pagina progetto: `pid`, `DomainID`, `projectUrl`, `mainDomain`, `competitor`.

## Export UI (fallback)

DevExtreme export client-side — **non affidabile in Playwright headless** (no evento download).

| Elemento | Selettore |
|----------|-----------|
| Trigger export tabella | `#exportStandardTable`, `.export-standard-table` |
| Modal | `#exportModal` |
| CSV | `#exportCsv` |
| XLSX | `#exportXlsx` |
| Export bulk Excel | `button:has-text("Esporta tutti i dati in Excel")` |

**Approccio preferito:** API POST con nonce da sessione browser.

## API autenticate (implementazione script)

Tutte le chiamate: `POST` con `FormData` + campo `nonce` (`window.csrf` o `$.ajaxSettings.data.nonce`).

| Report | Endpoint | Parametri chiave |
|--------|----------|------------------|
| Keyword monitorate | `/api/ajax/project/getmonitoredkeyfull` | `projectId`, `domainId` |
| Tutte le keyword | `/api/ajax/keyword/get-page-keywords` | `domainID`, `activeTab=all`, `args[skip]`, `args[take]` |
| OnPage SEO | `/project/view/seo/{pid}` (scrape grid DevExtreme) |
| Long tail | `/api/ajax/keyword/get-longtail-keywords` | `domainID`, `volumelimit[]`, `userLimit` |
| Content gap | `/api/ajax/domain/content-gap` | `domainID`, `competitor` (JSON string) |
| Content gap AI | stesso endpoint, filtro `intent=informational` lato script |
| Pagine principali | `/api/ajax/pages/getmainpages` | `iddominio` |
| Pagine potenziali | `/api/ajax/pages/getpotentialpages` | `iddominio` |
| Traffico su/giù | `/api/ajax/pages/growingpagesdash`, `decreasingpagedash` | `iddominio` |
| Cannibalizzazione | `/api/ajax/pages/cannibalization` | `iddominio`, `projectId` |
| Competitor | `/api/ajax/domain-vs-domain/competition` | `domainID`, `competitor` |
| Cluster | `/api/ajax/domain/getClustersResearch` | `domainID` |
| Cluster keyword | `/api/ajax/domain/getKeywordsClustersResearch` | `domainID` |
| FAQ / domande | `/api/ajax/domain/getFaq` | `domainID` |
| Keyword per URL | `/api/ajax/pages/getURLKeywords` | `iddominio`, `idurl` |

## API panoramica progetto (`/project/view/{pid}`)

Export in `seo/YYMMDD/seozoom/dashboard/`. Mapping completo: [dashboard-widgets.json](../../../references/dashboard-widgets.json).

| Widget | Endpoint / fonte | Parametri chiave |
|--------|------------------|------------------|
| Metriche (ZA/ZT/ZS/ZO) | `/api/ajax/project/domainstats` | `ProjectID`, `DomainID` |
| Andamento dominio / distribuzione / annuale | `/api/ajax/domain/get-chart-site-trend-data` | `domainID` |
| Backlink | `/api/ajax/links/counters` | `domainUrl` (= `mainDomain`) |
| Idee articoli | `/api/ajax/domain/suggest-articles` | `domainID` |
| Pagine competitor (suggerimenti) | `/api/ajax/copilot/suggestions` | `ProjectID` (filtro `COMPETITOR-PAGES`) |
| Trend competitor | `/api/ajax/project/competitorstats` | `ProjectID` |
| Posizionamento keyword monitorate | `/api/ajax/project/keywordsmetrics` | `ProjectID`, `url` |
| Andamento keyword progetto | `/api/ajax/project/keywordstrend` | `ProjectID` |
| Previsione traffico | JS globals (`seriesPrevisionData`, …) dopo warm dashboard | — |
| Keyword up/down (dashboard) | `/api/ajax/project/dashboardkeyup`, `dashboardkeydown` | `projectId` |

Ricognizione: `scripts/probe_dashboard_capture.py`.

## Percorsi UI (navigazione warm-up)

| Report | Path |
|--------|------|
| Rankings | `/project/view/rankings/{pid}` |
| Keyword studio (all) | `/project/view/keyword-studio/{pid}?tab=all` |
| Keyword studio (zero) | `/project/view/keyword-studio/{pid}?tab=zero` |
| Long tail | `/project/view/rankings/long-tail/{pid}` |
| Content gap | `/project/view/rankings/content-gap/{pid}` |
| Pagine | `/project/view/pages/overview-contents/{pid}?tab=page-N-tab` |
| Competitor | `/project/view/competitor/{pid}` |
| Cluster | `/project/view/rankings/clusters/{pid}` |
| Domande | `/project/view/rankings/questions/{pid}` |

## Mapping idurl

Costruito da `getmainpages`, `getpotentialpages` e righe `get-page-keywords` (campi `url`, `idurl`). URL normalizzati con trailing slash.

## Note operative

- Usare `wait_until=domcontentloaded` (non `networkidle`)
- Sessione Playwright in `.seozoom/session.json`
- Screenshot debug in `.seozoom/debug/` su retry falliti

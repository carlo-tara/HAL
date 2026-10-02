---
name: seo-import
kind: competency
version: 1.0.5
description: >-
  Import/export multi-fonte SEO (SeoZoom Playwright, GSC, GA4, GTM, GMC, Ads, CF):
  env, manifest, validazione, competitor project, troubleshooting. Solo L1 (no baseline L0).
---

# Competenza L1 — seo-import (a-seozoom)

Workflow e canoni per **import/export**. Gli script restano in `a-seozoom/scripts/` (path stabili).

**Asset operativi (non spostare):** [export-manifest.json](../../references/export-manifest.json), [dashboard-widgets.json](../../references/dashboard-widgets.json), [ui-selectors.json](../../references/ui-selectors.json).

---

## Quando applicare

Modalità Import / Export, refresh baseline, troubleshooting login/CAPTCHA/manifest, setup `SEOZOOM_PROJECT_COMPETITOR`.

---

## Prerequisiti

1. Python 3.10+ + Playwright (`scripts/requirements.txt`, `playwright install chromium`)
2. `.env` nel root progetto consumer (mai committare): `SEOZOOM_*`, `GOOGLE_*`, `GA4_*`, `GTM_*`, `GMC_*`, `GOOGLE_ADS_*`, `CLOUDFLARE_*` — dettaglio variabile in orchestratore `a-seozoom/SKILL.md`
3. `sitemap-enriched.json` per per-URL SeoZoom
4. `seo/export-manifest.json` nel consumer (fallback: asset HAL sopra)

---

## Comando import massivo

```bash
python3 agents/a-seozoom/scripts/seo_import_all.py \
  --project-root /path/to/project \
  --date $(date +%y%m%d) \
  --days 28
```

| Flag | Effetto |
|------|---------|
| `--force` | Sovrascrive cartella SeoZoom esistente |
| `--headed` | Browser visibile (login/CAPTCHA) |
| `--skip-seozoom` | Solo analytics |
| `--skip-gsc` / `--skip-ga4` / `--skip-gtm` / `--skip-gmc` / `--skip-google-ads` / `--skip-cf` | Salta fonte |
| `--skip-per-url` | Solo report globali SeoZoom |
| `--skip-dashboard` | Salta `seozoom/dashboard/` |
| `--skip-competitor-project` | Non esportare competitor anche se env settata |

Layout batch: `seo/YYMMDD/{seozoom,seozoom-competitor,google,cloudflare}/` + `import-report.md` / `export-report.json`.

---

## Export SeoZoom e competitor

```bash
python3 agents/a-seozoom/scripts/seozoom_export.py \
  --project-root /path/to/project \
  --date $(date +%y%m%d)
```

Se `SEOZOOM_PROJECT_COMPETITOR` valorizzata: stessa sessione → primary in `seozoom/` + competitor in `seozoom-competitor/` (globals + dashboard; per-URL competitor skip di default). Analisi comparativa: competenza `metriche-analisi`.

Analytics: `analytics_export_all.py` o script singoli (`gsc_export.py`, …).

### Cloudflare: export batch vs API live

| Uso | Cosa | Note |
|-----|------|------|
| **Batch** | `cf_analytics_export.py` → `seo/{YYMMDD}/cloudflare/cf_*.csv` | Path/status del **proprio** dominio; parte di `seo_import_all` |
| **Live multi-zona** | API Cloudflare GraphQL/Analytics (credenziali `CLOUDFLARE_*` in `.env`) | Confronto traffico reale vs **altri** domini/zone (requests, uniques, bandwidth, cache) quando l'utente lo chiede; non sostituisce i CSV batch |

Path account/zone e nomi competitor: skill L2. Non loggare token.

---

## Manifest e OK

Validazione:

```bash
python3 agents/a-seozoom/scripts/validate_export.py seo/YYMMDD/ --write-md
```

**OK** se file critici presenti e soglia CSV per-URL rispettata (adattabile in L2 / manifest progetto).

### FAILED ma usabile

Se `import-report` / `export-report` marca SeoZoom **FAILED** (es. `per_url_ok` sotto soglia, `missing-idurl`) ma i CSV **critici** del manifest e la **dashboard** metriche ci sono, il batch resta **usabile** per confronto, on-page e ricerca on-site. Non bloccare l’analisi solo sullo status FAILED. Elenca il gap (URL senza per-URL) e procedi.

**Contratto `import-report` (Batch usabile):** non forzare `ok=true`. Se `missing_critical=[]` e `dashboard_ok>0`, imposta `sources.seozoom.usable=true` (status MD: `FAILED (usable)`). `ok` e exit code core possono restare non-zero. Se `usable=true` e analytics critici (GSC/GA4) OK, il Batch SEO è **analizzabile** — procedi con delta/monitoring.

**GTM soft-fail:** se Tag Manager API è disabled (`accessNotConfigured` / 403) **oppure** `SEO_IMPORT_SOFT_GTM=1`, marca `sources.gtm` con `ok=true`, `soft_fail`/`skipped=true` e motivo — non far fallire hard il batch analytics. Preferire abilitare l’API in GCP quando serve export GTM reale.

### Retry export (timeout Playwright)

Se il primo passaggio `seozoom_export.py` / `seo_import_all.py` fallisce per timeout di navigazione (`Page.goto` o simile) ma `.env` e Playwright sono ok, **rilancia con `--force`** (stessa `--date` / `--project-root`) prima di dichiarare il batch inutilizzabile. Non ripetere all’infinito: dopo 1–2 retry, passa a `--headed` o export manuale.

### Batch misto competitor

Quando `SEOZOOM_PROJECT_COMPETITOR` è attiva:

1. Metriche e `keyword_all` (e file globals “core”) dal batch **latest** usabile
2. Se in `seozoom-competitor/` mancano ContentGap / grid / altri report (export error), usa l’ultimo batch **precedente completo** per quei file
3. Nel report cita **entrambe** le date `YYMMDD` (latest + donor)

File/path competitor specifici del sito restano in L2.

---

## Latest batch e manifest check

Esegui **sempre** all'avvio di task Analisi / Audit dati / piano editoriale basato su export (prima di citare numeri).

### Resolve latest batch

1. Elenca sottocartelle `seo/` che matchano `[0-9]{6}` (YYMMDD)
2. Ordina per intero **decrescente** → primo = **latest**
3. Se L2 indica file root persistenti (settings, log reindex), leggili insieme al batch
4. Se **latest** incompleto (manifest sotto): segnala gap; per metriche storiche usa l'ultimo batch **completo**

```bash
ls -d /path/to/project/seo/[0-9][0-9][0-9][0-9][0-9][0-9]/ 2>/dev/null | sort -r | head -1
```

### Manifest check

1. Confronta contenuto del batch vs `seo/export-manifest.json` (e checklist L2 tipo `seo/manifest-batch.md` se presente)
2. Elenca presenti / mancanti con impatto (niente numeri inventati sui file assenti)
3. Opzionale: `validate_export.py … --write-md` e leggi il report

Output minimo:

```markdown
## Manifest — seo/YYMMDD/
| File | Stato | Impatto se mancante |
|------|-------|---------------------|
| … | presente / mancante | … |
```

File attesi specifici del sito (nomi CSV brand, derivati newsletter): **solo in L2**.

---

## Architettura Playwright-only

- Login UI → progetto → API AJAX private (`sznew.seozoom.it`); mapping in [ui-navigation.md](references/ui-navigation.md)
- **Non** usare `SEOZOOM_API_KEY` / REST ufficiale come percorso primario per rankings/dashboard
- CSV per-URL: [url-to-filename.md](references/url-to-filename.md)
- Sessione: `.seozoom/session.json` (gitignored)

---

## Workflow import

```
Task Progress:
- [ ] 1. Verifica .env e Playwright
- [ ] 2. Carica skill L2 (path, skip fonti, soglie)
- [ ] 3. Esegui seo_import_all.py (o export singolo)
- [ ] 4. Leggi import-report.md / export-report.json
- [ ] 5. Se OK → passa a metriche-analisi / onpage / geo
- [ ] 6. Se MISSING → retry --headed o export manuale
```

---

## Troubleshooting

| Problema | Azione |
|----------|--------|
| Login fallito / CAPTCHA / 2FA | `--headed`, completa a mano |
| Sessione scaduta | Rimuovi `.seozoom/session.json` |
| API 401/400 | Ricarica progetto; verifica DomainID |
| Widget dashboard vuoto | Senza `--skip-dashboard`; aggiorna probe + dashboard-widgets |
| Export UI cambiato | Aggiorna ui-selectors / dashboard-widgets |
| Per-URL `missing-idurl` | URL assente da SeoZoom vs sitemap; vedi § FAILED ma usabile |
| Timeout `Page.goto` / export flaky | § Retry export (`--force`); poi `--headed` |
| Competitor ContentGap mancante | § Batch misto competitor |
| Google Ads token / permission | Centro API MCC; ometti LOGIN_CUSTOMER_ID se accesso diretto |
| GMC 403 | SA utente in Merchant Center + Merchant API GCP |

**Sicurezza:** non loggare password; non committare `.env` o `.seozoom/`.

---

## Override L2 tipici

Skip fonti, soglie manifest, `SEOZOOM_PROJECT` / `SEOZOOM_PROJECT_COMPETITOR`, path sitemap — in `.cursor/skills/seozoom-{progetto}/competencies/seo-import/SKILL.md` (solo delta).

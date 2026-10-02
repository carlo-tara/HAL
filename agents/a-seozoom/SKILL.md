---
name: a-seozoom
extends: a-agentzero
version: 1.9.0
model: orcarouter/deepseek/deepseek-v4-flash-free
model-fallback: cursor-default
extends-version: 1.6.15
competencies:
  - seo-import
  - metriche-analisi
  - onpage-seo
  - geo-citabilita
  - seo-audit
  - schema-markup
  - programmatic-seo
  - site-architecture
  - hreflang-i18n
  - topic-cluster
  - google-ads
description: >-
  Reason why: senza un filo unico tra dati, contenuti e Ads, SEO e GEO restano pezzi sparsi e poco utili.
  Agente SEO/GEO multi-progetto: orchestra import dati, analisi metriche, on-page, GEO/AEO,
  audit, schema, pSEO, IA, hreflang, topic-cluster e Google Ads (Search/PMax/Shopping).
  Usa proattivamente per SEO, GEO, SeoZoom, keyword, meta, Ads, menzioni AI, structured data.
---

# a-seozoom — SEO/GEO e import massivo

Orchestratore L1. Eredita da **a-agentzero**. Import, metriche, on-page, GEO e canoni distillati vivono nelle **competenze** (non duplicate qui). Script in `scripts/` (path stabili).

**Sorgente canonica:** HAL `a-seozoom/` (deploy via [deploy.sh](deploy.sh)).  
**Agente:** [agents/a-seozoom.md](agents/a-seozoom.md).  
**Brief:** [project-brief-template.md](project-brief-template.md).  
**Upstream:** [marketingskills-source.md](references/marketingskills-source.md) · [claude-seo-source.md](references/claude-seo-source.md) · [labat-seo-geo-aeo-source.md](references/labat-seo-geo-aeo-source.md) · [google-ads-agent-skills-source.md](references/google-ads-agent-skills-source.md)  
Update: `/update-marketing-repo` · `/update-claude-seo-repo` · `/update-labat-seo-geo-aeo-repo` · `/update-google-ads-agent-skills-repo`.

All'avvio: `a-agentzero` → **questo skill** → skill L2 se presente → per ogni id in `competencies:` risolvi L0→L1→L2 ([AGENT-PROTOCOL.md](../a-agentzero/AGENT-PROTOCOL.md) § Competenze). Le competenze SEO sono **solo L1** (nessuna baseline L0). Carica **solo** le competenze pertinenti al task.

---

## Competenze dichiarate

| Id | Path L1 | Ruolo |
|----|---------|-------|
| `seo-import` | [competencies/seo-import/](competencies/seo-import/SKILL.md) | Env, Playwright, import/export, manifest, troubleshooting |
| `metriche-analisi` | [competencies/metriche-analisi/](competencies/metriche-analisi/SKILL.md) | ZA/ZT/ZS/ZO, PagesWithPotential, competitor |
| `onpage-seo` | [competencies/onpage-seo/](competencies/onpage-seo/SKILL.md) | Title/meta/H1/FAQ, AEO surfaces corte; riuso `tono-di-voce` |
| `geo-citabilita` | [competencies/geo-citabilita/](competencies/geo-citabilita/SKILL.md) | GEO vs AEO, extractability, llms.txt evidence, ricerca on-site |
| `seo-audit` | [competencies/seo-audit/](competencies/seo-audit/SKILL.md) | Audit Quick/Full batch, Effort×Impact, drift |
| `schema-markup` | [competencies/schema-markup/](competencies/schema-markup/SKILL.md) | JSON-LD / rich results (retired ≠ vocabulary) |
| `programmatic-seo` | [competencies/programmatic-seo/](competencies/programmatic-seo/SKILL.md) | Pagine a scala template+dati |
| `site-architecture` | [competencies/site-architecture/](competencies/site-architecture/SKILL.md) | IA, URL, nav, link interni |
| `hreflang-i18n` | [competencies/hreflang-i18n/](competencies/hreflang-i18n/SKILL.md) | Multi-locale, parity, MT QA |
| `topic-cluster` | [competencies/topic-cluster/](competencies/topic-cluster/SKILL.md) | SERP-overlap + CSV SeoZoom → owner URL |
| `google-ads` | [competencies/google-ads/](competencies/google-ads/SKILL.md) | Search / PMax / Shopping: struttura, tracking, budget, feed |

---

## System 1 (Laya) Integration in SEO & GEO

Prima di impegnare System 2 in analisi semantiche complesse o audit estesi, l'agente `a-seozoom` utilizza **Laya (System 1)** per:
1. **Classificazione Intent Keyword (`router.py batch_routing`)**: Classifica in batch l'intento di ricerca delle keyword SeoZoom (`Transactional`, `Informational`, `Navigational`, `Commercial`) con latenza quasi nulla.
2. **Scoring del potenziale e Audit (`router.py batch_score`)**: Calcola in batch punteggi di priorità Effort×Impact per centinaia di URL o pagine con potenziale (`seo-audit`, `metriche-analisi`).
3. **Routing campagne Google Ads (`router.py routing`)**: Instrada rapidamente le metriche di inserzioni Search, PMax o Shopping verso le rispettive linee guida di ottimizzazione.

---

## Avvio dominio

1. **Skill figlia L2** — `extends: a-seozoom`; fallback legacy: `seo-*`, `seo-geo-*`
2. **Competenze** — carica L1 (e L2 override sotto `{figlio}/competencies/{id}/` se presenti) **pertinenti al task**
3. **Brief progetto** — path contenuti, sitemap, build (L2 o `project-brief-template.md`)
4. **`.env`** nel root progetto (mai committare)
5. **Playwright** per export SeoZoom

### Gerarchia in conflitto (SEO)

| Priorità | Fonte | Cosa governa |
|----------|-------|--------------|
| 1 | Override competenza L2 / skill figlia | Path, soglie, workflow locali |
| 2 | Brief / skill SEO correlate | Keyword policy, tono vs SEO |
| 3 | Competenze L1 + **questo orchestratore** | Canoni, script, checklist |
| 4 | **a-agentzero** | Protocollo, sicurezza |

Override rich-result Google: `claude-seo-source` + Search Central battono checklist Labat stale (FAQ/HowTo-as-SERP).

---

## Estensione di progetto

Scaffold: [extension-scaffold.md](../a-agentzero/references/extension-scaffold.md).  
Template: [extension-template.md](extension-template.md) (include `competencies/{id}/`).

Copia [references/export-manifest.json](references/export-manifest.json) nel consumer come `seo/export-manifest.json` se manca.

---

## Estensioni L2

Su progetti multi-skill SEO, preferisci **due figli sibling** sullo stesso L1 (non fondere data+editorial in un solo file):

| `role:` | Focus tipico | Esempi task |
|---------|--------------|-------------|
| `role: data` | Import, CSV, manifest, metriche, batch `seo/{YYMMDD}/` | `seo-import`, `metriche-analisi`, competitor |
| `role: editorial` | Title, meta, FAQ, CTA, publish checklist, on-page | `onpage-seo`, GEO surfaces corte |

Frontmatter L2: `role: data | editorial` (opz. `primary: true` su un solo figlio). Risoluzione task→role, primary, inferenza path/chat, altrimenti chiedi: [AGENT-PROTOCOL.md](../a-agentzero/AGENT-PROTOCOL.md) § **Multi-figlio**. I sibling non scelti restano in **Deleghe** (on-demand). Pattern validato su consumer GS / pirates / liberating; criterio scansione anche in [l2-generalization.md](../a-agentzero/sync/references/l2-generalization.md).

---

## Lettura selettiva

| Task | Competenza / file |
|------|-------------------|
| Import / export / troubleshooting / latest batch | `seo-import` |
| ZO/ZS/ZT/ZA, gap, cannibalizzazione | `metriche-analisi` + [metriche-seozoom.md](competencies/metriche-analisi/references/metriche-seozoom.md) |
| Cluster / SERP-overlap / owner URL | `topic-cluster` |
| Title/meta/FAQ / batch on-page (keyword ≠ copy) | `onpage-seo` (+ `tono-di-voce` se scrivi) |
| GEO vs AEO, llms.txt, citazioni AI, ricerca on-site | `geo-citabilita` |
| Health check / calo traffico / tecnico / drift | `seo-audit` |
| JSON-LD / rich results / retired types | `schema-markup` |
| Multi-locale / hreflang | `hreflang-i18n` |
| Landing a scala / directory / vs pages | `programmatic-seo` |
| Albero sito / URL / link interni | `site-architecture` |
| Campagne Ads / PMax / Shopping / ROI paid | `google-ads` |
| Corpo lungo / humanize / voce RSA | Delega **a-copywriter** |
| PageSpeed / CWV | Solo skill L2 |
| Refresh corpus upstream | `/update-marketing-repo` · `/update-claude-seo-repo` · `/update-labat-seo-geo-aeo-repo` · `/update-google-ads-agent-skills-repo` |

---

## Modalità operative

| Modalità | Competenza primaria |
|----------|---------------------|
| **Import** / **Export** | `seo-import` |
| **Analisi** | `metriche-analisi` |
| **Cluster** | `topic-cluster` |
| **Ottimizzazione** | `onpage-seo` (+ L2 path/build) |
| **GEO / AEO / ricerca on-site** | `geo-citabilita` |
| **Audit** | `seo-audit` |
| **Schema** | `schema-markup` |
| **i18n / hreflang** | `hreflang-i18n` |
| **pSEO** | `programmatic-seo` |
| **IA / struttura** | `site-architecture` |
| **Ads / paid** | `google-ads` |
| **PageSpeed** | L2 |

---

## Env (sintesi)

Dettaglio flag e layout batch: competenza `seo-import`. Variabili tipiche: `SEOZOOM_USER`, `SEOZOOM_PASSWORD`, `SEOZOOM_PROJECT`, `SEOZOOM_PROJECT_COMPETITOR` (opz.), `GOOGLE_APPLICATION_CREDENTIALS`, `GSC_SITE_URL`, `GA4_PROPERTY_ID`, `GTM_*`, `GMC_*`, `GOOGLE_ADS_*`, `CLOUDFLARE_*`.

**Auth:** GSC/GA4/GTM/GMC = service account; Google Ads = OAuth2 separato.

---

## Comando import (puntatore)

```bash
python3 agents/a-seozoom/scripts/seo_import_all.py \
  --project-root /path/to/project \
  --date $(date +%y%m%d) \
  --days 28
```

Flag, competitor, analytics, validazione, troubleshooting → [seo-import](competencies/seo-import/SKILL.md).

---

## Fonti dati

L'agente **non** usa API live in analisi: esegue import via script e legge `seo/{YYMMDD}/`. Ogni numero cita file + data batch.

| Fonte | Output tipico |
|-------|---------------|
| SeoZoom | `seozoom/*.csv`, `seozoom/dashboard/` |
| Competitor project | `seozoom-competitor/` (se env) |
| GSC/GA4/GTM/GMC/Ads | `google/` |
| Cloudflare | `cloudflare/` |
| Screaming Frog | Manuale `*_SEO-Spider.csv` |

Corpus upstream (canoni, non metriche progetto): `vendor/marketingskills/`, `vendor/claude-seo/`, `vendor/seo-geo-aeo-skill/` dopo clone/update.

---

## Perimetro

| Fai tu | Delega |
|--------|--------|
| Import/export, analisi CSV, priorità, cluster, hreflang | Copy lungo → **a-copywriter** |
| On-page title/meta/FAQ (con tono-di-voce) | Plugin/redirect → **a-wordpress** |
| GEO/AEO, audit, schema, pSEO, IA | |

---

## Checklist pre-consegna (SEO)

- [ ] Skill L2 caricata se presente
- [ ] Competenze pertinenti al task caricate (non tutte se solo import)
- [ ] Export più recente (cartella data più alta salvo indicazione)
- [ ] Ogni numero con fonte in `seo/`
- [ ] Non inventare volumi/posizioni
- [ ] Title/meta/FAQ: `onpage-seo` + `tono-di-voce` / L2 se scrittura
- [ ] Schema: non “assente” da solo curl se CMS JS; FAQ/HowTo ≠ leva SERP Google
- [ ] Checklist a-agentzero completata

---

## Apprendimento da sessione

`/learn ?` e `/learn !` da **a-agentzero**. Consolidamento in L2 o `seo/export-manifest.json` consumer, non qui.

---

## Riferimenti

| File | Contenuto |
|------|-----------|
| [competencies/seo-import/](competencies/seo-import/SKILL.md) | Import/export |
| [competencies/metriche-analisi/](competencies/metriche-analisi/SKILL.md) | Metriche / analisi |
| [competencies/onpage-seo/](competencies/onpage-seo/SKILL.md) | On-page + copy bridge |
| [competencies/geo-citabilita/](competencies/geo-citabilita/SKILL.md) | GEO / AEO / ricerca on-site |
| [competencies/seo-audit/](competencies/seo-audit/SKILL.md) | Audit |
| [competencies/schema-markup/](competencies/schema-markup/SKILL.md) | Schema |
| [competencies/programmatic-seo/](competencies/programmatic-seo/SKILL.md) | pSEO |
| [competencies/site-architecture/](competencies/site-architecture/SKILL.md) | IA sito |
| [competencies/hreflang-i18n/](competencies/hreflang-i18n/SKILL.md) | i18n / hreflang |
| [competencies/topic-cluster/](competencies/topic-cluster/SKILL.md) | Topic cluster |
| [references/marketingskills-source.md](references/marketingskills-source.md) | Pin marketingskills |
| [references/claude-seo-source.md](references/claude-seo-source.md) | Pin claude-seo |
| [references/labat-seo-geo-aeo-source.md](references/labat-seo-geo-aeo-source.md) | Pin Labat (no SPDX) |
| [references/export-manifest.json](references/export-manifest.json) | Asset script (fallback manifest) |
| [references/dashboard-widgets.json](references/dashboard-widgets.json) | Widget dashboard |
| [references/ui-selectors.json](references/ui-selectors.json) | Selettori UI |
| [project-brief-template.md](project-brief-template.md) | Brief |
| [extension-template.md](extension-template.md) | Template L2 |
| [agents/a-seozoom.md](agents/a-seozoom.md) | Subagent |

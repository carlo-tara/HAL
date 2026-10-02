---
name: seo-audit
kind: competency
version: 1.1.0
description: >-
  Audit SEO/GEO/AEO a priorità su batch SeoZoom/GSC: finding falsificabili,
  Effort×Impact, Quick/Full, drift batch-to-batch. Solo L1 (no baseline L0).
---

# Competenza L1 — seo-audit (a-seozoom)

Framework di diagnosi. Distillato da marketingskills `seo-audit` + claude-seo + metodologia Labat (riscritta).  
**Non** sostituisce `metriche-analisi` né `onpage-seo` (scrittura).

Pin: [marketingskills-source.md](../../references/marketingskills-source.md) · [claude-seo-source.md](../../references/claude-seo-source.md) · [labat-seo-geo-aeo-source.md](../../references/labat-seo-geo-aeo-source.md).

---

## Quando applicare

Audit sito/URL, “perché non ranka”, calo traffico, health check, review indexazione, confronto batch.  
pSEO → `programmatic-seo`. Markup → `schema-markup`. Citabilità → `geo-citabilita`. Multi-locale → `hreflang-i18n`. Cluster → `topic-cluster`.

---

## Scope

| | |
|--|--|
| **Quick** | Ultimo `seo/{YYMMDD}/` + campione; top finding |
| **Full** | Batch + Spider/GSC + checklist SEO/GEO/AEO + drift se possibile |

Conferma Quick/Full **solo** se scope ambiguo. Canone: [audit-framework.md](references/audit-framework.md). Drift: [drift-batch.md](references/drift-batch.md).

---

## Ordine di priorità

1. **Crawlability & indexation**
2. **Fondazioni tecniche** — HTTPS, mobile (CWV → **L2**)
3. **On-page** — title/meta/H1/intent (`onpage-seo` per scrittura)
4. **Qualità** — corpo lungo → **a-copywriter**
5. **GEO / AEO** — `geo-citabilita` (non FAQ/HowTo-as-SERP)
6. **Autorità / link** — no inventare DR/backlink

Ogni finding: evidenza + Effort + Impatto + falsificabilità + azione. Includere **What’s working**.

---

## Fonti dati

| Area | Fonte tipica |
|------|----------------|
| Rankings / opportunity | `seo/{YYMMDD}/seozoom/*.csv`, dashboard |
| Click/impression | `seo/{YYMMDD}/google/` GSC |
| Title/meta/H1/canonical/status | `*_SEO-Spider.csv` o crawl L2 |
| Bot / edge | `seo/{YYMMDD}/cloudflare/` |

Manca export recente → proponi **Import** (`seo-import`).

---

## Limitazioni

| Tema | Dove |
|------|------|
| PageSpeed / CWV | **Solo L2** |
| Plugin WP / redirect | **a-wordpress** |
| Copy lungo | **a-copywriter** |
| Score /10 obbligatorio, DOCX | Non L1 |
| Batch title/meta | `onpage-seo` + `metriche-analisi` |

---

## Output atteso

- Finding P1–P5 con Dimensione / Effort / Impatto / falsificabilità
- What’s working (evidenza)
- Citazione file/data batch
- “Non verificabile” dove manca strumento

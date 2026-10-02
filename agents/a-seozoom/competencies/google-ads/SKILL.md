---
name: google-ads
kind: competency
version: 1.1.2
description: >-
  Progetta e ottimizza campagne Google Ads (Search, Shopping/PMax): struttura,
  keyword, RSA (ruoli Pain/Promise/Proof), feed, tracking, budget; analisi ricorrente
  (CPA, spreco, anomalie, scenari budget). Distillato da agent-skills/google-ads +
  pattern ops pubblici. Solo L1 (no baseline L0). Usare per campaign pack, audit
  account, wasted spend, diagnostica CPA, anomaly check, forecast budget.
---

# Competenza L1 — google-ads (a-seozoom)

Canone operativo per **progettare, revisionare e analizzare** campagne paid Search + Shopping/PMax.
Distillato (criticato) da [itallstartedwithaidea/agent-skills](https://github.com/itallstartedwithaidea/agent-skills) `skills/google-ads/` (MIT).  
Metodi di **analisi ricorrente** (CPA / spreco / anomalie / scenari): [ops-analysis.md](references/ops-analysis.md) — ispirazione pubblica Ryze “6 most-used”, non vendor.

Pin corpus design: [google-ads-agent-skills-source.md](../../references/google-ads-agent-skills-source.md).

**Non** sostituisce `seo-import` (GMC/Ads export), `metriche-analisi` (gap organico) né **a-copywriter** (voce brand negli annunci).

## Non-goals

- **No** nuovo L1 `a-ads` — resta competenza guest sotto `a-seozoom` finché non ci sono ≥2 consumer che giustifichino lo split
- **Creatività / voce / lessico RSA** → **a-copywriter** (+ L2 brand); qui solo struttura, limiti, pin, refresh
- **SEO organico** (gap, on-page, topic) → `metriche-analisi` / `onpage-seo` / altre competenze seozoom — non questa
- **Outreach email/call draft** → `a-copywriter` (non enrichment angles come copy finale)

---

## Quando applicare

- Piano campagne, budget split, campaign pack
- RSA / keyword / negative / Quality Score
- PMax asset group, URL expansion, brand exclusions
- Feed Shopping / custom labels (con L2 GMC)
- Audit account o pre-launch checklist
- ROI / forecast presentabile al titolare (stime etichettate)
- **Post go-live:** anomaly check, CPA diagnostic, wasted spend, scenari budget, narrative stakeholder

Non applicare su puro SEO organico senza paid — resta `metriche-analisi` / `onpage-seo`.

---

## Ordine obbligatorio

```
Task Progress:
- [ ] 1. Tracking — purchase (o conversione primaria) verificata; Enhanced Conversions se possibile
- [ ] 2. Offer / landing — URL canoniche, message match, noindex/redirect OK
- [ ] 3. Feed (se Shopping/PMax) — disapprovals MC, labels, disponibilità
- [ ] 4. Struttura — campagne per intent; Brand Search solo se necessaria
- [ ] 5. Creative — RSA / asset PMax; tono → a-copywriter
- [ ] 6. Budget / bid — learning phase; shift ≤20–30% per volta
- [ ] 7. Deliverable file — pack + checklist (non solo chat)
- [ ] 8. Ops post-launch — cadenza in ops-analysis.md (anomaly → CPA on-trigger → wasted mensile)
```

Dettaglio: [tracking-budget.md](references/tracking-budget.md) · [campaign-design.md](references/campaign-design.md) · [pmax-shopping.md](references/pmax-shopping.md) · [ops-analysis.md](references/ops-analysis.md).

---

## Fonti dati

| Area | Fonte tipica |
|------|----------------|
| Keyword / intent organico | `seo/{YYMMDD}/seozoom/`, GSC `google/` |
| Prodotti / issue MC | `google/gmc_*.csv`, L2 feed-spec |
| Ads spend / search terms | Ads UI o export quando token OK (`GOOGLE_ADS_*`) |
| Ticket / AOV | report shop L2 o brief — **non inventare** |

Manca tracking o feed rosso → **stop spend** finché non risolto (L2 + `seo-import`).  
Analisi: solo dati forniti/export; se manca una metrica, **dichiaralo** (no stime silenziose).

---

## Deliverable tipici

| Artefatto | Contenuto |
|-----------|-----------|
| Campaign pack | Budget, campagne, AG, keyword, asset, negative |
| Tracking checklist | Gate pre-launch |
| ROI one-pager | Scenari + probabilità **etichettati stima** (per titolare) |
| Week-N / fase playbook | Search Terms, asset Low, ridistribuzione |
| Wasted-spend pack | Summary temi € + negative upload-ready |
| CPA diagnostic | Driver ranked by € impact + top 3 fix |

Path concreti = **L2** (es. `seo/google-ads-*/`).

---

## Deleghe

| Tema | Dove |
|------|------|
| Voce / lessico RSA | **a-copywriter** (+ L2 brand) |
| Plugin GMC / WP-CLI deploy | **a-wordpress** / L2 |
| Import GMC/Ads CSV | `seo-import` |
| Gap keyword organico | `metriche-analisi` |
| CWV / PageSpeed LP | Solo L2 |
| Remarketing Display/YouTube | Fase 2 — richiesta esplicita |
| Meta frequency / audience overlap | Fuori scope (Google-first); stessi principi in ops-analysis se chiesto |

---

## Limitazioni

- Niente Buddy™ / API SaaS upstream / write automatico su account Ads senza richiesta
- Niente numeri di performance inventati
- Niente Brand Search di default se organico già pos. 1 stabile
- Learning PMax: evitare rifacimenti strutturali nelle prime 2–4 settimane salvo spreco evidente
- Un job di analisi per run (no mega-prompt “fai tutto”)

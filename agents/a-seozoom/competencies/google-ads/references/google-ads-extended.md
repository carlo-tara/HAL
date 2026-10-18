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

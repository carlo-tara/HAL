---
name: programmatic-seo
kind: competency
version: 1.0.0
description: >-
  pSEO: pagine a scala da template+dati, playbook, anti-thin, hub-spoke, indexation.
  Domanda da export SeoZoom/GSC — no volumi inventati. Solo L1 (no baseline L0).
---

# Competenza L1 — programmatic-seo (a-seozoom)

Pagine SEO programmatiche. Distillato da upstream `marketingskills/skills/programmatic-seo` (MIT).  
Pin: [marketingskills-source.md](../../references/marketingskills-source.md).

---

## Quando applicare

Directory, location, comparison, integration, glossary, template pages a scala; “genera N landing keyword”. Audit post-launch → `seo-audit`. Schema template → `schema-markup`. IA hub → `site-architecture`.

---

## Principi

1. **Valore unico per pagina** — non solo variabili scambiate
2. **Dati difendibili** — proprietari > product-derived > UGC > licensed > public
3. **URL in subfolder** del dominio (non subdomain che spezza autorità) salvo vincolo L2
4. **Intent reale** — ogni URL risponde a una query verificata
5. **Qualità > quantità** — meglio 100 pagine utili che 10k thin
6. **No doorway / stuffing / duplicate** — rischio scaled content abuse

Volumi e competitor SERP: solo da `seo/{YYMMDD}/` o strumenti citati. Se manca dato → Import o “non stimabile”.

---

## Playbook (overview)

| Playbook | Pattern |
|----------|---------|
| Templates | `[type] template` |
| Curation | `best [category]` |
| Conversions | `[X] to [Y]` |
| Comparisons | `[X] vs [Y]` |
| Examples | `[type] examples` |
| Locations | `[service] in [location]` |
| Personas | `[product] for [audience]` |
| Integrations | `[A] [B] integration` |
| Glossary | `what is [term]` |
| Directory | `[category] tools` |
| Profiles | `[entity]` |

Dettaglio implementazione: [playbooks.md](references/playbooks.md). Upstream esteso: `vendor/marketingskills/skills/programmatic-seo/references/playbooks.md`.

---

## Framework implementazione

1. **Pattern keyword** — variabili, cardinalità, distribuzione volume (CSV)
2. **Dati** — fonte, refresh, ownership
3. **Template** — intro unica, sezioni data-driven, CTA intent-match, H1/title unici
4. **Linking** — hub-spoke, no orphan; breadcrumbs + schema
5. **Indexation** — sitemap dedicata per tipo; noindex varianti senza domanda; crawl budget

Cannibalizzazione: una keyword driver primaria per URL (sanity `onpage-seo` / `metriche-analisi`).

---

## Checklist pre-launch

- [ ] Valore unico verificabile per campione pagine
- [ ] Title/meta/H1 unici; schema dove eleggibile
- [ ] In sitemap e raggiungibili da hub
- [ ] Domanda aggregata citata da export (o esplicitamente non disponibile)
- [ ] Copy template: `tono-di-voce` se testo pubblicato; corpo lungo → **a-copywriter**

---

## Output atteso

- Strategy: playbook scelto, stima cardinalità, fonti dati
- Spec template: URL, title/meta pattern, outline, schema
- Piano indexation + monitoraggio post-launch (GSC coverage, ranking CSV)

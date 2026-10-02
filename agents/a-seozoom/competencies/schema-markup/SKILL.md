---
name: schema-markup
kind: competency
version: 1.1.0
description: >-
  Structured data JSON-LD (schema.org): tipi comuni, @graph, validazione rich results.
  Accuratezza vs contenuto visibile; detection ≠ curl; retired ≠ vocabulary. Solo L1.
---

# Competenza L1 — schema-markup (a-seozoom)

Canone structured data. Distillato da marketingskills `schema` + claude-seo `seo-schema` (MIT).  
Pin: [marketingskills-source.md](../../references/marketingskills-source.md) · [claude-seo-source.md](../../references/claude-seo-source.md).

---

## Quando applicare

Aggiungere/fixare/ottimizzare JSON-LD, rich snippet, Product/Article/Breadcrumb/Organization, Knowledge Panel signal. Audit ampio → `seo-audit`. Citabilità AI → anche `geo-citabilita` (schema aiuta extractability, non la sostituisce).

---

## Principi

1. **Accuratezza** — markup = contenuto visibile; niente review/price inventati
2. **JSON-LD** — preferito; in `<head>` o fine `<body>`; SSR su SPA
3. **Solo tipi con rich result Google mirato** quando l’obiettivo è SERP — vedi [deprecated-rich-results.md](references/deprecated-rich-results.md)
4. **Validare** prima del deploy (Rich Results Test / schema.org validator / GSC enhancements)
5. **Override Labat:** non spingere FAQPage/HowTo/ClaimReview/Speakable come leve AEO Google

Esempi tipi: [schema-types.md](references/schema-types.md).  
Esempi JSON upstream (on-demand): `vendor/marketingskills/skills/schema/references/schema-examples.md`.

---

## Tipi più usati (leva tipica)

| Type | Contesto | Minimo tipico | Note SERP |
|------|----------|---------------|-----------|
| Organization | Home / about | name, url (+ logo, sameAs) | Entity |
| WebSite | Home | name, url | |
| Article / BlogPosting | Editorial | headline, image, datePublished, author | |
| Product | PDP | name, image, offers | |
| BreadcrumbList | Trail nav | itemListElement | |
| SoftwareApplication | SaaS | name, offers | |
| FAQPage / HowTo | FAQ / tutorial | — | **No** rich result Google — vedi deprecated |

Combinare con `@graph` sulla stessa pagina.

---

## Detection (anti falso negativo)

CMS (Yoast, Rank Math, AIOSEO) spesso iniettano schema via JS. **Non** concludere “no schema” da solo fetch statico. Verifica: browser DOM, Rich Results Test, Spider JS-rendered.

---

## Implementazione per stack

| Stack | Approccio |
|-------|-----------|
| Static / SSG | Partial/include JSON-LD nei template |
| React/Next | Componente SSR che serializza JSON-LD |
| WordPress | Plugin o theme — path/plugin policy → **a-wordpress** + L2 |

pSEO a scala: template schema per playbook → `programmatic-seo` + questa competenza.

---

## Output atteso

- Blocco JSON-LD completo e valido (tipi ancora supportati per l’obiettivo)
- Checklist: match contenuto, required props, test tools, retired check
- Nota se schema esistente va sostituito o merged in `@graph`

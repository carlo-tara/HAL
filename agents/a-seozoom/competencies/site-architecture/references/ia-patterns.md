# IA patterns — sintesi

Distillato da marketingskills `site-architecture`. Dettaglio tipi sito / Mermaid: vendor upstream.

## Tipi sito (profondità tipica)

| Tipo | Depth | URL tipici |
|------|-------|------------|
| SaaS marketing | 2–3 | `/features/name`, `/blog/slug` |
| Content/blog | 2–3 | `/blog/slug`, `/category/slug` |
| E-commerce | 3–4 | `/category/sub/product` |
| Docs | 3–4 | `/docs/section/page` |
| Hybrid SaaS+content | 3–4 | product + resources + docs |
| Small business | 1–2 | `/services/name` |

## Albero ASCII (formato)

```
Homepage (/)
├── Features (/features)
│   ├── Analytics (/features/analytics)
│   └── Automation (/features/automation)
├── Pricing (/pricing)
├── Blog (/blog)
└── Contact (/contact)
```

## URL

- Preferire subfolder a subdomain per sezioni SEO-critical
- Una convenzione trailing-slash; coerente con canonical
- Evitare stop-word inutili; keyword solo se naturali
- Parametri: canonicalizzare o noindex secondo `seo-audit`

## Breadcrumb

Allineati all’albero URL; segmenti cliccabili tranne current. Markup → `schema-markup`.

## Nav anti-pattern

- Mega-menu con 20+ link non raggruppati
- Pagine money solo in footer
- Blog isolato senza hub tematici verso product
- pSEO spoke senza hub di categoria

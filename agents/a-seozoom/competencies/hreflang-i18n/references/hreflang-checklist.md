# Hreflang checklist (lean)

Distillato da claude-seo `seo-hreflang` + `content-parity.md` (MIT). Pin: [claude-seo-source.md](../../../references/claude-seo-source.md).

## Cluster validity

| Check | Fail tipico |
|-------|-------------|
| Self-ref | Manca hreflang verso sé / URL ≠ canonical |
| Reciprocità | A→B senza B→A |
| x-default | Assente con selector; oppure multipli |
| Codice | `en-UK`, `jp`, regione senza lingua, `es-LA` |
| Target | 4xx/5xx, redirect, noindex, non-canonical |
| Conflitto | HTML vs sitemap discordanti |
| Canonical cross-locale | Tutte le lingue → una sola URL |

## URL pattern

Preferire `/it/…`, `/en/…` (o ccTLD). Evitare query `?lang=` / `?locale=`.

## Parity (sample)

| Dimensione | Severity gap |
|------------|--------------|
| Pagina assente in una lingua dichiarata | Alto |
| Title/meta non localizzati | Alto |
| Schema tipo diverso / assente | Alto (tipi supportati) |
| Sezioni H2 ±1 ok; gap maggiori | Medio |
| Traduzione stale vs source (>30g tipico) | Medio–Alto |
| Valuta/unità/giurisdizione sbagliate | Alto |

## MT QA (machine translation)

Segnali di MT grezza: mix lingua in nav/CTA, brand US-only su locale IT, statistiche “americans” su `/it/`, termini non tradotti in schema. Copy fix → **a-copywriter**.

## Fonti dati AF

Spider hreflang columns, HTML `link[rel=alternate]`, sitemap alternate, GSC international (se ancora esposto), brief L2 elenco locale.

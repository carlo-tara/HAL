# Audit framework (canone L1)

Distillato da marketingskills `seo-audit` + claude-seo (falsificabilità) + metodologia Labat (Effort×Impact, Quick/Full, what’s working) riscritta per batch AF.  
Pin: [marketingskills-source.md](../../../references/marketingskills-source.md) · [claude-seo-source.md](../../../references/claude-seo-source.md) · [labat-seo-geo-aeo-source.md](../../../references/labat-seo-geo-aeo-source.md).

## Scope Quick vs Full

Chiedere **solo** se l’utente non ha già chiarito lo scope.

| Scope | Copertura AF |
|-------|----------------|
| **Quick** | Ultimo batch `seo/{YYMMDD}/` + campione on-page / home; top priorità |
| **Full** | Batch + Spider/GSC coverage + checklist SEO/GEO/AEO (`geo-citabilita`) + drift se ≥2 batch |

Non crawl illimitato come path primario. Se manca export: proponi `seo-import`.

## Finding format

```
[P1–P5] Titolo breve
Dimensione: SEO | GEO | AEO
Evidenza: path file o URL + data batch (o fetch se audit URL-only)
Effort: basso|medio|alto
Impatto: alto|medio|basso (numeri solo se in seo/)
Dipendenze: cosa deve essere vero prima
Falsificabilità: come sappiamo che l’azione ha fallito / leading indicator
Azione: 1 step concreto
```

Score 1–10 **non** obbligatorio. Status qualitativo (Needs Work / On Track / Strong) ok. Ogni metrica cita `seo/`.

## Deliverable minimo

1. Finding ordinati (matrice priorità)
2. **What’s working** — almeno 2–3 punti con evidenza (non solo gap)
3. Explicit “non verificabile” se manca strumento (CWV, schema senza browser, backlink)

## Principio whole-export

Non raccomandare “crea Team / FAQ / Case study” senza aver cercato in sitemap, Spider, nav export o batch. Se esiste altrove, valuta qualità SEO di quella URL.

## Crawlability

- robots.txt: nessun block involontario su sezioni money; sitemap referenziata
- XML sitemap: 200, solo canonical indexabili, aggiornato, formato valido
- Architettura: pagine chiave ≤ 3 click; orphan → `site-architecture`
- Crawl budget (siti grandi): parametri, faceted, infinite scroll senza pagination, session ID in URL

## Indexation

- Indexed vs atteso (GSC coverage / Spider status)
- noindex su URL strategici; soft 404; redirect chain/loop
- Canonical: self su unici; HTTPS/www/slash coerenti; niente canonical cross-locale

## On-page (diagnosi, non scrittura)

- Title unici, keyword driver sanity (`onpage-seo`)
- Meta dove CTR basso (GSC)
- Un H1; heading allineati a intent
- Intent mismatch = finding, non “aggiungi keyword”
- Immagini: alt mancanti / LCP candidate ovvio (dettaglio corto in `onpage-seo`)

## Internazionale (trigger)

Multi-locale → competenza `hreflang-i18n` (checklist completa). Sintesi errori tipici: self-ref, reciprocità, codice locale, target non-200, conflitto HTML vs sitemap, canonical cross-locale. Preferire `/it/`, `/en/`; evitare `?lang=`.

## Schema detection

| Metodo | Affidabile? |
|--------|-------------|
| `curl` / static fetch senza JS | No |
| Browser `script[type="application/ld+json"]` | Sì |
| Google Rich Results Test | Sì |
| Screaming Frog JS-rendered | Sì |

Retired types: `schema-markup` / [deprecated-rich-results](../../schema-markup/references/deprecated-rich-results.md) — non trattare assenza FAQ/HowTo rich result come P1.

## Drift

Confronto batch: [drift-batch.md](drift-batch.md).

## Cosa non fare

- Inventare traffico/posizioni senza GSC/GA4/SeoZoom in `seo/`
- Dichiarare CWV fail senza misurazione L2
- Audit “completo” senza export recente se il progetto ha pipeline import
- Score /10 o DOCX agency come deliverable obbligatorio
- Spingere FAQ/HowTo schema come leva Google

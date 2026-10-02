# Schema types — riferimento rapido

Proprietà minime orientative. Per eligibility rich result consulta documentazione Google aggiornata e [deprecated-rich-results.md](deprecated-rich-results.md).  
Esempi lunghi: upstream `schema/references/schema-examples.md` (marketingskills).

## Organization

Required-ish: `name`, `url`  
Consigliati: `logo`, `sameAs`, `contactPoint`

## WebSite

`name`, `url` — opzionale `potentialAction` SearchAction solo se search on-site reale.

## Article / BlogPosting

`headline`, `image`, `datePublished`, `author`  
Consigliati: `dateModified`, `publisher`, `description`

## Product

`name`, `image`, `offers` (price + availability + `priceCurrency`)  
Consigliati: `sku`, `brand`, `aggregateRating` **solo se** recensioni reali sulla pagina

## BreadcrumbList

`itemListElement`: `ListItem` con `position`, `name`, `item` (URL assoluti)

## FAQPage / HowTo

Vocabulary ancora valida; **non** leva rich result Google (vedi deprecated-rich-results).  
FAQ/HowTo on-page restano utili a chiarezza e citabilità non-Google; JSON-LD FAQ solo se esplicitamente richiesto senza claim SERP. Q&A utente reale → preferire `QAPage`.

## @graph

```json
{
  "@context": "https://schema.org",
  "@graph": [
    { "@type": "Organization", "name": "…", "url": "https://…" },
    { "@type": "BreadcrumbList", "itemListElement": [] }
  ]
}
```

## Errori comuni

- Date non ISO 8601
- URL relativi dove servono assoluti
- Markup di contenuto assente (spam risk)
- FAQ schema senza FAQ on-page
- AggregateRating inventato
- Raccomandare FAQPage/HowTo “per snippet Google”

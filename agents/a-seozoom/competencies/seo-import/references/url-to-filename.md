# Regola URL → nome file CSV SeoZoom

Convenzione usata in `seo/` dei progetti consumer e dagli script a-seozoom.

## Per-URL (`*__all_keywords.csv`)

```
https://example.it/blog/articolo/
  → https___example.it_blog_articolo__all_keywords.csv

https://example.it/
  → https___example.it__all_keywords.csv

https://example.it/categoria/prodotto/
  → https___example.it_categoria_prodotto__all_keywords.csv
```

**Algoritmo:**

1. Parti dall'URL completo con trailing slash (es. `https://example.it/blog/articolo/`)
2. Sostituisci `https://` con `https___`
3. Sostituisci ogni `/` con `_`
4. Rimuovi lo slash finale (ultimo `_` se presente dopo il dominio)
5. Aggiungi suffisso `__all_keywords.csv`

Implementazione in Python: `seozoom_lib.url_to_filename(url)` o `url_list.py`.

## File globali

I report globali hanno nomi fissi nel manifest (`seo/export-manifest.json` del progetto), indipendenti dall'URL. SeoZoom può scaricarli con nomi diversi; lo script li rinomina al nome canonico.

## Deduplicazione

Se SeoZoom genera `ContentGap (1).csv`, tieni solo il file senza suffisso numerico e elimina i duplicati.

# SERP overlap (lean)

Distillato da `vendor/claude-seo/skills/seo-cluster/references/serp-overlap-methodology.md` (MIT).  
Pin: [claude-seo-source.md](../../../references/claude-seo-source.md). Preferire sempre CSV SeoZoom prima di SERP live.

## Soglie overlap (top-10 organic URL normalizzati)

| Shared URLs | Relazione | Azione |
|-------------|-----------|--------|
| 7–10 | Same post | Una pagina; primary = volume più alto in `seo/` |
| 4–6 | Same cluster | Spoke adiacenti; 1 o 2 URL a seconda volume/intent |
| 2–3 | Interlink | Cluster vicini; link interni cross |
| 0–1 | Separate | Cluster distinti o fuori topic |

Tiebreak 3–4: stesso dominio vs pagine diverse, stesso intent, ratio volume (10× → pagina dedicata). In dubbio: stesso cluster, post separati.

## Ottimizzazione fetch

Pre-group per intent + head term; confronta SERP solo dentro i gruppi; spot-check 20% delle skip.  
Long-tail stesso head + stesso intent → assumere 4–6 senza fetch.

## AF wiring

| Input | Uso |
|-------|-----|
| `clusters_keyword.csv` / `keywords_cluster.csv` | Cluster seed SeoZoom |
| Cannibalizzazione | Owner URL unico per keyword |
| GSC queries×pages | Conferma intent/URL |
| WebSearch | Solo su richiesta / batch assente |

Volumi/posizioni: solo da file `seo/{YYMMDD}/`. Hub-spoke implementativo → `site-architecture` / `programmatic-seo`.

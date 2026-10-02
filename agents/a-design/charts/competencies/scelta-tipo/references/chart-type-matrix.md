# Matrice intent → tipo

Scelta default per **a-charts**. In dubbio: preferisci barre o linee; evita pie e dual-Y.

| Intent | Domanda tipica | Default | Alternativa | Evita |
|--------|----------------|---------|-------------|-------|
| Confronto categorie | Quale è più grande? | Barre verticali | Barre orizzontali (label lunghe) | Pie, radar |
| Ranking | Ordine dal migliore | Barre ordinate | Lollipop | Pie non ordinate |
| Trend nel tempo | Come cambia? | Linee | Aree (1–2 serie); barre se ≤8 punti discreti | Pie per anno |
| Composizione semplice | Quanto pesa ciascuna parte? (≤5) | Barre stacked o share bars | Pie/donut ≤5 | Pie >5 |
| Composizione nel tempo | Mix che evolve | 100% stacked bar/area | Small multiples per parte | Pie animate |
| Correlazione | X spiega Y? | Scatter | Scatter + trend | Linee false su categorie |
| Distribuzione | Forma / outlier | Histogram / box | Beeswarm (n piccolo) | Barre su bin mal scelti |
| Flusso / conversioni | Quanti passano lo step? | Funnel a barre | Sankey (flussi multipli; `d3-sankey` on-demand) | Pie a cascata |
| KPI singolo | Valore + delta | Numero grande ± sparkline | Bullet chart | Chart ornamentale |
| Precisione | Serve il numero esatto | Tabella | Tabella + conditional format | Chart decorativo |

---

## Heuristic rapide

- **Label lunghe** → barre orizzontali
- **>1 serie temporali** → linee multi-serie (max ~4–5) o small multiples
- **Due unità diverse** → due grafici affiancati, non dual-Y (salvo richiesta esplicita)
- **Prima/dopo o A/B** → barre affiancate o slope chart (pochi punti)
- **Mappa geografica** solo se la posizione geografica è il messaggio; altrimenti barre per regione

---

## Tipologiche avanzate (on-demand, non default)

Usare solo se il brief lo richiede esplicitamente. Implementazione D3: [d3-advanced.md](../../implementazione/references/d3-advanced.md).

| Intent | Quando ha senso | Default se in dubbio |
|--------|-----------------|----------------------|
| Gerarchia strutturale | Tree / cluster | Tabella indentata o barre per livello |
| Composizione gerarchica (area) | Treemap | Barre stacked / tabella share |
| Gerarchia radiale | Sunburst (debole per precisione) | Treemap o barre |
| Flussi bilaterali pochi nodi | Chord | Heatmap matrice o Sankey |
| Rete non gerarchica | Force-directed | Matrice di adiacenza / tabella |
| Geo come messaggio | Choropleth / geo path | Barre per regione |

Non promuovere pie/chord/sunburst da catalogo API: restano soggetti agli anti-pattern dell'orchestratore.

---

## Quando non fare un grafico

- Una sola cifra senza confronto → KPI testuale
- Audience chiede export numerico → tabella
- Dati incompleti / non confrontabili → dichiara limite; non “riempire” il vuoto

# Tipologiche D3 avanzate (on-demand)

Catalogo **opzionale**: usare solo se `scelta-tipo` / il brief richiedono esplicitamente gerarchie, reti, flussi circolari o geo. Non entrano nei default della [chart-type-matrix.md](../../scelta-tipo/references/chart-type-matrix.md).

Playbook base: [d3-cookbook.md](d3-cookbook.md). Colori: [d3-colour.md](d3-colour.md).

---

## Gate di ingresso

Prima di implementare:

1. La **ione geografica / gerarchia / rete **è** il messaggio? Altrimenti → barre / tabella.  
2. n nodi/link gestibile (<~200 DOM tipico; oltre → aggrega o canvas).  
3. Etichette leggibili senza hover obbligatorio per il messaggio primario.  
4. Nessun chord/sunburst “per effetto wow”.

---

## Tree / hierarchy

**Quando:** organigramma, decision tree, sitemap con profondità come messaggio.

```javascript
const root = d3.hierarchy(data);
d3.tree().size([innerH, innerW - 160])(root);

g.selectAll('path')
  .data(root.links())
  .join('path')
  .attr('d', d3.linkHorizontal().x(d => d.y).y(d => d.x))
  .attr('fill', 'none')
  .attr('stroke', 'currentColor')
  .attr('stroke-opacity', 0.4);

const node = g.selectAll('g.node')
  .data(root.descendants())
  .join('g')
  .attr('transform', d => `translate(${d.y},${d.x})`);
```

Alternativa layout: `d3.cluster`. Preferisci etichette testo a sole icone.

---

## Treemap

**Quando:** composizione gerarchica con area ≈ valore e confronto grezzo tra foglie. **Non** per confronti precisi (area < lunghezza).

```javascript
const root = d3.hierarchy(data)
  .sum(d => d.value)
  .sort((a, b) => b.value - a.value);

d3.treemap().size([innerW, innerH]).padding(2).round(true)(root);

const leaf = g.selectAll('g')
  .data(root.leaves())
  .join('g')
  .attr('transform', d => `translate(${d.x0},${d.y0})`);

leaf.append('rect')
  .attr('width', d => d.x1 - d.x0)
  .attr('height', d => d.y1 - d.y0)
  .attr('fill', d => colour(d.parent.data.name));
```

Caption: “area proporzionale a …”. Se serve precisione → tabella o barre.

---

## Sunburst / partition

**Quando:** gerarchia radiale e il brief lo chiede. Stesso caveat dell’area/angolo: debole per confronti precisi. Preferisci treemap o barre stacked se il messaggio è “quanto pesa”.

API: `d3.partition` + `d3.arc` su angolo × raggio.

---

## Chord

**Quando:** flussi bilaterali tra poche entità (matrice squaring). Spesso **illeggibile** oltre ~8–10 nodi → Sankey o heatmap matrice.

Richiede matrice `n×n` da edge list; etichette fuori dall’arco.

---

## Sankey (dipendenza esterna `d3-sankey`)

**Quando:** flussi multipli source→target con ampiezza ≈ valore (matrice: alternativa al funnel). **Non** è nel bundle `d3` core — richiede pacchetto `d3-sankey` (accordo dipendenza come da `output-targets`).

```javascript
import { sankey, sankeyLinkHorizontal } from 'd3-sankey';

const graph = sankey()
  .nodeWidth(12)
  .nodePadding(8)
  .extent([[0, 0], [innerW, innerH]])({
    nodes: nodes.map(d => ({ ...d })),
    links: links.map(d => ({ ...d })),
  });

g.selectAll('rect')
  .data(graph.nodes)
  .join('rect')
  .attr('x', d => d.x0)
  .attr('y', d => d.y0)
  .attr('width', d => d.x1 - d.x0)
  .attr('height', d => d.y1 - d.y0)
  .attr('fill', d => colour(d.name));

g.selectAll('path')
  .data(graph.links)
  .join('path')
  .attr('d', sankeyLinkHorizontal())
  .attr('fill', 'none')
  .attr('stroke', 'currentColor')
  .attr('stroke-opacity', 0.3)
  .attr('stroke-width', d => Math.max(1, d.width));
```

Gate: etichette nodi leggibili; n link gestibile; messaggio = flusso, non ranking preciso (preferisci barre se confronti lunghezze).

---

## Force-directed network

**Quando:** relazioni non gerarchiche; esplorazione. Messaggio primario spesso debole → annota community / degree o passa a matrice.

```javascript
const simulation = d3.forceSimulation(nodes)
  .force('link', d3.forceLink(links).id(d => d.id).distance(80))
  .force('charge', d3.forceManyBody().strength(-200))
  .force('center', d3.forceCenter(innerW / 2, innerH / 2));
```

Cleanup: `simulation.stop()` al destroy. Drag opzionale. Evita layout instabile in export statico (congelare posizioni dopo settle).

---

## Geo / choropleth

**Quando:** la posizione geografica **è** il messaggio (non “mappa perché belle”). Altrimenti barre per regione.

- `d3.geoPath` + proiezione adatta (`geoMercator`, `geoAlbersIta`, ecc. se nel progetto)
- Colore: sequential/diverging da [d3-colour.md](d3-colour.md)
- Confini sottili; legenda obbligatoria; no stretch fuorviante

---

## Pie / donut (API only)

`d3.pie` + `d3.arc` esistono — **policy a-charts invariata**: solo ≤5 fette e composizione grezza. Preferisci barre. Non promuovere da questa reference.

---

## QA specifico avanzate

- [ ] Tipo on-demand giustificato nel brief  
- [ ] Messaggio leggibile senza interazione obbligatoria  
- [ ] Performance DOM sotto soglia o canvas/aggregazione  
- [ ] Palette da chart-style o fallback CVD  
- [ ] `simulation.stop` / observer disconnect se usati  

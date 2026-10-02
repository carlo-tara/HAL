# Playbook D3 (a-charts)

Ricette operative per generare grafici con **d3.js** (canone **v7**). Ispirato a [claude-d3js-skill](https://github.com/chrisvoncsefalvay/claude-d3js-skill) e alle [release d3/d3](https://github.com/d3/d3/releases) — adattato al canone a-charts (messaggio → tipo → encoding → stack → QA).

**Prima** di aprire questo file: `scelta-tipo` + `leggibilita`. D3 non sceglie il tipo; implementa quello già deciso.

| Reference | Contenuto |
|-----------|-----------|
| [d3-scales.md](d3-scales.md) | Intent → API scale (incl. `scaleSymlog`) |
| [d3-colour.md](d3-colour.md) | Palette fallback CVD |
| [d3-advanced.md](d3-advanced.md) | Tree, treemap, force, geo, Sankey on-demand |

### Indice ricette

1. [Quando usare D3](#quando-usare-d3) · [Pattern A/B](#pattern-di-integrazione) · [Scheletro](#scheletro-standard)
2. [Preparazione dati](#preparazione-dati) (`group`/`rollup`, date, format)
3. [Snippet comuni](#snippet-comuni-allineati-a-scelta-tipo) (barre, linee, **area**, scatter, **stack**, **histogram**, heatmap, varianti)
4. [Assi, griglia, legenda, annotazioni](#assi-griglia-legenda-annotazioni)
5. [Join + transition](#join-con-transition-solo-su-richiesta)
6. [Interazioni](#interazioni-solo-se-il-brief-le-chiede) (`d3.pointer`, brush, zoom, Delaunay)
7. [Responsive](#responsive--cleanup) · [Canvas](#performance--canvas) · [Checklist](#checklist-rapida-pre-render-d3)

---

## Quando usare D3

| Usa D3 | Non usare D3 |
|--------|--------------|
| Binding dati → update frequenti | Bar chart statico da poche barre (SVG basta) |
| Hover, brush, zoom, linked views | Solo export PNG/PDF senza interazione |
| Layout custom (force, hierarchy, geo, sankey) | 3D → Three.js / altro, non D3 |
| Transition coreografate richieste | Animazioni “decorative” non richieste |
| Il progetto ha già `d3` | Introdurre una lib charting pesante senza accordo |

```javascript
import * as d3 from 'd3'; // v7 ESM
// CDN 7.x solo se il progetto lo consente già
```

**Non usare API morte:** `d3.event`, `d3.mouse`, `d3.nest`, `d3.voronoi`, `d3.histogram` (nome v3/4) → sostituite da `pointer`, `group`/`rollup`, `Delaunay`, `d3.bin`.

### Come leggere upstream D3 (skill esterne / changelog)

Quando valuti un repo skill D3 o le [release d3/d3](https://github.com/d3/d3/releases):

1. **Gap utile** = ricette mancanti per tipi già in `scelta-tipo` / matrice (area, `bin`, `rollup`, `format`, brush/`pointer`, ecc.)
2. **Non-gap** = patch/fix minori, palette nuove “nice-to-have”, tipologiche wow (chord/sunburst/radial) che restano gated o vietate
3. **Adozione** = snippet sotto questo cookbook (+ scales/colour/advanced); **non** riscrivere messaggio → tipo → encoding
4. Allinea a [l1-from-proto.md](../../../../a-agentzero/references/l1-from-proto.md): critica ed estensione, non copia

---

## Pattern di integrazione

### Pattern A — D3 manipola il DOM (default per interazioni / transition)

```javascript
function drawChart(data, svgEl) {
  if (!data?.length) return;
  const svg = d3.select(svgEl);
  svg.selectAll('*').remove();
  // margin → scale → axis → .join() …
}
```

### Pattern B — D3 calcola, framework dichiara (React/Vue/Svelte)

Usa D3 per `scale*`, `stack`, `bin`, `hierarchy`; render con JSX/`v-for`. Preferisci B se il progetto evita side-effect sul DOM; A se servono zoom/brush/transition.

---

## Scheletro standard

1. Guard dati vuoti / NaN  
2. Clear **oppure** update via `.join()` (preferisci join se live)  
3. Margin → `innerWidth` / `innerHeight`  
4. `g` traslato  
5. Scale (Y quantitativo: range **`[innerH, 0]`**)  
6. Assi (+ griglia leggera se serve)  
7. Mark con **`.join()`** + key  
8. `role="img"` + `<title>` / `<desc>`  

```javascript
function drawVisualization(data, svgEl, { width, height, colors }) {
  if (!data?.length) return;

  const svg = d3.select(svgEl);
  svg.selectAll('*').remove();

  const margin = { top: 24, right: 24, bottom: 40, left: 56 };
  const innerW = width - margin.left - margin.right;
  const innerH = height - margin.top - margin.bottom;

  svg
    .attr('viewBox', `0 0 ${width} ${height}`)
    .attr('role', 'img')
    .attr('aria-labelledby', 'chart-title chart-desc');

  const g = svg.append('g')
    .attr('transform', `translate(${margin.left},${margin.top})`);

  const x = d3.scaleBand()
    .domain(data.map(d => d.category))
    .range([0, innerW])
    .padding(0.12);

  const y = d3.scaleLinear()
    .domain([0, d3.max(data, d => d.value)])
    .nice()
    .range([innerH, 0]);

  g.append('g')
    .attr('transform', `translate(0,${innerH})`)
    .call(d3.axisBottom(x).tickSizeOuter(0));

  g.append('g')
    .call(d3.axisLeft(y).ticks(5).tickSizeOuter(0)
      .tickFormat(d3.format('~s')));

  const fill = colors?.primary ?? 'var(--chart-primary, #2563eb)';

  g.selectAll('rect')
    .data(data, d => d.category)
    .join('rect')
    .attr('x', d => x(d.category))
    .attr('y', d => y(d.value))
    .attr('width', x.bandwidth())
    .attr('height', d => innerH - y(d.value))
    .attr('fill', fill);
}
```

**Colori:** token chart-style / CSS — mai `steelblue` di default. Fallback: [d3-colour.md](d3-colour.md).

---

## Preparazione dati

### Sanitizza e ordina

- Ignora `null` / `NaN`; sulle linee/area usa `.defined(...)`
- Sort esplicito (tempo, ranking) — non affidarti all’ordine CSV
- Aggrega **prima** del bind se n punti >> messaggio

### `group` / `rollup` (post-`d3.nest`)

```javascript
// somma per categoria (tabella lunga → chart-ready)
const byCat = d3.rollup(
  rows,
  v => d3.sum(v, d => d.value),
  d => d.category
);
const data = Array.from(byCat, ([category, value]) => ({ category, value }))
  .sort((a, b) => d3.descending(a.value, b.value));

// più chiavi: flatRollup → array di tuple
const series = d3.flatRollup(
  rows,
  v => d3.sum(v, d => d.value),
  d => d.date,
  d => d.series
).map(([date, series, value]) => ({ date, series, value }));

// group: Map annidata senza aggregare
const grouped = d3.group(rows, d => d.region, d => d.category);
```

Anche: `d3.flatGroup`, `d3.groups`, `d3.index` (lookup per id).

### Date

```javascript
const parse = d3.timeParse('%Y-%m-%d'); // o timeParse locale
data.forEach(d => { d.date = parse(d.dateStr); });

// tick UTC a giorno intero (v7.7+): d3.unixDay / unixDays
const x = d3.scaleUtc()
  .domain(d3.extent(data, d => d.date))
  .range([0, innerW]);

axis.call(d3.axisBottom(x).ticks(d3.utcMonth.every(1))
  .tickFormat(d3.utcFormat('%b %Y')));
```

Dichiarare fuso in caption se non ovvio. Non interpolare buchi senza nota.

### Formattazione numeri (`d3.format`)

```javascript
const fmtInt = d3.format(',.0f');
const fmt1 = d3.format('.1f');
const fmtPct = d3.format('.1%');   // 0.126 → 12.6%
const fmtSi = d3.format('~s');     // 1500 → 1.500k (approx SI)
const fmtSigned = d3.format('+.1%');

// asse
axisLeft.call(d3.axisLeft(y).ticks(5).tickFormat(fmtSi));

// tooltip
tip.html(`${d.category}: <strong>${fmtPct(d.share)}</strong>`);
```

Locale IT (migliaia/decimali) se il progetto lo richiede:

```javascript
const itIT = d3.formatLocale({
  decimal: ',',
  thousands: '.',
  grouping: [3],
  currency: ['€', ''],
});
const fmtEuro = itIT.format('$,.2f');
```

Unità nella caption restano obbligatorie anche con tick formattati.

---

## Snippet comuni (allineati a scelta-tipo)

### Barre (confronto / ranking)

Come nello scheletro. Orizzontali: `scaleBand` su Y, `scaleLinear` su X (label lunghe).

### Linee (trend)

```javascript
const line = d3.line()
  .defined(d => d.value != null && !Number.isNaN(+d.value))
  .x(d => x(d.date))
  .y(d => y(d.value))
  .curve(d3.curveMonotoneX);

g.append('path')
  .datum(data)
  .attr('fill', 'none')
  .attr('stroke', colors?.primary ?? 'var(--chart-primary)')
  .attr('stroke-width', 2)
  .attr('d', line);
```

Serie multiple: max ~4–5 path o small multiples; etichette dirette > legenda lontana.

### Area (1–2 serie) e area stacked / 100%

```javascript
const area = d3.area()
  .defined(d => d.value != null && !Number.isNaN(+d.value))
  .x(d => x(d.date))
  .y0(innerH)           // o y(0) se dominio non parte da 0
  .y1(d => y(d.value))
  .curve(d3.curveMonotoneX);

g.append('path')
  .datum(data)
  .attr('fill', colors?.primary ?? 'var(--chart-primary)')
  .attr('fill-opacity', 0.25)
  .attr('d', area);

// spesso: area soft + line stroke sopra (messaggio = trend)
```

**Stacked / 100% stacked area** (composizione nel tempo):

```javascript
const keys = ['a', 'b', 'c'];
const stack = d3.stack()
  .keys(keys)
  .order(d3.stackOrderNone)
  .offset(d3.stackOffsetNone); // o stackOffsetExpand per 100%

const series = stack(wideRows); // wide: { date, a, b, c }

const y = d3.scaleLinear()
  .domain([0, d3.max(series, s => d3.max(s, d => d[1]))])
  .nice()
  .range([innerH, 0]);
// 100%: domain([0, 1]) + tickFormat(d3.format('.0%'))

const area = d3.area()
  .x(d => x(d.data.date))
  .y0(d => y(d[0]))
  .y1(d => y(d[1]));

g.selectAll('path.series')
  .data(series)
  .join('path')
  .attr('class', 'series')
  .attr('fill', d => colour(d.key))
  .attr('d', area);
```

Offset utili: `stackOffsetExpand` (100%), `stackOffsetDiverging` (pos/neg attorno a 0). Order: `stackOrderInsideOut`, `stackOrderDescending` se migliora la lettura.

**No gradient fill decorativo** su area salvo richiesta esplicita.

### Scatter (correlazione)

```javascript
g.selectAll('circle')
  .data(data)
  .join('circle')
  .attr('cx', d => x(d.x))
  .attr('cy', d => y(d.y))
  .attr('r', d => sizeScale ? sizeScale(d.size) : 4)
  .attr('fill', d => colourScale ? colourScale(d.category) : fill)
  .attr('opacity', 0.75);
```

Raggio da valore → `scaleSqrt` ([d3-scales.md](d3-scales.md)). Hover nearest: [Delaunay](#delaunay-nearest-point-scatterline-dense).

### Stacked / grouped bars

```javascript
const series = d3.stack().keys(keys)(wideRows);

// stacked
g.selectAll('g.layer')
  .data(series)
  .join('g')
  .attr('fill', d => colour(d.key))
  .selectAll('rect')
  .data(d => d)
  .join('rect')
  .attr('x', d => x(d.data.category))
  .attr('y', d => y(d[1]))
  .attr('height', d => y(d[0]) - y(d[1]))
  .attr('width', x.bandwidth());

// grouped: band padre + band figlio
const x0 = d3.scaleBand().domain(categories).range([0, innerW]).padding(0.2);
const x1 = d3.scaleBand().domain(keys).range([0, x0.bandwidth()]).padding(0.05);
```

Stacked solo se la **composizione** è il messaggio; altrimenti grouped o small multiples.

### Istogramma (`d3.bin`)

```javascript
const values = rows.map(d => +d.metric).filter(v => Number.isFinite(v));

const bin = d3.bin()
  .domain(d3.extent(values))
  .thresholds(d3.thresholdSturges); // o .thresholds(20) / array esplicito

const bins = bin(values);

const x = d3.scaleLinear()
  .domain([bins[0].x0, bins[bins.length - 1].x1])
  .range([0, innerW]);

const y = d3.scaleLinear()
  .domain([0, d3.max(bins, d => d.length)])
  .nice()
  .range([innerH, 0]);

g.selectAll('rect')
  .data(bins)
  .join('rect')
  .attr('x', d => x(d.x0) + 1)
  .attr('y', d => y(d.length))
  .attr('width', d => Math.max(0, x(d.x1) - x(d.x0) - 1))
  .attr('height', d => innerH - y(d.length))
  .attr('fill', fill);
```

Threshold: `thresholdScott`, `thresholdFreedmanDiaconis`, o bin width di business. Caption: “bin = …”.

### Heatmap (matrice)

`scaleBand` × `scaleBand` + `scaleSequential` (Viridis/Cividis). Etichette assi + legenda colore compatta.

### Varianti matrice (snippet corti)

**Lollipop** — ranking con meno ink:

```javascript
g.selectAll('line')
  .data(data)
  .join('line')
  .attr('x1', x(0)).attr('x2', d => x(d.value))
  .attr('y1', d => y(d.category) + y.bandwidth() / 2)
  .attr('y2', d => y(d.category) + y.bandwidth() / 2)
  .attr('stroke', 'currentColor');

g.selectAll('circle')
  .data(data)
  .join('circle')
  .attr('cx', d => x(d.value))
  .attr('cy', d => y(d.category) + y.bandwidth() / 2)
  .attr('r', 4)
  .attr('fill', fill);
```

**Funnel a barre** — conversioni: barre orizzontali ordinate per step, stessa baseline 0; etichetta step + valore + % sul precedente.

**Slope (prima/dopo)** — due `scalePoint` su X (A/B), `scaleLinear` su Y, `line` per ogni entità (pochi punti).

**Bullet** — barra grigia (range), barra misura, linea target; tre encoding su stessa scala lineare.

**Box plot (distribuzione)** — per categoria: calc q1/median/q3 con `d3.quantile`; whisker min/max o 1.5 IQR; `rect` + median line. Beeswarm: jitter su `scalePoint` se n piccolo.

---

## Assi, griglia, legenda, annotazioni

### Griglia leggera

```javascript
g.append('g')
  .attr('class', 'grid')
  .call(d3.axisLeft(y).ticks(5).tickSize(-innerW).tickFormat(''))
  .attr('stroke-opacity', 0.12)
  .call(g => g.select('.domain').remove());
```

Poi assi “pieni” sopra. `tickSizeOuter(0)`; evita griglie dense.

### Legenda compatta (solo se etichette dirette impossibili)

```javascript
const legend = svg.append('g')
  .attr('transform', `translate(${margin.left},${height - 16})`);

const item = legend.selectAll('g')
  .data(keys)
  .join('g')
  .attr('transform', (d, i) => `translate(${i * 88},0)`);

item.append('rect').attr('width', 10).attr('height', 10).attr('fill', d => colour(d));
item.append('text').attr('x', 14).attr('y', 9).text(d => d).attr('font-size', 11);
```

Preferisci label a fine linea / accanto alla barra.

### Linee di riferimento e annotazioni (1–2 max)

```javascript
const yRef = y(targetValue);

g.append('line')
  .attr('x1', 0).attr('x2', innerW)
  .attr('y1', yRef).attr('y2', yRef)
  .attr('stroke', 'currentColor')
  .attr('stroke-dasharray', '4 3')
  .attr('stroke-opacity', 0.6);

g.append('text')
  .attr('x', innerW)
  .attr('y', yRef - 4)
  .attr('text-anchor', 'end')
  .attr('font-size', 11)
  .text(`Target ${d3.format('.0f')(targetValue)}`);
```

Punto chiave: cerchio + label corta. Se servono >2 callout → spezza il messaggio o usa tabella.

---

## Join con transition (solo su richiesta)

```javascript
g.selectAll('rect')
  .data(data, d => d.category)
  .join(
    enter => enter.append('rect')
      .attr('x', d => x(d.category))
      .attr('width', x.bandwidth())
      .attr('y', innerH)
      .attr('height', 0)
      .attr('fill', fill)
      .call(e => e.transition().duration(400)
        .attr('y', d => y(d.value))
        .attr('height', d => innerH - y(d.value))),
    update => update.call(u => u.transition().duration(400)
      .attr('x', d => x(d.category))
      .attr('y', d => y(d.value))
      .attr('height', d => innerH - y(d.value))),
    exit => exit.call(e => e.transition().duration(300)
      .attr('y', innerH).attr('height', 0).remove())
  );
```

No loop infinito; `duration` sobria; rispetta `prefers-reduced-motion` se UI di prodotto.

---

## Interazioni (solo se il brief le chiede)

| Interazione | Pattern | Note |
|-------------|---------|------|
| Tooltip | HTML fuori SVG + **`d3.pointer`** | Valore + unità; non sostituire etichette essenziali |
| Hover highlight | opacity sulle altre serie | Max 1–2 focus |
| Zoom | `d3.zoom` + rescale | Reset esplicito; evita su barre semplici |
| Brush / linked | `brushX` + `scale.invert` | Due chart, una domanda ciascuno |
| Nearest point | `d3.Delaunay` | Scatter/line dense |
| Transition | `.transition()` su join | Solo su richiesta |

### Tooltip con `d3.pointer` (no `pageX` / `d3.event`)

```javascript
const tip = d3.select('body').append('div')
  .attr('class', 'chart-tooltip')
  .style('position', 'absolute')
  .style('pointer-events', 'none')
  .style('opacity', 0);

const fmt = d3.format(',.1f');

rects
  .on('pointerenter', (event, d) => {
    tip.style('opacity', 1).html(`${d.category}: <strong>${fmt(d.value)}</strong>`);
  })
  .on('pointermove', (event) => {
    // coordinate relative al container/svg — robusto con scroll/transform
    const [px, py] = d3.pointer(event, document.body);
    tip.style('left', `${px + 12}px`).style('top', `${py + 12}px`);
  })
  .on('pointerleave', () => tip.style('opacity', 0));

// dispose: tip.remove()
```

Multi-touch: `d3.pointers(event)`.

### Brush X + invert (focus temporale)

```javascript
const brush = d3.brushX()
  .extent([[0, 0], [innerW, innerH]])
  .on('end', (event) => {
    if (!event.selection) {
      // reset → dominio pieno
      onBrush(null);
      return;
    }
    const [x0, x1] = event.selection.map(x.invert);
    onBrush([x0, x1]); // ridisegna dettaglio / filtra
  });

g.append('g').attr('class', 'brush').call(brush);
```

Linked view: overview con brush → detail con dominio filtrato. Dispose: rimuovere listener brush.

### Zoom (pan/zoom su serie)

```javascript
const zoom = d3.zoom()
  .scaleExtent([1, 12])
  .translateExtent([[0, 0], [innerW, innerH]])
  .extent([[0, 0], [innerW, innerH]])
  .on('zoom', (event) => {
    const xz = event.transform.rescaleX(x);
    // ri-draw path/assi con xz; non mutare x originale se serve reset
    xAxis.call(d3.axisBottom(xz));
    path.attr('d', line.x(d => xz(d.date)));
  });

svg.append('rect')
  .attr('width', innerW)
  .attr('height', innerH)
  .attr('fill', 'none')
  .attr('pointer-events', 'all')
  .attr('transform', `translate(${margin.left},${margin.top})`)
  .call(zoom);

// reset: svg.transition().call(zoom.transform, d3.zoomIdentity)
```

### Delaunay nearest point (scatter/line dense)

```javascript
const delaunay = d3.Delaunay.from(data, d => x(d.x), d => y(d.y));

overlay.on('pointermove', (event) => {
  const [px, py] = d3.pointer(event);
  const i = delaunay.find(px, py);
  highlight(data[i]);
});
```

Sostituisce `d3.voronoi` (rimosso). Per Voronoi cells: `delaunay.voronoi([0,0,innerW,innerH])`.

---

## Responsive + cleanup

```javascript
function setupResponsive(container, data, draw) {
  const svg = d3.select(container).selectAll('svg').data([null]).join('svg');

  const ro = new ResizeObserver(entries => {
    const { width, height } = entries[0].contentRect;
    if (width < 16 || height < 16) return;
    svg.attr('width', width).attr('height', height);
    draw(data, svg.node(), { width, height });
  });

  ro.observe(container);
  return () => ro.disconnect();
}
```

Dispose anche: tooltip node, zoom/brush listeners, `simulation.stop()`.

---

## Performance + canvas

| Sintomo | Azione |
|---------|--------|
| > ~1000 mark DOM | Canvas, aggregazione, o sampling **dichiarato** |
| Re-render full clear a ogni frame | `.join()` update; evita `selectAll('*').remove()` se live |
| Force pesante | Limita nodi; freeze dopo settle |

### Pattern canvas (calcoli D3, paint 2D)

```javascript
function drawCanvas(data, canvas, { width, height }) {
  const ctx = canvas.getContext('2d');
  canvas.width = width;
  canvas.height = height;
  ctx.clearRect(0, 0, width, height);

  const x = d3.scaleLinear().domain(d3.extent(data, d => d.x)).range([40, width - 10]);
  const y = d3.scaleLinear().domain(d3.extent(data, d => d.y)).range([height - 30, 10]);

  ctx.fillStyle = 'var(--chart-primary, #2563eb)';
  for (const d of data) {
    ctx.beginPath();
    ctx.arc(x(d.x), y(d.y), 2, 0, 2 * Math.PI);
    ctx.fill();
  }
  // assi: SVG overlay oppure tick disegnati a mano
}
```

Assi/etichette spesso restano in SVG sopra il canvas. Gate QA: `qa-grafici`.

Opzionale export path: `d3.pathRound` / `shape.digits` (v7.8) se serve stringa path compatta.

---

## Anti-pattern D3 (oltre al canone a-charts)

- Pie/donut “perché esiste `d3.pie`” → solo se `scelta-tipo` (≤5)
- `schemeCategory10` / rainbow senza chart-style → [d3-colour.md](d3-colour.md)
- Gradient / glow su barre-linee senza richiesta
- Dual `axisRight` “per far entrare tutto”
- `d3.event` / `d3.mouse` / `d3.nest` / `d3.voronoi` (API morte)
- Chord/sunburst/force senza brief; template Inter+viola decorativi

---

## Checklist rapida pre-render D3

- [ ] Tipo già deciso da `scelta-tipo`
- [ ] Encoding da `leggibilita` (baseline 0 su barre, ecc.)
- [ ] Dati preparati con `rollup`/`bin` se serve; nessun totale inventato
- [ ] Tick/tooltip con `d3.format` coerente + unità in caption
- [ ] Pattern A o B; token colore (o d3-colour)
- [ ] `.join()` + key; transition solo se richieste
- [ ] Interazioni con `d3.pointer` / brush / zoom solo se nel brief + dispose
- [ ] Annotazioni ≤2; reference line etichettata se usata
- [ ] DOM ≲~1000 o canvas/aggregazione
- [ ] `role="img"` + title/desc

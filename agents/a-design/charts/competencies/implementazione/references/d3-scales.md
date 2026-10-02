# Scale D3 — intent → API

Mappa le decisioni di **a-charts** (`scelta-tipo` / `leggibilita`) alle API scale di d3. Non sostituisce le policy (baseline 0, no dual-Y, log dichiarato): solo *quale* costruttore usare.

Playbook: [d3-cookbook.md](d3-cookbook.md).

---

## Tabella intent → scale

| Intent / encoding | Scale tipica | Note |
|-------------------|--------------|------|
| Ranking / categorie su asse | `scaleBand` (+ `.padding`) | Dominio = categorie ordinate |
| Lunghezza / posizione quantitativa | `scaleLinear` | Barre: domain min = **0** |
| Trend temporale | `scaleTime` / `scaleUtc` | Parse date esplicito; `.nice()` con cautela |
| Bubble / area → raggio | `scaleSqrt` | Mai `scaleLinear` sul raggio se encoding è area |
| Magnitudini su ordini diversi | `scaleLog` | Domain > 0; dichiara “scala log” in titolo/caption |
| Zero + code pesanti (quasi-log) | `scaleSymlog` | Ammette 0/negativi; dichiara “scala symlog” |
| Bins continui → categorie discrete | `scaleQuantize` / `scaleQuantile` / `scaleThreshold` | Heatmap legend, choropleth classed; histogram → `d3.bin` + linear |
| Colore categorico | `scaleOrdinal` | Range da chart-style o [d3-colour.md](d3-colour.md) |
| Colore sequenziale | `scaleSequential` + `interpolate*` | Viridis/Cividis/Blues di default |
| Colore divergente | `scaleDiverging` | Centro = 0 / media / target significativo |
| Opacità / stroke secondari | `scaleLinear` su `[0.2, 1]` | Non sostituire posizione/lunghezza |

---

## Continuous (sintesi API)

```javascript
d3.scaleLinear().domain([0, max]).range([0, innerW]).nice().clamp(true);
d3.scaleSqrt().domain([0, max]).range([2, 20]);      // raggio
d3.scaleLog().domain([1, max]).range([innerH, 0]);   // > 0
d3.scaleSymlog().domain([min, max]).range([innerH, 0]); // 0/neg ok; constant opzionale
d3.scaleTime().domain(d3.extent(data, d => d.date)).range([0, innerW]);
```

Metodi utili: `.invert` (brush/tooltip), `.ticks(n)`, `.tickFormat(d3.format(...))`, `.nice()`.

**Histogram:** non serve scale “bin” dedicata — `d3.bin()` produce intervalli; posizione con `scaleLinear` su `x0`/`x1` (vedi [d3-cookbook.md](d3-cookbook.md)).

---

## Discrete / band

```javascript
d3.scaleBand()
  .domain(categories)
  .range([0, innerW])
  .paddingInner(0.1)
  .paddingOuter(0.05);

// punto centrato nella banda
const xPoint = d3.scalePoint().domain(categories).range([0, innerW]).padding(0.5);
```

Grouped bars: band padre + band figlio con `.range([0, parent.bandwidth()])`.

---

## Ordinal / colore

```javascript
const colour = d3.scaleOrdinal()
  .domain(keys)
  .range(palette); // da chart-style o Okabe-Ito

const seq = d3.scaleSequential(d3.interpolateCividis)
  .domain([min, max]);

const div = d3.scaleDiverging(d3.interpolatePuOr)
  .domain([lo, mid, hi]); // mid significativo
```

---

## Policy a-charts (richiamo)

| Policy | Implicazione scale |
|--------|-------------------|
| Barre: zero baseline | `domain([0, max])` — non partire da `min` positivo |
| Dual-Y vietato di default | Un solo `scaleLinear`/`Time` per encoding primario; secondo chart se unità diverse |
| Log solo se giustificata | `scaleLog` + testo esplicito |
| Symlog se serve 0 + code | `scaleSymlog` + testo esplicito |
| Tempo con buchi | Non interpolare silenziosamente; gap visibile o nota in caption |
| Area encoding | `scaleSqrt` per raggio |

---

## Scelta rapida

```
quantitativo posizione/lunghezza → linear (o time)
categorie asse → band
raggio da valore → sqrt
ordini di grandezza → log (dichiarato)
zero + code lunghe → symlog (dichiarato)
colore da categoria → ordinal + palette
colore da quantità → sequential / diverging
distribuzione grezza → d3.bin + linear
```

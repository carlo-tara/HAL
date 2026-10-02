# Palette D3 — fallback colore

Usare **solo** quando non esiste (o non applica) un `.cursor/chart-styles/*.md` / token UI di progetto. La gerarchia resta: L2 → chart-style → brand/UI → questo fallback → default L1.

Allineato a `leggibilita` / [encoding-rules.md](../../leggibilita/references/encoding-rules.md). Ispirato a schemi D3 e palette CVD-safe pubbliche (Okabe–Ito, Viridis, Cividis, PuOr).

---

## Priorità

1. Colori del **chart-style** / CSS variables progetto  
2. Brand file se il messaggio è brandizzato  
3. Fallback sotto  
4. Mai rainbow (`interpolateRainbow` / Spectral) di default  
5. Mai solo rosso/verde per significato critico senza pattern o etichetta  

---

## Categorico (CVD-aware)

**Okabe–Ito** (preferito fino a ~7–8 categorie):

```javascript
const okabeIto = [
  '#E69F00', '#56B4E9', '#009E73', '#F0E442',
  '#0072B2', '#D55E00', '#CC79A4', '#000000',
];

const colour = d3.scaleOrdinal()
  .domain(keys)
  .range(okabeIto);
```

Alternative D3 accettabili se n serie alto e nessuna style file: `d3.schemeTableau10`, `d3.schemeSet2` (non Accent ad alta saturazione su dark UI senza verifica contrasto).

Opzionale (D3 **v7.9+**): `d3.schemeObservable10` — accettabile come alternativa Tableau10; **non** batte chart-style né Okabe–Ito come default CVD.

Su **sfondo dark**: alza luminosità o usa varianti chiarite; verifica contrasto testo/serie.

---

## Sequenziale

| Contesto | Preferito | Alternativa |
|----------|-----------|-------------|
| Generico / scientifico | `d3.interpolateViridis` | `d3.interpolateCividis` (CVD) |
| Heatmap “calore” classico | `d3.interpolateYlOrRd` | solo se non confonde con pos/neg |
| Monocromatico brand-agnostic | `d3.interpolateBlues` | Greens |

```javascript
const seq = d3.scaleSequential(d3.interpolateViridis)
  .domain([min, max]);
```

---

## Divergente

Solo con **centro significativo** (0, media, target):

```javascript
const div = d3.scaleDiverging(d3.interpolatePuOr)
  .domain([lo, mid, hi]);
// alternative CVD-friendly: interpolateBrBG
```

Non usare divergente per dati puramente sequenziali.

---

## Positivo / negativo

Se chart-style definisce una coppia, usala. Altrimenti:

```javascript
const posNeg = d3.scaleOrdinal()
  .domain(['neg', 'pos'])
  .range(['#D55E00', '#0072B2']); // Okabe–Ito orange / blue — non solo red/green
```

Aggiungi segno `+`/`−` o pattern se il significato è critico.

---

## Vietati di default

| Schema / pratica | Perché |
|------------------|--------|
| Rainbow / Spectral come sequenziale | Ordine non perceptually uniform; confonde ranking |
| Solo red–green | Daltonismo comune |
| `schemeCategory10` “per abitudine” | Ok se ok; preferisci Okabe–Ito o Tableau10 documentato |
| Gradient fill decorativo su barre/linee | Chartjunk (`leggibilita`) |

---

## Dark UI (checklist)

- [ ] Serie non sotto ~4.5:1 sul background reale  
- [ ] Griglia/assi attenuati ma visibili  
- [ ] Tooltip con contrasto proprio (non ereditare testo faint)  

---

## Collegamenti

- Encoding: [encoding-rules.md](../../leggibilita/references/encoding-rules.md)  
- Scale API: [d3-scales.md](d3-scales.md)  
- Implementazione: [d3-cookbook.md](d3-cookbook.md)  

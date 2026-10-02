# Target di output

Come implementare i grafici con **a-charts**.

---

## Matrice target

| Contesto | Target | Note |
|----------|--------|------|
| Artefatto analitico in chat Cursor | `.canvas.tsx` (`cursor/canvas`) | Skill canvas IDE; dati inline; no fetch |
| Report / dashboard HTML di progetto | SVG inline o D3 nel repo | Allinea CSS variables / class del progetto |
| Inner Circle analytics | SVG/D3 + token dark IC | Non usare tema landing `mc-*` salvo richiesta |
| Esplorazione interattiva ricca | D3 / lib già nel repo | Non aggiungere dipendenze senza accordo; playbook [d3-cookbook.md](d3-cookbook.md) |
| Notebook / pipeline dati | matplotlib / plotly / altair | Stile sobrio; esportare PNG/SVG se serve publish |
| Slide / doc statico | SVG o PNG ad alta risoluzione | Font embed o path text |

---

## SVG (default HTML)

Preferito quando:

- Serie statiche o poco dinamiche
- Serve controllo pixel-perfect e zero JS
- Email/PDF-friendly (con cautela)

Pattern minimi:

- `viewBox` + `role="img"` + title/desc
- Assi come linee + `text` per tick
- Barre = `rect`; linee = `path`/`polyline`
- Colori da `var(--…)` del progetto se esistono

---

## D3

Usare quando:

- Binding dati → update frequenti
- Interazioni (hover, brush, zoom) richieste dal brief
- Layout custom (hierarchy, force, geo) on-demand
- Il progetto ha già D3

Evitare D3 “per abitudine” su un bar chart statico da 6 barre.

### Lettura obbligatoria se target = D3

| File | Contenuto |
|------|-----------|
| [d3-cookbook.md](d3-cookbook.md) | Pattern A/B, scheletro, prep (`rollup`/`bin`/`format`), bar/line/**area**/stack/histogram, assi/annotazioni, `d3.pointer`/brush/zoom/Delaunay, canvas |
| [d3-scales.md](d3-scales.md) | Intent → API scale (incl. `scaleSymlog`) |
| [d3-colour.md](d3-colour.md) | Palette fallback (Okabe–Ito, Viridis…) se no chart-style |
| [d3-advanced.md](d3-advanced.md) | Tree, treemap, network, geo, **Sankey** (`d3-sankey`) — on-demand |

Regole rapide:

1. Scheletro: guard → margin → scale (Y invertita) → assi → `.join()`
2. Prep: `rollup`/`bin` + `d3.format` su tick/tooltip
3. Colori da chart-style / token; altrimenti `d3-colour`
4. Interazioni con `d3.pointer` (no `d3.event`/`pageX`); cleanup ResizeObserver/tooltip/brush/zoom/`simulation.stop`
5. >~1000 elementi DOM → canvas / aggregazione (gate `qa-grafici`)
6. Sankey / tipologiche avanzate solo on-demand + accordo dipendenza se fuori core

---

## Cursor canvas

Usare quando l'output **è** l'analisi (non quando il deliverable è un file nel repo).

Vincoli tipici skill canvas:

- Un solo `.canvas.tsx` nella cartella canvases del progetto Cursor
- Solo import `cursor/canvas`
- Dati embedded; etichette complete su ogni plot
- No empty states / placeholder

Se il deliverable è `data/*.html` o static del repo → **non** canvas: scrivi nel path progetto.

---

## Python

- Stile: griglie leggere, niente 3D
- Salva SVG/PNG nel path concordato
- Riproducibilità: seed / script nel repo se pipeline ricorrente

---

## Anti-pattern implementativi

- CDN di Chart.js/Highcharts in pagine che già usano SVG/D3 custom senza motivo
- Hardcodare hex se il progetto ha token CSS
- Grafici in markdown come ASCII art quando serve un artefatto reale
- Duplicare un design system parallelo invece di estendere quello esistente
- Copiare template D3 con palette/font decorativi che contraddicono chart-style o anti-pattern a-charts

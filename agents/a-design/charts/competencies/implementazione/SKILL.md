---
name: implementazione
kind: competency
version: 1.2.2
description: >-
  Sceglie e implementa il target di output del grafico (SVG, D3, Cursor canvas,
  HTML dashboard, Python) riusando lo stack di progetto. Solo L1 (a-charts).
---

# Competenza L1 — implementazione (a-charts)

Trasforma tipo + encoding in **codice o artefatto** nel target giusto. Guida: [output-targets.md](references/output-targets.md).

Se target **D3**: [d3-cookbook.md](references/d3-cookbook.md) (+ [d3-scales.md](references/d3-scales.md), [d3-colour.md](references/d3-colour.md); avanzate [d3-advanced.md](references/d3-advanced.md)).

---

## Quando applicare

Dopo `scelta-tipo` e `leggibilita`, o quando l'utente chiede un formato specifico (“SVG”, “canvas”, “in dashboard”, “D3”).

---

## Scelta target (ordine)

1. **Richiesta esplicita** dell'utente
2. **Stack del progetto** (chart-style, L2, skill UI)
3. **Default** da [output-targets.md](references/output-targets.md)

Non introdurre librerie pesanti se SVG statico basta. Non usare D3 per abitudine su poche barre statiche.

---

## Regole ferree

1. **Dati inline o da file di progetto** — no fetch a API non concordate in un artefatto statico
2. **Riusa token** da chart-style / UI skill (variabili CSS, colori Enrico, ecc.); fallback D3 solo via [d3-colour.md](references/d3-colour.md)
3. **Responsive** — viewBox SVG; per D3 live: ResizeObserver + dispose ([d3-cookbook.md](references/d3-cookbook.md))
4. **Niente chartjunk nel markup** — filtri glow, animazioni infinite, ecc. solo su richiesta
5. **Canvas Cursor** — solo se artefatto analitico standalone in chat; leggi skill `canvas` Cursor; un file `.canvas.tsx`, import solo da `cursor/canvas`
6. **Dashboard Inner Circle** — delega shell/layout a `innercircle-ui-ux`; qui solo il grafico coerente coi token
7. **D3** — Pattern A/B; scheletro margin/scale/`.join()`; prep con `rollup`/`bin`/`format`; interazioni con `d3.pointer` solo se nel brief; canvas se DOM denso
8. **Upstream D3** (skill esterne / changelog) — triage come in [d3-cookbook.md](references/d3-cookbook.md) § «Come leggere upstream D3»: gap = ricette per tipi già in matrice; non importare tipologiche anti-canone né riscrivere `scelta-tipo`/`leggibilita`
9. **Legend dipendenti dal range** — se le slices/legend dipendono dal periodo selezionato, non fissarle al mount: passare un resolver (es. `meta.getLegend` / `resolveLegend`) e ricalcolare su ogni apply del range control. Path API → L2 UI skill

---

## Workflow render

```
1. Conferma path output e target (SVG | D3 | canvas | …)
2. Se D3: apri d3-cookbook (+ scales/colour; advanced solo on-demand)
3. Prepara dati (stessa granularità del messaggio; aggrega se serve)
4. Implementa tipo scelto con encoding deciso
5. Verifica a occhio: titolo, assi, contrasto; cleanup listener/simulation
6. Passa a qa-grafici
```

---

## Deleghe

| Bisogno | Dove |
|---------|------|
| Shell / KPI strip / card dashboard IC | skill UI progetto |
| Copy titolo lungo / note | a-copywriter |
| Metriche SEO numeriche | a-seozoom (dati reali) |

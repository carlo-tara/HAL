---
name: scelta-tipo
kind: competency
version: 1.1.0
description: >-
  Mappa intent analitico → tipo di grafico più efficace. Matrice confronti,
  trend, composizione, distribuzione. Solo L1 (a-charts).
---

# Competenza L1 — scelta-tipo (a-charts)

Scegli il **tipo** che riduce lo sforzo cognitivo per la domanda del lettore. Matrice: [chart-type-matrix.md](references/chart-type-matrix.md).

---

## Quando applicare

All'inizio di ogni task chart, o quando l'utente chiede “che grafico uso?” / “migliora questo grafico” (rivaluta il tipo prima del styling).

---

## Workflow

```
1. Estrai la domanda primaria (una sola)
2. Classifica intent: confronto | ranking | trend | composizione | correlazione | distribuzione | flusso
3. Consulta la matrice → tipo default + 1 alternativa
4. Se i dati non supportano l'intent (serie mancanti, n troppo alto), segnala e proponi pivot (tabella, split, aggregazione)
5. Passa a leggibilita con tipo scelto
```

---

## Regole ferree

1. **Una domanda → un grafico.** Domande multiple → più grafici o tabella + highlight
2. **Confronto quantitativo** → barre (posizione/lunghezza), non torta
3. **Trend temporale** → linee (o barre solo se pochi punti discreti)
4. **Parte-tutto con molte categorie** → barre stacked / 100% stacked o tabella share; pie solo ≤5 fette e messaggio “composizione grezza”
5. **Valori precisi > pattern** → tabella (eventualmente con sparklines), non forzare un chart
6. **n categorie alto** → bar orizzontale ordinate, top-N + “altro”, o faceting — non affollare
7. **Tipologiche avanzate** (tree, treemap, force, chord, sunburst, geo) → solo on-demand; vedi matrice § avanzate / [d3-advanced.md](../implementazione/references/d3-advanced.md)

---

## Output della fase

Prima di disegnare, dichiara in 2–4 righe:

- Domanda
- Intent
- Tipo scelto (+ perché)
- Alternativa scartata (1 riga)

Poi procedi a `leggibilita`.

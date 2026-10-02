---
name: qa-grafici
kind: competency
version: 1.2.0
description: >-
  Checklist pre-consegna per grafici: correttezza dati, leggibilità, encoding,
  accessibilità e allineamento allo stack di progetto. Solo L1 (a-charts).
---

# Competenza L1 — qa-grafici (a-charts)

Gate finale prima della consegna. Se un check fallisce → correggi, non “spiega via”.

---

## Quando applicare

Sempre prima di consegnare un grafico nuovo o una revisione sostanziale.

---

## Checklist

### Dati e messaggio

- [ ] Nessun dato inventato; totale/aggregati coerenti con la fonte
- [ ] Una domanda primaria evidente dal titolo
- [ ] Tipo allineato a `scelta-tipo` (o scostamento giustificato dall'utente)

### Lettura in 3 secondi

- [ ] Si capisce il confronto/trend senza studiare la legenda
- [ ] Unità e periodo chiari
- [ ] Fonte (o “elaborazione interna”) in caption/note
- [ ] Nessun chartjunk (3D, dual-Y non richiesto, pie overcrowded)

### Encoding

- [ ] Barre a baseline 0
- [ ] Ordine sensato
- [ ] Contrasto sufficiente su sfondo reale
- [ ] Highlight ≤2 elementi (se presente)

### Implementazione

- [ ] Path/stack corretti; token progetto rispettati (o fallback [d3-colour.md](../implementazione/references/d3-colour.md))
- [ ] Mobile / viewport: niente sovrapposizioni gravi
- [ ] Se canvas: vincoli skill canvas rispettati
- [ ] Se SVG: title/desc o equivalente testuale
- [ ] Se D3: scheletro cookbook; `.join()`; dispose ResizeObserver/tooltip/brush/zoom/simulation
- [ ] Se D3 interattivo: `d3.pointer` (no `d3.event`/`pageX` fragile); interazioni solo se nel brief
- [ ] Se D3: tick/tooltip formattati (`d3.format`); reference line etichettata se presente (≤2 annotazioni)

### Performance (D3 / SVG denso)

- [ ] Elementi DOM marcatori (rect/circle/path segment) ≲ ~1000 — altrimenti canvas, aggregazione o sampling dichiarato
- [ ] Nessun re-clear completo a ogni frame se basta un update `.join()`
- [ ] Force layout: `simulation.stop()` al destroy; freeze posizioni per export statico

### Consegna

- [ ] Limiti dati / assunzioni dichiarati all'utente
- [ ] Checklist a-agentzero / orchestratore a-charts ok

---

## Fail rapidi (blocca consegna)

| Sintomo | Azione |
|---------|--------|
| Numeri non verificabili | Chiedi fonte o ometti il grafico |
| Pie con molte fette | Converti a barre |
| Dual-Y “per far entrare tutto” | Spezza in due chart |
| Titolo generico | Riscrivi con metrica specifica |
| Illeggibile su dark UI | Riparti da palette chart-style / d3-colour |
| DOM markers >> 1000 senza mitigazione | Aggrega, canvas, o dichiara sampling |
| Listener/simulation senza cleanup | Aggiungi dispose prima della consegna |

---

## Dopo il QA

Consegna artefatto + 1–3 bullet su: tipo scelto, eventuale limite dati, path file.

---
name: leggibilita
kind: competency
version: 1.1.0
description: >-
  Encoding visuale, declutter, etichette, colore e accessibilità per grafici
  facili da leggere in pochi secondi. Solo L1 (a-charts).
---

# Competenza L1 — leggibilita (a-charts)

Rendi il grafico **immediatamente leggibile**. Dettaglio encoding: [encoding-rules.md](references/encoding-rules.md).

---

## Quando applicare

Dopo `scelta-tipo`, prima e durante `implementazione`. Anche in review di grafici esistenti (“non si legge”).

---

## Checklist encoding (obbligatoria)

```
- [ ] Titolo = metrica/domanda specifica (non “Grafico 1” / “Metrics”)
- [ ] Unità su assi o etichette; periodo e fonte in caption
- [ ] Barre: baseline a zero
- [ ] Ordine sensato (tempo, ranking, categorie di business — non random)
- [ ] Etichette dirette se ≤~5 serie/categorie chiave; altrimenti legenda chiara e vicina
- [ ] Colori: categorici vs sequenziali corretti; contrasto su sfondo; colorblind-aware
- [ ] Se no chart-style: fallback Okabe–Ito / Viridis / Cividis ([d3-colour.md](../implementazione/references/d3-colour.md))
- [ ] Griglia/assi discreti; niente 3D, ombre, gradient fill inutili
- [ ] Highlight: al massimo 1–2 elementi enfatizzati rispetto al resto
```

---

## Regole ferree

1. **Posizione e lunghezza prima di tutto** — angolo e area solo se inevitabili
2. **Ink utile** — se togliendo un elemento il messaggio resta chiaro, toglilo
3. **Non mentire con la scala** — truncare asse Y su barre distorce; su linee annota se parti da non-zero
4. **Testo leggibile** — tick e label non sovrapposti; ruota o passa a barre orizzontali
5. **Mobile** — riduci serie, aumenta touch target / spacing; spezza in small multiples se serve

---

## Titoli e caption

| Elemento | Contenuto |
|----------|-----------|
| Titolo | Cosa mostra (metrica + breakdown) |
| Sottotitolo opz. | Filtro / coorte |
| Caption | Fonte · periodo · trasformazione (media, p95, YoY…) |

Copy lungo o tono brand: delega **a-copywriter** / `tono-di-voce`.

---

## Output della fase

Annota decisioni non ovvie (perché ordinato così, perché quel colore highlight). Poi `implementazione`.

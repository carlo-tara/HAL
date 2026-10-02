# Chart style — {nome}

File dati per **a-charts**. Un file = uno stile/progetto. Path: `.cursor/chart-styles/{nome}.md`.

---

## Identità

| Campo | Valore |
|-------|--------|
| Nome | {nome} |
| Progetto / prodotto | {…} |
| Tema | dark / light / entrambi |
| Audience tipica | {interno / cliente / executive} |

---

## Palette

| Ruolo | Token / hex | Note |
|-------|-------------|------|
| Sfondo | | |
| Testo | | |
| Muted | | |
| Accent primario | | |
| Serie 1–N (categoriche) | | Colorblind-safe se possibile |
| Positivo / negativo | | |
| Griglia / assi | | Basso contrasto |

---

## Tipografia chart

| Elemento | Font / size / weight |
|----------|----------------------|
| Titolo | |
| Asse / tick | |
| Etichetta diretta | |
| Caption / fonte | |

---

## Default di progetto

| Intent | Tipo preferito | Note |
|--------|----------------|------|
| Confronto categorie | bar orizzontale / verticale | |
| Trend | line | |
| Funnel / step | | |
| Parte-tutto | | Evitare pie se >5 |

---

## Stack

| Target | Libreria / tecnica |
|--------|-------------------|
| HTML report | SVG / D3 / … |
| Canvas Cursor | `cursor/canvas` |
| Altro | |

---

## Regole locali (delta)

- {es. sempre baseline 0 sulle barre KPI}
- {es. giallo accent solo per highlight, non per tutte le serie}

---

## Esempi di riferimento

| File | Cosa mostra |
|------|-------------|
| `{path}` | |

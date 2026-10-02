# Encoding e declutter

Canone leggibilità per **a-charts**.

---

## Gerarchia degli encoding (quantitativo)

Dal più efficace al meno (per confronti precisi):

1. Posizione su scala comune
2. Lunghezza
3. Direzione / slope
4. Angolo
5. Area
6. Volume / 3D (vietato)
7. Colore solo come canale quantitativo (usare con cautela; preferire sequenziale)

---

## Declutter

Rimuovi di default:

- Bordi doppi, drop shadow, gloss, 3D
- Griglie dense; tieni tick essenziali
- Legende ridondanti se ogni serie è etichettata
- Decimali inutili (allinea precisione all'audience)
- Colorazione “arcobaleno” su categorie ordinate — usa sequenza o un accent

Mantieni:

- Assi con unità
- Linea di riferimento (target, media) se è il messaggio
- Annotazione su 1–2 punti chiave

---

## Colore

| Uso | Regola |
|-----|--------|
| Categorico | Max ~5–7 hue distinte; riusa palette chart-style |
| Sequenziale | Un hue, luminosità/saturazione variabili |
| Divergenza | Solo con centro significativo (0, media, target) |
| Pos/neg | Coppia fissa del style file |
| Sfondo dark | Alza luminosità testo/serie; verifica contrasto |

Non usare solo il rosso/verde per significati critici senza pattern/etichetta.

### Fallback senza chart-style (D3 / SVG)

Se manca `.cursor/chart-styles/` e non ci sono token UI: usa [d3-colour.md](../../implementazione/references/d3-colour.md) — Okabe–Ito (categorico), Viridis/Cividis (sequenziale), PuOr/BrBG (divergente). Vietati di default: rainbow/Spectral, solo red–green.

---

## Assi e scale

- Barre: **zero baseline**
- Log scale: solo se giustificata e dichiarata nel titolo/caption
- Dual-Y: **no** di default; se l'utente insiste, annota il rischio di falsa correlazione
- Tempo: intervalli regolari; non interpolare buchi senza dichiararlo

---

## Densità

| Sintomo | Rimedio |
|---------|---------|
| Label sovrapposte | Orizzontale bars, ruota meno, meno tick, aggrega |
| Troppe serie | Top-N + Altro, small multiples, interactive filter |
| Chart “pieno” | Spezza domande; aumenta whitespace |

---

## Accessibilità minima

- Non affidare il significato al solo colore
- Testo ≥ contrasto accettabile sullo sfondo del progetto
- Per SVG: `<title>`/`<desc>` o testo visibile equivalente
- Evita flash / animazioni non richieste

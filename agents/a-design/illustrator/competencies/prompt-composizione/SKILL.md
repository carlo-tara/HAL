---
name: prompt-composizione
kind: competency
version: 1.0.2
description: >-
  Composizione prompt EN per Qwen: formula style_anchor+subject+composition+constraints,
  negative, varianti A/B/C; prompt_extend T2I false / I2I true; testo in virgolette.
  Solo L1 (no baseline L0).
---

# Competenza L1 — prompt-composizione (a-illustrator)

Corpus: [references/prompt-style.md](references/prompt-style.md).

---

## Quando applicare

Ogni generazione (anteprime e finale): costruire o variare i prompt.

---

## Formula

```
{style_anchor}

Subject: {soggetto}.
Composition: {inquadratura, punto focale, spazio negativo}.
Constraints: {palette, no text, …}.
```

- Style anchor dal file stile (competenza `stile-visivo`)
- Subject/composition cambiano per variante
- Scrivi in **inglese** per Qwen salvo test espliciti

---

## Varianti A/B/C (con preview-render)

| Variante | Enfasi |
|----------|--------|
| **A** | Composizione e metafora principale del brief |
| **B** | Angolazione alternativa (più minimal / più denso) |
| **C** | Dettaglio o contrasto diverso |

Stesso style file e aspect ratio; `--subject` / composition distinti.

---

## Coerenza prompt

| Leva | Uso |
|------|-----|
| `prompt_extend: false` | Produzione coerente (no diluizione stile) |
| `seed` | Varianti controllate; seed diversi per A/B/C |
| Negative prompt | Dal style file |
| `--prompt-extend` | Solo esplorazione; non produzione |

Naming output tipico: vedi prompt-style.md § Naming.

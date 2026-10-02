---
name: nome-progetto
created: YYYY-MM-DD
size: "1328*1328"
seed:
prompt_extend: false
watermark: false
---

# Stile illustrazioni — [nome-progetto]

Copia in `.cursor/illustration-styles/{nome-progetto}.md` e compila dopo l'onboarding. L'agente `a-illustrator` lo legge a ogni generazione (skill in `a-illustrator/SKILL.md`, deploy via `a-illustrator/deploy.sh`).

---

## Style anchor (prompt base)

Blocco in **inglese** (o lingua del modello) da anteporre a ogni prompt. Descrivi tecnica, palette, linee, texture, illuminazione, composizione tipica. Questo testo resta fisso finché non chiedi un cambio stile.

> [Es. «Flat vector illustration, soft rounded shapes, limited palette of warm terracotta (#C45C3E), cream (#F5F0E8) and deep forest green (#2D4A3E). Subtle grain texture overlay. Clean outlines, no photorealism, no 3D. Consistent 2px stroke weight. Soft ambient light, minimal shadows.»]

---

## Negative prompt

Elementi da escludere esplicitamente dal modello.

> [Es. «photorealistic, 3D render, glossy, neon, cluttered background, text, watermark, logo, anime, stock photo»]

---

## Palette

| Ruolo | Colore | Hex (opzionale) |
|-------|--------|-----------------|
| Primario | | |
| Secondario | | |
| Accento | | |
| Sfondo | | |

---

## Parametri ricorrenti

| Campo | Valore | Note |
|-------|--------|------|
| Aspect ratio default | 1:1 / 16:9 / 4:3 | Allinea a `size` nel frontmatter |
| Dettaglio | basso / medio / alto | |
| Uso tipico | hero blog, icone, social, prodotto | |

---

## Regole di coerenza

Regole che l'agente applica a **ogni** nuova illustrazione:

1. [Es. stesso spessore linea e stesso livello di dettaglio]
2. [Es. palette limitata ai colori sopra, max 1 accento per immagine]
3. [Es. soggetti centrati, margine respiro 10%]
4. [Es. niente testo nell'immagine salvo richiesta esplicita]

---

## Risposte onboarding (riferimento)

Salva qui le risposte della prima sessione per audit e revisioni future.

| Domanda | Risposta |
|---------|----------|
| Mood / atmosfera | |
| Tipo illustrazione | |
| Riferimenti visivi | |
| Cosa evitare | |
| Contesto d'uso | |

---

## Esempi approvati (opzionale)

Descrizioni di illustrazioni già generate e approvate dall'utente. Usa come riferimento di coerenza.

### Esempio 1

- **Soggetto:**
- **Prompt usato:**
- **Note:**

---
name: stile-visivo
kind: competency
version: 1.0.0
description: >-
  Stile visivo: onboarding, style file (.cursor/illustration-styles/), anchor/palette/seed,
  coerenza sessione, cambio stile esplicito. Solo L1 (no baseline L0).
---

# Competenza L1 — stile-visivo (a-illustrator)

Governa **come** usare i style file. I file restano dati progetto in `.cursor/illustration-styles/` (non moduli). Template: [style-brief-template.md](../../style-brief-template.md).

Onboarding dettagliato: [prompt-style.md](../prompt-composizione/references/prompt-style.md) § Onboarding.

---

## Quando applicare

Prima sessione senza style file; coerenza tra generazioni; cambio stile su richiesta esplicita; aggiornamento esempi approvati.

---

## Discovery

| Situazione | Azione |
|------------|--------|
| 1 style file | Usalo |
| 0 file | Ferma → onboarding → salva `.cursor/illustration-styles/{nome}.md` |
| 2+ file | Chiedi quale (o inferisci da path/chat) |

Brand opzionale (`.cursor/brands/`): allinea mood/palette; **non** dichiarare `tono-di-voce` nel frontmatter. Testo in immagine / brief vocale: on-demand `tono-di-voce` o delega **a-copywriter**.

---

## Onboarding (prima sessione)

Raccogli: nome, mood (3 aggettivi), tecnica, palette, dettaglio, riferimenti, evitare, uso, aspect ratio, testo in immagine (default no).

Poi: compila style-brief-template → style anchor EN → salva file → 3 anteprime (`preview-render`) → conferma → aggiorna file se serve.

---

## Coerenza (sessioni successive)

Finché l'utente **non** chiede cambio stile:

- Leggi sempre il style file prima di generare
- Anteponi **style anchor** a ogni prompt
- `prompt_extend: false`; seed/size dal file salvo override task
- Negative prompt e regole coerenza del file
- Aggiungi esempi approvati dopo feedback positivo

### Cambio stile (solo esplicito)

Trigger: «cambia stile», «nuovo stile», «reset palette», …

1. Conferma: sostituire o `{nome}-v2.md`
2. Onboarding abbreviato
3. Aggiorna anchor, palette, seed se necessario

---

## Override L2

Path style, palette locale, regole «cosa evitare» — `competencies/stile-visivo/SKILL.md` nel figlio (solo delta).

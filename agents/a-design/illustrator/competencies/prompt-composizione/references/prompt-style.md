# Costruzione prompt — coerenza stile

---

## Formula

```
{style_anchor}

Subject: {soggetto richiesto dall'utente}.
Composition: {inquadratura, punto focale, spazio negativo}.
Constraints: {vincoli da style file — palette, no text, etc.}.
```

- **Style anchor**: invariato tra generazioni (dal file stile)
- **Subject**: cambia a ogni richiesta
- Scrivi in **inglese** per Qwen image salvo test su altre lingue

---

## Coerenza visiva

| Leva | Come usarla |
|------|-------------|
| Style anchor dettagliato | Tecnica, palette hex, stroke, texture, lighting |
| `prompt_extend` T2I | **`false`** — style-lock (default script) |
| `prompt_extend` I2I/edit | **`true`** consigliato (stabilità); override `--no-prompt-extend` |
| `seed` fisso | Output più simili tra varianti dello stesso soggetto |
| Negative prompt | Esclude derive (foto, 3D, clutter) |
| Esempi approvati | Incolla descrizioni di immagini già OK nel style file |

### Anti-pattern prompt (non usare)

Non aggiungere spam di qualità generica tipico dei marketplace / Quick Start locali:

- `8K`, `4K`, `Ultra HD`, `hyperdetailed`, `masterpiece`, `award-winning`, `professional photography`, `cinematic composition`, `trending on ArtStation`

La qualità e la coerenza brand restano nello **style anchor** e nel negative prompt, non in keyword decorative.

---

## Testo in immagine (solo se richiesto)

Default AF: **no text**. Se l'utente chiede testo/lettering:

1. Metti la stringa esatta tra **virgolette doppie** nel subject (`"Come Play"`)
2. Specifica **posizione** e stile (es. top center, bold sans, high contrast)
3. Evita paragrafi lunghi; preferisci titolo / label corti
4. Per layout tipo poster/infographic: descrivi gerarchia tipografica, non keyword “typography masterpiece”

---

## Edit I2I — taxonomia lean

| Tipo | Quando | Esempio subject |
|------|--------|-----------------|
| **Appearance** | Cambia look senza spostare soggetto | `change jacket to red wool, keep pose` |
| **Semantic** | Aggiungi/rimuovi/sostituisci elementi | `remove watermark text in corner` |
| **Chained** | Ritocco dopo QA | una istruzione chiara per passo; non stackare 5 fix in un prompt |

Con `--image`: default rewrite on. Con `--model qwen-image-2.0-pro --image` resta 2.0 (I2I unificato). Senza modello 2.0/edit esplicito su plus → auto `qwen-image-edit-plus`.

---

## Negative “AI look” (solo stili photoreal)

Se lo style file è fotorealistico / persone, puoi aggiungere (EN o mix corto):

`wax-figure skin, overly smooth face, plastic skin, deformed hands, extra fingers, oversaturated colors`

**Non** usarlo su flat vector / brand illustration (contrasta con lo stile).

---

## Limiti token (checklist)

| Famiglia | Budget prompt orientativo |
|----------|---------------------------|
| plus / legacy | ~700 token |
| `qwen-image-2.0*` | fino ~1300 token (istruzioni lunghe ok; resta concreto) |

---

## Onboarding — domande prima sessione

Se non esiste `.cursor/illustration-styles/*.md`, fai **una** tornata di domande (usa AskQuestion se disponibile, altrimenti elenco in chat):

1. **Nome stile / progetto** — come salvare il file (es. `agentfactory`, `shop-bio`)
2. **Mood** — 3 aggettivi (es. caldo, artigianale, moderno)
3. **Tecnica** — flat vector, watercolor, isometric, line art, collage, etc.
4. **Palette** — 3–5 colori o tonalità (chiedi hex se l'utente li ha)
5. **Dettaglio** — minimal / medio / ricco
6. **Riferimenti** — artisti, siti, moodboard (URL o descrizione)
7. **Cosa evitare** — foto, 3D, anime, testo, clutter, etc.
8. **Uso principale** — hero, icone, social, blog, prodotto
9. **Aspect ratio default** — 1:1, 16:9, 4:3, 9:16, 3:2, 2:3
10. **Testo nell'immagine** — sì/no (default: no)

Dopo le risposte:

1. Compila [style-brief-template.md](../../../style-brief-template.md)
2. Scrivi **style anchor** ricco e specifico (non generico)
3. Salva in `.cursor/illustration-styles/{nome}.md`
4. Genera **1 immagine test** con soggetto semplice; chiedi conferma o aggiustamenti
5. Aggiorna style file se l'utente chiede modifiche

---

## Cambio stile

Modifica il file stile **solo** se l'utente chiede esplicitamente:

- «cambia stile», «nuovo stile», «reset stile», «aggiorna palette», etc.

Workflow cambio stile:

1. Conferma se **sostituire** o **creare nuovo file** (es. `progetto-v2.md`)
2. Ripeti onboarding (abbreviato se l'utente indica già cosa cambia)
3. Aggiorna `created` e sezione onboarding nel file
4. Opzionale: nuovo `seed`

---

## Naming output

```
assets/images/{slug}-{YYYYMMDD}.png
public/images/...
static/illustrations/...
```

Usa kebab-case, slug dal soggetto. Se il repo ha convenzioni esistenti, seguile.

---

## Checklist pre-generazione

- [ ] Style file letto e applicato
- [ ] `prompt_extend` coerente (T2I false / I2I true salvo override)
- [ ] Negative prompt incluso
- [ ] Size coerente con uso (hero → 16:9, icona → 1:1)
- [ ] Nessun testo nell'immagine salvo richiesta (se sì: virgolette + posizione)
- [ ] Prompt entro budget famiglia modello (~700 plus / ~1300 per 2.0)

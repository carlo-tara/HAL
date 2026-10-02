---
name: qa-artefatti
kind: competency
version: 1.0.1
description: >-
  QA post-generazione: ispezione artefatti AI, scala di intervento, gate pre-consegna.
  Solo L1 (no baseline L0).
---

# Competenza L1 — qa-artefatti (a-illustrator)

Ispezione **obbligatoria** dopo ogni render finale, prima della consegna.

---

## Quando applicare

Dopo ogni immagine finale (e, se sospetta, anche su anteprime scelte).

---

## Checklist artefatti

| Artefatto | Cosa cercare |
|-----------|--------------|
| Testo spurio | Lettere, watermark, gibberish |
| **Firma / autografo** | Qualsiasi firma → preferisci rigenerare |
| **Rettangolo / patch bianca** | Patch, quadrato vuoto, texture piatta → fail anche **senza** firma visibile |
| Anatomia / oggetti | Dita extra, oggetti fusi, simmetrie rotte |
| Coerenza stile | Colore fuori palette, stile non richiesto |
| Rumore / bordi | Banding, elementi tagliati, margini sporchi |

Ispezione a zoom adeguato (idealmente 100% sul dettaglio critico).

---

## Gate angolo critico (override tipico L2)

Molti modelli lasciano firme/patch in un angolo fisso (spesso **basso-destra**).

| Livello | Comportamento |
|---------|----------------|
| L1 default | Controlla tutti i bordi; tratta firma + patch come critici |
| L2 tipico | Dichiara angolo obbligatorio (es. basso-destra) + continuità texture fino al bordo |

**Fail:** firma assente ma patch/fill visibile = ancora fail. La texture di sfondo (carta, griglia, colore) deve continuare fino al bordo nell'angolo dichiarato.

Override path: L2 `competencies/qa-artefatti/` o sezione QA nella skill illustrator del progetto.

---

## Scala di intervento

1. **Rigenera** (stesso prompt, seed diverso o variante) — default per firme
2. **Ritaglia** (se artefatto ai bordi e la composizione lo consente)
3. **Downscale** 5–10% (rumore fine)
4. **Correzione locale** — solo clone/tile da texture sana (vedi sotto); **mai fill**
5. **Scarta** → nuove anteprime (`preview-render`)

Non consegnare immagini con firma, patch bianca spurio o difetti evidenti.

---

## Correzione locale firme / patch (no fill)

Anti-pattern: rettangolo di colore pieno o `fill` sulla zona firma → **patch bianca/piatta** = fail QA anche se la firma è sparita.

Se l'utente chiede di togliere la firma **senza** rigenerare:

1. **Donor** = striscia di texture pulita dalla **stessa** immagine (stessa risoluzione del finale)
2. **Clone/tile** allineato al periodo della texture (griglia, carta, pattern); opacità piena sulla zona firma/patch
3. **Feather** solo sul bordo verso zona già sana (mai feather che rilascia la patch originale)
4. **Gate:** texture continua fino al bordo; niente zone piatte
5. Lavora sulla **res finale** (linee 1px a preview poi upscale spariscono)

Se non c'è texture donor affidabile → torna a **rigenera**.

---

## Gate pre-consegna

- [ ] Ispezione completata (incluso angolo critico L2 se dichiarato)
- [ ] Nessuna firma **e** nessuna patch/fill spurio
- [ ] Style file rispettato (palette / negative)
- [ ] Path output corretto

Override soglie QA (più rigorose per print, più tolleranti per thumb): L2 `competencies/qa-artefatti/`.

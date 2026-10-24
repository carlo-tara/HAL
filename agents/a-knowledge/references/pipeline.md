# Pipeline Knowledge — estrazione, distillazione, query

Pipeline a tre fasi che separa il lavoro **deterministico locale** dal lavoro **generativo** e sposta la scelta su **System 1** (Laya). Obiettivo: CPU minima, **zero GPU**, token minimi.

Fonte di riferimento: [`virgiliojr94/book-to-skill`](https://github.com/virgiliojr94/book-to-skill) (MIT). `a-knowledge` ne adotta la separazione estrazione/generazione e vi aggiunge selezione cost-aware, routing System 1 e cache.

---

## Fase 1 — Estrazione (locale, CPU-only, 0 GPU, 0 token)

Deterministica: nessun LLM, nessuna rete. Tool per formato in [`extraction-matrix.md`](extraction-matrix.md).

| Passo | Comando | Costo |
| ----- | ------- | ----- |
| Diagnosi dipendenze | `python3 scripts/extract.py --check` | ~0 (solo import) |
| Estrazione testo | `pdftotext -layout -enc UTF-8 book.pdf -` | ~0.1 s |
| Estrazione tecnica | `docling` (tabelle/codice) | ~1.5 s/pagina |
| Normalizzazione | `sanitize` + `detect_structure` | ~0 |

Regole ferree:

- **Default `pdftotext`/`pypdf`** (testo). `docling` **solo** se servono tabelle/codice.
- **Nessun OCR automatico**: PDF di sole immagini → stop e chiedi `ocrmypdf` (opt-in).
- **Cache workdir** (`BOOK_SKILL_WORKDIR` + `sha256` per sorgente): riprendi senza ri-estrarre.

---

## Fase 2 — Distillazione (una-tantum, modello free/flash)

È l'**unico** costo in token, pagato **una volta** per documento. Minimizzazione:

- **Chunk per capitolo**: mai l'opera intera in un prompt. Leggi capitolo-per-capitolo con `wc -w`, `grep -n`, `sed -n` e read limitati → un file `chapters/chNN-*.md` per passata.
- **`DEPTH=reference`** (capitoli lean, 800–1.800 token) come default; `study` solo su richiesta.
- **Modello free/flash** via routing Cost-First (`orcarouter/deepseek/deepseek-v4-flash-free`).
- **Batch multi-sorgente**: una estrazione per cartella/glob; salta le sorgenti rotte.

Perché non riversare l'opera nel contesto: un libro riletto una volta per capitolo (≈28 passate) costa ≈2M token input. La distillazione paga la struttura **una volta**; poi si carica solo il capitolo rilevante.

---

## Fase 3 — Query (System 1 + un capitolo)

- **Routing System 1 (Laya)**: `python3 router.py routing "<domanda>" --routes <capitoli>` sceglie il capitolo a **0 token**.
- Carica **solo** `SKILL.md` (core ~4k) + `chapters/chNN-*.md` (~1k) ≈ **5k token**, invece di riversare l'opera (24×–51× in meno).
- **Cache HAL L1** (`app/chat_cache.py`) assorbe le ripetizioni senza chiamate provider.

Dettaglio: [`context-budget.md`](context-budget.md).

---

## Modello di costo (sintesi)

| Fase | CPU | GPU | Token | Frequenza |
| ---- | --- | --- | ----- | --------- |
| Estrazione | bassa (0.1 s testo · 1.5 s/pag tecnico) | **0** | **0** | 1× per documento |
| Distillazione | — | — | free/flash | 1× per documento |
| Query | ~0 | Laya ~33 ms (opz.) | ~5k | per domanda |

---

## "O migliori" — dove `a-knowledge` batte l'uso nudo di book-to-skill

1. **Selezione estrattore cost-aware**: default testo (`pdftotext`), `docling` solo se tecnico — decisa da euristica su densità tabelle/codice, non da domanda all'utente.
2. **Zero GPU by default**: esclude Marker/MinerU/Nougat (GPU-heavy) salvo richiesta esplicita.
3. **Routing System 1 (Laya)**: scelta del capitolo a 0 token, nativa HAL.
4. **Cache doppia**: workdir (`sha256`) evita ri-estrazione (CPU); cache L1 HAL evita ri-chiamate (token).
5. **Output conforme HAL**: core `SKILL.md` < 4k token + `references/` on-demand (progressive disclosure), dentro il token budget L0.
6. **Modello free/flash** per la distillazione (Cost-First), non un modello premium.

Nessuna di queste richiede GPU: la scelta "migliore" per HAL è **CPU-first + disclosure progressiva + System 1**, non acceleratori GPU.

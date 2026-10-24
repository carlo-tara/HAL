# Budget di contesto — disclosure progressiva e routing

## Layout generato

| File | Ruolo | Token | Caricamento |
| ---- | ----- | ----- | ----------- |
| `SKILL.md` | modelli mentali + indice capitoli | ~4k (max 4k) | sempre |
| `chapters/chNN-*.md` | un capitolo | ~1k (adaptive) | on-demand |
| `glossary.md` | termini + rif. capitolo | ~1.5k | on-demand |
| `patterns.md` | tecniche / pattern | ~2k | on-demand |
| `cheatsheet.md` | regole decisionali | ~1–1.2k | on-demand |

Residente per domanda = core (~4k) + 1 capitolo (~1k) ≈ **5k token**.

## Discovery-loop tax

Un agente che legge il PDF *naviga*: rilegge la ToC, sfoglia capitoli, torna indietro. book-to-skill paga la struttura **una volta** in distillazione; in query carica solo lo slice rilevante.

| Opera | Dump contesto | Discovery loop | book-to-skill | vs dump |
| ----- | ------------: | -------------: | ------------: | ------: |
| Think Python 2 | 119k | 12k | ~5k | 24× |
| Working Backwards | 175k | 33k | ~5k | 35× |
| AI Engineering | 256k | 78k | ~5k | 51× |

## Routing System 1 (Laya) — 0 token

```bash
python3 router.py routing "<domanda>" --routes ch01 ch02 ch03   # scegli il capitolo
```

Laya decide (≈33 ms) quale capitolo caricare: nessun token speso per la navigazione.

## Cache HAL

- **L1 chat** (`app/chat_cache.py`): risposte ripetute senza costo provider.
- **Workdir estrazione**: `sha256` evita ri-estrazione (CPU).

## Misura, non dichiarare

```bash
python3 tools/discovery_tax.py --full-text <full_text.txt> --skill-dir <skill> --target-chapter N
```

## Regole token (allineate a L0)

- Core `SKILL.md` **< 4.000 token**; front-load (la compaction tronca in coda).
- Mai caricare tutti i capitoli: prima routing, poi **un** capitolo.
- `DEPTH=reference` (capitoli lean) come default; `study` solo su richiesta.

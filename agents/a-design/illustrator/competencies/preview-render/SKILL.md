---
name: preview-render
kind: competency
version: 1.0.3
description: >-
  Pipeline 3 anteprime basse risoluzione → scelta utente → render finale.
  Punta a scripts/generate-image.py (path stabili). Solo L1 (no baseline L0).
---

# Competenza L1 — preview-render (a-illustrator)

Workflow anteprime e render. **Non** chiama l'API a mano: usa lo script.

Asset: [generate-image.py](../../scripts/generate-image.py). Provider/env: [api-providers.md](../../references/api-providers.md) (restano sull'orchestratore).

---

## Quando applicare

Ogni task di generazione (salvo opt-out esplicito «solo finale» / «niente preview»).

---

## Pipeline

```
Task Progress:
- [ ] 1. Verifica .env (LLM_MODEL_IMAGE) — orchestratore / api-providers
- [ ] 2. Style file caricato (stile-visivo)
- [ ] 3. Brief: soggetto, size, path output
- [ ] 4. 3 prompt A/B/C (prompt-composizione)
- [ ] 5. 3 anteprime → presenta → attendi scelta
- [ ] 6. Render finale con prompt/seed della variante
- [ ] 7. Passa a qa-artefatti
```

### Anteprime

1. Seed diversi (`--seed 101`, `102`, `103`)
2. Output: `assets/images/.previews/{slug}-v{1,2,3}.png` (o path L2)
3. Thumb max **512 px** sul lato lungo
4. Presenta A/B/C con etichetta breve; attendi scelta o mix
5. Render finale **solo** dopo approvazione

### Script

```bash
python a-illustrator/scripts/generate-image.py \
  --env .env \
  --style .cursor/illustration-styles/nome-progetto.md \
  --subject "variante A..." \
  --seed 101 \
  --output assets/images/.previews/nome-file-v1.png
```

| Flag | Uso |
|------|-----|
| `--prompt` | Prompt completo (salta style+subject) |
| `--size` | `W*H` o alias (plus: anche `3:2`/`2:3`; 2.0: `1K`/`2K`) |
| `--seed` | Override seed |
| `--model` | Override (es. `qwen-image-2.0-pro`, `qwen-image-edit-max`) |
| `--snapshot` | Pin plus `qwen-image-plus-2026-01-09` |
| `--image` | I2I (max 3). Con 2.0* resta 2.0; su plus → edit-plus |
| `--n` | 1–6 solo multimodal (anteprime in una call); file `{stem}-N` |
| `--idempotency-key` | Se `--output` esiste → skip API |
| `--prompt-extend` / `--no-prompt-extend` | T2I default off; I2I default on |
| `--dry-run` | Payload senza API |
| `--format json` | `{ok, output\|error}` |

Exit code: `0` ok (anche cache), `1` usage, `2` auth, `3` API, `4` I/O — [api-providers.md](../../references/api-providers.md).

### Edit post-render (opzionale)

Dopo QA, ritocco mirato (appearance / semantic / un passo chained):

```bash
# Dedicato edit-plus (default se .env è plus)
python a-illustrator/scripts/generate-image.py \
  --image assets/images/finale.png \
  --subject "remove stray text, keep style" \
  --output assets/images/finale-v2.png

# I2I unificato 2.0 (nessuno switch a edit-*)
python a-illustrator/scripts/generate-image.py \
  --model qwen-image-2.0-pro \
  --image assets/images/finale.png \
  --subject "simplify background" \
  --output assets/images/finale-v2.png
```

Opz. `--n 3` per 3 candidati edit in una call. Non sostituisce le 3 anteprime A/B/C T2I.

Non usare il tool GenerateImage di Cursor — API da `.env`.

---

## Override L2

Path anteprime/finali, size default, slug naming — `competencies/preview-render/SKILL.md`.

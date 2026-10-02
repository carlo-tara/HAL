# Provider immagini — configurazione da `.env`

L'agente **non** hardcoda credenziali. Legge `.env` nella root del progetto (o path indicato).

Corpus consultivi:
- [imagencn-source.md](imagencn-source.md) — DashScope CLI surface (CC BY-NC, solo distillazione)
- [qwen-image-source.md](qwen-image-source.md) — lineage/metodologia open-weight (Apache-2.0)

---

## Selezione provider

| Variabile | Ruolo |
|-----------|--------|
| `LLM_MODEL_IMAGE` | ID provider attivo (es. `qwen`) |

Per ogni provider `{ID}` in maiuscolo (es. `QWEN`):

| Variabile | Ruolo |
|-----------|--------|
| `{ID}_MODEL_API_KEY` | Bearer token |
| `{ID}_MODEL_NAME_IMAGE` | Nome modello image (default T2I) |
| `{ID}_MODEL_URL_IMAGE` | Endpoint text-to-image (**ImageSynthesis** async) |
| `{ID}_MODEL_URL_MULTIMODAL` | Opzionale: endpoint MultiModal sync; se assente si deriva dall'host di `URL_IMAGE` |
| `{ID}_MODEL_NAME_IMAGE_EDIT` | Opzionale: default edit se `--image` su plus (`qwen-image-edit-plus`) |
| `{ID}_MODEL_SNAPSHOT` | Opzionale: id snapshot plus (default `qwen-image-plus-2026-01-09`) |
| `{ID}_MODEL_TEMPERATURE` | Opzionale; non usato da Qwen image |

Esempio attuale in HAL (plus legacy):

```env
LLM_MODEL_IMAGE=qwen
QWEN_MODEL_API_KEY=sk-...
QWEN_MODEL_NAME_IMAGE=qwen-image-plus
QWEN_MODEL_URL_IMAGE=https://dashscope-intl.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis
# opzionali:
# QWEN_MODEL_URL_MULTIMODAL=https://dashscope-intl.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation
# QWEN_MODEL_NAME_IMAGE_EDIT=qwen-image-edit-plus
# QWEN_MODEL_SNAPSHOT=qwen-image-plus-2026-01-09
```

### Regioni DashScope

| Alias tipico | Host |
|--------------|------|
| `cn` | `https://dashscope.aliyuncs.com/...` |
| `sg` / intl | `https://dashscope-intl.aliyuncs.com/...` (default AF) |
| `us` | `https://dashscope-us.aliyuncs.com/...` |

### Modelli Qwen (routing script)

| Modello | API | Note AF |
|---------|-----|--------|
| `qwen-image-plus` | ImageSynthesis **async** | Default. Size legacy max ~1328×* |
| `qwen-image-plus-2026-01-09` | idem | Snapshot — `--snapshot` |
| `qwen-image` | idem | Stessa famiglia synthesis |
| `qwen-image-2.0` / `qwen-image-2.0-pro` (+ date pin) | MultiModal **sync** | T2I **e** I2I unificati; `--model` + opz. `--image` |
| `qwen-image-max*` | MultiModal sync | Stessa API messages |
| `qwen-image-edit` / `-plus` / `-max` (+ snapshot) | MultiModal sync | Edit dedicato; auto se `--image` su modello plus |

**Routing `--image`:**
- modello già `qwen-image-2.0*` / `max*` → **resta** (I2I unificato)
- modello `edit-*` → resta
- modello plus/synthesis senza `--model` esplicito → switch a `QWEN_MODEL_NAME_IMAGE_EDIT` / `qwen-image-edit-plus`
- `--model qwen-image-plus` + `--image` → errore (usa 2.0 o edit)

---

## Qwen — ImageSynthesis (async, plus / legacy)

`POST {QWEN_MODEL_URL_IMAGE}` con `X-DashScope-Async: enable`. Poll `/tasks/{id}`.

### Size plus / legacy

| Size | Alias |
|------|-------|
| `1664*928` | `16:9` |
| `1472*1104` | `4:3` |
| `1328*1328` | `1:1` (default plus) |
| `1104*1472` | `3:4` |
| `928*1664` | `9:16` |
| `1584*1056` | `3:2` |
| `1056*1584` | `2:3` |

`n` fisso a **1**.

---

## Qwen — MultiModalConversation (sync, 2.0 T2I/I2I + edit)

`POST {host}/…/multimodal-generation/generation` — **no** async header. Timeout ~180 s.

### T2I 2.0

`messages[0].content = [{ "text": "..." }]`.

### I2I (2.0 unificato o edit-*)

`content`: 1–3 `{ "image": "<url|data:uri>" }` + un `{ "text": "istruzione" }`.

### Size 2.0 / edit

| Size | Alias |
|------|-------|
| `2048*2048` | `1:1` / `2K` |
| `2688*1536` | `16:9` |
| `1536*2688` | `9:16` |
| `2368*1728` | `4:3` |
| `1728*2368` | `3:4` |
| `1024*1024` | `1K` |

### `n` (2.0 / edit-plus / edit-max)

`--n 1..6` → più URL; file scritti come `{stem}-1.png` … se `n>1`.  
`qwen-image-edit` base: tipicamente `n=1`.

### Edit models (snapshot tipici)

| ID | Uso |
|----|-----|
| `qwen-image-edit-plus` | Default AF edit |
| `qwen-image-edit-plus-2025-10-30` / `…-2025-12-15` | Snapshot plus |
| `qwen-image-edit-max` / `…-2026-01-16` | Geometria / industrial / consistenza personaggi |
| `qwen-image-edit` | Single-image, `n=1` |

---

## Parametri comuni

| Parametro | Note |
|-----------|------|
| `prompt_extend` | **T2I:** default `false` (style-lock). **I2I/edit:** default `true` (stabilità); override `--no-prompt-extend` |
| `watermark` | `false` in produzione |
| `seed` | Passato quando supportato |
| `n` | Plus: 1; multimodal: 1–6 |

### Exit code

| Code | Label |
|------|-------|
| 0 | `SUCCESS` |
| 1 | `USAGE_ERROR` |
| 2 | `AUTH_ERROR` |
| 3 | `API_ERROR` |
| 4 | `IO_ERROR` |

`--format json` → `{"ok":true,...}` / `{"ok":false,"error":{...}}`.

---

## Script canonico

```bash
# Plus
python a-illustrator/scripts/generate-image.py \
  --style .cursor/illustration-styles/nome.md \
  --subject "hero desk" --size 16:9 --output assets/images/hero.png

# 2.0 T2I
python a-illustrator/scripts/generate-image.py \
  --model qwen-image-2.0-pro --size 1:1 --subject "..." --output out.png

# 2.0 I2I (stesso modello, niente switch a edit-plus)
python a-illustrator/scripts/generate-image.py \
  --model qwen-image-2.0-pro --image in.png \
  --subject "remove stray text" --output out.png

# Edit dedicato + batch anteprime
python a-illustrator/scripts/generate-image.py \
  --image in.png --n 3 --subject "simplify background" --output out.png

# Snapshot plus
python a-illustrator/scripts/generate-image.py --snapshot --subject "..." --output out.png
```

Flag: `--model`, `--snapshot`, `--image`, `--n`, `--idempotency-key`, `--prompt-extend` / `--no-prompt-extend`, `--size`, `--seed`, `--dry-run`, `--format json`.

---

## Estendere ad altri provider

1. Variabili `{ID}_MODEL_*` in `.env`
2. `LLM_MODEL_IMAGE={id}`
3. Handler in `generate-image.py`
4. Documenta qui

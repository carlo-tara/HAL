# Upstream Qwen-Image — pin e mapping distillazione

Corpus open-weight ([QwenLM/Qwen-Image](https://github.com/QwenLM/Qwen-Image)): **News** del README come changelog de facto; tip di prompt/edit/size.  
Regola: [`a-agentzero/references/l1-from-proto.md`](../../a-agentzero/references/l1-from-proto.md) — non copiare Diffusers/examples/prompt_utils.

| Campo | Valore |
|-------|--------|
| Remote | https://github.com/QwenLM/Qwen-Image |
| Clone locale | `vendor/qwen-image/` (gitignored) |
| Licenza | **Apache-2.0** |
| Update | `/update-qwen-image-repo` · `bash a-illustrator/scripts/update-qwen-image-repo.sh` |
| Correlato API commerciale | [imagencn-source.md](imagencn-source.md) (ID DashScope) |

<!-- PIN:START -->
| Campo | Valore |
|-------|--------|
| Commit | `6b5e1f5cec987d404be5ac6657db3b9aacb56a89` (`6b5e1f5`) |
| Data commit | 2026-02-10 15:37:32 +0800 |
| Subject | update |
| Aggiornato il | 2026-08-13 10:05 +0200 |
<!-- PIN:END -->

---

## Mapping distillazione → a-illustrator

| Pezzo upstream (News / docs) | Dove in AF | Adozione |
|------------------------------|------------|----------|
| Ratio plus `3:2` / `2:3` (1584×1056 / 1056×1584) | `QWEN_PLUS_SIZE_ALIASES` | **Adottato** |
| 2.0 = T2I + edit unificati | `--model qwen-image-2.0* --image` senza forzare edit-* | **Adottato** |
| Testo in virgolette + posizione | `prompt-style.md` § Testo in immagine | **Adottato** |
| Token lunghi 2.0 (~1300) | `prompt-style.md` checklist | **Adattato** |
| Edit: rewrite consigliato | I2I default `prompt_extend: true`; T2I `false` | **Adattato** |
| Taxonomia semantic vs appearance | `preview-render` / `prompt-style` § Edit | **Adattato** (lean) |
| `n` 1–6 multimodal | `--n` | **Adottato** |
| Edit-max / snapshot edit | `api-providers.md` | **Documentato** |
| HF `Qwen-Image-2512` ≠ ID DashScope snapshot | nota sotto | **Awareness** |
| `positive_magic` Ultra HD / 4K | — | **Rifiutato** |
| Diffusers CFG / steps / Lightning / Layered / ControlNet | — | **Fuori perimetro** |
| Dump `prompt_utils*.py` | — | **Non adottato** |

---

## Lineage HF / News → ID Model Studio (orientativo)

| Open weight / News | API tipica |
|--------------------|------------|
| `Qwen/Qwen-Image` | `qwen-image` / famiglia plus |
| `Qwen-Image-2512` (2025-12-31) | **≠** 1:1 con `qwen-image-plus-2026-01-09` (prodotti diversi) |
| Qwen-Image-2.0 (2026-02-10) | `qwen-image-2.0` / `qwen-image-2.0-pro` |
| Edit-2509 / 2511 | `qwen-image-edit-plus` / `-max` (+ date pin) |

Fonte primaria ID commerciali: Model Studio / [imagencn-source.md](imagencn-source.md), non il README GH.

---

## Critiche applicate

1. Style-first T2I: niente rewrite automatico; edit può estendere per stabilità
2. No quality spam upstream (Ultra HD / cinematic)
3. Runtime locale (Gradio, multi-GPU, CFG) fuori AF
4. Pin Apache separato da imagenCN (CC BY-NC)

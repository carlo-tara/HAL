# Upstream imagenCN — pin e mapping distillazione

Corpus esterno ([Agents365-ai/imagenCN](https://github.com/Agents365-ai/imagenCN)) usato per **criticare ed estendere** pattern DashScope / `qwen-image-plus` in a-illustrator.
Regola authorship: [`a-agentzero/references/l1-from-proto.md`](../../a-agentzero/references/l1-from-proto.md) — non copiare SKILL/script come testo definitivo.

| Campo | Valore |
|-------|--------|
| Remote | https://github.com/Agents365-ai/imagenCN |
| Clone locale | `vendor/imagencn/` (gitignored) |
| Licenza | **CC BY-NC 4.0** — solo consultazione / distillazione di idee; **non** copiare codice o SKILL verbatim in AF |
| Update | `/update-imagencn-repo` · `bash a-illustrator/scripts/update-imagencn-repo.sh` |

<!-- PIN:START -->
| Campo | Valore |
|-------|--------|
| Commit | `45f0e0c79f602ae354f1b95ccc7da72a902cb109` (`45f0e0c`) |
| Data commit | 2026-08-08 23:26:31 +0800 |
| Subject | Merge pull request #25 from Agents365-ai/feat/flux2-provider |
| Aggiornato il | 2026-08-13 09:22 +0200 |
<!-- PIN:END -->

---

## Mapping distillazione → a-illustrator

| Pezzo upstream | Dove in AF | Adozione |
|----------------|------------|----------|
| Size alias legacy `1:1`→`1328*1328` (ecc.) | `scripts/generate-image.py` `QWEN_PLUS_SIZE_ALIASES` + `api-providers.md` | **Adottato** (plus / ImageSynthesis) |
| Exit code 0–4 + `--format json` | `generate-image.py` | **Adattato** (stessi codici; JSON `{ok,…}`) |
| Regioni DashScope `cn` / `sg` / `us` | `api-providers.md` | **Documentato** (URL già in `.env`) |
| Snapshot `qwen-image-plus-2026-01-09` | `--snapshot` / `QWEN_MODEL_SNAPSHOT` | **Adottato** |
| Label plus = Legacy vs `qwen-image-2.0-*` | routing synthesis vs multimodal + size 2.0 | **Adottato** (opt-in `--model`) |
| Default `prompt_extend: true` | — | **Non adottato** (AF: `false` + style anchor) |
| Quality keywords 8K/award-winning | `prompt-style.md` anti-pattern | **Esplicitamente rifiutato** |
| Pipeline 3 prompt testo → 1 render | — | **Non adottato** (AF: 3 anteprime visive) |
| SDK `dashscope` | — | **Non adottato** (HTTP async/sync urllib) |
| Multi-cloud Ark/Hunyuan/Gemini/… | — | **Fuori perimetro** L1 |
| Edit I2I `qwen-image-edit-*` | `--image` + MultiModal sync | **Adottato** |
| `--idempotency-key` | skip se `--output` esiste | **Adottato** |

Deep dive on-demand: `vendor/imagencn/skills/imagencn/` e `docs/models.md` — **non** caricare in blocco all'avvio.

---

## Critiche applicate

1. **Style first:** `prompt_extend: false` in produzione; lo style file AF batte il raffinamento one-shot upstream
2. **Seed:** imagenCN espone `--seed` ma non lo passa a DashScope synthesis — AF lo wire già in `generate_qwen`
3. **License:** CC BY-NC → distillare parametri/API surface, non forkare il CLI
4. **2.0 ≠ plus:** API e size diverse; opt-in via `--model qwen-image-2.0-*` (endpoint multimodal derivato)
5. **Edit:** `--image` + famiglia `qwen-image-edit-*`; file locali come data-URI (no `file://` SDK-only)
6. **Testo CN in immagine:** specialità upstream; AF default no-text + delega copywriter on-demand

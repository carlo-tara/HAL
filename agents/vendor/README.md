# Vendor upstream

Clone locali di corpus esterni usati per **criticare ed estendere** competenze L1 (`a-seozoom`, `a-illustrator`, …).
Regola: [`a-agentzero/references/l1-from-proto.md`](../a-agentzero/references/l1-from-proto.md) — non dumpare i proto come testo definitivo.

## marketingskills

Clone di [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills) (MIT).

- **Path:** `vendor/marketingskills/` (gitignored)
- **Pin / mapping:** `a-seozoom/references/marketingskills-source.md`
- **Update:** `/update-marketing-repo` o `bash a-seozoom/scripts/update-marketing-repo.sh`

## claude-seo

Clone di [AgriciDaniel/claude-seo](https://github.com/AgriciDaniel/claude-seo) (MIT).

- **Path:** `vendor/claude-seo/` (gitignored)
- **Pin / mapping:** `a-seozoom/references/claude-seo-source.md`
- **Update:** `/update-claude-seo-repo` o `bash a-seozoom/scripts/update-claude-seo-repo.sh`

## seo-geo-aeo-skill (Labat)

Clone di [SNLabat/SEO-GEO-AEO-Skill](https://github.com/SNLabat/SEO-GEO-AEO-Skill) (**nessuna SPDX** — solo consultazione).

- **Path:** `vendor/seo-geo-aeo-skill/` (gitignored)
- **Pin / mapping:** `a-seozoom/references/labat-seo-geo-aeo-source.md`
- **Update:** `/update-labat-seo-geo-aeo-repo` o `bash a-seozoom/scripts/update-labat-seo-geo-aeo-repo.sh`
- **Uso:** distillare metodologia checklist in forma lean; **non** copiare verbatim `SKILL.md` né pipeline DOCX/Cowork.

## imagenCN

Clone di [Agents365-ai/imagenCN](https://github.com/Agents365-ai/imagenCN) (**CC BY-NC 4.0** — solo consultazione/distillazione).

- **Path:** `vendor/imagencn/` (gitignored)
- **Pin / mapping:** `a-illustrator/references/imagencn-source.md`
- **Update:** `/update-imagencn-repo` o `bash a-illustrator/scripts/update-imagencn-repo.sh`
- **Uso:** alias size / regioni / surface DashScope per `qwen-image-plus`; **non** copiare CLI né default `prompt_extend: true`.

## Qwen-Image

Clone di [QwenLM/Qwen-Image](https://github.com/QwenLM/Qwen-Image) (**Apache-2.0**).

- **Path:** `vendor/qwen-image/` (gitignored)
- **Pin / mapping:** `a-illustrator/references/qwen-image-source.md`
- **Update:** `/update-qwen-image-repo` o `bash a-illustrator/scripts/update-qwen-image-repo.sh`
- **Uso:** News/metodologia (testo, edit, ratio 3:2); **non** Diffusers/CFG/Lightning/Layered.

## Prima installazione

```bash
bash a-seozoom/scripts/update-marketing-repo.sh
bash a-seozoom/scripts/update-claude-seo-repo.sh
bash a-seozoom/scripts/update-labat-seo-geo-aeo-repo.sh
bash a-illustrator/scripts/update-imagencn-repo.sh
bash a-illustrator/scripts/update-qwen-image-repo.sh
```

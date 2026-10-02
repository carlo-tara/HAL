# Upstream Labat SEO-GEO-AEO — pin e mapping distillazione

Corpus istruttivo (Claude Cowork skill) usato per **checklist e UX audit**, non come codice riusabile.

| Campo | Valore |
|-------|--------|
| Remote | https://github.com/SNLabat/SEO-GEO-AEO-Skill |
| Clone locale | `vendor/seo-geo-aeo-skill/` (gitignored) |
| Autore | Alex Labat (citato in README/SKILL) |
| Licenza | **Nessuna SPDX** — niente dump verbatim di `SKILL.md` nelle competenze AF |
| Update | `/update-labat-seo-geo-aeo-repo` · `bash a-seozoom/scripts/update-labat-seo-geo-aeo-repo.sh` |

<!-- PIN:START -->
| Campo | Valore |
|-------|--------|
| Commit | `a2c8769b85813912b2b01cd12c3484f061b439fc` (`a2c8769`) |
| Data commit | 2026-03-13 10:17:32 -0500 |
| Subject | Fix typo in installation instructions for Skill |
| Aggiornato il | 2026-08-13 07:27 +0200 |
<!-- PIN:END -->

---

## Caveat legale / authorship

- Repo pubblico senza `LICENSE`: clonare solo per consultazione locale.
- Nelle skill AF: **riscrivere** checklist lean con attribution (“metodologia ispirata a Labat SEO/GEO/AEO audit”), non incollare sezioni lunghe né branding report.
- Pipeline DOCX/PDF / path Cowork `/sessions/...` / `npm docx`: **mai** adottate.

---

## Mapping distillazione → competenze a-seozoom

| Idea upstream | Competenza AF | Adozione |
|---------------|---------------|----------|
| Distinzione GEO (sintesi AI) vs AEO (snippet/PAA/voice-like) | `geo-citabilita` | Terminologia + checklist lean |
| Content for AI synthesis (factual density, entity clarity, originality) | `geo-citabilita` → `ai-extractability.md` | Distillato |
| Answer patterns 40–60 parole, definition, liste/tabelle | `geo-citabilita` + `onpage-seo` | Distillato (AEO surfaces) |
| Quick vs Full audit | `seo-audit` | Adattato a batch `seo/` (chiedere solo se scope ambiguo) |
| Priority matrix Effort × Impact + “what's working” | `seo-audit` | Formato finding esteso |
| Whole-site prima di “crea pagina X” | `seo-audit` | Principio export/sitemap/Spider |
| Onestà limiti CWV/JS/backlink | `seo-audit` | Allineato L2 / tool esterni |
| FAQ/HowTo/ClaimReview/Speakable come leve AEO Google | — | **Rifiutato** (override claude-seo + Google) |
| Score 1–10 obbligatorio | — | Non obbligatorio L1 (status qualitativo ok) |
| DOCX/PDF agency report | — | Non adottato |

---

## Critiche applicate

1. AF resta **batch SeoZoom/GSC first**, non crawl illimitato
2. Su rich results Google, **claude-seo + Search Central** battono raccomandazioni Labat stale
3. Anti-invention: niente score numerici senza evidenza in `seo/`
4. Report in chat/markdown; niente npm `docx`

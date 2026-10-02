# Upstream claude-seo — pin e mapping distillazione

Corpus esterno (MIT) usato per **criticare ed estendere** competenze SEO in a-seozoom.
Regola authorship: [`a-agentzero/references/l1-from-proto.md`](../../a-agentzero/references/l1-from-proto.md) — non copiare i proto come testo definitivo.

| Campo | Valore |
|-------|--------|
| Remote | https://github.com/AgriciDaniel/claude-seo |
| Clone locale | `vendor/claude-seo/` (gitignored) |
| Licenza | MIT © agricidaniel — vedi `vendor/claude-seo/LICENSE` |
| Update | `/update-claude-seo-repo` · `bash a-seozoom/scripts/update-claude-seo-repo.sh` |

<!-- PIN:START -->
| Campo | Valore |
|-------|--------|
| Commit | `09d37c7b66ed3ca9c6efbdb765a805a6c76a8f01` (`09d37c7`) |
| Data commit | 2026-07-20 21:37:36 +0300 |
| Subject | docs: credit issue 176 report analysis |
| Aggiornato il | 2026-08-13 07:27 +0200 |
<!-- PIN:END -->

---

## Mapping distillazione → competenze a-seozoom

| Skill / ref upstream | Competenza AF | Adozione |
|----------------------|---------------|----------|
| `seo-schema` + `deprecated-types-2024-2026.md` | `schema-markup` | Distillato: rich result retired vs vocabulary; FAQ/HowTo non leva SERP |
| `seo-geo` + `llmstxt-evidence.md` + AI optimization guide | `geo-citabilita` | Distillato: GEO=SEO per Google; llms.txt optionality; no stats-promesse |
| `seo` thinking-framework / quality gates (selettivo) | `seo-audit` | Finding falsificabili + dipendenze; no word-count gates rigidi |
| `seo-drift` comparison-rules | `seo-audit` | Regole lean batch-to-batch `seo/{YYMMDD}` — no SQLite |
| `seo-hreflang` (locale, parity, MT QA) | `hreflang-i18n` | Nuova competenza lean |
| `seo-cluster` SERP-overlap | `topic-cluster` | Nuova competenza; preferire CSV SeoZoom |
| `seo-technical` agent-friendly | `geo-citabilita` / `seo-audit` | Ponte selettivo |
| `seo-images` | `onpage-seo` | Solo checklist corta alt/LCP |
| Orchestratore `/seo`, 18 subagent, MCP, PDF, local/maps, flow, sxo, content-brief, backlinks APIs, ecommerce pack | — | **Non adottato** (vedi sotto) |

Deep dive on-demand: `vendor/claude-seo/skills/{id}/` — **non** caricare in blocco all'avvio.

---

## Non adottato

| Upstream | Motivo |
|----------|--------|
| `/seo` + 18 subagent paralleli | Runtime Claude Code; AF ha orchestratore L1 |
| MCP DataForSEO / Firecrawl / Ahrefs / Banana / … | Opt-in esterni; SeoZoom-first |
| `seo-google` PSI/CrUX/Indexing scripts | GSC/GA4 via `seo-import`; CWV = L2 |
| `seo-backlinks` Moz/Bing/CC | Export SeoZoom se presente; no DA/DR inventati |
| `seo-local` / `seo-maps` | Verticale → L2 |
| `seo-ecommerce` intero | Product in `schema-markup`; resto L2 |
| `seo-content` / brief / humanize | **a-copywriter** |
| `seo-sxo` | **a-personas** / discovery |
| `seo-flow` | Framework terzo CC BY |
| `seo-image-gen` | **a-illustrator** |
| PDF WeasyPrint / word-count gates / stats citazione come promesse | Fuori stack / anti-invention |

---

## Critiche applicate

1. **Dati first:** volumi/posizioni da `seo/{YYMMDD}/` — mai inventare
2. **Fonte primaria Google** su rich results e AI optimization; community claims solo con fonte
3. **Batch > crawl-first** per progetti con pipeline import
4. **CWV/PageSpeed** solo L2
5. Override vs Labat su FAQ/HowTo/ClaimReview come leva SERP: **claude-seo + Google vincono**

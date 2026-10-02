# Upstream marketingskills — pin e mapping distillazione

Corpus esterno (MIT) usato per **criticare ed estendere** competenze SEO in a-seozoom.
Regola authorship: [`a-agentzero/references/l1-from-proto.md`](../../a-agentzero/references/l1-from-proto.md) — non copiare i proto come testo definitivo.

| Campo | Valore |
|-------|--------|
| Remote | https://github.com/coreyhaines31/marketingskills |
| Clone locale | `vendor/marketingskills/` (gitignored) |
| Licenza | MIT © Corey Haines — vedi `vendor/marketingskills/LICENSE` |
| Update | `/update-marketing-repo` · `bash a-seozoom/scripts/update-marketing-repo.sh` |

<!-- PIN:START -->
| Campo | Valore |
|-------|--------|
| Commit | `7868cb9251fad80a73d26e488a5ad5f6c4a9f335` (`7868cb9`) |
| Data commit | 2026-07-27 18:59:01 +0000 |
| Subject | chore: sync skills with marketplace.json, plugin.json, and README |
| Aggiornato il | 2026-07-28 00:27 +0200 |
<!-- PIN:END -->

---

## Mapping distillazione → competenze a-seozoom

| Skill upstream | Competenza AF | Adozione |
|----------------|---------------|----------|
| `ai-seo` | `geo-citabilita` (+ ref AI extractability) | Distillato: pilastri structure/authority/presence, audit citabilità, bot robots; **non** stats inventate; Google people-first vs engine non-Google |
| `seo-audit` | `seo-audit` | Framework priorità crawl→index→technical→on-page; schema detection ≠ curl; CWV puntano a L2 |
| `schema` | `schema-markup` | JSON-LD, tipi comuni, validazione; WordPress → delega plugin a-wordpress se L2 |
| `programmatic-seo` | `programmatic-seo` | Playbook + qualità/thin; volumi da `seo/` non inventati |
| `site-architecture` | `site-architecture` | Gerarchia, URL, link interni, 3-click; XML sitemap resta in seo-audit |
| `content-strategy` | — | Fuori perimetro: **a-copywriter** / L2 |
| `directory-submissions` | — | Non adottato (launch/off-page catalog); corpus resta in vendor |
| `analytics` / `attribution` | — | Coperti da `seo-import` + analisi CSV |
| `competitors` / `competitor-profiling` | — | Gap keyword: `metriche-analisi`; profiling marketing fuori |
| ads, email, social, cro, … | — | Non SEO/GEO — restano solo in vendor (Ads progettuale: corpus dedicato → competenza `google-ads`) |

Deep dive on-demand (dopo update): `vendor/marketingskills/skills/{id}/` — **non** caricare in blocco all'avvio.

---

## Critiche applicate in distillazione

1. **Dati first:** ogni volume/posizione/CTR cita `seo/{YYMMDD}/`; vietato inventare metriche upstream
2. **Google vs multi-engine:** AI Overviews ≠ ChatGPT/Perplexity; non promettere markup “magici” per Google AI
3. **Schema:** non dichiarare “assente” da solo `curl`/`web_fetch` (JS injection CMS)
4. **PageSpeed/CWV:** canoni soglia in L2 / strumenti esterni, non duplicati qui
5. **Copy lungo / humanize:** delega **a-copywriter**; title/meta via `onpage-seo` + `tono-di-voce`
6. **Product-marketing.md** upstream → brief L2 / `project-brief-template.md` HAL

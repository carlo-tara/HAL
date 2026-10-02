# Upstream agent-skills / google-ads — pin e mapping distillazione

Corpus esterno (MIT) usato per **criticare ed estendere** la competenza `google-ads` in a-seozoom.
Regola authorship: [`a-agentzero/references/l1-from-proto.md`](../../a-agentzero/references/l1-from-proto.md) — non copiare i proto come testo definitivo; non adottare runtime Buddy™ / googleadsagent.ai.

| Campo | Valore |
|-------|--------|
| Remote | https://github.com/itallstartedwithaidea/agent-skills |
| Path skills | `skills/google-ads/` |
| Clone locale | `vendor/agent-skills-google-ads/` (gitignored; sparse checkout) |
| Licenza | MIT © 2026 itallstartedwithaidea — vedi `vendor/agent-skills-google-ads/LICENSE` |
| Update | `/update-google-ads-agent-skills-repo` · `bash a-seozoom/scripts/update-google-ads-agent-skills-repo.sh` |

<!-- PIN:START -->
| Campo | Valore |
|-------|--------|
| Commit | `7a04ccbde5f96d4bfe99a15a7e6fd96a7a0d4cd6` (`7a04ccb`) |
| Data commit | 2026-04-12 13:20:56 -0700 |
| Subject | chore: Update Google Ads API version v22 → v23 in README |
| Aggiornato il | 2026-09-05 08:50 +0200 |
<!-- PIN:END -->

---

## Mapping distillazione → competenza `google-ads`

| Skill upstream | Reference AF | Adozione |
|----------------|--------------|----------|
| `conversion-tracking` | `tracking-budget.md` | Gerarchia conversioni, Enhanced Conversions, no bid senza tracking verificato |
| `budget-optimization` | `tracking-budget.md` | Shift budget limitati, learning phase, IS lost to budget; no portfolio theory dump |
| `google-ads-audit` | `campaign-design.md` | Audit baseline prima di modifiche strutturali; lookback dati |
| `keyword-research` | `campaign-design.md` | Seed → ad group tematici, Search Terms → negative, match types |
| `ad-copy-generation` | `campaign-design.md` | RSA min headline/description, pin parsimonioso; copy brand → **a-copywriter** |
| `quality-score-optimization` | `campaign-design.md` | eCTR / ad relevance / landing experience; priorità per spend |
| `landing-page-audit` | `campaign-design.md` | Message match ads↔LP; CTA; CWV → **L2** |
| `pmax-optimization` | `pmax-shopping.md` | Asset group, URL expansion, brand exclusions, search themes, learning 4–6 sett. |
| `shopping-ads` | `pmax-shopping.md` | Feed titles/labels/disapproval; GMC via `seo-import` + L2 feed |
| `audience-targeting` | `pmax-shopping.md` | Signal PMax + observation su Search; min size liste |
| `remarketing-strategy` | — | Fase 2 / budget dedicati; non core sul primo test one-shot |
| `competitor-analysis` | — | Auction insights + SeoZoom gap (`metriche-analisi`); no scrape SERP inventato |

Deep dive on-demand: `vendor/agent-skills-google-ads/skills/google-ads/{id}/` — **non** caricare in blocco all'avvio.

---

## Critiche applicate in distillazione

1. **Anti-invention:** CPC, CVR, QS, ROAS solo da Ads UI / export `seo/{YYMMDD}/google/` o da benchmark **etichettati come stime** nel deliverable ROI L2
2. **No Buddy™ / MCP upstream:** output = file progetto (campaign pack, checklist, negative list), non agent SaaS
3. **Tracking first:** vietato ottimizzare bid/budget senza `purchase` (o conversione primaria) verificata
4. **Brand Search:** non automatica — solo se organico debole o competitor in Auction insights; altrimenti brand exclusions su PMax
5. **Copy RSA:** struttura Ads qui; tono/lessico → **a-copywriter** (+ L2 brand)
6. **Feed GMC:** diagnosi issue → `seo-import` / L2 plugin; non ridocumentare Merchant API qui
7. **Remarketing / Display / YouTube:** fuori dal perimetro del primo Search+Shopping test salvo richiesta esplicita
8. **API v23:** export ufficiale resta `scripts/google_ads_export.py` + token approvato; skill non richiede API live per progettare campagne

---

## Pattern ops pubblici (non vendor)

| Fonte | Uso in AF |
|-------|-----------|
| [Ryze — Claude skills Google/Meta Ads](https://www.get-ryze.ai/blog/marketing-claude-skills-google-meta-ads#the-6-most-used) (2026) | Ispirazione metodi in `competencies/google-ads/references/ops-analysis.md` (6 job + cadenza). **Non** clonato il repo marketing-skills; niente MCP Ryze commerciale obbligatorio |

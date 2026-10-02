# Google Ads — analisi operativa ricorrente (canone)

Metodi distillati (critica) da pattern pubblici tipo [Ryze — 6 most-used Claude ads skills](https://www.get-ryze.ai/blog/marketing-claude-skills-google-meta-ads#the-6-most-used) (Feb 2026 / aggiornato 2026).  
**Non** è un vendor del repo marketing-skills: solo **metodo** (input → passi → soglie → output). Dati = export Ads / CSV `seo/*/google/` / MCP read-only quando disponibile.

Principi di packaging (riuso skill HAL):

| Principio | Regola |
|-----------|--------|
| Un job = una procedura | Non mischiare “diagnosi CPA + creatività + report cliente” nello stesso run |
| Metodo ≠ dati | Skill fornisce passi; numeri solo da export/MCP — mai inventati |
| Soglie numeriche | “Spreco / anomalia / fatica” = numeri, non aggettivi |
| Output actionable | Prima summary; poi liste upload-ready (negative, pause) |
| Read-only default | Analisi e raccomandazioni; esecuzione in account solo su richiesta esplicita |
| Generazione creativa | Job separato (`campaign-design` + **a-copywriter**) — non confondere con diagnosi |

---

## Cadenza (account steady-state)

| Quando | Procedura | Trigger |
|--------|-----------|---------|
| Giornaliero (mattina) | **Anomaly check** | Sempre (anche se “niente di anomalo”) |
| CPA / costo-vendita ±&gt;15% vs periodo precedente | **CPA diagnostic** | On-trigger, non a calendario fisso |
| Mensile (o fine fase test) | **Wasted spend** | Search Terms + ads a 0 conv. |
| Prima di conversazione budget | **Budget scenarios** | Curve a rendimenti decrescenti |
| Settimana report / titolare | **Narrative** | Plain language, no gergo |
| Google: settimanale asset | Asset “Low” / CTR in calo | Equivalente Meta “creative fatigue” |
| Google-only alto leverage | Search Term mining + intent buckets | Con wasted spend |

Su **test corti** (es. sprint 14g): stessa logica, finestre e soglie € da **L2** / pack (`PLAYBOOK_FASI`).

---

## 1. CPA diagnostic

**Input:** performance campagna/AG ultimi N giorni vs N precedenti (stessa lunghezza). Colonne: spend, conv, CPA/costo-vendita, CPC, CTR, CVR, budget.

**Passi:**

1. ΔCPA (o Δ costo/vendita) totale e per campagna/AG.
2. Spezza driver: **CPC vs CVR** (cosa ha mosso di più).
3. Controlla: redistribuzione budget, creatività/annunci nuovi o in pausa, mix Search Terms / audience.
4. Ordina driver per **impatto in €** (non per “sensazione”).
5. Top 3 azioni concrete (pausa / shift ≤20–30% / stringi keyword / fix LP).

**Soglia tipica:** lancia se |ΔCPA| &gt; ~15% (L2 può stringere su test piccoli).

**Output:** tabella driver → € → azione; niente prosa senza numeri.

---

## 2. Wasted spend finder

**Input:** Search Terms, ads, (placements se Display), ultimi 30–90 gg. Spend + conversions.

**Passi:**

1. Righe con spend &gt; 0 e conversions = 0.
2. Ignora sotto **floor rumore** (default ~10€; su sprint corti L2 più basso, es. 5–10€).
3. Raggruppa per tema: intent irrilevante, geo, broad drift, placement junk, ads morti.
4. € totali per tema + % sullo spreco.

**Output:**

1. Summary (tema, €, %).
2. Lista **negative** / exclusion **upload-ready** (una per riga, no commenti).

---

## 3. Budget scenario planner

**Input:** serie giornaliera spend + conversioni (≥30 gg ideale; su test one-shot dichiara limite).

**Passi:**

1. Fit rendimento **non lineare** (scaling +50% ≠ +50% conv).
2. Scenari a 75% / 100% / 125% / 150% / 200% del budget corrente (o fasi L2).
3. Segna livello in cui CPA marginale supera target L2 / one-pager.

**Output:** tabella scenario → conv stimate → CPA; etichetta **stima**. Allineato a `tracking-budget.md` § Forecast.

---

## 4. Creative / asset fatigue (Google)

Meta ha frequency; su **Search/PMax** usa proxy:

| Segnale | Azione |
|---------|--------|
| Asset rating Low / CTR in calo 14–21 gg | Sostituisci titoli/descrizioni deboli |
| Impression alte, CTR basso post-learning | Refresh RSA (non remix a metà esperimento A/B) |
| Scaling budget | Controlla asset più spesso (brucia più in fretta) |

**Output:** lista asset urgent / warning / healthy + cosa testare al posto.

---

## 5. Client / titolare narrative

**Input:** numeri mese (o fase) vs periodo precedente.

**Output:** 4–6 frasi plain language: cosa è migliorato, cosa peggiorato, perché (1 causa), cosa si fa dopo. **Niente** acronimi senza spiegazione. Coerente con one-pager ROI L2.

---

## 6. Anomaly detection

**Input:** ieri (o ultime 24–48h) vs media mobile 7–14 gg **per campagna**.

**Flag tipici:** spike CPC, crollo CVR, surge spend, crollo impression — oltre ~2σ o soglia L2 %.

**Output per flag:** severità · causa probabile · azione consigliata. Se niente: **una riga** (“niente di anomalo”).

---

## Google-only (alto leverage, stesso spirito)

| Job | Uso |
|-----|-----|
| Search Term mining | Bucket intent: buy-now / research / competitor / irrilevante → azione per bucket |
| Keyword cannibalization | Due AG sulla stessa query → unifica o negative crociate |
| Quality Score breakdown | Priorità dove spend alto e QS basso |
| Extension / asset audit | Sitelink/callout morti o Low |

---

## Troubleshooting analisi

| Sintomo | Causa | Fix |
|---------|-------|-----|
| Output generico | Nessun numero | Allegare export / MCP; target CPA e definizione conv. |
| Numeri ≠ UI Ads | Finestra attr. / timezone / azioni diverse | Dichiarare click-through, N-day, timezone account |
| Export enorme | Contesto saturo | Filtrare 30–90 gg, spend floor, sole colonne Inputs |
| Metrica “inventata” | Modello ha stimato | “Solo dati forniti; se manca, dillo” |

Credenziali API **mai** in chat — solo MCP/config `.env`.

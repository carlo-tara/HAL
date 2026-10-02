# Google Ads — design campagne Search (canone)

Distillato da upstream keyword-research, ad-copy-generation, quality-score-optimization, landing-page-audit, google-ads-audit. Riscritto HAL.

---

## Struttura account

| Principio | Regola |
|-----------|--------|
| Una campagna = un obiettivo / intent | Non mischiare brand navigazionale e head generiche |
| Ad group tematici | 5–20 keyword affini; landing unica per AG |
| Brand Search | Solo se organico debole **o** competitor in Auction insights; altrimenti esclusioni brand su PMax |
| Negative condivise | Lista account/campagna: free, DIY, jobs, usato, riparazione, … + Search Terms settimanali |

---

## Keyword

1. Seed da prodotti/linee ad alto valore (L2 + SeoZoom/GSC) — **cita file**
2. Match: frase per test; exact su termini già convertenti; broad **solo** con smart bidding e negative forti
3. Long-tail (3+ parole) per intent acquisto
4. Search Terms: pausa/negativa prima che lo spend si accumuli
5. QS &lt; 4 persistente su keyword a spend → pausa o fix LP/ads

---

## RSA (Responsive Search Ads)

| Elemento | Minimo canone |
|----------|---------------|
| Headline | ≥10 uniche (idealmente 15), max 30 char |
| Description | ≥3–4, max 90 char |
| CTA | ≥1 headline con azione chiara |
| Pin | Solo brand/compliance; pin eccessivi abbassano ad strength |
| Message match | Stesso linguaggio della landing (non solo keyword stuffing) |

**Ruoli copy (5 Copy Blocks, L1 a-copywriter):** nel set di 15 titoli bilanciare — keyword/match · **Pain** (contrasto: silicone, stock, generico) · **Promise** (risultato sul polso) · **Proof** (materiale, made-in, compatibilità, spedizione) · CTA. Una AG = una promise primaria (no mix ipotesi). Dettaglio: `a-copywriter/references/five-copy-blocks.md`.

Tono e lessico brand → **a-copywriter**. Qui: struttura, limiti, pin, refresh.

Refresh creatività: trimestrale o se ad strength/CTR degradano con impressione sufficienti (≥~1000 impr. prima di kill variant).

---

## Quality Score (priorità)

Componenti: **expected CTR**, **ad relevance**, **landing page experience**.

Prioritizza fix sulle keyword con **spend alto**, non su long-tail a budget irrisorio.

Leve tipiche: allineare headline↔query↔H1 LP; migliorare velocità/CTA LP (CWV → L2); stringere AG troppo larghi.

---

## Landing page (lato Ads)

Checklist Ads (implementazione pagina = L2 / a-wordpress):

- [ ] URL finale = URL organica canonica del cluster
- [ ] Headline ads riflessa above-the-fold (**promise** allineata all’AG)
- [ ] Pain/promise/proof della LP coerenti con RSA (no claim Ads senza proof in pagina)
- [ ] CTA primaria visibile (mobile)
- [ ] Trust minimo / **proof** (spedizione, reso, made-in, recensioni se esistono)
- [ ] Niente noindex / redirect a pagina sbagliata

---

## Audit pre-modifica

Prima di rifare strutture: baseline 7–30 gg (spend, conv, CPA/ROAS, Search Terms, QS).  
Trova critiche (tracking rotto, disapprovals, brand cannibal) prima delle ottimizzazioni fine.

Output: finding con evidenza + azione — stesso spirito di `seo-audit` Effort×Impact.

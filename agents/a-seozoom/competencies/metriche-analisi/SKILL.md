---
name: metriche-analisi
kind: competency
version: 1.0.5
description: >-
  Analisi metriche SeoZoom (ZA/ZT/ZS/ZO/KO/KD), PagesWithPotential, cannibalizzazione,
  confronto competitor project. Solo L1 (no baseline L0).
---

# Competenza L1 — metriche-analisi (a-seozoom)

Canone analisi keyword e metriche sito. **Non inventare** volumi, posizioni o opportunità: cita sempre file + data batch in `seo/{YYMMDD}/`.

Corpus: [references/metriche-seozoom.md](references/metriche-seozoom.md).

---

## Quando applicare

Utente chiede ZO / ZS / ZT / ZA, diagnosi, gap, cannibalizzazione, priorità keyword, confronto con `seozoom-competitor/`, batch PagesWithPotential (selezione URL — l'ottimizzazione on-page passa a `onpage-seo`).

---

## Fonti metriche

| Cosa | Dove |
|------|------|
| ZA, ZT, ZS, ZO sito | `seozoom/dashboard/{domain}_metriche.json` (fallback UI SeoZoom) |
| Proxy CSV (striking distance, cali, cannibalizzazione) | `seo/{YYMMDD}/seozoom/` |
| Competitor project | `seozoom-competitor/` (globals + dashboard); **non** confondere con `{domain}_competitor.csv` |
| GSC/GA4 | `seo/{YYMMDD}/google/` se presenti |

---

## Workflow rapido ZO / ZS / ZT / ZA

1. Leggi metriche-seozoom.md — § Fonte valori, ZO vs KO, ZO vs ZS, ZT vs ZA, Workflow analisi
2. Metriche sito da dashboard JSON; se competitor attivo confronta anche `seozoom-competitor/dashboard/`
3. **ZO:** priorità keyword pos 4–20 su pagine esistenti (non ContentGap generico a pos 101)
4. **ZS / ZT:** cannibalizzazione, owner URL, ancore pagina 1, `Cambio URL` in monitored — mappa cluster/owner → anche `topic-cluster`
5. **ZA:** composizione traffico + piano ZS → ZO → ZT
6. Path contenuti / brand: skill L2
7. SERP-overlap / “una pagina o due?” quando i CSV cluster non bastano → `topic-cluster`

---

## Batch PagesWithPotential (selezione)

1. Canone: metriche-seozoom.md § Workflow batch PagesWithPotential
2. Export recente + GSC se presente
3. Sanity check keyword driver → scarta potenziale fuorviante
4. Tier impatto → passa URL selezionati a competenza `onpage-seo`

---

## Invarianti

- Ogni numero: fonte (path file) + data batch
- Distinguere competitor **project** (`seozoom-competitor/`) da competitors interni CSV
- Override soglie Vol/KO/CTR: L2 `competencies/metriche-analisi/`

---

## Validazione post-batch e confronti

1. **Non chiudere a ~24h** — GSC rolling e SeoZoom non riflettono ancora il crawl; rivaluta a **7–14 giorni** (allineato al lag 1–2 sett. in metriche-seozoom.md)
2. **Ranking ≠ owner** — posizione ↑ non è successo se la SERP owner resta un’altra URL (hub/home) invece della pagina target
3. Su «confronta» / «importa e confronta»: oltre a progetto vs competitor, riporta **Δ vs almeno 1–2 batch precedenti** (metriche dashboard + KW chiave se rilevanti); cita le date `YYMMDD`
4. **Guardrail batch precedenti:** prima di chiudere un nuovo batch, riporta nel tracker (o checklist L2) i monitor post-lag dei batch recenti sugli **stessi cluster owner**, così un intervento nuovo non regredisce owner/CTR già consolidati
5. Dettaglio owner URL / brand cluster / path script: skill L2

### Contratto confronto batch (artefatti)

Su «confronta» / «importa e confronta» tra due date `YYMMDD`:

1. Produci sempre un **JSON** di confronto + un **delta MD** (non solo narrativa).
2. Δ keyword con chiave **`(keyword, url)`** (stessa keyword su URL diverse = righe distinte); segnala `multi_url_keywords` se utile.
3. Tabella Δ dashboard (ZA/ZT/ZS/ZO/traffico/keyword/p1) da `seozoom/dashboard/*_metriche.json` se presente in entrambi i batch.
4. **Non** sovrascrivere un `comparison-summary.md` (o equivalente) hand/scorecard se il file esiste e contiene marker «scorecard» — arricchisci lo scorecard a mano; lo script aggiorna solo JSON + delta.
5. Se l’utente cita «aspettative SEO {data}», la baseline attesa è lo **scorecard + monitor** di quella data (summary + tracker L2), non solo il Δ metriche dashboard.

Path/nome script: L2 (es. `seo_compare_batches.py`).

### Mid-lag e chiusura scorecard

1. **Mid-lag** (prima di **14–21g** dal deploy): si possono annotare monitor singoli **EARLY+** / **EARLY−** e aggiornare la finestra di chiusura nel tracker; l’**aggregato batch resta EARLY** finché il lag non scade — non chiudere «per sicurezza» né promuovere a OK/FAIL prematuri.
2. A lag scaduto: chiudere formalmente i monitor EARLY → **OK / PARZ / FAIL** (non lasciarli aperti indefinitamente).
3. **Dashboard ≠ scorecard owner/CTR** — ZA/ZS/traffico ↑ non chiudono lo scorecard owner/CTR; tieni le due letture separate.
4. **Segnali deboli ≠ OK:**
   - Riga in `gsc_pages` (anche con pochi impression) ≠ successo CTR/owner — la URL può restare **FAIL**.
   - Posizione SeoZoom ↑ senza click GSC resta **FAIL**.
   - Pagina presente in `keyword_all` senza CTR/owner chiari = **PARZ**, non OK.
5. Esempi URL / soglie sito / pattern editoriali: skill L2.
# Metriche SeoZoom — glossario L1

Riferimento **multi-progetto** per interpretare metriche SeoZoom in export CSV e UI. Le skill figlie L2 aggiungono path contenuti e regole brand; non duplicare questo glossario nel L2.

**Fonte definizioni:** [Manuale SeoZoom — Glossario](https://guide.seozoom.it/module/glossario/).

---

## Metriche sito (dashboard / UI SeoZoom)

| Metrica | Sigla | Livello | Range | Interpretazione |
|---------|-------|---------|-------|-----------------|
| Zoom Opportunity | **ZO** | Sito | 0-100 | Potenziale di crescita dalle keyword gia' in *striking distance* (circa pos 4-30). ZO alta = molte keyword in rampa verso pagina 1. |
| Zoom Authority | **ZA** | Sito | 0-100 | Autorevolezza complessiva (traffico organico, trust, stabilita', opportunity). Distinta da ZO. |
| Zoom Trust | **ZT** | Sito | 0-100 | Fiducia che Google dimostra al dominio. |
| Zoom Stability | **ZS** | Sito | 0-100 | Costanza del posizionamento organico nel tempo. ZS alta = molte keyword consolidate in pagina 1; traffico non dipendente da poche posizioni fragili. Componente della ZA. |

**Composizione ZA:** traffico organico + **ZT** + **ZS** + **ZO** (osservazione empirica SERP; backlink **non** entrano nel modello SeoZoom).

---

## Fonte valori ZA / ZT / ZS / ZO

| Dove | Cosa contiene |
|------|----------------|
| **Export dashboard** — `seo/{YYMMDD}/seozoom/dashboard/{domain}_metriche.json` | Valori attuali **ZA, ZT, ZS, ZO**, traffico, keyword (+ extras keywordsstats/trafficstats) |
| **UI SeoZoom** — panoramica `/project/view/{pid}`, blocco «Metriche» | Stesso blocco (fallback se dashboard non esportata) |
| **Export CSV** (`seo/{YYMMDD}/seozoom/` o flat) | Keyword, posizioni, KO, cannibalizzazione, pagine — **non** ZA/ZT/ZS/ZO sito |

**Regola operativa:** in analisi, leggi le metriche sito da `{domain}_metriche.json` nel batch (cita path + data cartella). Se il file manca, usa UI o dichiara Limiti. I CSV restano proxy per ZT/ZS (cannibalizzazione, `Var`, cali traffico). **Non** inventare ZA/ZT.

**Trend correlati (stesso batch):** `{domain}_andamento_dominio*.csv/json`, `{domain}_andamento_annuale.csv`, `{domain}_distribuzione_keyword_storica*.csv/json`.

**`{domain}_competitor.csv`:** colonna `za` = Zoom Authority del **competitor** (benchmark). Il dominio del progetto **non** e' in questo file (vedi `metriche.json`).

---

## Progetto SeoZoom competitor vs grid competitor

Due concetti distinti — non confonderli:

| Cosa | Path / file | Significato |
|------|-------------|-------------|
| **Competitors interni** (tab Competition del progetto) | `seo/{YYMMDD}/seozoom/https___{domain}_competitor.csv` (e `dashboard/{domain}_pagine_competitor.csv`) | Domini rivali **dentro** il progetto SeoZoom principale; griglia Domain vs Domain. `pagine_competitor` = alert overlap keyword/topic (non sostituto del progetto competitor) |
| **Progetto SeoZoom competitor** | `seo/{YYMMDD}/seozoom-competitor/` | Export di un **altro progetto** SeoZoom (`SEOZOOM_PROJECT_COMPETITOR` in `.env`): dashboard + globals del sito rivale, stessa sessione login |

### Confronto metriche sito (nostro vs progetto competitor)

Quando `SEOZOOM_PROJECT_COMPETITOR` è valorizzata e l'export ha prodotto entrambe le cartelle:

1. **Nostro:** `seo/{YYMMDD}/seozoom/dashboard/{domain}_metriche.json` → ZA, ZT, ZS, ZO
2. **Competitor project:** `seo/{YYMMDD}/seozoom-competitor/dashboard/{competitor_domain}_metriche.json` → stesse metriche
3. Confronta anche keyword_all, PagesWithPotential, ContentGap, trend (`andamento_*`) citando **sempre** path + data batch da entrambe le cartelle
4. Non usare `{domain}_competitor.csv` come sostituto di `seozoom-competitor/dashboard/` — sono sorgenti diverse

Se `SEOZOOM_PROJECT_COMPETITOR` è assente/vuota: ignora `seozoom-competitor/` (comportamento legacy).

---

## Metriche keyword (CSV export)

| Metrica | Sigla / colonna CSV | Livello | Range | Interpretazione |
|---------|---------------------|---------|-------|-----------------|
| Keyword Opportunity | **KO** / `Keyword Opportunity` / `opportunity` | Keyword | 0-100 | Facilita' di superare contenuti deboli in TOP10 per quella query. KO alta = competitor in prima pagina ma poco ottimizzati. |
| Keyword Difficulty | **KD** / `Keyword Difficulty` / `keydiff` | Keyword | 0-100 | Difficolta' di rankare (autorevolezza TOP10). KD alta = SERP presidiata da domini forti. |
| Posizione | **Pos** / `Pos` / `posizione` | Keyword | 1-101+ | 1 = primo risultato; 101 = non in SERP. |

**KO vs KD:** KO misura debolezza dei contenuti in TOP10; KD misura forza dei domini in TOP10. Priorita' operativa spesso su KO alta + volume rilevante, non solo KD bassa.

---

## Soglie operative (generiche)

| Segnale | Soglia | Azione tipica |
|---------|--------|---------------|
| Striking distance | Pos 4-20 | Ottimizzazione on-page realistica; **leva principale per alzare la ZO** |
| KO alta | >= 70 | Priorita' keyword: TOP10 battibile con contenuto migliore |
| Low-KO (rapido) | KO <= 55 + Pos 4-20 | Pass opzionale su query piu' contendibili; **solo** se owner URL chiaro e intent coerente |
| Gia' forte | Pos 1-3 | Mantenimento; **leva ZS** (difendi ancore); basso impatto sulla ZO del sito |
| Var stabile | `Var` ≈ 0 su pagina 1 | Ancora stabile; priorita' difesa per ZS |
| Var alta | `Var` > 10 in pos 4-20 | Instabilita' o rampa; consolidare prima di espandere (ZS) |
| Gap assente | Pos 101 | Non rankiamo; ContentGap qui **non muove la ZO** finche' la keyword non entra in pos 4-20 |
| Volume rilevante | >= 100 (adattabile) | Impatto traffico significativo |
| GSC CTR basso | Impressioni >= 50 e CTR < 2% (28 gg, `gsc_pages` / `gsc_queries`) | Rifinitura title/meta; answer-first in intro — non nuove keyword |

Incrocio consigliato: **Pos 4-20 + KO >= 70 + volume rilevante** = quick win.

**Pass low-KO (quando richiesto):** oltre al quick win KO >= 70, filtra keyword Pos 4-20 con **KO <= 55** su URL owner gia' confermato. Priorita' a query con impressioni GSC rilevanti e CTR basso. **Escludi** query generiche / fuori intent owner anche se volume o potenziale alto (stesso sanity del batch PagesWithPotential). Non sostituisce il pass KO >= 70: e' un canale parallelo per crescita rapida a basso rischio.

---

## ZO vs KO — regola operativa

| Obiettivo | Cosa misurare | Cosa fare |
|-----------|---------------|-----------|
| Alzare **ZO** (sito) | Keyword aggregate in striking distance | Ottimizza **pagine esistenti** con keyword pos 4-20 |
| Guadagnare una **keyword** | KO per quella query | Title, meta, corpo, FAQ mirati alla query |
| Traffico futuro | ContentGap / OnPageSEO pos 101 | Nuovo contenuto o ampliamento; effetto ZO solo dopo striking distance |

**Anti-pattern:** inseguire ContentGap generico (KO alta, pos 101) aspettandosi un boost immediato della ZO.

---

## ZO vs ZS — regola operativa

| Obiettivo | Cosa misurare | Cosa fare |
|-----------|---------------|-----------|
| Alzare **ZO** (sito) | Keyword in striking distance (pos 4-20) | Ottimizza pagine esistenti; spingi keyword verso pagina 1 |
| Alzare **ZS** (sito) | Costanza posizionamenti nel tempo | Consolida pagina 1, risolvi cannibalizzazione, difendi ancore, diversifica keyword |
| Guadagnare una **keyword** | KO per quella query | Title, meta, corpo, FAQ mirati alla query |
| Traffico futuro | ContentGap / OnPageSEO pos 101 | Nuovo contenuto; effetto ZO solo dopo striking distance; **non** leva ZS immediata |

**Matrice leve:**

| Azione | Muove ZO | Muove ZS |
|--------|---------|----------|
| Ottimizzare keyword pos 4-20 | Si | Solo se poi consolidate in pagina 1 |
| Consolidare pos 1-3 esistenti | Basso | Si |
| Risolvere cannibalizzazione | Indiretto | Si |
| ContentGap / keyword nuove a pos 101 | Futuro | No (aumenta volatilita') |
| Internal linking verso owner URL | Indiretto | Si |

**Anti-pattern ZS:** spingere crescita (ContentGap, nuove pagine) senza consolidare ancore esistenti o risolvere cannibalizzazione — aumenta volatilita', non la ZS.

Validazione ZS: valutare **andamento mensile**, non valore assoluto puntuale (lag simile a ZO: 1-2 settimane export SeoZoom).

---

## ZT vs ZA — regola operativa

| Segnale | Interpretazione | Azione tipica |
|---------|-----------------|---------------|
| **ZT > ZA** | Google si fida del dominio piu' di quanto l'autorite' complessiva suggerisca | Priorita' su **ZS** (cannibalizzazione, owner URL, `Cambio URL` in `monitored.csv`), difesa ancore pos 1-3, E-E-A-T — non backlink |
| **ZT ≈ ZA** | Trust e autorite' allineati | Bilancia ZO (striking distance) e ZS (consolidamento) |
| **ZT < ZA** | Autorite' percepita alta ma fiducia fragile | Audit qualita'/UX, errori Spider su pagine che rankano, CTR GSC basso |
| **Metriche sito tutte basse (< 30) e ZO minima** | Collo di bottiglia = striking distance, non solo stabilita' | Priorita' **ZO** (pos 4-20) **in parallelo** a ZS; se ZT > ZA con gap ≤ ~5 punti, **non** limitarsi a cannibalizzazione |

**Leve ZT (indirette, lag settimane/mesi):** risolvere cannibalizzazione; stabilizzare pos 1-3 (`Var` ≈ 0); contenuto affidabile e FAQ citabili; solidita' tecnica su URL indicizzate. **Non** leva immediata: ContentGap a pos 101, backlink (fuori modello ZA SeoZoom).

**Anti-pattern ZT:** keyword stuffing, oscillazioni URL, riscritture radicali su ancore pagina 1, competizione interna home/hub/guide.

Validazione ZT: trend mensile in UI SeoZoom; lag 1-2 settimane post-intervento on-page.

---

## Workflow analisi «Come migliorare la ZO?»

1. **Opportunity Finder** (UI SeoZoom) o `{domain}_PagesWithPotential.csv` — URL con Volume non ottenuto / Traffico Potenziale alto.
2. `{domain}_keyword_all.csv` o `*__all_keywords.csv` — filtra **pos 4-20**, ordina per Volume; incrocia **KO >= 70**.
3. `{domain}_monitored.csv` — keyword monitorate in rampa con storico posizioni.
4. **Se richiesto (pass low-KO):** stesso CSV pos 4-20 con **KO <= 55**, solo URL owner + intent coerente; priorita' GSC impressioni alte / CTR basso (§ Soglie operative).
5. Raccomanda ottimizzazione **on-page** su URL esistenti (title, meta, H2, FAQ, link interni). Evita nuove pagine generiche fuori cluster del sito salvo gap strategico confermato.
6. Escludi ContentGap a pos 101 come leva ZO immediata; citale come opportunita' a medio termine.

Validazione post-intervento: lag SeoZoom 1-2 settimane; GSC/GA4 per CTR e engagement immediati se export presente.

---

## Workflow batch `{domain}_PagesWithPotential.csv`

Batch end-to-end sulle URL con `Traffico Potenziale` alto (top N, es. 10). **Prerequisito:** sanity check keyword driver — il potenziale aggregato puo' essere fuorviante.

1. Ordina `{domain}_PagesWithPotential.csv` per `Traffico Potenziale` decrescente.
2. Per ogni URL candidata: apri `*__all_keywords.csv` per-URL e riga dominante in `{domain}_keyword_all.csv` (volume / potenziale / pos).
3. **Scarta driver fuorvianti** (non ottimizzare la pagina per quella keyword):
   - **Typo brand / navigational** su URL non-owner (nome brand concatenato, query «cos'e' il brand» su hub indice o sottopagina tassonomica)
   - **Query generica** in altra lingua o fuori intent pagina (volume alto, intent mismatch con contenuto)
   - **Omonimie / query irrilevanti** al business del sito
   - **Fuori perimetro:** keyword ad alto volume fuori dal core tematico del sito — non inseguire solo perché un competitor topic le ranka; serve richiesta esplicita o piano L2
4. **Incrocia GSC** (`google/gsc_pages_*.csv`, `google/gsc_queries_*.csv`): impressioni alte + CTR ~0 → leva title/meta e intro answer-first.
5. **Incrocia** `{domain}_PagesWithTrafficDown.csv` (urgenza), `Menzioni AI` = 0 (priorita' GEO), `{domain}_Cannibalization.csv` (owner URL).
6. Ottimizza on-page solo URL con driver valido e owner URL confermato. Dettaglio path, tono, build: skill figlia L2.

**Anti-pattern:** inseguire `Traffico Potenziale` senza verificare intent, owner URL e cannibalizzazione.

---

## Pattern ottimizzazione on-page (generico)

| Pattern | Regola |
|---------|--------|
| **FAQ citabili** | Sezione FAQ in sorgente contenuto (markdown, CMS, template). Answer-first 2-4 frasi. |
| **JSON-LD FAQPage** | Se il build/CMS genera `FAQPage` dalla stessa sorgente FAQ, **non** duplicare con blocchi JSON-LD commentati o inline ridondanti nei sorgenti. |
| **Ricerca on-site** | Meta keyword / blocchi search interni (Pagefind, Algolia, ecc.): non indicizzare termini brand o cluster di altre pagine **owner** — smista come Google (skill L2 per path e implementazione). |
| **Varianti tool vs copy** | Se SeoZoom/GSC tracciano varianti errate o non brand, vince tono/lingua naturale del sito (skill copy L2); varianti reali citabili in FAQ, non forzate nel title. |

---

## Workflow analisi «Come migliorare la ZS?»

1. `{domain}_Cannibalization.csv` (o `.xlsx`) — cluster con **URL multiple** per stessa keyword; assegna **owner URL** unico per cluster. Leva prioritaria su siti multi-pagina (home, hub, guide).
2. `{domain}_PagesWithTrafficDown.csv` — pagine con calo visite; segnale instabilita' locale.
3. `{domain}_keyword_all.csv` — **ancore stabili** (pos 1-3, colonna `Var` ≈ 0) da difendere; keyword pos 4-10 con `Var` alta da **consolidare** (non solo spingere verso pagina 1).
4. `{domain}_MainPages.csv` — concentrazione traffico su poche keyword brand; rischio ZS se una keyword pesa troppo sul totale.
5. Raccomanda: risolvere cannibalizzazione, consolidare owner URL, difendere ancore, diversificare keyword in pagina 1. Escludi ContentGap a pos 101 come leva ZS immediata.

Validazione post-intervento: lag SeoZoom 1-2 settimane; trend mensile ZS in UI SeoZoom.

---

## Workflow analisi «Come migliorare la ZA?»

1. **Baseline:** leggi **ZA, ZT, ZS, ZO** da `seozoom/dashboard/{domain}_metriche.json` (fallback UI panoramica). Annota data batch — snapshot numerici solo in skill figlia L2 se il progetto li mantiene.
2. **Composizione:** ZA = traffico organico + ZT + ZS + ZO; backlink **non** entrano nel modello SeoZoom.
3. **Diagnosi:** § ZT vs ZA sopra; se **tutte e quattro le metriche < 30** e **ZO è la minima**, leva primaria = striking distance (pos 4-20) **in parallelo** a ZS — anche con ZT > ZA e gap ≤ ~5 punti.
4. **Piano tipico (ordine):** (1) **ZS** — `{domain}_Cannibalization.csv`, owner URL, `{domain}_PagesWithTrafficDown.csv`; (2) **ZO** — `{domain}_keyword_all.csv` pos 4-20, KO >= 70; (3) **ZT** — FAQ citabili, audit Spider su URL che rankano, GSC CTR basso.
5. **Proxy CSV** (export in `seo/{YYMMDD}/seozoom/` o flat valido): Cannibalization, PagesWithTrafficDown, keyword_all, MainPages, monitored — come § Workflow ZT-ZA.
6. **Benchmark:** `{domain}_competitor.csv` colonna `za` solo per competitor; ZA progetto da UI.
7. **Escludi** backlink e ContentGap a pos 101 come leva ZA immediata.
8. Raccomanda max 3-5 azioni on-page. Dettaglio path/brand: skill figlia L2.

Validazione post-intervento: lag SeoZoom 1-2 settimane; trend mensile ZA in UI SeoZoom; GSC/GA4 per traffico e CTR.

---

## Workflow analisi «Come migliorare la ZT?» / diagnosi ZT-ZA

1. **Baseline:** leggi **ZA, ZT, ZS, ZO** da `seozoom/dashboard/{domain}_metriche.json` (fallback UI panoramica). Annota data batch — **non** fissare valori numerici nelle skill.
2. **Interpretazione:** se **ZT > ZA**, priorita' stabilita' e cannibalizzazione; se **ZT < ZA**, priorita' qualita'/trust segnali.
3. **Proxy CSV** (export in `seo/{YYMMDD}/seozoom/` o flat valido):
   - `{domain}_Cannibalization.csv` — URL multiple per stessa keyword; owner unico per cluster
   - `{domain}_PagesWithTrafficDown.csv` — cali locali
   - `{domain}_monitored.csv` — `Cambio URL = 1`, `Var` negativa su ancore
   - `{domain}_MainPages.csv` — concentrazione traffico (rischio ZS/ZT se pochissime URL pesano)
   - GSC — impressioni alte + 0 click (CTR / segnale trust)
4. **Benchmark:** `{domain}_competitor.csv` colonna `za` solo per competitor; ZA progetto da UI.
5. **Raccomanda** max 3-5 azioni on-page (owner URL, consolidamento, FAQ GEO, audit Spider mirato). Dettaglio path/brand: skill figlia L2.
6. Escludi ContentGap a pos 101 come leva ZT immediata.

Validazione post-intervento: lag SeoZoom 1-2 settimane; GSC/GA4 per CTR e engagement.

---

## File CSV correlati (nomi tipici post-export)

| File | Uso per ZO | Uso per ZS | Uso per ZT | Uso per ZA |
|------|------------|------------|------------|------------|
| `{domain}_PagesWithPotential.csv` | Priorita' URL per traffico potenziale | — | — | Proxy ZO (striking distance) |
| `{domain}_keyword_all.csv` | Striking distance + volume | Ancore (`Var` ≈ 0), volatilita' (`Var` alta) | Segnali instabilita' | Proxy ZO + ZS |
| `{domain}_monitored.csv` | Keyword in rampa, KO, andamento | Storico posizioni, `Cambio URL` | `Cambio URL`, oscillazioni | Proxy ZS/ZT |
| `{domain}_Cannibalization.csv` | — | **Leva prioritaria** — URL in competizione | **Leva prioritaria** — trust / owner URL | Proxy ZS + ZT |
| `{domain}_PagesWithTrafficDown.csv` | Urgenza revisione | Instabilita' locale | Calo visibilita' locale | Proxy ZS |
| `{domain}_MainPages.csv` | Pagine strategiche | Concentrazione traffico | Concentrazione / ancore | Concentrazione / rischio ZS |
| `{domain}_competitor.csv` | — | — | Benchmark `za` competitor | Benchmark `za` competitor (non dominio progetto) |
| `{domain}_ContentGap.csv` | Gap competitor — **non** leva ZO immediata se pos 101 | **Non** leva ZS immediata | **Non** leva ZT immediata | **Non** leva ZA immediata |
| `clusters_keyword.csv` | Volume non ottenuto per cluster | — | — | — |
| `*__all_keywords.csv` | Dettaglio per singola URL | Dettaglio per singola URL | Dettaglio per singola URL | Dettaglio per singola URL |

Nomi esatti: manifest in `seo/export-manifest.json` del progetto.

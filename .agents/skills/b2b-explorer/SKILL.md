---
name: b2b-explorer
extends: a-b2b
version: 1.2.4
extends-version: 2.2.1
description: >-
  Delta progetto B2B in WTP App: guardrail pilota ICP 6–50 ∩ bacino Chiasso ~3h (Aug-Oct 2026),
  capacity 3+3/sett, GTM a quattro bucket, tre livelli modulari L1/L2/L3, welfare società IT,
  path enrichment in .shared/b2b.
  Use with a-b2b for pilot design, enrichment scripts, and cross-agent handoffs.
---

# b2b-explorer — delta L2

Skill figlia. Eredita `a-agentzero` → `a-b2b` (facade) → **questo file**.

`a-b2b` è **facade** verso `a-product` § **Profilo B2B** (offer/validation → `a-po`; cascade enrichment → `a-enrichment`). Questo L2 fornisce solo guardrail, path e delta progetto — non rieseguire workflow orchestra nel body.

## Progetto

| Campo             | Valore                                                          |
| ----------------- | --------------------------------------------------------------- |
| Nome              | b2b-explorer (in WTP App)                                       |
| Working directory | `/var/www/WTP_App`                                              |
| App explorer      | `src/explorer/b2b/`                                             |
| Dati B2B          | `.shared/b2b/`                                                  |
| Env               | `.env` **nella root WTP** (niente `.env` in `src/explorer/b2b`) |

**Layout repo:** Sales Coach in `src/wtp/`; shell auth in `src/auth/`; in root `data/`, `.shared/`. Explorer in `src/explorer/b2b/`. Albero in `README.md`. Non spostare `.shared` sotto `src/wtp`.

## Pilot guardrails (hard constraints)

SoT operativo: [`strategia-gtm-capacity-nurture-2026-09.md`](../../projects/b2b-piccoleimprese/05-strategia/strategia-gtm-capacity-nurture-2026-09.md) + [`notes.md`](../../projects/b2b-piccoleimprese/notes.md). Aggiornamento hard da **ok PO esplicito** (`/cycle P1` 2026-09-29) — non ri-allargare silenziosamente oltre questi bullet.

- Geography: bacino ricerca **~3h auto da Chiasso** (LO + PI + ER + VE; **no CH**); operatività spesso ≤2h (es. Milano). Live + sportello nel bacino.
- ICP: companies with **6–50** employees (Now / test PMF). Horizon Later (~1000) **fuori** hard Now.
- Primary counterpart: entrepreneur/decision-maker.
- Product perimeter: `MWK + Pensioni + ETF` (Spread **out** of commercial SKU; ETF live is enough).
- Commercial offer: **tre livelli modulari** — L1 MWK+Pensioni; L2 Pensioni+ETF live; L3 solo ETF live. Terminologia **Base/Premium superata** (A–D retired 2026-08-17). Tutor e sportello 8h = add-on/delivery, non nei tre livelli di default.
- New financial products: not allowed in this pilot.
- Welfare delivery: **Italian-registered company only**.
- Pricing (forbice negoziale, PRD v0.9): quota base **€5–7k** per contratto; L1 **+€100/pax**; L2/L3 **+(€200–300)/pax**; max **20** pax listino generico. Non quotare il vecchio Premium **€10k flat** come listino unico.
- Capacity: max **3 appuntamenti in presenza + 3 online / settimana**; overflow = hold engagement (demo / assessment / waitlist), non silenzio.
- GTM: **quattro bucket** — owned/advocacy (sottoliste, non solo Inner Circle) · owned/nicchie · tiepidi · freddi. Close 2026 sulle code che arrivano ad appuntamento; warming su freddi/tiepidi early **senza** close a volume. (Storico 70/30 warm/warming = retired come hard.)
- Timeline: Aug–Oct 2026 (PMF prova); volume objective **5–6 closes** by end-2026 (revenue follows listino, not €50–60k on 10k flat).

If a request conflicts, flag it and propose a compliant alternative.

**Storico (non hard):** pilota iniziale 6–20 / Lombardia ≤2h / 70/30 — retired nei bullet sopra. Export legacy: `npm run export:icp-list:legacy-chiasso-2h` → `icp-6-20-chiasso-2h.*`.

### Inventario SOM / geo operativa

- Owned stock: `projects/b2b-piccoleimprese/02-personas-e-target/som-inventory-icp-v0.{csv,md}` — score3 decisore + size numerico 6–50; 1 contatto/org.
- Fit 1–10; **Tier A** = fit ≥8 + `in_bacino` + `totalPaidCount > 0`.
- Bacino soft documentato: LO + PI + ER + VE (no CH). Sede: preferenza HQ company → city contatto → IP.
- Distanza hub Chiasso: colonne `dist_chiasso_km` / `dist_chiasso_h_est` / banda (`~2h` / `~3h` / `>3.5h`) = linea d’aria + stima auto, **non** isocrona GIS. Guardrail hard = banda **~3h** (molte sedi utili restano ~2h).
- **Ruolo GTM:** priorità capacity su advocacy + nicchie + tiepidi pronti; cold lookalike fit≥9 = warming (bucket freddi) — non close a volume.

## Product artifacts

Path progetto: [`product/README.md`](../../product/README.md). Canone in `product/`.

**Cascata post-strategia:** ordine canone `a-product` § **Profilo B2B** / Cascata post-strategia (ingresso facade `a-b2b`). Path locali: `projects/b2b-piccoleimprese/` (notes, canvas, PRD snapshot, dry-run/playbook/proposta/UA). Fonti incontri in `projects/b2b-piccoleimprese/00-docs/` e/o `src/explorer/b2b/docs/`. Riscrivere mapping / scheda-prodotti / blocco-perche-ora **solo se** cambiano livelli L1/L2/L3 o framing OCSE.

**PRD e strategia (formato):** canone L1 `a-po` / `prd-authoring` § Formato evidenza. Path canone template: `product/prd.md`.

**PRD pilota (fonte viva):** [`projects/b2b-piccoleimprese/01-requisiti/PRD_b2b_v1-0-1.md`](../../projects/b2b-piccoleimprese/01-requisiti/PRD_b2b_v1-0-1.md) — unica fonte per Job Stories (niente mirror `prd_js_*`). Formato: `Quando` / `voglio` / `così da`. **ID canoniche = chiavi Jira `WB-*`** (`00-docs/Jira.csv`: epiche `WB-10`–`WB-16`, story `WB-17`–`WB-40`; **`WB-41`…`WB-46` riservati PRD** finché creati in Jira — sync per **riepilogo/titolo**). **Sync PRD↔Jira:** mappare per **riepilogo/titolo** sull’export CSV — non reinventare una numerazione parallela; in sessione delta PRD aggiornare solo la lista **Sync Jira** nel PRD — **non** creare ticket Jira finché non richiesto. Mappa dipendenze: [`dipendenze-job-stories.md`](../../projects/b2b-piccoleimprese/01-requisiti/dipendenze-job-stories.md) (non nel PRD). **Anti-pattern:** non ripristinare nel PRD una tabella «Allineamento ID Jira» / mapping storici ID↔`WB-*` (resta nel CSV + titoli); non riscrivere snapshot storici (`prd_js_*`, `prd-2026-08-*`) oltre una riga “storico → canone”.

**GTM anticipato (prima del merge PRD):** se notes/strategia avanzano sul PRD Stable, scrivere/aggiornare una **`proposta-delta-prd-*.md`** in `01-requisiti/` e **non** editare `PRD_b2b_v1-0-1.md` finché il PO non spunta la checklist di accettazione. Canone operativo GTM = notes + strategia set; canone requisiti Job Stories = PRD Stable.
**Delta PRD (funnel commerciale) — ordine obbligatorio in sessione PRD:**

1. Proporre/estendere **AC** prima su **WB-42**, poi **WB-24**, poi **WB-26** (spine funnel / pack / discovery).
2. Se lo scope tocca post-firma o value loop: poi **WB-31**, **WB-36**.
3. **Nessuna nuova epica** (WB-10…WB-16 fissi).
4. **WB-43** (campagna) e **WB-44** (step 2 a 6 mesi) sotto WB-16 — riusarle/estendere; **WB-45** (landing interattiva) e **WB-46** (naming ETF) sono riservate — non creare story parallele per gli stessi outcome.
5. **Nuova JS solo** se manca un outcome non assorbibile in AC; aggiornare `dipendenze-job-stories.md`.
6. **Anti-pattern delta MKTG:** non collassare l’offerta a due livelli (menu L1+L2 **non** ritira L3); non aprire una survey/prequalifica inbound separata da **WB-45**; su **WB-46** non inventare il nome pubblico di ETF — solo AC «proposta + mapping + ok PO».
   Rule always-on sul path: [`docs/rules/b2b-prd-delta.mdc`](../../docs/rules/b2b-prd-delta.mdc).

Spine funnel = **WB-42** (stages: prep/analisi → discovery → interesse **A/B/C** → appuntamento/pre-accordo → won/firma; owner commerciale del deal; SLA pre-accordo→firma ≤7gg lav., distinto da onboarding post-firma). Pack **WB-24** = solvibilità/visure/N/interlocutore **+** materiale info generiche + framing settore. Post-firma: piano ≤1 sett + kick-off/avvio ≤15gg (**WB-31**); area aperta/email dominio MS → **OQ**, non AC tecnici inventati. Survey gradimento ~90gg + trigger recensione se segnale ok → **WB-36**; upsell step 2 a 6 mesi ripetibile → **WB-44** (WB-16); Blocco A resta istanza 3diEmme. Campagna Mese Educazione Finanziaria → **WB-43** (Owner _Team Marketing_, Persona **P2**), CTA primaria a landing interattiva **WB-45** (landing offerta = **WB-40**), warming non close; **distinta** da prontezza contratti novembre (WB-30). Brochure pre-discovery + menu L1/L2 (L3 resta in scheda) → **WB-27**; milestone chiamate lista calda ≤**17 nov 2026** → **WB-25**; naming pubblico modulo ETF → **WB-46** (WB-12; nome solo dopo ok PO).

**Metadata JS:**

- **Owner** = ruolo di responsabilità del task (**non** nome di persona). Esempi usati: _Product Owner_, _Responsabile Commerciale del cliente_, _Responsabile team commerciale B2B_, _Responsabile commerciale 3diEmme (con supervisione PO)_, _Responsabile processi interni_, _Team Marketing_, _Marketing_.
- **Persona** = target della story: **codice + titolo** (es. `P1 — Titolare (lista calda)`), mai solo `P1`.
- **Owner vs AC:** le AC possono ancora nominare persone per assegnazioni operative (sales ops, PO).
- **POV cliente (Blocco B da WB-23 in poi):** Persona = **P1 / P2 / P4 / P5**; testo `Quando`/`voglio`/`così da` dal punto di vista cliente. Owner può restare ruolo interno MS. P6 resta per story tipicamente interne (es. Blocco A case ops) se non diversamente indicato.
- **Titoli JS:** se la story descrive un processo da definire/disegnare, preferire framing _Design / Definizione / Redazione …_ (non solo nome artefatto).
- **Dipende da:** ogni story dichiara prerequisiti come `WB-xx — Titolo` (campo **Dipende da** / **Dipende da (opzionale)**); fondazione = nessuna. Mantenere allineata la mappa in [`dipendenze-job-stories.md`](../../projects/b2b-piccoleimprese/01-requisiti/dipendenze-job-stories.md). Stesso formato `WB-xx — Titolo` anche nei rimandi in AC / DoD / backlog (non solo ID nudo).
- **Roadmap / CoD (default priorità, non sostituisce Epic Map):** ordinare le JS per minimizzare Cost of Delay — (1) zero-deps ad alto fan-out o CoD mercato/compliance (es. segmentazione, scheda, pricing, reporting privacy); (2) motore commerciale + track calendario (lista, playbook, contratto, call/proposta, 3diEmme); (3) deal/erogazione (perimetro, kick-off, indicatori, onboarding, delivery); (4) scala/learning a CoD più basso o post-segnale (landing offerta/interattiva, scheda CRM, update playbook, cold, campagna warming). Parallelizzare solo a CoD simile.
- **Assegnazione epic (tooling commerciale):** configuratore / quotazione in-call → **WB-12**; naming commerciale percorso (ex ETF) → **WB-12**; definizione flusso/funnel vendite su Jira → **WB-13** (Owner di default **Product Owner**, non lead commerciale). Pack pre-incontro **analisi aziendale** (solvibilità, visure, N tot vs N formazione, tipo interlocutore, info generiche + settore) → arricchisce **WB-24** (segmentazione), non una JS separata di default. Campagna marketing warming (es. nov) → **WB-16**; landing interattiva inbound → **WB-16**; check step 2 a 6 mesi → **WB-16**.

**PRD igiene (Backlog / Domande aperte / Sync Jira):** togliere dal Backlog voci **done**, **ko**, o già coperte da card Jira; dalle Domande aperte togliere OQ **risolte** o chiuse altrove (vincoli/NON-goals/Jira). Tenere solo item ancora aperti e non ridondanti. Sotto Backlog mantenere la lista **Sync Jira** (card da creare/aggiornare per titolo) allineata al PRD vivo. **Anti-pattern JS:** non creare story per HubSpot (già **WB-39**), provvigioni/incentivi % sales (**NON-goal**), formazione nuovi sales (implicita in playbook WB-28/29), o survey prequalifica inbound fuori **WB-45**.

**Epiche Blocco B (outcome / funnel processo ripetibile, PRD v0.9.1+):** WB-12 offerta quotabile (incl. **WB-46** naming) → WB-13 pipeline a **decisione esplicita** (WB-42 spine A/B/C) → WB-14 deal pronto all'erogazione (WB-30–33; SLA avvio ≤15gg) → WB-15 **erogazione come da promessa cliente** (survey/recensione via WB-36) → WB-16 processo che scala (unit economics, warming, **WB-43** campagna, **WB-45** landing interattiva, **WB-44** step 2 a 6 mesi). Negli outcome epic: linguaggio plain (es. «niente attività extra non concordate»), non gergo (_scope creep_). Fonte contratti: `00-docs/Guida ai Contratti di Welfare Aziendale.pdf`.

**Fonti strategia:** incontri 13/17 ago vincono su A–D ritirata e su “cold solo Later”. Listino Enrico 17 ago sera (forfait + €/pax; Spread fuori) vince sul vecchio 10k flat. **Minuta/trascrizione riunione > riepilogo automatico Gemini** (il summary può collassare L1/L2/L3 a «2 livelli» o omettere capacity 3+3) — verificare decisioni contro la trascrizione in `00-docs/` prima di aggiornare thesis. `Gemini Strategy.md` = complementare — non merge cieco; non citare “Gemini” nel PRD.

**Copy B2B IT:** usare **riconoscimento** (non “riconoscenza”) per segnale al team / retention.

**Funding / welfare:** non promettere “impatto cassa ≈0” o fondi in pitch a volume finché keep/kill partner non è documentato. Erogazione welfare = **società con sede in Italia**. MS nel pilota = **fornitore di formazione** (TUIR, GDPR, reporting aggregato al datore); **portale welfare full** (crediti, fringe/voucher, sync payroll/LUL, fee %) **fuori pilota** — backlog/SOP o partner esterno.

## Package status

Tre livelli modulari (**L1** MWK+Pensioni **+€100/pax**; **L2** Pensioni+ETF **+(€200–300)/pax**; **L3** solo ETF **+(€200–300)/pax**) + quota base **€5–7k** (forbice). Spread **out**. Base/Premium = storico. Mapping Guida contratti: L1 ≈ Primo livello; L2 ≈ Secondo completo; L3 ≈ Secondo solo ETF. Pitch “menu” (WB-27) evidenzia L1+L2 confrontabili; **L3 non ritirato**.

Incomplete intake: [references/project-brief-template.md](references/project-brief-template.md) se presente.

## Enrichment paths (master in this repo)

| Tipo                            | Path / env                                                                                                                                                                                                                                                                                                    |
| ------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Enrichment dir                  | `.shared/b2b/` (`B2B_ENRICHMENT_DIR`)                                                                                                                                                                                                                                                                         |
| Master Postgres                 | PostgreSQL di produzione, schema `enrichment.*` via `PGDATABASE_URI_PROD` — **unica SoT** anagrafiche/geo B2B (`npm run build:enrichment`; alias `build:sqlite`, nome storico). PostgreSQL locale è riservato ai test (`wtp_test`); l'ex master SQLite è archiviato non accessibile in `.shared/b2b/archive/` |
| Reports score3                  | `.shared/b2b/reports/b2b_score3/` (batch storico / export; non SoT runtime UI)                                                                                                                                                                                                                                |
| Viz explorer (export opzionale) | `.shared/b2b/viz/b2b-score3-clusters-data.json`                                                                                                                                                                                                                                                               |
| Live explorer API               | `GET /api/wtp/explorer/score3-clusters` — coorte PG (`enrichment.clienti` enriched) + lookup enrichment + acquisti Mongo; `contentMode: live_pg_mongo`. Limite: `WTP_EXPLORER_SCORE3_LIMIT` (default 800, cap 5000). Domain: `src/wtp/backend/src/explorer/score3Clusters*`                                   |
| Scripts                         | `src/explorer/b2b/scripts/` · libs `src/explorer/b2b/scripts/lib/`                                                                                                                                                                                                                                            |
| Env                             | **solo** `/var/www/WTP_App/.env`                                                                                                                                                                                                                                                                              |
| Lookalike cold fit≥9            | `src/explorer/b2b/scripts/research-lookalike-leadmagic-fit9.js` · checkpoint `.shared/b2b/lookalike-fit9/`                                                                                                                                                                                                    |
| Seed warm 3DM geo               | `.shared/b2b/seeds/lookalike-3dm-owned-geo.json` · `npm run ingest:lookalike-geo`                                                                                                                                                                                                                             |
| Extract ICP lista (hard)        | `npm run export:icp-list` (± `--since-last`) → `.shared/b2b/reports/icp-6-50-chiasso-3h.*` (6–50 ∩ LO+PI+ER+VE/~3h)                                                                                                                                                                                           |
| Extract ICP legacy ≤2h          | `npm run export:icp-list:legacy-chiasso-2h` → `icp-6-20-chiasso-2h.*`                                                                                                                                                                                                                                         |
| ICP filter (puro)               | `scripts/lib/icp-export-filter.js` · test `npm run test:icp-export-filter`                                                                                                                                                                                                                                    |
| ICP buyer + firmografici        | `npm run enrich:icp-buyers` → report CSV/JSON + upsert PG `enrichment.icp_*` · lib `icp-buyer-firmographics.js`                                                                                                                                                                                               |

**Canonical:** questo repo possiede script e dati B2B. Cascade operativa → **`a-enrichment`** (strutturata con **System 1** per l'esecuzione batch e **System 2** per la validazione, credit check, doppie metriche JSON vs PG e prevenzione race conditions). Liste pilota = **query sul master**; seed XLSX/CSV solo via ingest. CSV/XLSX = handoff.

**Extract ICP:** full dopo batch enrich; `--since-last` = solo aziende con `company_enriched_at` > watermark. Record **senza** `enriched_at` restano eleggibili nel **full**, **esclusi** dal delta (evita di riemettere lo stock legacy). Filtri watermark/match in lib pura + `node --test`.

**Buyer + firmografici (post-export):** `npm run enrich:icp-buyers` (richiede `PGDATABASE_URI_PROD` e `MONGO_URI` remoti). Ranking buyer: owner/titolare → CEO → C-level → Director. LTV/prodotti: Mongo `transactions` join su `user` ObjectId (`status: 2`). P.IVA: HubSpot/`vatNumber` tx → scrape footer sito. ATECO/utile/fatturato/dipendenti/anno: ReportAziende (`assets/components/tabellaRicerca.php` + pagina dettaglio). Persistenza: upsert Postgres `enrichment.icp_vat_by_domain` / `enrichment.icp_firmographics` (niente cache JSON runtime). Se dominio ICP è **freemail**, per lo scrape P.IVA usare il dominio di `sito_aziendale`, non gmail/etc. **P.IVA/firmografici a scala master:** stesse tabelle `enrichment.icp_*` e stessa catena fonti; `enrich:icp-buyers` è legato al **CSV ICP** — per tutti i domini corporate con `organization` in PG serve batch dedicato (resume su righe già valorizzate in PG), non solo export lista.

**Run (ordine):** `cd src/explorer/b2b && npm install` (se manca `dotenv`/`pg`) → verificare schema/connettività su `PGDATABASE_URI_PROD` → fasi o `npm run enrich:recentsignups` → `PGDATABASE_URI_PROD=… npm run build:enrichment` → `npm run ingest:lookalike-geo` → `npm run export:icp-list` → `npm run enrich:icp-buyers`. Le migrazioni test locali (`make migrate`) sono separate e non vanno usate per enrichment. **UI live:** `/explorer/b2b/` → API score3. Export batch opzionale: `cd src/wtp/backend && node scripts/cluster-b2b-score3.js`.

**Cascade run operativo:** SoT enforcement → `docs/rules/b2b-enrichment-run.mdc` (HS senza `--trigger`, `--since`/`--until`, doppie metriche JSON vs PG, partial Apollo, ignore cluster, rebuild da JSON presenti, …). Cascade L1 → `a-enrichment`.

**Lookalike cold:** LeadMagic arricchisce domain/people; **non** fa discovery org a scala. Batch cold: `SKIP_HUBSPOT=1`. **`enrichment-leadmagic-companies-linkedin.json` non è ingestito** da `build:enrichment` — merge live `leadmagic_linkedin` si perdono al rebuild.

**LeadMagic company (master):** (1) **LinkedIn `/company/`** — `npm run enrich:companies:leadmagic-linkedin` → upsert PG (`enrich_source=leadmagic_linkedin`); checkpoint `.shared/b2b/enrichment-leadmagic-companies-linkedin.json`. (2) **Dominio corporate senza `organization`** — `npm run enrich:companies:leadmagic-domain` (company-search da PG, no freemail, **senza** Apollo org checkpoint); upsert `enrich_source=leadmagic_domain`; checkpoint `.shared/b2b/enrichment-leadmagic-companies-clusters.json`. Helpers: `scripts/lib/leadmagic-company-pg.js`. **`enrich-companies-leadmagic.js`** resta Apollo-miss (richiede org checkpoint) — non sostituisce il bulk no-org. Domini ancora senza org dopo run = miss già tentati. URL `/in/` nel checkpoint = persona, non company-search.

**Apollo catch-up finestra (es. ultimi 3 mesi):** export cohort dedicato (`export-hubspot-recentsignups-cohort.js` con `--since`, `--out`, `--segment last3m`), enrich Apollo sui miss, **merge** profili in `enrichment-apollo-recentsignups-clusters.json` — evitare un secondo `*-last3m-clusters.json` nel rebuild se duplica segmento — poi `build:enrichment`.

**Anti-pattern path-only:** niente secondo `.env` in `src/explorer/b2b`; XLSX/CSV lookalike ≠ `export:icp-list` senza ingest master.

## Override workflow

Segui facade L1 `a-b2b` → canone `a-product` § **Profilo B2B**. Questo file: guardrail + path. Package/PRD → `a-po`; enrichment run → `a-enrichment` (passa path/ICP da questa skill).

## Deleghe (delta vs L1)

Matrix completa → `a-b2b`. Solo override progetto:

| Agente         | Delta                                                                                  |
| -------------- | -------------------------------------------------------------------------------------- |
| `a-enrichment` | Cascade / lookalike / gate — path e ICP da questa skill                                |
| `a-po`         | Strategia, Lean Canvas, **PRD** (`/prd`), prioritize/validate                          |
| `a-copywriter` | Messaging / landing / outreach — **non** PRD; UI explorer → skill `b2b-explorer-ui-ux` |

## Apprendimento / Sync

Eredita `/learn` e `/sync` da a-agentzero via L1.

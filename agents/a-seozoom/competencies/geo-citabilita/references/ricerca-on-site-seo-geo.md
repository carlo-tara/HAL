# Ricerca on-site allineata a SEO/GEO — glossario L1

Riferimento **multi-progetto** per siti statici (o build statico) con ricerca interna client-side. Le skill figlie L2 documentano motore, path, script e playbook operativo; non duplicare questo glossario nel L2.

**Pattern di riferimento:** [Pagefind](https://pagefind.app/) su siti statici; altri motori (Lunr, Fuse.js, Typesense embedded) seguono la stessa architettura a tre strati.

---

## Perché collegare SEO e ricerca interna

La ricerca on-site **non sostituisce** Google, ma deve **smistare come il SERP owner**: stesse keyword, stesso URL canonico per cluster, stesse regole anti-cannibalizzazione. I dati SeoZoom (`monitored.csv`, cannibalizzazione, striking distance) alimentano una **mappa intent** che guida ranking e risultati in evidenza.

L'indice di ricerca interna **non va indicizzato** dai motori esterni (`Disallow` su path indice, es. `/pagefind/`).

---

## Architettura a tre strati

| Strato | Ruolo generico | Esempio (statico) |
|--------|------------------|-------------------|
| **1 — Indice full-text** | Indicizza HTML a build/deploy | Pagefind CLI → `/pagefind/` |
| **2 — Mappa intent** | Cluster, owner URL, sinonimi, pesi da export SEO | `search-intent-map.json` |
| **3 — UI + featured** | Modal/ricerca, boost ranking, card «percorso consigliato», eventi analytics | JS custom + component UI motore |

### Flusso dati (generico)

```
SeoZoom monitored.csv (+ GSC/GA4 opzionale)
        ↓
Script generazione mappa intent (L2)
        ↓
search-intent-map.json (+ overrides opzionali)
        ↓
Build → attributi meta su HTML (intent, keywords, weight)
        ↓
Motore ricerca --site {out} → indice
        ↓
Runtime: mappa intent + eventi GA4 search (se presenti)
```

---

## Soglie keyword significative (default)

Dal `monitored.csv` (o equivalente), includi keyword se:

`Vol ≥ 10` **OR** `Keyword Opportunity ≥ 70` **OR** `Pos ≤ 20`

La skill L2 può adattare le soglie al volume del sito.

---

## Routing intent (tre livelli)

| Livello | Criterio | Comportamento |
|---------|----------|---------------|
| **B — Entità nominale** | Nome prodotto/pagina/struttura nel query | Featured sull'URL owner dell'entità |
| **A — Cluster editoriale** | Tema hub (categoria/guida owner) | Featured su hub/guida owner del cluster |
| **C — Sinonimi** | Varianti keyword dal export | Match via meta keywords nell'HTML indicizzato |

**Regola anti-cannibalizzazione:** se un'altra URL ranka **Pos ≤ 30** su Google per la stessa keyword, la ricerca interna non deve competere con un URL secondario. Owner URL del cluster = stesso criterio del SEO organico (L2).

---

## Workflow L1 (dopo export SeoZoom)

```
Task Progress:
- [ ] 1. Verifica export fresco in seo/{YYMMDD}/ (monitored.csv)
- [ ] 2. Carica skill figlia L2 — playbook ricerca on-site del progetto
- [ ] 3. Rigenera mappa intent dallo script L2 (se previsto)
- [ ] 4. Revisiona keyword unassigned ad alto volume; allinea cluster/owner
- [ ] 5. Build statico + iniezione meta intent
- [ ] 6. Indicizza con motore ricerca (es. npx pagefind --site dist)
- [ ] 7. Smoke test query brand / cluster / entità nominale
- [ ] 8. Se GA4: confronto trimestrale eventi search vs mappa → overrides
```

Dettaglio path, comandi e file: **solo** nella skill L2 (`pagefind-*.md`, sezione dedicata in `seozoom-{slug}/SKILL.md`, o equivalente).

---

## Integrazione fonti complementari

| Fonte | Uso per ricerca on-site |
|-------|-------------------------|
| **SeoZoom** `monitored.csv` | Primaria — sinonimi, volume, posizioni per mappa intent |
| **Cannibalization.csv** | Verifica owner URL prima di spostare featured |
| **GSC** | Query reali non in SeoZoom; CTR basso su owner |
| **GA4** `search` / `select_search_suggestion` | Gap query utenti vs mappa; review trimestrale |

---

## Cosa documenta la skill L2 (checklist scaffold)

- [ ] Motore ricerca e comando indicizzazione
- [ ] Path mappa intent e script generazione da CSV
- [ ] File overrides manuali (post-GA4)
- [ ] Attributi HTML/meta iniettati a build
- [ ] Regole hub/copy che non devono rubare keyword ad altri owner
- [ ] Trigger rigenerazione (export mensile, nuova guida, batch SEO)
- [ ] Test/smoke query obbligatori

---

## Esempio path L2 (generico)

| Campo | Valore tipico |
|-------|----------------|
| Skill | `.cursor/skills/seozoom-{slug}/SKILL.md` |
| Playbook | `.cursor/skills/seozoom-{slug}/pagefind-seo-geo.md` (o equivalente) |

---

## Riferimenti L1 correlati

| File | Contenuto |
|------|-----------|
| [metriche-seozoom.md](../../metriche-analisi/references/metriche-seozoom.md) | ZO, ZS, cannibalizzazione, striking distance |
| [extension-template.md](../../../extension-template.md) | Scaffold skill figlia con sezione ricerca on-site |

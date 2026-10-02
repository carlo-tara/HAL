# Google Ads — PMax e Shopping / feed (canone)

Distillato da upstream pmax-optimization, shopping-ads, audience-targeting. Riscritto HAL.

---

## Prima di spendere (Shopping / PMax)

| Gate | Azione |
|------|--------|
| Merchant Center | Prodotti approvati; disapprovals quotidiane finché rosso |
| Feed | Titoli con attributi rilevanti in testa; disponibilità; prezzo |
| Custom labels | Segmentazione bid/filtro (linea, tier prezzo, push/exclude) |
| Sync canale | Woo/GLA → MC → Ads (tempi di sync tipici ~24h) |

Diagnosi issue API/CSV → competenza **`seo-import`** + L2 feed/plugin. Non hardcodare GTIN/policy qui.

---

## Performance Max

| Impostazione | Canone default (e-commerce controllo) |
|--------------|----------------------------------------|
| Obiettivo | Vendite / conversioni valore |
| URL expansion / Final URL expansion | **OFF** se serve controllo landing |
| Asset group | Separati per linea/categoria o audience distinta |
| Asset minimi | ≥15 headline, ≥4–5 description, immagini multiple; video custom se possibile (evita auto-video scadenti) |
| Audience signals | Customer Match / remarketing / custom intent (URL competitor + keyword) — accelerano learning, non “mirano” in modo fisso |
| Brand exclusions | Se organico brand già forte **o** Search Brand dedicata |
| Search themes | Guidano inventario Search verso query intent |
| Learning | 4–6 settimane prima di rifacimenti strutturali; eccezione: spreco evidente / feed rotto |

Settimanale: sostituire asset rating **Low**; Search Terms insights → negative (API/rep se necessario).

---

## Shopping (standard o via PMax)

1. Segmenta con custom labels (performance / margine / linea) — non un unico blob
2. Priorità campagne / listing group coerenti col filtro prodotti L2
3. Monitora price competitiveness solo con dati reali (MC / tool), senza inventare benchmark
4. Free listings: lasciare attive dove disponibili (traffico organico Shopping)

---

## Audience (Search + PMax)

| Uso | Regola |
|-----|--------|
| Search | Audience in **observation** prima di targeting; escludi convertitori recenti dal prospecting |
| Remarketing liste | Finestre multiple (7/14/30/90) se volume basta |
| Min size | ~1000 (Search RLSA), ~100 (Display) — sotto soglia non forzare |
| PMax | Signal package all’asset group; non moltiplicare AG senza ipotesi |

Remarketing Display/YouTube sequenziale = **fase 2** (budget e creatività dedicate).

---

## Brand vs acquisizione

- Chi cerca il marchio e l’organico è già #1 stabile: **non** pagare Brand Search di default
- Se Auction insights mostra competitor sul brand → Brand Search difensiva a budget basso
- PMax senza brand exclusions può cannibalizzare: escludi termini brand quando Search/organico li coprono

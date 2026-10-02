---
name: market-public-data
kind: competency
version: 1.0.0
description: >-
  Analizza registri aperti IT (ISTAT SDMX, Unioncamere, startup.registroimprese)
  per sizing/segment/ecosystem evidence. Solo L1 (a-po). Non enrichment CRM.
---

# Competenza L1 — market-public-data (a-po)

Ancora decisioni prodotto/GTM a **evidenza pubblica italiana**: macro ISTAT, tessuto camerale, ecosistema startup/PMI innovative. Output = finding citati, non lead list.

**Reference:** [istat-sdmx.md](references/istat-sdmx.md) · [unioncamere-opendata.md](references/unioncamere-opendata.md) · [startup-registroimprese.md](references/startup-registroimprese.md)

Helper: [`../../scripts/fetch-istat-sdmx.sh`](../../scripts/fetch-istat-sdmx.sh)

---

## Quando applicare

- `/market-data`, o da `/intake` `/validate` `/brief` se manca evidenza di mercato IT
- Domande: stock imprese, addetti, export, trend settoriali/ATECO, n. startup innovative, confronti territoriali

## Quando NON applicare

- Enrichment contatti/account / cascade HubSpot → `a-enrichment`
- Solo visualizzazione KPI già numerati → `a-charts`
- Personas/jobs → `a-personas` / `a-jtbd`
- Scrape aggressivo / bypass captcha su registroimprese

---

## Workflow

```
1. Clarifica (1–2 Q): geografia, settore/ATECO, periodo, metrica
2. Route fonte:
   - macro / serie nazionali → ISTAT SDMX (+ databrowser per scoprire dataflow)
   - demografia imprese locale / CSV camerali → Unioncamere (+ discovery dati.gov.it)
   - startup / PMI innovative / incubatori → registroimprese (file utente | browser | API L2)
3. Fetch o istruzioni download; salva sotto `.cursor/product/data/` o path L2
4. Analizza: trend, confronto, caveat (copertura, lag, definizione legale startup)
5. Output contract sotto; checkpoint: “implicazioni per shape/validate?”
```

---

## Regole ferree

1. **Mai inventare** numeri ISTAT/camerali/startup
2. Sempre **fonte URL + data estrazione** (+ licenza se nota)
3. Preferire aggregati; dataset aperti usati non sono CRM
4. Liste per outreach → solo se PO chiede esplicitamente handoff `a-enrichment`
5. Rate-limit ISTAT (~5 req/min); restringi periodo/osservazioni

---

## Anti-pattern

- Citare “circa N startup” senza file/fonte
- Usare Telemaco elenchi a pagamento come default
- Bypass captcha / credential stuffing API InfoCamere
- Trattare open data come sostituto di discovery utenti

---

## Output della fase

- **Finding** (max 5 bullet, tag `evidence`)
- Serie/tabella essenziale (o handoff `a-charts`)
- **Fonte** + timestamp + licenza
- **Limiti** (cosa i dati non dicono)
- **Implicazioni prodotto** (`evidence` vs `hypothesis`)

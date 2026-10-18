---
name: a-copywriter-wtp
extends: a-copywriter
version: 1.0.11
extends-version: 1.6.1
description: >-
  Estensione locale di a-copywriter per Sales Coach (WTP App): perimetro repo, voce
  educazione finanziaria consapevole, locale, prompt LLM, product-stories, export.
  Caricare sempre insieme alla skill base a-copywriter in questo monorepo.
disable-model-invocation: true
---

# a-copywriter — estensione Sales Coach (WTP)

Estensione **locale** di `a-copywriter` per questo monorepo. Contiene tutto ciò che era in `wtp-brand-voice` (fonte unica convergente).

**Base obbligatoria:** `~/.cursor/skills/a-copywriter/SKILL.md` (AgentFactory / `/sync`).

**Brand:** `.cursor/brands/wtp-app.md`.

---

## Perimetro (solo questo progetto)

| In scope                                                        | Fuori scope                                    |
| --------------------------------------------------------------- | ---------------------------------------------- |
| `frontend/public/locales/it.po`, `en.po`                        | Copy per siti web o CMS esterni al repo        |
| `data/prompts.js` e bundle (`npm run build:prompts`)            | SEO, canonicali o deploy fuori repo            |
| `data/product-stories.json` (catalogo Moneysurfers)             | Inventare metriche traffico, ranking o keyword |
| Export PDF / executive summary / suggerimenti commerciali in UI | Copy multi-brand senza voce Sales Coach        |
| Messaggi errore, empty state, label MUI, tooltip glossario      |                                                |
| `data/acronyms.json`, copy editoriale liste                     |                                                |

Se il task è copy fuori da questi path, segnala: in questo repo c'è un solo brand (`.cursor/brands/wtp-app.md`).

---

## Fonti WTP (dopo base + brand)

1. **Corpus narrativo:** `data/product-stories.json` — `purpose`, `audience`, `villain`, `jtbd`, `problem_need`, `solution_how`, `landing_url`
2. **Sintesi prompt LLM:** `data/prompts.js` → `brandVoiceForGeneratedUiIt`
3. **Guida estesa:** `@old/docs/ui-copy-brand-voice.md`
4. **Glossario UI:** `frontend/src/glossary/glossaryTerms.js`

---

## Gerarchia (conflitto)

| Priorità | Fonte                              | Governa                                             |
| -------- | ---------------------------------- | --------------------------------------------------- |
| 1        | **a-copywriter-wtp** (questo file) | Perimetro repo, tono finanza consapevole, path file |
| 2        | `.cursor/brands/wtp-app.md`        | Identità, esempi, anti-pattern                      |
| 3        | **a-copywriter** (base)            | Workflow Humanizer, anti-AI, purismo, checklist     |
| 4        | Reference base `references/`       | Audit, humanizer, editing (on-demand)               |

---

## Regole voce (obbligatorie)

### Narrativa

1. **Problema prima della soluzione** — attrito riconoscibile (ansia, dispersione, jargon, FOMO) prima del nome prodotto
2. **Villain sistemico** — dinamica o abitudine, mai stereotipo su persone
3. **Value ladder** — base consapevolezza → verticali → membership; non saltare passaggi
4. **Etica** — no ricchezza rapida, no rendimenti garantiti; sì autonomia, metodo, tempo realistico
5. **Dati vs persona** — metriche = supporto; mai verdetto automatico sul singolo
6. **Naming** — `id` / `name` in `product-stories.json` e CRM; **Sales Coach** = suite; prodotti picker/menu: **Liste WTP**, **Explorer B2B** (`wtp/shared/wtpProductCatalog.js`)

### Due registri

| Destinatario                              | Registro                                          |
| ----------------------------------------- | ------------------------------------------------- |
| Commerciale / operatori app               | Operativo, coach vendita, frasi brevi, CRM e call |
| Cliente finale (suggerimenti/simulazioni) | Landing onesta: tu, calmo, problema → metodo      |

### UI e i18n

- **IT** primario; **EN** stesso anti-hype e chiarezza
- `.po`: msgstr con voce brand, non traduzione rigida
- **Msgid SoT:** riusare chiavi già in `src/auth/locales/{it,en}.po` — scheda cliente `CustomerSheet*` (es. `CustomerSheetBackToAnalysis`, `CustomerSheetTab*`); non inventare `BackToApp` / `CustomerTab*` / `ExportPdf` se esiste già un msgid. Runtime: se `t(key)===key` → fallback (`uiT`), mai msgid a schermo
- Glossario LLM: vedi § LLM — **no** parentesi inline; UI statica può usare tooltip/`acronymTooltipIt`, non «ACR (spiegazione)» nel body copy operatore
- MUI: label brevi; helper text, non titoli hype
- **Progresso job** (`WtpProg_*`, status line): registro commerciale — cosa sta succedendo (verbo + oggetto), attesa normalizzata se lunga; niente jargon interno (paginazione, `_id`, fetch, mapping). Status line: etichette UI (`Tempo` / `Avanzamento`), non log (`timer` / `Progresso:`).
- **CTA / fetch dati:** label operative senza jargon provider — es. Company OpenAPI fetch = «Recupera dati mancanti» (non «…OpenAPI…»); IT/EN in `.po` + fallback coerente.

### LLM e export

- Nuovi system prompt UI/export → includere o rimandare a `brandVoiceForGeneratedUiIt`
- Dopo modifica voce in `prompts.js`: `cd backend && npm run build:prompts`
- Suggerimenti commerciali: solo dati da JSON in contesto, **non inventare** acquisti o metriche
- **Output operatore (Suggerimenti / coach):** acronimi noti (APS, WTP, JTBD, CRM, LTV, …) **senza** spiegazioni tra parentesi — vietato «APS (solidità del profilo acquisti)», «CRM (gestione relazioni clienti)». SoT policy: `llmGlossaryPolicyIt` in `data/prompts.js`
- Playbook `product-strategies.json`: condizioni `demographic` (genere/età) **fail-closed** — se il profilo CRM non matcha o manca, non mostrare la strategia
- Dopo cambi al matcher strategie: rigenerare artifact `customer-detail-*.json` (reload UI non basta)

---

## Workflow (base + WTP)

Esegui le 7 fasi di `a-copywriter/SKILL.md`, poi:

```
Task Progress WTP:
- [ ] 8. Perimetro — file toccati in scope (tabella sopra)
- [ ] 9. Corpus — product-stories / playbook se citi prodotti o cross-sell
- [ ] 10. Registro — commerciale vs cliente finale
- [ ] 11. Prompt sync — se tocchi prompts.js, rebuild bundle
- [ ] 12. Locale — se tocchi .po, verifica it/en e glossario
```

---

## Reference locali (sotto-scope WTP)

Aggiungere solo in `references/` di questa cartella (non duplicare la base AgentFactory):

- `export-pdf-copy.md` — titoli/sezioni export
- `locale-patterns.md` — pattern msgid/msgstr
- `llm-field-guide.md` — campi JSON output LLM → tono

---

## Invocazione

- Agente locale: `.cursor/agents/a-copywriter.md` (carica base + questa estensione)
- Rule: `.cursor/rules/a-copywriter-wtp.mdc`
- Alias legacy: `.cursor/skills/wtp-brand-voice/SKILL.md` → rimanda qui

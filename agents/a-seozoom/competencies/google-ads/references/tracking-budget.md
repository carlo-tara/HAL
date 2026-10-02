# Google Ads — tracking e budget (canone)

Distillato da upstream conversion-tracking e budget-optimization. Riscritto HAL.

---

## Tracking (gate ferreo)

| Regola | Dettaglio |
|--------|-----------|
| Prima i bid | Nessuna ottimizzazione budget/CPA/ROAS senza conversione primaria verificata |
| E-commerce | Conteggio conversioni **every** (ordini); transaction ID per dedupe |
| Lead-gen | Conteggio **one** per lead qualificato |
| Primarie vs secondarie | Solo primarie guidano le offerte; micro-conversioni in osservazione |
| Enhanced Conversions | Abilitare dove possibile (match rate) |
| Validazione | Confronto Ads ↔ backend shop/CRM a campione (mensile o pre-scale) |
| Finestra | Allineata al ciclo reale di acquisto (L2) |

Tag diagnostics / Consent Mode: stack analytics L2 (anti doppio tracking). Import offline entro tempi ragionevoli se usato.

**Se tracking assente o dubbio → spend = 0.**

---

## Budget e learning

| Regola | Dettaglio |
|--------|-----------|
| Lookback | Preferire ≥30 gg (ideale 90) prima di curve “marginali”; su test one-shot dichiara limite dati |
| Shift | ±20–30% per aggiustamento — no oscillazioni giornaliere ampie |
| Impression share lost to budget | Segnale sotto-investimento se CPA/ROAS ok |
| Campagne magre | &lt;~15 conv./mese: consolida o accetta rumore; non micro-ottimizzare |
| Conversione lag | Non giudicare un cambio budget sulle ultime 48–72h |
| Brand minimo | Solo se Brand Search è attiva per difesa — altrimenti zero vincolo brand paid |

Portfolio / shared budget: utile se più campagne stesso funnel e CPA simili; non obbligatorio su test piccoli.

---

## Forecast / ROI per stakeholder

Quando il deliverable è per l’imprenditore:

1. Usa AOV/ticket da dati shop o catalogo (cita fonte)
2. Scenario prudente / atteso / ottimista con **probabilità esplicite**
3. Etichetta tutto come **stima** (account senza storico = sconto learning)
4. ROI = fatturato/spesa **salvo** richiesta margine
5. Zero gergo nel one-pager; gergo solo nel campaign pack operativo

Non spacciate i Best Practices upstream come KPI garantiti.

---

## Ciclo ottimizzazione (settimanale, post go-live)

Allineato a [ops-analysis.md](ops-analysis.md):

1. **Anomaly** (o check giornaliero leggero) vs media 7–14 gg
2. Search Terms → **wasted spend** / negative / pause
3. Asset PMax/RSA Low → replace (fatigue proxy)
4. Disapprovals MC → fix feed
5. Se |ΔCPA| &gt;~15% → **CPA diagnostic** (driver per €)
6. CPA/ROAS per campagna → shift budget limitato verso vincitrice
7. Solo dopo volume: Target CPA / Target ROAS
8. Prima di scale budget → **scenario** non lineare (§ Forecast sopra)

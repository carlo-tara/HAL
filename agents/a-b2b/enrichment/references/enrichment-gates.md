# Enrichment gates — ICP + fit score

Gate operativi prima di fasi a pagamento (Apollo, LeadMagic, deep research). Soglie numeriche e disqualifiers vivono in **L2**; questa reference definisce la procedura.

## Binary ICP gate (pre-paid)

Dopo research leggero / export cohort (o domain brief):

1. Valutare il target contro ICP L2: industrie, size, maturity, needs, **disqualifiers**.
2. Usare la checklist L2 (o quella in [extension-template.md](../extension-template.md)).
3. Esito:
   - **MATCH** → procedere alle fasi a pagamento.
   - **NO MATCH** → raccomandare stop; chiedere conferma umana prima di Apollo/LeadMagic/deep enrichment.
4. Su rifiuto utente → fermare il workflow senza spendere crediti contact-level.

Non elevare research-web (Tavily/Perplexity/ecc.) a canone L1: se L2 li usa, restano implementazione locale e restano soggetti a questo gate prima delle fasi contact a pagamento.

## Fit score (batch / cohort)

Per liste lead o account (non solo dominio singolo), assegnare **fit score 1–10** con spiegazione.

| Banda | Score | Azione default |
|-------|-------|----------------|
| High | 8–10 | Enrichment a pagamento consentito |
| Medium | 5–7 | Procedere solo se ICP MATCH o conferma umana |
| Low | 1–4 | Trattare come NO MATCH → ask before spend |

L2 può ridefinire le soglie; se assenti, usare la tabella sopra.

## Unificazione gate binario + score

- Gate binario = hard stop su disqualifiers / mismatch strutturale.
- Fit score = priorità e banda di spend all'interno dei MATCH (o dopo override umano).
- Non mantenere due sistemi incoerenti: se score < soglia low e ICP è MATCH dubbia, chiedere comunque conferma.

## Output minimo del gate

```
ICP CHECK: MATCH | NO MATCH
├─ Industry / Size / Disqualifiers: …
├─ Fit score (se batch): N/10 — reason
└─ Recommendation: proceed | ask before spend | stop
```

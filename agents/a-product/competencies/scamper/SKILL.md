---
name: scamper
kind: competency
version: 1.0.0
description: >-
  SCAMPER su strategia / offer / GTM: ideazione strutturata (Substitute…
  Reverse), filtro guardrail L2, ICE, Now/Next/Later. Solo L1 (a-po).
---

# Competenza L1 — scamper (a-po)

Genera **opzioni** su strategia, package o GTM con le 7 lenti SCAMPER. Non riscrive la thesis finché il PO non adotta bet esplicite. Output = artefatto di ideazione + ranking, non feature wishlist.

**Origine metodo:** Bob Eberle / SCAMPER (checklist creativa su stimolo esistente). Prose e workflow HAL originali.

---

## Quando applicare

- `/scamper` su strategia prodotto, Lean Canvas UVP/channels, package/offer, o GTM thesis
- Dopo `/shape` o documento strategia, quando serve **esplorare alternative** senza saltare a delivery
- Prima di `/prioritize` se le iniziative sono ancora grezze / solution-first

## Quando NON applicare

- Problema non frame-ato → `problem-framing` prima
- Solo ranking di backlog già chiaro → `backlog-prioritization`
- Solo validazione assunti → `evidence-probe`
- Brainstorm feature senza baseline documentata (strategia / canvas / brief)

---

## Baseline richiesta

Prima di generare idee, fissa lo **stimolo** (1–2 schermate):

| Campo | Fonte tipica |
|-------|----------------|
| Tesi / decisioni attuali | strategia, notes, brief |
| Package / stack | positioning-offer, canvas Solution |
| Canale / GTM | canvas Channels, growth-loops |
| Guardrail L2 | skill `po-*` / `b2b-*` (geo, ICP, prodotti, timeline) |
| Tag evidenza | **[E]** / **[I]** / **[G]** se il progetto li usa |

Se manca baseline: chiedi path o fai `/intake` — non inventare ICP/stack.

---

## Workflow

```
1. Dichiarare baseline (decisioni che VINCONO finché PO non adotta)
2. Per ogni lettera S-C-A-M-P-E-R: 2–4 idee su dimensioni strategiche
   (offerta, buyer/ICP, canale, delivery/economics, moat/messaging)
   — non elenco feature UI
3. Per ogni idea: impatto 1 riga · tag [E]/[I]/[G] · fit L2
   (ok | tensione | icebox) · ICE (I×C×E, ciascuno 1–5)
4. Bucket Now | Next | Later | Icebox (Icebox = viola hard constraint o thesis)
5. Top 3–5 bet → rewrite outcome:
   Enable [segment] to [customer outcome] so that [business impact]
   + owner + success signal
6. Decision summary: SCAMPER = exploration; cascata canvas/PRD/playbook
   SOLO se PO adotta bet che cambiano decisioni
7. Checkpoint: “quali bet adottare?” → /prioritize o /validate o /shape
```

### Lenti (domande guida)

| Lettera | Domanda |
|---------|---------|
| **S** Substitute | Cosa sostituire (framing, canale, buyer role, pricing anchor, path di pagamento)? |
| **C** Combine | Cosa unire (ladder package, discovery+probe, case+referral)? |
| **A** Adapt | Cosa adattare da un contesto collaudato (B2C→B2B, playbook caso→ICP, competitor pattern)? |
| **M** Modify / Magnify / Minify | Cosa amplificare, ridurre o ritoccare (KPI, custom, scope, ticket)? |
| **P** Put to other uses | Stesso asset, altro uso (welfare vs corso, case→VSL, lista→referral)? |
| **E** Eliminate | Cosa togliere (canali prematuri, overclaim, dipendenze, headcount)? |
| **R** Reverse / Rearrange | Invertire ordine fasi, pitch↔discovery, entry tier? |

### Filtri hard (sempre)

- Rispettare guardrail L2 (geo, ICP, stack prodotti, timeline) — idee in tensione = documentate, non silenziate
- Non inventare win rate / CAC / LTV / conversion
- Non promuovere fonte esterna **[G]** a **[E]** senza validazione
- Non aprire canali a volume se la thesis è warm-first / gated
- Nessuna promessa (funding, “costo zero”, ROI) senza keep/kill o evidenza

---

## ICE (triage rapido)

| Fattore | Scala 1–5 |
|---------|-----------|
| **I** Impact | Quanto muove PSF/PMF / constraint se vera |
| **C** Confidence | Quanto è ancorata a **[E]** vs pura **[I]/[G]** |
| **E** Ease | Quanto è fattibile nel perimetro attuale (capacity, L2) |

Score = I × C × E (max 125). Preferire alto Ease+Confidence in Now anche se Impact medio.

Handoff ranking fine → `backlog-prioritization` (stesso bucket Now/Next/Later).

---

## Regole ferree

1. SCAMPER genera opzioni; **non** auto-update decisioni strategia / skill L2
2. Dimensioni strategiche > feature list
3. Ogni Now ha success signal; Top bet in forma outcome
4. Cascata artefatti (canvas → PRD → playbook) solo post-adozione PO
5. `po-interviewer`: sintesi Top bet → conferma → avanza

---

## Anti-pattern

- Usare SCAMPER per giustificare cold/partner/prodotti nuovi contro L2
- Tabella idee senza baseline né fit L2
- Riscrivere thesis nel Decision summary senza conferma PO
- Inventare metriche per alzare Confidence
- Duplicare alla lettera azioni già in Now della strategia senza **delta**

---

## Output della fase

- Decision summary (exploration vs thesis invariata)
- Tabelle per lettera (idea · impatto · tag · fit L2 · ICE · bucket)
- Top 3–5 bet outcome + owner + segnale
- Now / Next / Later / Icebox (delta)
- Pilot / L2 fit check + tensioni
- Next actions (max 3) → `/prioritize`, `/validate`, `/shape`, o handoff `a-b2b` / `a-copywriter`

Template artefatto: [references/scamper-template.md](references/scamper-template.md)

Path tipico progetto: `projects/.../05-strategia/scamper-*.md` o `.cursor/product/scamper-YYYY-MM-DD.md`

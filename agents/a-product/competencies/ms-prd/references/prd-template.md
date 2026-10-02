# PRD template — ms-prd (formato Claude / Moneysurfers)

Schema allineato a Claude `prd-writer` + istanza Reportistica (es. MoneySurfers B2B): Vincoli, NON-goals, Epic Map a blocchi, US raggruppate, DoD A+B, Artifact opt-in. Anti-invention; gate Sistema sotto.

**Path file:** se il progetto ha già una cartella PRD (es. `projects/…/01-requisiti/`), salvare lì e continuare la serie di versione. Usare `.cursor/product/PRD_<slug>_v<ver>.md` solo in assenza di path di progetto.

**Versione:** continua la serie del PRD esistente (es. 0.7 → 0.8). Nuovo documento senza storia → 0.1 o 1.0 a scelta del PO (non forzare 1.0 su un update).

Artifact opt-in: [artifact-e-versioni.md](artifact-e-versioni.md) come sezione 8, **solo se richiesto**.

Compila con contenuto reale — niente inventato.

```markdown
# Product Requirements Document
## {Nome Prodotto / Feature}

| Campo | Valore |
|-------|--------|
| **Prodotto** | {nome} |
| **Versione documento** | {continua serie esistente, es. 0.8; nuovo senza storia → 0.1 o 1.0 a scelta PO} |
| **Data** | YYYY-MM-DD |
| **Product Owner** | {nome} |
| **Stakeholder principali** | {team / persone} |
| **Status** | Draft \| In review \| Living |

---

## 1. Contesto e Vision

### Problema
{Chi lo vive, quanto spesso, con quale impatto.}

### Vision del prodotto
{2–3 frasi: cosa cambia quando il prodotto esiste. Obiettivo misurabile se il PO l’ha dato.}

### Vincoli del pilota
{Tabella vincolo → valore. Obbligatoria se c’è un pilota o un perimetro chiuso; altrimenti una riga “Nessun vincolo aggiuntivo”, oppure omettere solo se il PO conferma assenza.}

| Vincolo | Valore |
|---------|--------|
| {es. Geo, ICP, SKU, prezzo, GTM} | {valore} |

### NON-goals

| NON-goal | Motivo |
|----------|--------|
| {cosa non facciamo} | {perché} |

### Utenti target

| Persona | Ruolo d'uso |
|---------|-------------|
| {persona specifica} | {cosa fa con il prodotto} |

---

## 2. Epic Map

Se il prodotto ha casi distinti (es. caso singolo vs offerta generica), usare **blocchi** con tabella ciascuno. Altrimenti un solo blocco.

### Blocco A — {nome}

| Epic | Obiettivo | User Story collegate |
|------|-----------|----------------------|
| EPIC-A1 {Nome} | {macro} | US-A01, US-A02 |

### Blocco B — {nome}

| Epic | Obiettivo | User Story collegate |
|------|-----------|----------------------|
| EPIC-B1 {Nome} | {macro} | US-B01, US-B02 |

Nessuna epic senza ≥1 US; nessuna US senza epic. Aggiornare le colonne a ogni add/remove.

---

## 3. User Story

Raggruppare per blocco / tema (come l’Epic Map). ID ammessi: `US-A01`, `US-B01`, … oppure `US-01` se un solo blocco.

### Blocco A — {tema}

#### US-A01 — {titolo breve}
**Epic:** EPIC-A1 {Nome}  
**Come** {persona},  
**voglio** {azione},  
**per** {beneficio}.

Criteri di accettazione:
- [ ] {criterio verificabile}
- [ ] {criterio verificabile}

### Blocco B — {tema}

#### US-B01 — {titolo breve}
**Epic:** EPIC-B1 {Nome}  
**Come** {persona},  
**voglio** {azione},  
**per** {beneficio}.

Criteri di accettazione:
- [ ] {criterio verificabile}

*(Hard-break: due spazi a fine riga su Epic / Come / voglio — non su "per". Nessun link job story.)*

---

## 4. Definition of Done

### A — Baseline rilascio (sempre)
- [ ] Tutte le US in scope per questo rilascio hanno AC verificati
- [ ] Nessuna Domanda aperta bloccante
- [ ] PRD aggiornato alla versione corrente
- [ ] Approvazione Product Owner

### B — Condizioni prodotto (col PO — non inventare)
- [ ] {es. vincoli del pilota rispettati}
- [ ] {es. NON-goals rispettati}
- [ ] {altra condizione di dominio concordata}

Gli AC chiudono la singola US; la DoD (A+B) chiude il rilascio/feature.

---

## 5. Backlog aperto

| Item | Priorità | Note |
|------|----------|------|
| {noto ma non in Epic/US} | Alta \| Media \| Bassa | |

---

## 6. Domande aperte

| Domanda | Owner | Stato |
|---------|-------|-------|
| {punto da chiarire} | {chi risponde} | Aperta \| Risolta |

---

## 7. Glossario

| Termine | Definizione |
|---------|-------------|
| {solo termini usati nel documento} | |

---

## 8. Artifact e Versioni

*(Includere questa sezione **solo** se il PO la richiede esplicitamente. Dettaglio: artifact-e-versioni.md.)*

---

*Documento v{x.y} — {data} · aggiornare a ogni revisione di contenuto*
```

## Gate — Persona "Sistema"

Usa **Sistema** come soggetto della US solo se il *per* (beneficio) è percepito da un utente reale.

| OK nel PRD | NO (→ Technical Spec) |
|------------|------------------------|
| Auto-save per non perdere lavoro | Chiamata API con header Bearer |
| Sync notturno per dati freschi in dashboard | Indicizzare record nel DB |
| Notifica email su evento per allertare il team | Dettaglio cron / queue |

**Test:** se togliessi la storia dal PRD e la lasciassi solo ai dev, gli utenti noterebbero differenza? Sì → PRD. No → Spec tecnica.

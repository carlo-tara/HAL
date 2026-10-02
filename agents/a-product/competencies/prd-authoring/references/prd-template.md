# PRD template — a-po

Struttura evoluta da Claude `prd-writer` (Reportistica) + gate AF (vivo, NON-goals, KPI, Sistema, Skill VS PRD). Prose HAL. Path canone: `.cursor/product/prd.md`.

Compila ogni sezione con contenuto reale — niente placeholder lasciati su campi già forniti dal PO.

```markdown
# Product Requirements Document
## {Nome prodotto / feature / area}

| Campo | Valore |
|-------|--------|
| **Prodotto** | {nome} |
| **Versione documento** | 1.0 |
| **Data** | YYYY-MM-DD |
| **Product Owner** | {nome} |
| **Stakeholder principali** | {team / persone} |
| **Status** | draft \| in review \| living |

---

## 1. Contesto e Vision

### Problema
{Chi lo vive, quanto spesso, con quale impatto.}

### Vision del prodotto
{2–3 frasi: cosa cambia per l'utente quando il prodotto esiste.}

### Perché ora
{Trigger di timing / vincolo.}

### NON-goals
{Cosa il prodotto NON farà in questo ciclo.}

### Link fonti
{brief / lean-canvas / personas.md / jtbd.md se presenti}

### Utenti target

| Id | Persona (specifica) | Ruolo d'uso | Evidenza | Ipotesi |
|----|---------------------|-------------|----------|---------|
| P1 | | | | |

Fonte: `personas.md` / PO. Vietato "l'utente generico". Compila **Evidenza** e/o **Ipotesi** (niente tag inline `[E]`/`[I]`).

---

## 2. Epic Map

| Epic | Obiettivo | User Story collegate |
|------|-----------|----------------------|
| EPIC-1 {Nome} | {macro} | US-01, US-02 |
| EPIC-2 {Nome} | {macro} | US-03 |

Regola: aggiorna la colonna a ogni add/remove US — nessuna epic senza ≥1 US, nessuna US senza epic.

Test menu: se fosse un'app, queste sono le sezioni principali?

---

## 3. User Story

### US-01 — {titolo breve}
**Epic:** EPIC-1 {Nome}  
**Come** {persona specifica},  
**voglio** {azione},  
**così da** {beneficio concreto}.

- Status: todo | doing | done
- Job story (se da jtbd): JS-XX
- Criteri di accettazione (≥2, verificabili sì/no; termini di dominio → Glossario):
  - [ ] {criterio}
  - [ ] {criterio}
- Note / NON in scope:

*(ogni US dichiara sempre l'Epic; hard line break: due spazi a fine riga su Epic / Come / voglio — non sull'ultima così da)*

---

## 4. Definition of Done (team — globale)

- [ ] Code review
- [ ] Test eseguiti (livello concordato)
- [ ] Doc / PRD aggiornati
- [ ] Approvazione PO

≠ criteri di accettazione (che sono per singola US).

---

## 5. Backlog aperto

| Item | Priorità | Note |
|------|----------|------|
| {noto ma non ancora in Epic/US} | Alta \| Media \| Bassa | |

---

## 6. KPIs

| Metrica | Baseline | Target | Come misurata |
|---------|----------|--------|---------------|

---

## 7. Domande aperte

| # | Domanda | Owner | Scadenza | Stato |
|---|---------|-------|----------|-------|
| 1 | | | | Aperta \| Risolta |

---

## 8. Glossario

| Termine | Definizione |
|---------|-------------|
| {solo termini usati nel documento} | |

---
```

**Artifact e Versioni** — non di default. Solo se il PO chiede di tracciare artifact digitali (dashboard, mockup, script): vedi [artifact-e-versioni.md](artifact-e-versioni.md) e aggiungi come sezione 9.

Versioning documento: nuovo PRD → **1.0**; revisioni di contenuto → minor (1.1, 1.2…). Snapshot opzionale: `prd-YYYY-MM-DD.md` se il PO chiede versioning esplicito oltre al canone.

---

## Gate — Persona "Sistema"

Usa **Sistema** come soggetto solo se il *così da* è percepito da un utente reale.

| OK nel PRD | NO (→ Technical Spec) |
|------------|------------------------|
| Auto-save così da non perdere lavoro | Chiamata API con header Bearer |
| Sync notturno così da dati freschi in dashboard | Indicizzare record nel DB |
| Notifica email su evento così da allertare il team | Dettaglio cron / queue |

**Test:** se togliessi la storia dal PRD e la lasciassi solo ai dev, gli utenti noterebbero differenza? Sì → PRD. No → Spec tecnica.

Tre casi tipici OK: automazione che sostituisce lavoro manuale; background con effetto visibile; integrazione con impatto UX.

---

## AC vs DoD

| | Criteri di accettazione | Definition of Done |
|--|-------------------------|-------------------|
| Scope | Per **singola** storia | **Tutte** le storie |
| Forma | Verificabili sì/no, specifici | Contratto di qualità team |
| Esempio scarso | "Il filtro funziona" | (n/a) |
| Esempio utile | "Filtro 1 stella → solo rating=1; &lt;500ms; stato attivo evidenziato" | Review + test + doc + OK PO |

---

## Sizing (regola pratica)

| Scala | Lunghezza | Storie |
|-------|-----------|--------|
| Piccolo (2–4 sett.) | ~2–4 pagine | 3–6 US |
| Medio (1–3 mesi) | ~5–10 pagine | 10–20 US in Epic |
| Grande | Più PRD (uno per Epic/area) | — |

---

## Checklist rapida (live-check)

**Prima di scrivere:** utente/evidenza o hypothesis esplicita; problema chiaro; buy-in stakeholder.

**Durante:** formato Come/voglio/così da; ≥2 AC/storia; Epic↔US bidirezionale; NON-goals; OQ con owner+scadenza; backlog aperto aggiornato.

**Prima di condividere:** Vision leggibile da fuori; nessun placeholder residuo; glossario = solo termini usati.

**Durante sprint:** PRD allineato a planning; Done marcati; OQ aggiornate.

---

## PRD vs altri artefatti AF

| Artefatto | Ruolo |
|-----------|--------|
| Product brief | Decisione / GTM / ipotesi — non Epic/US |
| Lean Canvas | Ipotesi business early — alimenta Vision |
| personas / jtbd | Input discovery — non sostituiscono US+AC |
| `.feature` (a-gherkin) | Spec BDD dopo US+AC |
| Skill AF | Come l'AI esegue un processo ripetibile — deriva dal PRD |

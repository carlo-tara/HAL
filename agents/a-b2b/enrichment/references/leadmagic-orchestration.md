# LeadMagic — orchestration phase1 / phase2

Schema riusabile per consumer L2 (path/script restano nel progetto). Complementa la cascade A in [SKILL.md](../SKILL.md) § Cascade A (step LeadMagic).

---

## When

Dopo HubSpot + Apollo (o sui soli miss), quando LeadMagic è abilitato e non `SKIP_LEADMAGIC`.  
Phase2 è **opzionale** e budget-capped: non avviarla senza budget/crediti espliciti.

---

## Phase model

| Phase | Goal | Typical endpoints | Stop when |
|-------|------|-------------------|-----------|
| **1 — Profile / fill** | Completare persona/account mancanti sul cohort | `b2b-profile`, `company-enrich`, `profile-search` (L2 sceglie l’ordine) | Cap chiamate, budget crediti, coda vuota, o 429 esauriti |
| **2 — Deep / verify** | Arricchimenti secondari (mobile, verify, LinkedIn deep) su sottoinsieme qualificato | endpoint L2-specifici | `PHASE2_BUDGET` esaurito o code vuote |

**Anti-pattern:** phase2 su tutto il cohort senza gate; spend prima di ICP/fit (vedi [enrichment-gates.md](enrichment-gates.md)).

---

## Controls (env conceptuali)

I nomi esatti sono L2; i **ruoli** sono L1:

| Control | Role |
|---------|------|
| Max calls / session | Hard cap sulle HTTP phase1 (0 = no cap oltre budget) |
| Concurrency | Parallelismo HTTP (rispettare rate limit vendor) |
| Checkpoint every N | Persistenza incrementale (JSON +/o SQLite) — ripresa after crash |
| Budget crediti phase1 | Soft cap spesa sessione |
| Budget crediti phase2 | Soft cap spesa deep |
| Skip flag | `SKIP_LEADMAGIC` (truthy) → salta entrambe le fasi |

---

## Persistence

- **Master** = SQLite (un master per product line); CSV solo handoff.
- Chiave riga tipica: `(email, segmento|cohort, provider)` con `provider=leadmagic`.
- Scrivere `endpoint` usato + campi standard (`job_title`, `seniority`, `company_name`, `linkedin_url`, `recognized`, …) così i rerun sono idempotenti.
- Checkpoint: flush periodico; non tenere solo RAM su run lunghi.

---

## Credit report

A fine run (o fine phase): report lookup/crediti LeadMagic distinti da Apollo/HubSpot.  
Se phase2 non partita: dichiararlo (budget 0 / skip / no queue).

---

## Fatti vendor misurati (brainbeez newleads 2026-10→11; AGG-09 — soglia ≥2 forzata su indicazione owner 2026-11-28)

- `employee-finder`: l'array di risposta arriva sotto la chiave **`data`** (la doc dice `employees`: obsoleta). Costo restituito 0.05 crediti/dipendente; risposta vuota = gratis; **nessuna email** nel payload (email-finder ≈1 credito/item, off di default).
- 429 transitori con ≥8 worker paralleli, ~95% recuperabili ritentando (`--retry-errors`): progettare la coda con retry, non con worker sincroni.

## L2 delta

Path script (`*-orchestration.js`, `*-phase2-queues.js`, …), default numerici, segment rules e comandi Cursor restano nel figlio `extends: a-enrichment`.

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

## L2 delta

Path script (`*-orchestration.js`, `*-phase2-queues.js`, …), default numerici, segment rules e comandi Cursor restano nel figlio `extends: a-enrichment`.

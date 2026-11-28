# Domain-first enrichment workflow

Entrypoint **B** parallelo alla cascade cohort/CRM (entrypoint **A** in `a-enrichment` SKILL). Non sostituisce A.

## Quando usarlo

- Singolo dominio o account (`acme.com`) da qualificare prima di un batch.
- Prospect fuori dal CRM / senza export cohort.
- Deep-dive su top lead dopo un lead-research batch.

## Fasi

1. **Research & ICP check** — overview azienda (fonte L2 o tool progetto); valutare vs ICP + [enrichment-gates.md](enrichment-gates.md).
2. **Deep enrichment** (solo se MATCH o conferma umana):
   - Company brief (iniziative, leadership, signal).
   - Target titles da ICP L2.
   - Apollo: org → people → enrich ([lead-research-output.md](lead-research-output.md) § Apollo 3-step).
   - LeadMagic opzionale: email verify + mobile su miss / quando chiave presente.
3. **Strategy output** — angolo outreach / conversation starters (non draft email/call).
4. **Merge opzionale** — scrivere nel master SQLite solo se in scope; altrimenti handoff CSV/report.
5. **Credits report** — conteggio lookup per provider usati.

## Fatti vendor Apollo (brainbeez newleads 2026-10→11; AGG-09 — soglia ≥2 forzata su indicazione owner 2026-11-28)

- MCP e headcount-baseline richiedono **master key**: chiave scoped → 403 `API_INACCESSIBLE`; la chiave REST può morire a metà sessione → OAuth-MCP è il canale affidabile (il registro tool di Zed si aggiorna solo a reload e lo `enabled` in settings è autoritativo).
- Il filtro **buying-intent non è esposto via API**: le liste intent sono indistinguibili dai dati ⇒ deduplicarle per headcount growth + nome file.
- `Apollo Account Id` negli export **non è chiave di join** (org name ≠ account name, 6/16 orfani misurati) → join per dominio.

## Output a sezioni

1. ICP check (+ fit score se applicabile)
2. Company brief
3. Contacts (email verify status, LinkedIn, notes)
4. Strategy (trigger signal, angle) — drafting → `a-copywriter` se richiesto
5. API credits used
6. Next actions (merge master / CSV / deeper research)

## Micro-QA (opzionale)

Se `photo_url` Apollo punta a avatar LinkedIn generico (`static.licdn.com/aero-v1/...`), flaggare profilo potenzialmente stale.

## Anti-pattern

- Spendere Apollo/LeadMagic prima del gate ICP.
- Trattare questo workflow come unico cascade (ignorare cohort/CRM quando il progetto è batch).
- Hardcodare path provider research-web in L1.

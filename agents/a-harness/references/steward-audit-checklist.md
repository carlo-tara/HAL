# Steward — checklist audit periodica

Usata da `/steward` e da `docs/harness-engineering.md`.

- [ ] Ciclo R/G/R su commit recenti
- [ ] Commit con **perché** architetturale
- [ ] Context budget ≤4 file
- [ ] Codice minimizzato (design difensivo)
- [ ] Termini vs `docs/glossary.md`
- [ ] Nessun import cross bounded context
- [ ] `make ready-for-review` funzionante e documentato (CI-first)
- [ ] Nessuna regola harness morta — verifica meccanica L2↔`Makefile`: ogni target elencato negli artefatti della Platform API (tabelle/§) deve esistere davvero (`make help` contro tabella; caso brainbeez 2026-10-27, audit #2: 6 target dichiarati ma assenti → aggiunti)
- [ ] Hooks/Make = guarantees (no always/never solo in prompt)
- [ ] Failure modes: forget conventions / fake green / scope creep / abandon / invented API / silent regression
- [ ] Freeze list aggiornata
- [ ] Harness changelog aggiornato se infra cambiata
- [ ] Anti self-harness (no secondo agent loop / CLI ad hoc)

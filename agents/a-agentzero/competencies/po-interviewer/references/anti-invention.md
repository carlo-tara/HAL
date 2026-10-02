# Anti-invention

## Vietato

- Inventare personas, job, unmet needs o scenari BDD come **attivi/confermati** senza ratifica PO
- Inventare demografia, reddito, età, SLA, microcopy lockata, threat model non in evidenza
- Chiudere gap di coverage inventando behavior assente da `jtbd.md` / seeds / PO
- Spacciare inferenze intuitive come research empirica

## Consentito

- Bozze `status: hypothesis` con `source:` (prd | mockup | po | po_nl | inferenza)
- Domande al PO per colmare gap
- Generazione da NL (`/add`, `/add-story`, `/add-need`, `/add-scenario`) **come hypothesis** fino a conferma
- Marcare `untestable_as_ui` / `out_of_scope` con motivazione

## Regola d’oro

Se togliendo l’etichetta `hypothesis` il testo sembrerebbe un fatto di prodotto, **non** è ancora esportabile come attivo.

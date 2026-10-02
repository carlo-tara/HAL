# Coverage model

Tre layer obbligatori. Un gap in qualsiasi layer = coverage incompleta (salvo waiver PO nel README).

## Layer 1 — JTBD

| Sorgente | Deve mappare a |
|----------|----------------|
| Ogni `SS-xx` attivo | ≥1 Scenario (tag `@seed-ssNN`) |
| Ogni `N-xx` high-opportunity non `untestable_as_ui` | ≥1 Scenario che lo esercita (`@need-nNN`) |
| Ogni Core Job | ≥1 `@journey` (o waiver esplicito) |
| Job map steps critici | Coperti da journey o Scenario dedicati |

Non inventare behavior fuori da jtbd/PRD/mockup. Orphan → waiver PO o escalate `a-jtbd`.

## Layer 2 — UI controls

Ogni controllo interattivo rilevabile da mockup/PRD/UI binding (vedi [ui-interaction-inventory.md](ui-interaction-inventory.md)):

| Famiglia | Esempi |
|----------|--------|
| CTA | primary gated, secondary, link testuali |
| Form | submit, validation, campi obbligatori, reset |
| Nav | tab, back/prev/next, ricerca portafogli |
| Disclosure | expand/collapse, overlay open/close |
| Selection | card Consigliato/Alternativa, radio/checkbox |

**Gap UI** = controllo senza Scenario e senza waiver. Preferire Scenario intent-based (esito), non cronaca click.

## Layer 3 — External IO

Ogni fonte esterna o persistenza (vedi [external-io-catalog.md](external-io-catalog.md)):

| Famiglia | Esempi |
|----------|--------|
| Spreadsheet-sourced data | catalogo ETF da foglio DASHBOARDS (anche se embedded statico) |
| Browser storage | `localStorage` catalogo custom |
| Static embeds | portfolio list, REBALANCE_DATA, prezzi mock |
| DB/API server | solo se nel PRD; altrimenti documentare assenza |

**Gap IO** = fonte/failure mode osservabile senza Scenario.

## File clustering

- 1 file ≈ 1 flusso/capability/Core Job
- Più Scenario per file OK
- README traccia Seed/Need **e** UI/IO → Scenario/file

## Out of scope

- Behavior in PRD ma assente dal mockup → backlog/`blocked_for`, non Scenario attivi
- SLA inventati (perf) o threat inventati (secure) senza evidenza PO

# Validate workflow (`/validate`, `/gap`)

## Report obbligatorio

### A. JTBD

| Check | Pass |
|-------|------|
| Ogni SS attivo ha Scenario | |
| Need prioritari esercitati o `untestable_as_ui` | |
| Ogni Core Job ha `@journey` o waiver | |
| Nessun Scenario order-dependent | |

### B. UI inventory

| Check | Pass |
|-------|------|
| Inventory presente in README | |
| Ogni UI-xx → Scenario o waiver | |
| Controlli gated (CTA/terms) coperti | |

### C. IO inventory

| Check | Pass |
|-------|------|
| Inventory IO presente in README | |
| Persistenza / degrado storage coperti se applicabili | |
| Assenza DB/API documentata se fase 1 | |

### D. Qualità

| Check | Pass |
|-------|------|
| `# language: it` | |
| No selettori DOM nei passi | |
| Tag coerenti ([tagging.md](tagging.md)) | |
| Backlog `blocked_for` non tradotto in Scenario attivi | |

## Output

- Elenco gap (SS/N/UI/IO)
- Smell (Given fragili, journey implicita, file monolitici)
- Draft fix proposti — scrittura solo dopo conferma PO (`/export`)

`/gap` = stesso report, read-only, senza proporre export automatico.

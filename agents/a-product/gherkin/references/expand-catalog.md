# Expand catalog

Famiglie edge da applicare **dopo** happy path e inventory UI/IO. Scope sempre col PO.

## Generiche (preesistenti)

| Famiglia | Tag | Esempi |
|----------|-----|--------|
| boundary | `@boundary` | valori limite, gated CTA, campi numerici invalidi |
| flow-interruption | `@flow-interruption` | chiudi overlay, cambia tab, storage failure mid-flow |
| network / infra | `@edge-infra` | solo se prodotto ha rete; errori osservabili |
| auth | `@auth` | solo se prodotto ha auth |

## UI control families

| Famiglia | Tag | Esempi |
|----------|-----|--------|
| primary CTA | `@ui-control` | enabled/disabled, post-click navigation |
| secondary / link | `@ui-control` | Terms, footer, "Accesso dashboard" |
| form validation | `@ui-control` `@boundary` | required, non-numeric, empty |
| cancel / back | `@ui-control` | senza perdita dati critici |
| disclosure | `@ui-control` | expand/collapse intro |
| tab / nav | `@ui-control` | Portafoglio/PAC/Tracking; prev/next portfolio |
| overlay | `@ui-control` | Terms, Dashboard, Aggiungi ETF, ribilancio |
| empty / error state | `@ui-control` `@edge` | no search results, incomplete registration |

## External IO families

| Famiglia | Tag | Esempi |
|----------|-----|--------|
| spreadsheet-sourced | `@spreadsheet-source` `@external-io` | search catalog matches embedded DASHBOARDS data |
| storage persist | `@storage` `@external-io` | custom ETF survives reload |
| storage degrade | `@storage` `@flow-interruption` | blocked localStorage |
| static determinism | `@external-io` `@boundary` | stesso profilo → stesso consiglio |

## Regole

- `/expand` sceglie famiglie rilevanti dall'inventory, non tutte in assoluto
- `/cover` chiude gap inventory; `/expand` aggiunge varianti edge su happy già presenti
- `/secure` e `/perf` restano cataloghi dedicati (non duplicare qui threat/SLA)

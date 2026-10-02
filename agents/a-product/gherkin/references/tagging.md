# Tagging

## Identità

| Tag | Uso |
|-----|-----|
| `@persona-pNN` | Persona primaria dello scenario |
| `@job-jNN` | Core Job |
| `@seed-ssNN` | Scenario seed JTBD |
| `@need-nNN` | Unmet need esercitato |

## Ruolo nello suite

| Tag | Uso |
|-----|-----|
| `@journey` | Percorso E2E self-contained del Core Job |
| `@happy-path` | Caso felice |
| `@edge` | Variante non-exception |
| `@boundary` | Limiti input/stato |
| `@exception` | Blocco / rifiuto / percorso alternativo |
| `@flow-interruption` | Interruzione senza corruzione dati |

## UI / IO

| Tag | Uso |
|-----|-----|
| `@ui-control` | Scenario centrato su controllo interattivo |
| `@external-io` | Coinvolge fonte/persistenza esterna |
| `@storage` | Browser storage / persistenza locale |
| `@spreadsheet-source` | Dati originati da spreadsheet (anche embedded) |
| `@edge-infra` | Fallimenti infrastrutturali osservabili |

## Secure / perf

Gestiti dalla competenza `bdd-security-performance` (`@authz`, `@input`, `@session`, `@privacy`, `@abuse`, `@feedback`, `@latency`, …).

## Regole

- Tag multipli OK; preferire precisione a quantità
- Feature-level: `@persona-*` `@job-*`; Scenario-level: seed/need/journey/ui/io

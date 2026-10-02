# Suite README template

# Features coverage — {prodotto}

Suite generata da `a-gherkin` a partire da `jtbd.md` + `personas.md` + PRD/mockup.

## Features coverage

| Seed / Need / Job | Scenario | File | Note |
| --- | --- | --- | --- |
| SS-01 | … | ….feature | @journey |

## UI inventory

| ID | Schermata | Controllo | Scenario / waiver | File |
| --- | --- | --- | --- | --- |
| UI-01 | … | … | … | … |

## IO inventory

| ID | Fonte | Comportamento | Scenario / waiver | File |
| --- | --- | --- | --- | --- |
| IO-01 | … | … | … | … |

## Journey map

- **J-01**: JM-… → … — file `….feature`

## Edge / security / performance in scope

| Famiglia | Present | Out of scope |
| --- | --- | --- |
| boundary | | |
| ui-control | | |
| external-io / storage | | |
| security | | |
| performance | | |

## Out of scope / backlog

| Item | Stato | Motivo |
| --- | --- | --- |
| … | blocked_for / hypothesis | … |

## Note per il coding agent

Vedi handoff `a-gherkin/references/handoff-to-dev.md`. Contratto = `features/*.feature`; interazioni semantiche, non selettori CSS fragili.

# External IO catalog

Famiglie di fonti esterne / persistenza da coprire quando presenti in PRD o mockup.

## Come costruire l'inventory

1. Cerca nel PRD/mockup: spreadsheet, DB, API, `localStorage`, file embed, sync
2. Distingui: **origine dati** vs **runtime failure** vs **assenza intenzionale**
3. Solo failure/comportamenti **osservabili in UI** → Scenario
4. ID stabili `IO-01`…

## Famiglie

| Famiglia | Tag tipici | Cosa testare |
|----------|------------|--------------|
| Spreadsheet source | `@spreadsheet-source` `@external-io` | Catalogo/dati derivati dal foglio; coerenza campi (ISIN, nome, prezzo); assenza di edit "silenzioso" del foglio in-app se out of scope |
| Browser storage | `@storage` `@external-io` | Persistenza cross-session; rimozione; degrado se storage bloccato |
| Static embed | `@external-io` | Liste portfolio/prezzi/REBALANCE deterministici; stesso input → stesso output |
| Server DB / API | `@external-io` `@edge-infra` | Solo se nel prodotto; errori rete/auth osservabili |
| No DB (fase 1) | — | Documentare in README "assenza DB" come out of scope, non inventare Scenario DB |

## Failure modes comuni (UI-osservabili)

| Trigger | Then tipico |
|---------|-------------|
| Storage non disponibile | Dato resta in sessione; messaggio di salvataggio fallito; resto del flusso non bloccato |
| Catalogo vuoto / no match | Empty state; form manuale disponibile se previsto |
| Dati statici mancanti per un portfolio | UI non propone ribilanciamento / messaggio chiaro (se specificato) |

## Anti-pattern

- Inventare sync real-time o DB se PRD dice static/local only
- Assertare struttura interna dello spreadsheet oltre a ciò che l'utente vede
- Scenario "il server risponde 500" senza prodotto server-side

## Output

- Tabella IO inventory in `features/README.md`
- Scenario dedicati o `Rule:` di persistenza/degrado nel file del flusso interessato

# UI interaction inventory

Checklist per estrarre controlli da mockup / PRD / `ui_bindings` in jtbd **prima** di scrivere Gherkin.

## Come costruire l'inventory

1. Elenca schermate/flussi (landing, wizard step, tab, overlay)
2. Per ogni schermata, elenca controlli interattivi (pulsanti, link, form, toggle, tab)
3. Per ogni controllo, definisci casi: happy, edge, exception/blocked
4. Assegna `id` stabile (`UI-01`…) e mappa a Scenario o waiver

## Template riga inventory

| ID | Schermata | Controllo | Azione utente | Esito atteso | Tipo | Scenario / waiver |
|----|-----------|-----------|---------------|--------------|------|-------------------|
| UI-01 | Landing | CTA Cerca portafoglio | click senza consenso | resta bloccata | exception | … |

## Famiglie da non dimenticare

| Famiglia | Domande guida |
|----------|---------------|
| Primary CTA | Quando è enabled/disabled? Cosa cambia dopo il click? |
| Secondary / link | Apre overlay, naviga, o solo testo? |
| Form fields | Obbligatori? Validazione? Valori di default? Persistono al cambio vista? |
| Checkbox / terms | Gate su CTA? Testo apribile senza sbloccare? |
| Cards / choice | Consigliato vs Alternativa vs altro; selezione mutua? |
| Tabs | Cambio tab perde dati? Stato indipendente? |
| Expand/collapse | Contenuto nascosto resta nel DOM logicamente disponibile? |
| Overlay / panel | Open/close senza perdita dati? Escape/chiudi? |
| Search / filter | Empty result? Match ISIN/nome/simbolo? |
| Prev/next / browse | Limiti di lista? Wrap? |
| Apply / confirm bulk | Singolo vs tutti; undo? |

## Anti-pattern

- Scenario che cita `#id`, classi CSS, coordinate
- Un Scenario per ogni pixel di hover senza esito di business
- Saltare controlli "secondari" (Terms, footer didattico, dashboard entry) senza waiver

## Output

- Tabella inventory in `features/README.md` (sezione UI inventory)
- Tag Scenario: `@ui-control` (+ seed/need se applicabile)

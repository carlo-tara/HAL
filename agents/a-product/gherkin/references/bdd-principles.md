# BDD principles (L1)

1. Specifica **comportamento osservabile** e intento utente, non implementazione.
2. Given costruisce stato; When è azione utente; Then è esito dichiarativo.
3. Scenari indipendenti: nessun "Scenario N lascia stato per N+1".
4. Journey lunghe: tag `@journey` + Given che ripristina il punto di partenza logico.
5. Non cronaca di click; raggruppa azioni in passi di business.
6. Lingua: `# language: it` nei progetti IT salvo L2 diversa.
7. Inventory UI/IO guida la completezza; i passi restano intent-level.

# Gherkin style

- Header: `# language: it`
- `Funzionalità:` / `Scenario:` / `Schema dello scenario:` / `Regola:` / `Contesto:` (IT keywords)
- Commenti `#` per job id, UI binding, fonti (jtbd/PRD) — non per assert
- `Regola:` per cluster boundary/exception sullo stesso flusso
- Outline + `Esempi:` quando cambia solo una dimensione (fase, campo, navigazione)
- Evitare passi "clicca il bottone X"; preferire "conferma per proseguire" / "apre il tab PAC"

# Selector strategy (handoff only)

Nei `.feature`: linguaggio utente.

Nel prompt handoff al coding agent:

- Preferire ruolo, label, testo visibile, `getByRole` / equivalenti
- Evitare `#id`, classi generate, nth-child fragili
- Data-testid solo se esplicitamente nella design system del progetto

# Component decision — Skills vs MCP vs Hooks vs Sub-agent

Mnemonic:

> **Knowledge → skill · Access → MCP · Guarantees → hook/Make · Persona/fresh context → competency (sub-agent role)**

| Bisogno | Scegli | Affidabilità |
|---------|--------|--------------|
| Come facciamo X (procedura) | Competenza / SKILL | Probabilistica (modello segue) |
| Raggiungere sistema esterno + credenziali | MCP (L2 opt-in) | Strutturata |
| Deve succedere sempre (lint, test, no-skip) | Hook o target `make` | Deterministica |
| Ruolo Navigator/Driver/Steward | Competenza di fase | Contesto isolato via fase |

## Regola AF

Se ripeti «always/never» in prompt → **promuovi** a hook o target Make (`platform-api` / steward).

Non scrivere skill che fanno `curl` con secret → MCP o CLI documentata nel Makefile.

Pin: [pin-curated-lists.md](pin-curated-lists.md)

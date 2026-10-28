---
name: a-harness
extends: a-agentzero
version: 1.9.1
extends-version: 1.12.0
description: >-
  Reason why: senza test, gate Make e ritmi sostenibili, lo sviluppo non ha uscita verificabile né qualità stabile.
  Meta-Harness: TDD XP, Steward, DDD, Makefile gates, session progress, when-stuck, Plan→Act, L3.
  Skill-layer sopra Zed/Claude. Not for product discovery or BDD authoring.
---

# a-harness — Meta-Harness (L1)

Agente L1 orchestratore dello sviluppo TDD/XP. Eredita da **a-agentzero**.

**Caricamento Dinamico & System 1 (Laya):**

- **Progressive disclosure** — carica le competenze on-demand (`context-budget`); non caricare tutto L1.
- **System 1 Gating (Laya):** Pre-filtro rapido (routing test failure, score rischio blocco) prima di invocare System 2 (deep reasoning) via `python3 router.py triage` o `router.py score`.
- Durante l'uso di test runner, adotta il troncamento dei log (es. via `head_lines: 5`, `tail_lines: 15`).
- **Post-deploy gate funzionale** — `health` verde e container ricreato non sono prova di contratto: dopo ogni deploy/`make up` verifica una chiamata reale sul percorso primario (response 200 + riga di log di successo). Caso reale: un `NameError` nell'hook di logging faceva rispondere 500 a ogni `/predict` per giorni, con `/health` regolarmente verde.
- **Static analysis gate (policy L1)** — senza un gate statico standardizzato ogni progetto inventa la propria quality bar e i nodi act chiudono senza uscita verificabile. Tool stack: `ruff` (lint/format), `pyright` o `mypy` (types), `shellcheck` (severity error); audit opzionali (dead-code, secrets, deps) aggregati in `check-static`. Target esposti nella Platform API (`references/makefile-template.mk`): `lint`, `types`, `check-static`, `check-static-diff` (soli file del diff di nodo), `pre-commit`. Uscita di un nodo act: `check-static-diff` = 0 e baseline globale non peggiorata; whitelist documentata, mai un bypass silenzioso.

## Output (Contratto)

- **Zero conversazione.**
- Solo diff sintetici, comandi `make` o report di esito in listato/tabella.

Per l'elenco esatto delle competenze (steward, TDD, progress), le tabelle Slash command (es. /red, /green, /cycle) e i prerequisiti (Platform API, Glossario):
Leggi `references/harness-extended.md`.

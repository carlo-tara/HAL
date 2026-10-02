# Bounded contexts — HAL

Mappa confini del meta-repo. Ogni `/slice` dichiara quale context è attivo.

## Context map

| Context | Path modulo | Responsabilità | Integrazioni |
|---------|-------------|----------------|--------------|
| Protocol / L0 | `a-agentzero/` | Protocollo ereditarietà, sicurezza non sovrascrivibile, `/learn`, `/sync`, comandi L0, competenze baseline, `agent-version.sh` | → Domain Agents via `extends:`; → Tooling via scripts; → Consumer Delta via scaffold |
| Domain Agents / L1 | `a-copywriter/`, `a-illustrator/`, `a-seozoom/`, `a-wordpress/`, `a-personas/`, `a-jtbd/`, `a-gherkin/`, `a-charts/`, `a-b2b/`, `a-product/`, `a-po/`, `a-enrichment/`, `a-harness/`, `a-uiux/` | Skill di dominio, competencies locali, extension-template, deploy per agente | ← Protocol; → Consumer Delta (template L2); → Tooling (`deploy.sh`) |
| Consumer Delta / L2 | `.cursor/skills/*/` (qui: `harness-agentfactory/`); nei consumer: `{repo}/.cursor/skills/` | Delta progetto: path, brand, override, bootstrap locale | ← L1 via `extends:`; non importa codice L1 cross-tree |
| Tooling / Sync-Deploy | `deploy-all.sh`, `a-*/deploy.sh`, `a-agentzero/scripts/`, `scripts/export-*.sh`, `dist/` | Deploy dual-runtime, report versioni, export pack Claude | ← Protocol/L1 path; emette report STALE |
| Docs / Harness meta | `docs/`, `Makefile`, `.cursor/product/` | Glossario, bounded contexts, Platform API, progress, manuali harness | Legge path L0/L1; non muta business skill senza slice |

## Regole

1. **Nessun import diretto** di contenuti skill tra L1 sibling (no copia corpus cross-dominio senza pin/promozione `/sync <`)
2. Integrazioni solo via colonna Integrazioni (`extends`, deploy symlink, eventi di report)
3. Shared kernel: `a-agentzero/AGENT-PROTOCOL.md` + competenze L0 — owner Protocol / L0
4. Makefile (Docs / Harness meta) è l'unico ingresso verify; non sostituire con bash one-off in chat

## Eventi di dominio pubblici

| Evento | Publisher | Subscribers | Schema |
|--------|-----------|-------------|--------|
| VersionChainStale | Tooling / Sync-Deploy | Steward, operatori `/sync` | `{ agent, parentVersion, extendsVersion }` |
| ReadyForReviewPassed | Docs / Harness meta | Umano (intent review) | `{ session_id, exit: 0 }` |
| L2GeneralizationCandidate | Protocol (`/sync <`) | Steward / autori L1 | `{ path, dup\|promote }` |

## Port pubblici (alternativa a eventi)

| Port | Context | Consumatori |
|------|---------|-------------|
| `Makefile` targets (`test-unit`, `pre-commit`, `ready-for-review`, …) | Docs / Harness meta | a-harness, CI, operatori |
| `agent-version.sh chain\|pending\|competency-chain` | Tooling / Sync-Deploy | sync-agents, Make, `/sync ?` |
| `sync-agents.sh [--dry-run]` | Tooling / Sync-Deploy | `/sync !`, Make `test-unit` |
| `deploy-all.sh` / `a-*/deploy.sh` | Tooling / Sync-Deploy | sync-agents, operatori |

## Waiver temporanei

| Waiver | Motivo | Scadenza |
|--------|--------|----------|
| `test-int` / `test-e2e` / `db-*` / `check-parity` = `@true` | Meta-repo senza app suite / DB / dual-canon | Fino a introduzione tooling reale documentato in L2 |

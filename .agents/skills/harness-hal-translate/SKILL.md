---
name: harness-hal-translate
extends: a-harness
version: 1.0.1
extends-version: 1.10.1
description: >-
  Reason why: senza Platform API e gate, il progetto delegato resterebbe uno script privo di uscita verificabile.
  Delta harness per hal_translate (MT locale LibreTranslate/Argos): Makefile Platform API, path artefatti, N/A documentati, safety note specifiche del servizio MCP/locale.
---

# harness-hal-translate — delta L2

Skill figlia (L2). All'avvio: L0 `a-agentzero` → L1 `a-harness` → **questo file**. Solo override di path, stack e gate — non rieseguire il workflow L1 nel body.

## Progetto

| Campo             | Valore                                                                           |
| ----------------- | -------------------------------------------------------------------------------- |
| Nome              | hal_translate (MT locale LibreTranslate/Argos)                                   |
| Working directory | `/var/www/hal_translate`                                                         |
| Stack             | Docker (immagine ufficiale libretranslate) + adapter Python stdlib-only (urllib) |
| Bootstrap profile | **standard** (2026-10-31)                                                        |
| Effort default    | thorough                                                                         |

## Path locali

| Artefatto        | Path                                |
| ---------------- | ----------------------------------- |
| Platform API     | `Makefile` (root)                   |
| Glossario        | `docs/glossary.md`                  |
| Bounded contexts | `docs/bounded-contexts.md`          |
| PRD              | `docs/PRD.md`                       |
| Progress         | `docs/product/agent-progress.md`    |
| Residui          | `./ToDo.md`                         |
| Changelog        | `CHANGELOG.md` (Keep a Changelog)   |
| Docker           | `Dockerfile` + `docker-compose.yml` |

## Target Makefile

| Target        | Comando                                      |
| ------------- | -------------------------------------------- |
| \`test-unit\` | \`python3 -m pytest -q\`                     |
| \`docker-up\` | \`docker compose up -d\` (engine :5075)      |
| probe         | \`docker compose --profile tools run probe\` |

## N/A documentati (L1)

- \`test-int\`: test contro engine reale al via in M1 (ToDo); oggi N/A documentato.
- \`test-e2e\`/\`check-parity\`: N/A.

## Bounded context attivi

Vedi `docs/bounded-contexts.md`; ogni `/slice` dichiara il context toccato.

## Safety note specifiche

- **Ricaduta LLM mai silenziosa**: \`select_backend\` ritorna \"llm\" solo se esplicito o nessun backend locale; va annotata nel evento metriche.
- **tokens.total=0** è contrattuale per gli eventi \`translation_stage\` (accettazione hal_system2 P2).
- **Secreti**: API key solo via \`.env\` del consumer/engine, mai nel compose versionato.
- **Post-deploy**: healthcheck verde ≠ contratto → \`app/probe.py\` (traduzione reale) obbligatorio dopo ogni upgrade.

## Ref cross-progetto

- Consumer/mandante: `hal_system2/ToDo.md` cluster «MCP delegation — token shrink» (`#token-shrink`).
- Shared: `agents` e `.agents` = symlink verso `/var/www/hal_gateway`; i gate L0/L1 valgono invariati.

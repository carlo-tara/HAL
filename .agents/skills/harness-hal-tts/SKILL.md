---
name: harness-hal-tts
extends: a-harness
version: 1.0.1
extends-version: 1.10.1
description: >-
  Reason why: senza Platform API e gate, il progetto delegato resterebbe uno script privo di uscita verificabile.
  Delta harness per hal_tts (TTS locale piper1-gpl): Makefile Platform API, path artefatti, N/A documentati, safety note specifiche del servizio MCP/locale.
---

# harness-hal-tts — delta L2

Skill figlia (L2). All'avvio: L0 `a-agentzero` → L1 `a-harness` → **questo file**. Solo override di path, stack e gate — non rieseguire il workflow L1 nel body.

## Progetto

| Campo             | Valore                                                                        |
| ----------------- | ----------------------------------------------------------------------------- |
| Nome              | hal_tts (TTS locale piper1-gpl)                                               |
| Working directory | `/var/www/hal_tts`                                                            |
| Stack             | Python 3.12 stdlib http.server + binario piper1-gpl (ARG release da spike M0) |
| Bootstrap profile | **standard** (2026-10-31)                                                     |
| Effort default    | thorough                                                                      |

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

| Target              | Comando                                                  |
| ------------------- | -------------------------------------------------------- |
| \`test-unit\`       | \`python3 -m pytest -q\` (DI runner, nessun binario req) |
| \`docker-build/up\` | compose :8093 localhost                                  |

## N/A documentati (L1)

- \`test-int\`: sintesi reale post-spike M0; oggi N/A (DI runner copre il contratto).
- \`test-e2e\`: N/A; health+speech probe manuale in M1.

## Bounded context attivi

Vedi `docs/bounded-contexts.md`; ogni `/slice` dichiara il context toccato.

## Safety note specifiche

- **Verità dellexit**: exit≠0 di piper → RuntimeError/500, mai audio vuoto o 200 finto (test \`exit_verita\`).
- **Cache = rigenerabile**: \`/data/cache\` volume, non evento storico; non scrivere in \`events/\`.
- **rhasspy/piper archiviato**: usare solo release OHF-Voice \`piper1-gpl\`; URL mai hardcodati nei test (ARG Dockerfile).

## Ref cross-progetto

- Consumer/mandante: `hal_system2/ToDo.md` cluster «MCP delegation — token shrink» (`#token-shrink`).
- Shared: `agents` e `.agents` = symlink verso `/var/www/hal_gateway`; i gate L0/L1 valgono invariati.

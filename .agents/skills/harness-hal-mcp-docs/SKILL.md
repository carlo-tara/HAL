---
name: harness-hal-mcp-docs
extends: a-harness
version: 1.1.1
extends-version: 1.10.2
description: >-
  Reason why: senza Platform API e gate, il progetto delegato resterebbe uno script privo di uscita verificabile.
  Delta harness per hal_mcp_docs (MCP estrazione documenti): Makefile Platform API, path artefatti, N/A documentati, safety note specifiche del servizio MCP/locale.
---

# harness-hal-mcp-docs — delta L2

Skill figlia (L2). All'avvio: L0 `a-agentzero` → L1 `a-harness` → **questo file**. Solo override di path, stack e gate — non rieseguire il workflow L1 nel body.

## Progetto

| Campo             | Valore                                                           |
| ----------------- | ---------------------------------------------------------------- |
| Nome              | hal_mcp_docs (MCP estrazione documenti)                          |
| Working directory | `/var/www/hal_mcp_docs`                                          |
| Stack             | Python 3.12 + pypdf (lazy import); core stdlib (zipfile/re/json) |
| Bootstrap profile | **standard** (2026-10-31)                                        |
| Effort default    | thorough                                                         |

## Path locali

| Artefatto          | Path                                                                 |
| ------------------ | -------------------------------------------------------------------- |
| Platform API       | `Makefile` (root)                                                    |
| Glossario          | `docs/glossary.md`                                                   |
| Bounded contexts   | `docs/bounded-contexts.md`                                           |
| PRD                | `docs/PRD.md`                                                        |
| Slice contratti    | `docs/slices/` (es. M2-chapter-route)                                |
| Spike              | `docs/spikes/` (tier N, M3)                                          |
| Benchmark          | `docs/benchmark-m1.md` + `scripts/bench_m1.py`                       |
| Progress           | `docs/product/agent-progress.md`                                     |
| Work Graph/handoff | `product/state/`                                                     |
| Residui            | `./ToDo.md`                                                          |
| Changelog          | `CHANGELOG.md` (Keep a Changelog)                                    |
| Docker             | `Dockerfile` + `docker-compose.yml`                                  |
| Chunk-store        | `HAL_CHUNKS_DIR` (default `/data/chunks`), layout `<base>/<doc_id>/` |

## Target Makefile

| Target               | Comando                                                        |
| -------------------- | -------------------------------------------------------------- |
| \`test-unit\`        | \`pytest -q -m "not integration"\`                             |
| \`test-int\`         | \`pytest -q -m integration\` (contratto stdio su `app.server`) |
| \`pre-commit\`       | \`check-static-diff\`                                          |
| \`ready-for-review\` | come L1 (gate Make)                                            |

## N/A documentati (L1)

- \`test-e2e\`/\`check-parity\`: N/A (nessun runtime dual-canon).
- \`sync-assets\`: rimosso dal Platform API (nessun asset da sincronizzare, graph N4).

## Bounded context attivi

Vedi `docs/bounded-contexts.md`; ogni `/slice` dichiara il context toccato.

## Safety note specifiche

- **Manifest-only**: il tool ritorna SOLO il manifest (doc_id/sha256/conteggi); assert di test: contenuto pagine mai nella risposta. `doc_search`/`chapter_route` restituiscono solo puntatori (id+score), mai corpo chunk.
- **Idempotenza**: stesso \`sha256\` → non riscrivere chunk.
- **CPU-first**: nessun modello GPU nel tier D; spike N (MinerU/docling) solo via slice dedicato con via libera GPU.
- **Laya Retrieval**: opzionale e solo query-time — env `HAL_GATEWAY_ROOT` (mai path hardcoded), `HAL_LAYA=off` per offline/failsafe; astensione o servizio irraggiungibile → `escalate` con indice minimo, mai verdetti fabricati, mai System 2 invocato dal MCP.
- **doc_id validato**: `^[A-Za-z0-9_-]{1,128}$` — caratteri di percorso respinti (scritture confinate alla base chunk, PRD §5).

## Ref cross-progetto

- Consumer/mandante: `hal_system2/ToDo.md` cluster «MCP delegation — token shrink» (`#token-shrink`).
- Shared: `agents` e `.agents` = symlink verso `/var/www/hal_gateway`; i gate L0/L1 valgono invariati.

# Bounded contexts — HAL Gateway

Mappa confini (seed da `/bootstrap` standard 2026-10-25, verificata sui file reali).
Ogni `/slice` dichiara quale context è attivo. Rifinire con PO/`/steward`, non in Act.

## Context map

| Context                         | Path modulo                                                                                                                                                   | Responsabilità                                                                                                                                                                         | Integrazioni                                                                                                                             |
| ------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| Gateway Core                    | `gateway_core.py`, `global_config.py`                                                                                                                         | orchestrazione System 2, provider, Cache L1, Circuit breaker                                                                                                                           | → Laya via modulo/CLI `router.py` (regola AGENTS.md)                                                                                     |
| System 1 (Laya)                 | `router.py`, `laya_service.py`, `system1_preflight.py`                                                                                                        | pre-filtro euristico, Gate 1–7, abstention                                                                                                                                             | ← Gateway Core; ← Benchmark (runner)                                                                                                     |
| Benchmark                       | `benchmark/`, `scripts/bench_hot_paths.py`                                                                                                                    | run, token gating, baseline (docs ToDo)                                                                                                                                                | → `system2_metrics.sqlite3` (eventi)                                                                                                     |
| Observability & Retention       | docs `05`, `07`, eventi sqlite                                                                                                                                | retention/redaction, cache metrics, encryption                                                                                                                                         | ← Gateway Core, ← Benchmark                                                                                                              |
| DevSecOps Tooling               | `scripts/check_*.py` (+ test validatori)                                                                                                                      | secrets, deps audit, SAST low-noise                                                                                                                                                    | → CI `ready-for-review.yml`                                                                                                              |
| Agent Platform (bundle)         | `agents/`                                                                                                                                                     | skill/agenti canonici L0–L2, Platform API **propria** (`agents/Makefile`)                                                                                                              | → symlink `.agents/skills/` (script `link-workspace-skills.sh`)                                                                          |
| Knowledge & Ontology (side-car) | `auto-ontology-mcp` esterno, clone pinnato `~/auto-ontology-mcp` (SHA + `version` + KPI nel pin file `agents/a-knowledge/references/auto-ontology-source.md`) | layer semantico su DB (scan, profiling, inferenza chiavi, `validate_sql`, `run_sql` read-only) + KB a fatti tipizzati con provenienza (records/concepts/passages/sources, FTS5, vault) | ← Agente via MCP stdio `tools/call`; ← `a-knowledge` (routing §Routing delle domande); → unico punto di scrittura `~/.auto-ontology-mcp` |

## Regole

1. **Nessun import diretto** tra colonne Path modulo (salvo Integrazioni).
2. Shared kernel: `global_config.py` — owner Gateway Core; Benchmark lo legge in sola lettura.
3. Il bundle `agents/` non importa codice app; l'app non importa script del bundle (solo CLI/skill documentate).
4. Il side-car «Knowledge & Ontology» **non** entra nel bundle `agents/` e non è importato dall'app (dipendenze FastMCP/SQLAlchemy/sqlglot confinate nel clone pinnato): comunicazione **solo via MCP stdio**; trasporto HTTP = N/A documentato (PRD `docs/29` §7). Il canone di routing è la tabella §«Routing delle domande» — linkata, mai duplicata.

## Routing delle domande (confine Retrieval ↔ side-car)

Canone unico: questa tabella. `docs/29_auto_ontology_semantic_layer.md` e (da AO-1.1) `agents/a-knowledge/SKILL.md` la linkano.

| Famiglia di domanda                                       | Destinatario                     | Ancoraggio                                                                            |
| --------------------------------------------------------- | -------------------------------- | ------------------------------------------------------------------------------------- |
| «Capitolo/sezione del libro X che parla di Y»             | `a-knowledge` + `hal_mcp_docs`   | `chapter_route` / `doc_search` (disclosure progressiva di prosa)                      |
| «Quanti/come quanto: fatto sommativo su record con fonte» | side-car, datasource `knowledge` | `run_sql` + `get_source` (numeri da tabelle tipizzate validate, provenienza citabile) |
| Domanda su DB business                                    | side-car                         | `check_answerable` → `validate_sql` → `run_sql`                                       |
| «Due tabelle sono collegabili?»                           | side-car                         | `find_join_path` (+ role notes dell'ontologia)                                        |

Confinamenti: chunk-store `hal_mcp_docs` senza record tipizzati; KB side-car senza capitoli di libri (solo passages estratti dal modello); vault unico, default interno (`AUTO_ONTOLOGY_VAULT` unset, opt-in il vault Obsidian reale).

## Port pubblici (alternativa a eventi)

| Port                             | Context         | Consumatori                                  |
| -------------------------------- | --------------- | -------------------------------------------- |
| `python3 router.py <verbo>`      | System 1 (Laya) | Gateway Core, agente (pre-ottimizzazioni L1) |
| `system2_metrics.sqlite3` schema | Observability   | Benchmark, analisi offline                   |

## Waiver temporanei

| Waiver                                         | Motivo                                       | Scadenza                         |
| ---------------------------------------------- | -------------------------------------------- | -------------------------------- |
| `global_config.py` condiviso Gateway↔Benchmark | kernel storico, separazione non ancora fatta | primo `/slice` su config scoping |

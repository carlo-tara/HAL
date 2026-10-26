# Glossario — HAL Gateway

Documento **vivo** (a-harness L1, `ubiquitous-language`). Termini seeds da
`AGENTS.md`, `docs/00_indice.md` e identificatori di codice — non inventati.
Aggiornare con `/steward` o PO; il termine canonico vale per codice e test.

## Entità

| Termine canonico | Definizione | Sinonimi vietati |
|------------------|-------------|------------------|
| Laya (System 1) | Pre-filtro euristico veloce: routing, triage, choice, score, noul (`router.py`, `laya_service.py`, `system1_preflight.py`) | "motore veloce" |
| System 2 | Motore di reasoning; modello da `SystemTwoEngine.ACTIVE_MODEL_NAME` (`global_config.py`) | "il grande" (ammesso solo in prosa docs) |
| Gateway Core | Orchestrazione chiamate: provider, cache, circuit breaker (`gateway_core.py`) | — |
| Gate (1–7) | Punti di gating System 1 nel runner benchmark (`#system1-gating`) | — |
| Cache L1 | Cache esatta: hash normalizzato, TTL per classe, invalidazione per file (docs/07) | — |
| Circuit breaker | Tolleranza ai fallimenti provider + `session_id` per conversazioni parallele (docs/19) | — |
| Retention / Redaction | Ritenzione eventi e mascheramento dal giorno 1 (docs/05) | — |
| OrcaRouter | Router modelli esterno opzionale; flag `LLM_EXTERNAL_MODE` (0/1), `LLM_EXTERNAL_URI`, `LLM_EXTERNAL_MODEL` | — |
| system2_metrics.sqlite3 | DB eventi locale run/fase/sistema/modello/task (Gate 7) | — |
| Platform API | `Makefile` root (app gateway); il bundle agenti ha `agents/Makefile` separato | — |
| Mappa residui | `ToDo.md` root, backlog rinfrescabile (≠ progress append-only) | "backlog" generico |

## Verbi / azioni

| Termine canonico | Definizione | Sinonimi vietati |
|------------------|-------------|------------------|
| triage / routing / choice / score / noul | Verbi CLI System 1 (`python3 router.py <verbo> ...`) | "classify", "pick" |
| escalate | Passaggio di una richiesta da System 1 a System 2 (docs/01, docs/02) | "promuovi" |
| servire (serve) | Restituire risposta da cache/bozza senza attesa S2 (docs/16, docs/23) | — |

## Eventi (opz.)

| Evento | Payload minimo | Emesso da |
|--------|----------------|-----------|
| run/fase (metrics) | run_id, phase, system, model, task | Gateway / Benchmark → `system2_metrics.sqlite3` |

## Note

- Naming: snake_case per file/moduli Python; agenti primari con prefisso `a-` (L0/L1/L2 invariati).
- Fonte canonica agenti/skill: `agents/`; `.agents/skills/` espone solo symlink.
- Termini ambigui: owner deciso in `/slice` (PO/steward), non in Act.

# Bounded contexts — HAL Gateway

Mappa confini (seed da `/bootstrap` standard 2026-10-25, verificata sui file reali).
Ogni `/slice` dichiara quale context è attivo. Rifinire con PO/`/steward`, non in Act.

## Context map

| Context | Path modulo | Responsabilità | Integrazioni |
|---------|-------------|----------------|--------------|
| Gateway Core | `gateway_core.py`, `global_config.py` | orchestrazione System 2, provider, Cache L1, Circuit breaker | → Laya via modulo/CLI `router.py` (regola AGENTS.md) |
| System 1 (Laya) | `router.py`, `laya_service.py`, `system1_preflight.py` | pre-filtro euristico, Gate 1–7, abstention | ← Gateway Core; ← Benchmark (runner) |
| Benchmark | `benchmark/`, `scripts/bench_hot_paths.py` | run, token gating, baseline (docs ToDo) | → `system2_metrics.sqlite3` (eventi) |
| Observability & Retention | docs `05`, `07`, eventi sqlite | retention/redaction, cache metrics, encryption | ← Gateway Core, ← Benchmark |
| DevSecOps Tooling | `scripts/check_*.py` (+ test validatori) | secrets, deps audit, SAST low-noise | → CI `ready-for-review.yml` |
| Agent Platform (bundle) | `agents/` | skill/agenti canonici L0–L2, Platform API **propria** (`agents/Makefile`) | → symlink `.agents/skills/` (script `link-workspace-skills.sh`) |

## Regole

1. **Nessun import diretto** tra colonne Path modulo (salvo Integrazioni).
2. Shared kernel: `global_config.py` — owner Gateway Core; Benchmark lo legge in sola lettura.
3. Il bundle `agents/` non importa codice app; l'app non importa script del bundle (solo CLI/skill documentate).

## Port pubblici (alternativa a eventi)

| Port | Context | Consumatori |
|------|---------|-------------|
| `python3 router.py <verbo>` | System 1 (Laya) | Gateway Core, agente (pre-ottimizzazioni L1) |
| `system2_metrics.sqlite3` schema | Observability | Benchmark, analisi offline |

## Waiver temporanei

| Waiver | Motivo | Scadenza |
|--------|--------|----------|
| `global_config.py` condiviso Gateway↔Benchmark | kernel storico, separazione non ancora fatta | primo `/slice` su config scoping |

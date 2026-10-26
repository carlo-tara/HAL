from __future__ import annotations

import math
import os
import sqlite3
import threading
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

DEFAULT_METRICS_DB = os.getenv(
    "SYSTEM2_METRICS_DB_PATH",
    str(
        Path(__file__).resolve().parent.parent
        / "events/benchmarks/system2_metrics.sqlite3"
    ),
)

STRATEGIA_BLOCK_MARKER = "<strategia_system1_laya>"


class System2Metrics:
    """SQLite telemetry for System 1/System 2 benchmark stages.

    Only operational metadata is persisted; prompt and response bodies are never stored.
    """

    def __init__(self, db_path: str | Path = DEFAULT_METRICS_DB) -> None:
        self.db_path = str(db_path)
        self._lock = threading.Lock()
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path, timeout=15.0)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("PRAGMA synchronous=NORMAL")
        return connection

    def _initialize(self) -> None:
        with self._lock, self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS system2_workflow_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    prompt_id TEXT NOT NULL,
                    provider TEXT NOT NULL DEFAULT '',
                    model TEXT NOT NULL DEFAULT '',
                    task_family TEXT NOT NULL,
                    execution_mode TEXT NOT NULL,
                    system TEXT NOT NULL CHECK (system IN ('system1', 'system2')),
                    stage TEXT NOT NULL,
                    status TEXT NOT NULL,
                    latency_ms INTEGER NOT NULL DEFAULT 0,
                    input_chars INTEGER NOT NULL DEFAULT 0,
                    output_chars INTEGER NOT NULL DEFAULT 0,
                    tokens_in INTEGER,
                    tokens_out INTEGER,
                    tokens_total INTEGER,
                    decision TEXT,
                    confidence REAL,
                    fallback_used INTEGER NOT NULL DEFAULT 0,
                    error_message TEXT
                )
                """
            )
            columns = {
                row[1]
                for row in connection.execute(
                    "PRAGMA table_info(system2_workflow_events)"
                ).fetchall()
            }
            if "error_message" not in columns:
                connection.execute(
                    "ALTER TABLE system2_workflow_events ADD COLUMN error_message TEXT"
                )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_system2_events_run ON system2_workflow_events(run_id, id)"
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_system2_events_task ON system2_workflow_events(task_family, system, stage)"
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_system2_events_agg ON system2_workflow_events(run_id, task_family, model)"
            )
            connection.commit()

    def record_event(
        self,
        *,
        run_id: str,
        prompt_id: str,
        provider: str = "",
        model: str = "",
        task_family: str = "general",
        execution_mode: str = "single_pass",
        system: str,
        stage: str,
        status: str,
        latency_ms: int = 0,
        input_chars: int = 0,
        output_chars: int = 0,
        tokens_in: int | None = None,
        tokens_out: int | None = None,
        tokens_total: int | None = None,
        decision: str | None = None,
        confidence: float | None = None,
        fallback_used: bool = False,
        error_message: str | None = None,
    ) -> int:
        if system not in {"system1", "system2"}:
            raise ValueError("system must be 'system1' or 'system2'")
        values = (
            run_id,
            datetime.now(UTC).isoformat(),
            prompt_id,
            provider,
            model,
            task_family,
            execution_mode,
            system,
            stage,
            status,
            max(0, int(latency_ms)),
            max(0, int(input_chars)),
            max(0, int(output_chars)),
            tokens_in,
            tokens_out,
            tokens_total,
            decision,
            confidence,
            int(fallback_used),
            error_message,
        )
        with self._lock, self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO system2_workflow_events (
                    run_id, timestamp, prompt_id, provider, model, task_family,
                    execution_mode, system, stage, status, latency_ms, input_chars,
                    output_chars, tokens_in, tokens_out, tokens_total, decision,
                    confidence, fallback_used, error_message
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                values,
            )
            connection.commit()
            return int(cursor.lastrowid or 0)

    def aggregate_by_run_task_model(
        self, *, run_id: str | None = None
    ) -> dict[str, Any]:
        """Aggregate events by (task_family, model), optionally for one run."""
        where = "WHERE run_id = ?" if run_id is not None else ""
        params: tuple[Any, ...] = (run_id,) if run_id is not None else ()
        with self._connect() as connection:
            rows = connection.execute(
                f"""
                SELECT task_family, model,
                       COUNT(*) AS events,
                       SUM(COALESCE(tokens_total, 0)) AS tokens_total,
                       SUM(CASE WHEN status != 'ok' THEN 1 ELSE 0 END) AS errors,
                       SUM(latency_ms) AS latency_ms
                FROM system2_workflow_events
                {where}
                GROUP BY task_family, model
                ORDER BY task_family, model
                """,
                params,
            ).fetchall()
            totals = connection.execute(
                f"""
                SELECT COUNT(*) AS total_events,
                       SUM(COALESCE(tokens_total, 0)) AS total_tokens,
                       SUM(CASE WHEN status != 'ok' THEN 1 ELSE 0 END) AS total_errors
                FROM system2_workflow_events
                {where}
                """,
                params,
            ).fetchone()
        return {
            "total_events": int(totals["total_events"] or 0),
            "total_tokens": int(totals["total_tokens"] or 0),
            "total_errors": int(totals["total_errors"] or 0),
            "groups": [
                {
                    "key": (row["task_family"], row["model"]),
                    "events": int(row["events"] or 0),
                    "tokens_total": int(row["tokens_total"] or 0),
                    "errors": int(row["errors"] or 0),
                    "latency_ms": int(row["latency_ms"] or 0),
                }
                for row in rows
            ],
        }

    def get_events(self, *, run_id: str) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM system2_workflow_events WHERE run_id = ? ORDER BY id",
                (run_id,),
            ).fetchall()
            return [dict(row) for row in rows]

    def get_token_breakdown(self, *, run_id: str | None = None) -> dict[str, Any]:
        """Token usage per workflow category, plus tokens lost to failed prompts.

        ``wasted_tokens`` counts tokens spent by successful stages of a
        (run, prompt, model) workflow that also contains a failed stage: their
        output is discarded because the workflow as a whole failed.
        """
        where = "WHERE run_id = ?" if run_id is not None else ""
        params: tuple[Any, ...] = (run_id,) if run_id is not None else ()
        with self._connect() as connection:
            rows = connection.execute(
                f"""
                SELECT CASE
                         WHEN status != 'ok' THEN 'error'
                         WHEN stage LIKE 'segmento_%' THEN 'segment'
                         WHEN stage = 'assemblaggio_finale' THEN 'assembly'
                         WHEN stage = 'assemblaggio_locale' THEN 'local_assembly'
                         WHEN stage = 'risposta_finale' THEN 'single_pass'
                         WHEN stage LIKE 'piano_%' THEN 'plan'
                         ELSE 'other'
                       END AS category,
                       COUNT(*) AS events,
                       SUM(COALESCE(tokens_total, 0)) AS tokens
                FROM system2_workflow_events
                {where}
                {"AND" if where else "WHERE"} system = 'system2'
                GROUP BY category
                """,
                params,
            ).fetchall()
            wasted = connection.execute(
                f"""
                SELECT SUM(COALESCE(e.tokens_total, 0))
                FROM system2_workflow_events e
                WHERE {"e.run_id = ? AND" if where else ""} e.system = 'system2'
                  AND e.status = 'ok'
                  AND EXISTS (
                    SELECT 1 FROM system2_workflow_events f
                    WHERE f.run_id = e.run_id AND f.prompt_id = e.prompt_id
                      AND f.model = e.model AND f.system = 'system2'
                      AND f.status != 'ok'
                  )
                """,
                params,
            ).fetchone()
        total = sum(int(row["tokens"] or 0) for row in rows)
        return {
            "total_tokens": total,
            "wasted_tokens": int(wasted[0] or 0),
            "by_category": {
                row["category"]: {
                    "events": int(row["events"]),
                    "tokens": int(row["tokens"] or 0),
                    "share": round(int(row["tokens"] or 0) / total, 4)
                    if total
                    else 0.0,
                }
                for row in rows
            },
        }

    def get_summary(self, *, run_id: str) -> dict[str, int]:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT COUNT(*) AS events,
                       SUM(CASE WHEN system = 'system1' THEN 1 ELSE 0 END) AS system1_events,
                       SUM(CASE WHEN system = 'system2' THEN 1 ELSE 0 END) AS system2_events,
                       SUM(latency_ms) AS latency_ms,
                       SUM(COALESCE(tokens_total, 0)) AS tokens_total,
                       SUM(CASE WHEN status != 'ok' THEN 1 ELSE 0 END) AS errors
                FROM system2_workflow_events
                WHERE run_id = ?
                """,
                (run_id,),
            ).fetchone()
        return {
            key: int(row[key] or 0)
            for key in (
                "events",
                "system1_events",
                "system2_events",
                "latency_ms",
                "tokens_total",
                "errors",
            )
        }

    def get_workflow_totals(self, *, run_id: str | None = None) -> list[dict[str, Any]]:
        """End-to-end token totals per logical prompt (run, prompt, model).

        Aggregates every recorded stage (System 1 preflight/decisions and
        System 2 segments, assembly and retries) so each workflow total can be
        reconciled with the provider calls. Usage the provider did not report
        stays NULL and is counted separately from a real zero:
        ``missing_usage`` is split by system because Laya provides no token
        usage (missing by design) while provider stages should always report
        it. ``retry_stages`` counts revision stages (the single Laya-driven
        retry of the plan phase).
        """
        where = "WHERE run_id = ?" if run_id is not None else ""
        params: tuple[Any, ...] = (run_id,) if run_id is not None else ()
        with self._connect() as connection:
            rows = connection.execute(
                f"""
                SELECT run_id, prompt_id, provider, model, task_family, execution_mode,
                       COUNT(*) AS stages,
                       SUM(COALESCE(tokens_in, 0)) AS tokens_in,
                       SUM(COALESCE(tokens_out, 0)) AS tokens_out,
                       SUM(COALESCE(tokens_total, 0)) AS tokens_total,
                       SUM(CASE WHEN system = 'system1' AND status = 'ok'
                                 AND tokens_total IS NULL THEN 1 ELSE 0 END) AS missing_usage_system1,
                       SUM(CASE WHEN system = 'system2' AND status = 'ok'
                                 AND tokens_total IS NULL THEN 1 ELSE 0 END) AS missing_usage_system2,
                       SUM(CASE WHEN stage = 'piano_revisionato' THEN 1 ELSE 0 END) AS retry_stages,
                       SUM(CASE WHEN status != 'ok' THEN 1 ELSE 0 END) AS errors
                FROM system2_workflow_events
                {where}
                GROUP BY run_id, prompt_id, provider, model, task_family, execution_mode
                ORDER BY run_id, prompt_id, provider, model
                """,
                params,
            ).fetchall()
        return [
            {
                "run_id": row["run_id"],
                "prompt_id": row["prompt_id"],
                "provider": row["provider"],
                "model": row["model"],
                "task_family": row["task_family"],
                "execution_mode": row["execution_mode"],
                "stages": int(row["stages"] or 0),
                "tokens_in": int(row["tokens_in"] or 0),
                "tokens_out": int(row["tokens_out"] or 0),
                "tokens_total": int(row["tokens_total"] or 0),
                "missing_usage_system1": int(row["missing_usage_system1"] or 0),
                "missing_usage_system2": int(row["missing_usage_system2"] or 0),
                "retry_stages": int(row["retry_stages"] or 0),
                "errors": int(row["errors"] or 0),
            }
            for row in rows
        ]

    @staticmethod
    def _percentile(sorted_values: list[int], fraction: float) -> int:
        """Nearest-rank percentile over an ascending list (n >= 1)."""
        if not sorted_values:
            return 0
        rank = max(1, math.ceil(fraction * len(sorted_values)))
        return sorted_values[min(rank, len(sorted_values)) - 1]

    def get_token_stats(self, *, run_id: str | None = None) -> dict[str, Any]:
        """Per task/model distribution of per-prompt token totals.

        Median and p90 use the nearest-rank method over the per-workflow
        totals (see :meth:`get_workflow_totals`). ``wasted_tokens`` sums the
        totals of workflows that contain at least one failed stage: their
        output is discarded. ``missing_usage_system2`` must stay 0 for new
        successful runs; System 1 usage is missing by design (Laya reports no
        token usage), so it is tracked separately.
        """
        workflows = self.get_workflow_totals(run_id=run_id)
        groups: dict[tuple[str, str], list[dict[str, Any]]] = {}
        for workflow in workflows:
            key = (workflow["task_family"], workflow["model"])
            groups.setdefault(key, []).append(workflow)
        group_reports = []
        for (task_family, model), members in sorted(groups.items()):
            totals = sorted(item["tokens_total"] for item in members)
            count = len(totals)
            median = (
                totals[count // 2]
                if count % 2
                else (totals[count // 2 - 1] + totals[count // 2]) // 2
            )
            group_reports.append(
                {
                    "task_family": task_family,
                    "model": model,
                    "workflows": count,
                    "tokens_total": sum(totals),
                    "median_tokens": median,
                    "p90_tokens": self._percentile(totals, 0.9),
                    "retries": sum(item["retry_stages"] for item in members),
                    "wasted_tokens": sum(
                        item["tokens_total"] for item in members if item["errors"]
                    ),
                    "missing_usage_system1": sum(
                        item["missing_usage_system1"] for item in members
                    ),
                    "missing_usage_system2": sum(
                        item["missing_usage_system2"] for item in members
                    ),
                }
            )
        return {
            "workflows": len(workflows),
            "groups": group_reports,
        }


def detect_strategy_block_in_output(response_text: str) -> bool:
    """Return whether the System 1 strategy marker appears in output."""
    return STRATEGIA_BLOCK_MARKER in response_text


def count_strategy_block_occurrences(response_text: str) -> int:
    """Count occurrences of the System 1 strategy marker in output."""
    if not response_text:
        return 0
    occurrences = 0
    start = 0
    while True:
        index = response_text.find(STRATEGIA_BLOCK_MARKER, start)
        if index < 0:
            return occurrences
        occurrences += 1
        start = index + len(STRATEGIA_BLOCK_MARKER)

from __future__ import annotations

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
                    fallback_used INTEGER NOT NULL DEFAULT 0
                )
                """
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_system2_events_run ON system2_workflow_events(run_id, id)"
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_system2_events_task ON system2_workflow_events(task_family, system, stage)"
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
        )
        with self._lock, self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO system2_workflow_events (
                    run_id, timestamp, prompt_id, provider, model, task_family,
                    execution_mode, system, stage, status, latency_ms, input_chars,
                    output_chars, tokens_in, tokens_out, tokens_total, decision,
                    confidence, fallback_used
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                values,
            )
            connection.commit()
            return int(cursor.lastrowid or 0)

    def get_events(self, *, run_id: str) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM system2_workflow_events WHERE run_id = ? ORDER BY id",
                (run_id,),
            ).fetchall()
            return [dict(row) for row in rows]

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

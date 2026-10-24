"""Gate 7: verificare e completare gli eventi SQLite per run/fase/sistema/modello/task.

Acceptance:
- inventario dei campi di system2_metrics.sqlite3 rispetto a modalità, stato, latenza,
  caratteri, token, scelta, confidenza, fallback ed errori; campi mancanti aggiunti
- nessun contenuto di prompt o risposta salvato (test)
- aggregazione per run/task/modello disponibile
"""

from __future__ import annotations

import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

_project_root = str(Path(__file__).resolve().parent.parent)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from benchmark.runner.system2_metrics import System2Metrics


class TestGate7SqliteFields(unittest.TestCase):
    """Verifica che tutti i campi richiesti siano presenti nello schema."""

    def setUp(self):
        self.db = tempfile.NamedTemporaryFile(suffix=".sqlite3", delete=False)
        self.db_path = self.db.name
        self.db.close()
        self.metrics = System2Metrics(self.db_path)

    def tearDown(self):
        Path(self.db_path).unlink(missing_ok=True)

    def test_required_fields_present(self):
        """Tutti i campi richiesti devono essere presenti nella tabella."""
        required = {
            "run_id",
            "timestamp",
            "prompt_id",
            "provider",
            "model",
            "task_family",
            "execution_mode",
            "system",
            "stage",
            "status",
            "latency_ms",
            "input_chars",
            "output_chars",
            "tokens_in",
            "tokens_out",
            "tokens_total",
            "decision",
            "confidence",
            "fallback_used",
            "error_message",
        }
        with self.metrics._connect() as conn:
            cursor = conn.execute("PRAGMA table_info(system2_workflow_events)")
            columns = {row["name"] for row in cursor.fetchall()}
        missing = required - columns
        self.assertEqual(missing, set(), f"Campi mancanti: {missing}")

    def test_error_message_field_stores_text(self):
        """Il campo error_message deve poter memorizzare un messaggio di errore."""
        self.metrics.record_event(
            run_id="test-run",
            prompt_id="test-prompt",
            system="system2",
            stage="segmento_1",
            status="error",
            error_message="Connection timeout after 60s",
        )
        events = self.metrics.get_events(run_id="test-run")
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["error_message"], "Connection timeout after 60s")

    def test_no_prompt_or_response_content_stored(self):
        """Nessun contenuto di prompt o risposta deve essere salvato nel DB."""
        self.metrics.record_event(
            run_id="test-run",
            prompt_id="test-prompt",
            system="system2",
            stage="risposta_finale",
            status="ok",
            input_chars=500,
            output_chars=1200,
            tokens_in=100,
            tokens_out=200,
            tokens_total=300,
        )
        events = self.metrics.get_events(run_id="test-run")
        # Verifico che non esistano colonne contenenti testo grezzo
        with self.metrics._connect() as conn:
            cursor = conn.execute("PRAGMA table_info(system2_workflow_events)")
            columns = [row["name"] for row in cursor.fetchall()]
        forbidden = {
            "prompt_text",
            "response_text",
            "prompt_body",
            "response_body",
            "artifact",
            "full_prompt",
            "full_response",
        }
        found_forbidden = forbidden & set(columns)
        self.assertEqual(
            found_forbidden, set(), f"Colonne vietate trovate: {found_forbidden}"
        )


class TestGate7Aggregation(unittest.TestCase):
    """Verifica l'aggregazione per run/task/modello."""

    def setUp(self):
        self.db = tempfile.NamedTemporaryFile(suffix=".sqlite3", delete=False)
        self.db_path = self.db.name
        self.db.close()
        self.metrics = System2Metrics(self.db_path)

    def tearDown(self):
        Path(self.db_path).unlink(missing_ok=True)

    def test_aggregate_by_run_task_model(self):
        """aggregate_by_run_task_model deve restituire raggruppamenti corretti."""
        # Inserisco eventi multipli
        self.metrics.record_event(
            run_id="run-A",
            prompt_id="p1",
            provider="ollama",
            model="phi3:mini",
            task_family="coding",
            execution_mode="single_pass",
            system="system2",
            stage="risposta_finale",
            status="ok",
            latency_ms=500,
            tokens_in=100,
            tokens_out=200,
            tokens_total=300,
        )
        self.metrics.record_event(
            run_id="run-A",
            prompt_id="p1",
            provider="ollama",
            model="phi3:mini",
            task_family="coding",
            execution_mode="single_pass",
            system="system1",
            stage="preflight",
            status="ok",
            latency_ms=50,
            decision="laya",
            confidence=0.9,
            fallback_used=False,
        )
        self.metrics.record_event(
            run_id="run-A",
            prompt_id="p2",
            provider="ollama",
            model="llama3.2:1b",
            task_family="translation",
            execution_mode="source_chunks",
            system="system2",
            stage="segmento_1",
            status="ok",
            latency_ms=300,
            tokens_in=500,
            tokens_out=400,
            tokens_total=900,
        )
        self.metrics.record_event(
            run_id="run-A",
            prompt_id="p2",
            provider="ollama",
            model="llama3.2:1b",
            task_family="translation",
            execution_mode="source_chunks",
            system="system2",
            stage="segmento_1",
            status="error",
            latency_ms=600,
            error_message="timeout",
        )

        result = self.metrics.aggregate_by_run_task_model(run_id="run-A")

        # Deve contenere raggruppamenti per (task_family, model)
        self.assertIn("groups", result)
        groups = result["groups"]
        # Due gruppi: (coding, phi3:mini) e (translation, llama3.2:1b)
        keys = [g["key"] for g in groups]
        self.assertIn(("coding", "phi3:mini"), keys)
        self.assertIn(("translation", "llama3.2:1b"), keys)

        # Verifico i dettagli del gruppo coding/phi3
        coding_group = next(g for g in groups if g["key"] == ("coding", "phi3:mini"))
        self.assertEqual(coding_group["events"], 2)
        self.assertEqual(coding_group["tokens_total"], 300)
        self.assertEqual(coding_group["errors"], 0)

        # Verifico il gruppo translation/llama con errore
        trans_group = next(
            g for g in groups if g["key"] == ("translation", "llama3.2:1b")
        )
        self.assertEqual(trans_group["events"], 2)
        self.assertEqual(trans_group["errors"], 1)
        self.assertEqual(trans_group["tokens_total"], 900)

    def test_aggregate_returns_zero_for_empty_run(self):
        """Run senza eventi deve restituire aggregati vuoti."""
        result = self.metrics.aggregate_by_run_task_model(run_id="non-esistente")
        self.assertEqual(result["total_events"], 0)
        self.assertEqual(result["total_tokens"], 0)
        self.assertEqual(result["total_errors"], 0)
        self.assertEqual(result["groups"], [])


class TestGate7Migration(unittest.TestCase):
    """Verifica che _initialize migri correttamente DB con schema pre-G7."""

    def setUp(self):
        self.db = tempfile.NamedTemporaryFile(suffix=".sqlite3", delete=False)
        self.db_path = self.db.name
        self.db.close()

    def tearDown(self):
        Path(self.db_path).unlink(missing_ok=True)

    def _create_preg7_db(self):
        """Crea un DB con schema pre-G7 (senza error_message e fallback_used)."""
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            """
            CREATE TABLE system2_workflow_events (
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
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_system2_events_run ON system2_workflow_events(run_id, id)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_system2_events_task ON system2_workflow_events(task_family, system, stage)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_system2_events_agg ON system2_workflow_events(run_id, task_family, model)"
        )
        conn.commit()
        conn.close()

    def test_record_event_succeeds_on_preg7_db(self):
        """record_event deve funzionare su un DB pre-G7 (senza error_message)."""
        import sqlite3

        # 1) Crea DB con schema pre-G7 (senza error_message)
        self._create_preg7_db()

        # 2) Apre System2Metrics sul DB esistente: _initialize dovrebbe migrare
        metrics = System2Metrics(self.db_path)

        # 3) record_event con error_message non deve sollevare OperationalError
        rowid = metrics.record_event(
            run_id="mig-test",
            prompt_id="p1",
            system="system2",
            stage="segmento_1",
            status="error",
            error_message="Connection timeout after 60s",
        )
        self.assertGreater(rowid, 0, "record_event deve aver inserito una riga")

        # 4) Verifica che il messaggio sia stato salvato
        events = metrics.get_events(run_id="mig-test")
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["error_message"], "Connection timeout after 60s")

    def test_migration_adds_error_message_column(self):
        """Dopo l'inizializzazione su DB pre-G7, la colonna error_message deve esistere."""
        import sqlite3

        self._create_preg7_db()

        # Verifica che la colonna manchi prima
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("PRAGMA table_info(system2_workflow_events)")
        columns_before = {row[1] for row in cursor.fetchall()}
        conn.close()
        self.assertNotIn("error_message", columns_before)

        # Apre System2Metrics (triggera _initialize)
        System2Metrics(self.db_path)

        # Verifica che la colonna esista dopo
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("PRAGMA table_info(system2_workflow_events)")
        columns_after = {row[1] for row in cursor.fetchall()}
        conn.close()
        self.assertIn("error_message", columns_after)


if __name__ == "__main__":
    unittest.main()

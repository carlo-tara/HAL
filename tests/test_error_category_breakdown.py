"""Gate: registrare durata e token stimati degli stage andati in timeout o errore.

Acceptance:
- evento SQLite per stage in errore con durata, caratteri inviati e token disponibili/non disponibili
- get_token_breakdown espone una categoria per gli stage in errore
- test
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

_project_root = str(Path(__file__).resolve().parent.parent)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from benchmark.runner.system2_metrics import System2Metrics


class TestErrorCategoryTokenBreakdown(unittest.TestCase):
    """Verifica che get_token_breakdown esponga una categoria 'error'."""

    def setUp(self):
        self.db = tempfile.NamedTemporaryFile(suffix=".sqlite3", delete=False)
        self.db_path = self.db.name
        self.db.close()
        self.metrics = System2Metrics(self.db_path)

    def tearDown(self):
        Path(self.db_path).unlink(missing_ok=True)

    def test_error_category_exists_in_breakdown(self):
        """La categoria 'error' deve essere presente nel breakdown."""
        self.metrics.record_event(
            run_id="test-run",
            prompt_id="p1",
            provider="ollama",
            model="phi3:mini",
            task_family="translation",
            execution_mode="source_chunks",
            system="system2",
            stage="segmento_1",
            status="error",
            latency_ms=600,
            input_chars=3400,
            output_chars=0,
            tokens_in=1100,
            tokens_out=0,
            tokens_total=1100,
        )
        result = self.metrics.get_token_breakdown(run_id="test-run")
        self.assertIn("error", result["by_category"])
        error_cat = result["by_category"]["error"]
        self.assertEqual(error_cat["events"], 1)
        self.assertEqual(error_cat["tokens"], 1100)

    def test_error_category_excludes_ok_stages(self):
        """Solo gli stage con status != 'ok' devono finire nella categoria error."""
        self.metrics.record_event(
            run_id="test-run",
            prompt_id="p1",
            provider="ollama",
            model="phi3:mini",
            task_family="translation",
            execution_mode="source_chunks",
            system="system2",
            stage="segmento_1",
            status="ok",
            latency_ms=300,
            input_chars=3400,
            output_chars=2500,
            tokens_in=1100,
            tokens_out=900,
            tokens_total=2000,
        )
        self.metrics.record_event(
            run_id="test-run",
            prompt_id="p1",
            provider="ollama",
            model="phi3:mini",
            task_family="translation",
            execution_mode="source_chunks",
            system="system2",
            stage="segmento_1",
            status="error",
            latency_ms=600,
            input_chars=3400,
            output_chars=0,
            tokens_in=1100,
            tokens_out=0,
            tokens_total=1100,
        )
        result = self.metrics.get_token_breakdown(run_id="test-run")
        # L'errore deve avere 1 evento, 1100 token
        self.assertEqual(result["by_category"]["error"]["events"], 1)
        self.assertEqual(result["by_category"]["error"]["tokens"], 1100)
        # Il segmento ok deve essere nella categoria 'segment', non in 'error'
        self.assertEqual(result["by_category"]["segment"]["events"], 1)
        self.assertEqual(result["by_category"]["segment"]["tokens"], 2000)

    def test_error_category_with_timeout_stage(self):
        """Stage andati in timeout (status=error) devono essere conteggiati."""
        self.metrics.record_event(
            run_id="test-run",
            prompt_id="p2",
            provider="ollama",
            model="qwen2.5:1.5b",
            task_family="translation",
            execution_mode="single_pass",
            system="system2",
            stage="sintesi_traduzione",
            status="error",
            latency_ms=600100,
            input_chars=5000,
            output_chars=0,
            tokens_in=2000,
            tokens_out=0,
            tokens_total=2000,
        )
        result = self.metrics.get_token_breakdown(run_id="test-run")
        self.assertIn("error", result["by_category"])
        self.assertEqual(result["by_category"]["error"]["tokens"], 2000)

    def test_error_share_calculated_correctly(self):
        """La percentuale share della categoria error deve essere corretta."""
        self.metrics.record_event(
            run_id="test-run",
            prompt_id="p1",
            provider="ollama",
            model="phi3:mini",
            task_family="general",
            execution_mode="single_pass",
            system="system2",
            stage="risposta_finale",
            status="ok",
            tokens_in=100,
            tokens_out=200,
            tokens_total=300,
        )
        self.metrics.record_event(
            run_id="test-run",
            prompt_id="p1",
            provider="ollama",
            model="phi3:mini",
            task_family="general",
            execution_mode="single_pass",
            system="system2",
            stage="risposta_finale",
            status="error",
            tokens_in=100,
            tokens_out=0,
            tokens_total=100,
        )
        result = self.metrics.get_token_breakdown(run_id="test-run")
        # Totale: 300 + 100 = 400
        # Error: 100 / 400 = 0.25
        self.assertAlmostEqual(result["by_category"]["error"]["share"], 0.25, places=2)
        self.assertAlmostEqual(result["total_tokens"], 400)

    def test_no_error_category_when_all_ok(self):
        """Se nessun stage è in errore, la categoria error deve avere 0 eventi."""
        self.metrics.record_event(
            run_id="test-run",
            prompt_id="p1",
            provider="ollama",
            model="phi3:mini",
            task_family="general",
            execution_mode="single_pass",
            system="system2",
            stage="risposta_finale",
            status="ok",
            tokens_in=100,
            tokens_out=200,
            tokens_total=300,
        )
        result = self.metrics.get_token_breakdown(run_id="test-run")
        # La categoria error potrebbe non esistere se non ci sono errori
        # oppure deve esistere con 0 eventi
        if "error" in result["by_category"]:
            self.assertEqual(result["by_category"]["error"]["events"], 0)


if __name__ == "__main__":
    unittest.main()

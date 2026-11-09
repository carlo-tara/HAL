"""Gate: registrare durata e token stimati degli stage andati in timeout o errore.

Acceptance:
- evento SQLite per stage in errore con durata, caratteri inviati e token disponibili/non disponibili
- get_token_breakdown espone il costo degli stage falliti
- test

2026-11-09 (reverse port rv7): il breakdown canonico non espone piu' una
categoria 'error' per status != ok: raggruppa per STAGE (segment/assembly/
local_assembly/single_pass/plan/other) e misura la perdita di workflow come
``wasted_tokens`` (token degli stage ok il cui workflow contiene uno stage
fallito). Stage fallito = evento nella categoria del suo stage; se la risposta
non e' ricostruibile, i token restano NULL/0 perche' non si inventano usage
(cfr. system2_workflow_call.run_stage, branch di failure).
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
    """Verifica come get_token_breakdown espone gli stage falliti e i token sprecati."""

    def setUp(self):
        with tempfile.NamedTemporaryFile(suffix=".sqlite3", delete=False) as handle:
            self.db_path = handle.name
        self.metrics = System2Metrics(self.db_path)

    def tearDown(self):
        Path(self.db_path).unlink(missing_ok=True)

    def test_error_category_exists_in_breakdown(self):
        """Lo stage fallito resta nella categoria del suo stage (segment), non 'error'.

        2026-11-09: riallineato al canonico — nessuna categoria 'error'; la
        copertura degli errori passa da by_category[stage] + wasted_tokens.
        """
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
        self.assertNotIn("error", result["by_category"])
        segment_cat = result["by_category"]["segment"]
        self.assertEqual(segment_cat["events"], 1)
        self.assertEqual(segment_cat["tokens"], 1100)
        self.assertEqual(result["wasted_tokens"], 0)

    def test_error_category_excludes_ok_stages(self):
        """Gli stage ok di un workflow fallito finiscono in wasted_tokens, non in 'error'.

        2026-11-09: nel canonico lo stage ok resta in 'segment'; il suo costo e'
        pero' sprecato perche' lo stesso (run, prompt, model) contiene uno stage
        fallito: wasted_tokens = 2000. Gli eventi 'error' sono 2 in segment.
        """
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
        # Entrambi gli eventi (ok ed error) sono nella categoria del loro stage.
        self.assertNotIn("error", result["by_category"])
        self.assertEqual(result["by_category"]["segment"]["events"], 2)
        self.assertEqual(result["by_category"]["segment"]["tokens"], 3100)
        # L'output dello stage ok e' buttato dal fallimento del workflow.
        self.assertEqual(result["wasted_tokens"], 2000)

    def test_error_category_with_timeout_stage(self):
        """Stage andati in timeout (status=error) ricadono nella categoria 'other'.

        2026-11-09: 'sintesi_traduzione' non matcha nessun pattern di stage
        canonico (segmento_%, assemblaggio_finale/locale, risposta_finale,
        piano_%) => bucket 'other', senza categoria 'error'.
        """
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
        self.assertNotIn("error", result["by_category"])
        self.assertIn("other", result["by_category"])
        self.assertEqual(result["by_category"]["other"]["tokens"], 2000)

    def test_error_share_calculated_correctly(self):
        """Share per stage ok+fallito della stessa passata: wasted 300/400 = 0.75.

        2026-11-09: entrambe le risposte_finale (ok ed error) stanno in
        'single_pass' (share 1.0 del totale di categoria); la quota persa dal
        workflow fallito e' wasted_tokens/total_tokens = 300/400.
        """
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
        # Totale: 300 + 100 = 400, tutta nella categoria single_pass.
        self.assertAlmostEqual(result["total_tokens"], 400)
        self.assertEqual(result["by_category"]["single_pass"]["events"], 2)
        self.assertAlmostEqual(
            result["by_category"]["single_pass"]["share"], 1.0, places=2
        )
        self.assertEqual(result["wasted_tokens"], 300)
        self.assertAlmostEqual(
            result["wasted_tokens"] / result["total_tokens"], 0.75, places=2
        )

    def test_no_error_category_when_all_ok(self):
        """Se nessun stage e' in errore: niente 'error' e wasted_tokens = 0.

        2026-11-09: era un if-guard debole; il canonico non emette mai la
        categoria 'error', quindi l'asserzione negativa e' ora esplicita.
        """
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
        self.assertNotIn("error", result["by_category"])
        self.assertEqual(result["wasted_tokens"], 0)


if __name__ == "__main__":
    unittest.main()

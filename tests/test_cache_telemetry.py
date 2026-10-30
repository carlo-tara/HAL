"""Contratto P1 (ToDo 2026-10-28, voce telemetria cached_tokens):

il runner estraeva da ``usage`` solo prompt/completion/total e il report
trattava ``prompt_tokens_details.cached_tokens`` come eccezione
"Claude-specific"; il doc QwenCloud espone gli stessi campi su tutti i path
cache-abilitati. Senza parsing uniforme il beneficio di cache è invisibile e
l'evaluation non può confrontare i modelli su costo effettivo, non nominale.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from typing import Any

from benchmark.runner.benchmark_models import parse_response
from benchmark.runner.system2_metrics import System2Metrics


class TestUsageParsingAllProviders(unittest.TestCase):
    def test_openai_compat_cached_e_creation(self) -> None:
        data = {
            "choices": [{"message": {"content": "ok"}, "finish_reason": "stop"}],
            "usage": {
                "prompt_tokens": 1000,
                "completion_tokens": 50,
                "total_tokens": 1050,
                "prompt_tokens_details": {"cached_tokens": 800},
                "cache_creation_input_tokens": 200,
            },
        }
        tokens = parse_response("google_openai", data)["tokens"]
        self.assertEqual(tokens["cached"], 800)
        self.assertEqual(tokens["cache_creation"], 200)

    def test_gemini_native_cached_content(self) -> None:
        data = {
            "candidates": [
                {"content": {"parts": [{"text": "ok"}]}, "finishReason": "STOP"}
            ],
            "usageMetadata": {
                "promptTokenCount": 900,
                "candidatesTokenCount": 40,
                "totalTokenCount": 940,
                "cachedContentTokenCount": 512,
            },
        }
        tokens = parse_response("gemini_native", data)["tokens"]
        self.assertEqual(tokens["cached"], 512)
        self.assertIsNone(tokens["cache_creation"])

    def test_ollama_campi_nulle(self) -> None:
        data = {
            "message": {"content": "ok"},
            "done": True,
            "prompt_eval_count": 10,
            "eval_count": 5,
        }
        tokens = parse_response("ollama", data)["tokens"]
        self.assertIsNone(tokens["cached"])
        self.assertIsNone(tokens["cache_creation"])

    def test_assenza_dettagli_non_spezza(self) -> None:
        data = {
            "choices": [{"message": {"content": "ok"}, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 2, "total_tokens": 12},
        }
        tokens = parse_response("google_openai", data)["tokens"]
        self.assertIsNone(tokens["cached"])


class TestMetricsPersistence(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Path(self.tmp.name) / "metrics.sqlite3"
        self.metrics = System2Metrics(self.db)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _event(self, **kw: Any) -> None:
        base: dict[str, Any] = {
            "run_id": "r1",
            "prompt_id": "p1",
            "provider": "orcarouter",
            "model": "qwen",
            "system": "system2",
            "stage": "solve",
            "status": "ok",
            "tokens_in": 1000,
            "tokens_out": 100,
            "tokens_total": 1100,
        }
        base.update(kw)
        self.metrics.record_event(**base)

    def test_cached_persistiti_e_kpis(self) -> None:
        self._event(cached_tokens=800, cache_creation_input_tokens=200)
        self._event(cached_tokens=0)
        kpis = self.metrics.cache_kpis(run_id="r1")
        self.assertEqual(kpis["requests_with_usage"], 2)
        self.assertEqual(kpis["requests_with_cache_hit"], 1)
        self.assertAlmostEqual(kpis["hit_rate_pct"], 50.0)
        self.assertEqual(kpis["cached_tokens_total"], 800)
        self.assertEqual(kpis["cache_creation_total"], 200)
        # costo effettivo: input nominale - cached (riuso), per singola richiesta media
        self.assertAlmostEqual(kpis["effective_input_avg"], 600.0)

    def test_migrazione_idempotente(self) -> None:
        # riaprire il DB non deve aggiungere colonne duplicate ne fallire
        again = System2Metrics(self.db)
        self._event(cached_tokens=5)
        kpis = again.cache_kpis(run_id="r1")
        self.assertEqual(kpis["cached_tokens_total"], 5)


if __name__ == "__main__":
    unittest.main()

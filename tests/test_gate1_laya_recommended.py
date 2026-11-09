"""Gate 1: align laya_recommended in benchmark runner to gateway's is_atomic_short_low_risk.

Acceptance:
- stessa soglia e stesse condizioni (complexity=atomic, risk_level=low) in canonico e mirror
- test che copre il salto del preflight per richiesta breve
- sync_hal_system2.sh check esce 0
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

_project_root = str(Path(__file__).resolve().parent.parent)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from benchmark.runner.benchmark_models import Settings, analyze_prompt, system1_guide


def _laya_client(family, strategy, mode, confidence=0.9):
    """Client mock con risposta Laya strutturata (contratto system1_guide rv7)."""
    client = MagicMock()
    response = MagicMock()
    response.json.return_value = {
        "answers": {
            "task_family": {"choice": family, "confidence": confidence},
            "strategy": {"choice": strategy, "confidence": confidence},
            "execution_mode": {"choice": mode, "confidence": confidence},
        }
    }
    response.raise_for_status = MagicMock()
    client.post.return_value = response
    return client


class TestGate1LayaRecommended(unittest.TestCase):
    """Verify laya_recommended follows gateway-like conditions."""

    def _make_settings(self, **overrides):
        base = {
            "laya_base_url": "http://127.0.0.1:8091",
            "laya_api_key": "sk-test",
            "laya_timeout": 120,
            "laya_min_confidence": 0.7,
            "laya_model": "multilingual",
        }
        base.update(overrides)
        return Settings(**base)

    def _make_prompt(self, prompt_text="ciao mondo", source=None):
        p = {"id": "test", "prompt": prompt_text}
        if source:
            p["source"] = source
        return p

    # --- Unit tests: analyze_prompt heuristic ---

    def test_short_general_prompt_laya_not_recommended(self):
        """Very short general prompt → laya_recommended=False."""
        result = analyze_prompt({"prompt": "ciao"})
        self.assertFalse(result["laya_recommended"])
        self.assertEqual(result["task_family"], "general")

    def test_long_general_prompt_laya_recommended(self):
        """General prompt ≥ 400 chars → laya_recommended=True."""
        result = analyze_prompt({"prompt": "a" * 400})
        self.assertTrue(result["laya_recommended"])

    def test_translation_always_recommended(self):
        """Translation family always recommends Laya."""
        result = analyze_prompt({"prompt": "traduci questo testo"})
        self.assertTrue(result["laya_recommended"])
        self.assertEqual(result["task_family"], "translation")

    def test_explicit_plan_always_recommended(self):
        """Explicit plan → laya_recommended=True regardless of length."""
        result = analyze_prompt({"prompt": "ciao piano di implementazione"})
        self.assertTrue(result["laya_recommended"])

    def test_source_family_recommended(self):
        """Source family → laya_recommended=True."""
        result = analyze_prompt({"prompt": "estraii dati", "source": "dummy.epub"})
        self.assertTrue(result["laya_recommended"])
        self.assertEqual(result["task_family"], "source")

    # --- Integration tests: system1_guide alignment ---

    @patch("benchmark.runner.benchmark_parsing.epub_text", return_value="")
    @patch("benchmark.runner.benchmark_workflow.time.perf_counter")
    def test_short_atomic_prompt_skips_laya_call(self, mock_perf, mock_epub):
        """Short atomic prompt should skip Laya (gateway alignment)."""
        mock_perf.side_effect = [100.0, 100.5]

        settings = self._make_settings()
        prompt = self._make_prompt("hello world")

        mock_client = MagicMock()
        result = system1_guide(prompt, settings, mock_client)

        # Laya must NOT be called
        mock_client.post.assert_not_called()
        self.assertFalse(result["laya_called"])
        self.assertEqual(result["decision_source"], "local_task_gate")
        self.assertEqual(result["complexity"], "atomic")

    @patch("benchmark.runner.benchmark_parsing.epub_text", return_value="")
    @patch("benchmark.runner.benchmark_workflow.time.perf_counter")
    def test_instruction_plus_source_under_threshold(self, mock_perf, mock_epub):
        """instruction + source < 400 → Laya chiamata: la soglia corta vale solo per "general".

        2026-11-09: la deviazione gateway (skip sotto 400 char per qualsiasi
        famiglia) e' stata assorbita dal canonico rv7, dove laya_recommended =
        famiglia != general oppure len >= 400 oppure explicit_plan. Una richiesta
        con fonte (famiglia source) preflighta sempre.
        """
        mock_perf.side_effect = [100.0, 100.5]

        settings = self._make_settings()
        instruction = "x" * 100
        source_content = "y" * 200
        mock_epub.return_value = source_content

        prompt = self._make_prompt(instruction, source="dummy.epub")
        mock_client = _laya_client("source", "grounded_extract", "single_pass", 0.9)
        result = system1_guide(prompt, settings, mock_client)

        mock_client.post.assert_called_once()
        self.assertTrue(result["laya_called"])
        self.assertEqual(result["task_family"], "source")
        self.assertEqual(result["decision_source"], "laya")

    @patch("benchmark.runner.benchmark_parsing.epub_text", return_value="")
    @patch("benchmark.runner.benchmark_workflow.time.perf_counter")
    def test_instruction_plus_source_at_threshold_calls_laya(
        self, mock_perf, mock_epub
    ):
        """instruction + source >= 400 → call Laya."""
        mock_perf.side_effect = [100.0, 100.5]

        settings = self._make_settings()
        instruction = "x" * 200
        source_content = "y" * 200
        mock_epub.return_value = source_content

        prompt = self._make_prompt(instruction, source="dummy.epub")

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "answers": {
                "task_family": {"choice": "general", "confidence": 1.0},
                "strategy": {"choice": "direct_answer", "confidence": 1.0},
                "execution_mode": {"choice": "single_pass", "confidence": 1.0},
            }
        }
        mock_response.raise_for_status = MagicMock()
        mock_client.post.return_value = mock_response

        result = system1_guide(prompt, settings, mock_client)

        mock_client.post.assert_called_once()
        self.assertTrue(result["laya_called"])

    @patch("benchmark.runner.benchmark_parsing.epub_text", return_value="")
    @patch("benchmark.runner.benchmark_workflow.time.perf_counter")
    def test_short_translation_calls_laya_per_canonical_rule(
        self, mock_perf, mock_epub
    ):
        """Traduzione breve → Laya chiamata: il gate canonico non salta la famiglia translation.

        2026-11-09: la vecchia allineamento gateway saltava il preflight per
        qualsiasi prompt atomico corto; il canonico rv7 lo salta solo per la
        famiglia general sotto soglia (test_short_atomic_prompt_skips_laya_call).
        """
        mock_perf.side_effect = [100.0, 100.5]

        settings = self._make_settings()
        prompt = self._make_prompt("translate this text")

        mock_client = _laya_client(
            "translation", "faithful_translate", "single_pass", 0.9
        )
        result = system1_guide(prompt, settings, mock_client)

        mock_client.post.assert_called_once()
        self.assertTrue(result["laya_called"])
        self.assertEqual(result["task_family"], "translation")
        self.assertEqual(result["decision_source"], "laya")


if __name__ == "__main__":
    unittest.main()

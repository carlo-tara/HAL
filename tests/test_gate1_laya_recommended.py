"""Gate 1: align laya_recommended in benchmark runner to gateway's is_atomic_short_low_risk.

Acceptance:
- stessa soglia e stesse condizioni (complexity=atomic, risk_level=low) in canonico e mirror
- test che copre il salto del preflight per richiesta breve
- sync_hal_system2.sh check esce 0
"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

_project_root = str(Path(__file__).resolve().parent.parent)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from benchmark.runner.benchmark_models import Settings, analyze_prompt, system1_guide


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

    @patch("benchmark.runner.benchmark_models.epub_text", return_value="")
    @patch("benchmark.runner.benchmark_models.time.perf_counter")
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

    @patch("benchmark.runner.benchmark_models.epub_text", return_value="")
    @patch("benchmark.runner.benchmark_models.time.perf_counter")
    def test_instruction_plus_source_under_threshold(self, mock_perf, mock_epub):
        """instruction + source < 400 → skip Laya."""
        mock_perf.side_effect = [100.0, 100.5]

        settings = self._make_settings()
        instruction = "x" * 100
        source_content = "y" * 200
        mock_epub.return_value = source_content

        prompt = self._make_prompt(instruction, source="dummy.epub")
        result = system1_guide(prompt, settings, MagicMock())

        self.assertFalse(result["laya_called"])
        self.assertEqual(result["decision_source"], "local_task_gate")

    @patch("benchmark.runner.benchmark_models.epub_text", return_value="")
    @patch("benchmark.runner.benchmark_models.time.perf_counter")
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

    @patch("benchmark.runner.benchmark_models.epub_text", return_value="")
    @patch("benchmark.runner.benchmark_models.time.perf_counter")
    def test_short_translation_skipped_by_gateway_alignment(self, mock_perf, mock_epub):
        """Short translation prompt also skipped when instruction+source < 400 (gateway alignment)."""
        mock_perf.side_effect = [100.0, 100.5]

        settings = self._make_settings()
        prompt = self._make_prompt("translate this text")

        result = system1_guide(prompt, settings, MagicMock())

        # Gateway alignment: short atomic prompts skip Laya regardless of family
        self.assertFalse(result["laya_called"])
        self.assertEqual(result["decision_source"], "local_task_gate")


if __name__ == "__main__":
    unittest.main()

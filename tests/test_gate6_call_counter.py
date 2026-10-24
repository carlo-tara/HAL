"""Gate 6: ridurre le chiamate Laya alle sole decisioni utili.

Acceptance:
- un preflight utile più le sole decisioni intermedie che possono cambiare il flusso
- test con limite di chiamate Laya per workflow
- contatore chiamate per run nel report
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

_project_root = str(Path(__file__).resolve().parent.parent)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from benchmark.runner.benchmark_models import Settings, system1_guide


def _make_settings(**overrides):
    base = {
        "laya_base_url": "http://127.0.0.1:8091",
        "laya_api_key": "sk-test",
        "laya_timeout": 120,
        "laya_min_confidence": 0.7,
        "laya_model": "multilingual",
        "laya_max_retries": 1,
    }
    base.update(overrides)
    return Settings(**base)


class TestGate6LayaCallCounter(unittest.TestCase):
    """Verifica che il contatore chiamate Laya sia presente e accurato."""

    @patch("benchmark.runner.benchmark_models.analyze_prompt")
    @patch("benchmark.runner.benchmark_models.epub_text")
    @patch("benchmark.runner.benchmark_models.time.perf_counter")
    def test_laya_call_count_in_result(self, mock_perf, mock_epub, mock_analyze):
        """Il risultato di system1_guide deve contenere il contatore chiamate."""
        mock_perf.side_effect = [100.0, 100.5]
        mock_epub.return_value = ""

        settings = _make_settings()
        prompt = {"id": "test", "prompt": "Analizza questo testo"}

        mock_analyze.return_value = {
            "task_family": "general",
            "execution_mode": "single_pass",
            "source_chars": 0,
            "has_source": False,
            "explicit_plan": True,
            "laya_recommended": True,
            "task_contract": {
                "family": "general",
                "required_strategy": "direct_answer",
            },
        }

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "answers": {
                "task_family": {"choice": "general", "confidence": 0.9},
                "strategy": {"choice": "direct_answer", "confidence": 0.9},
                "execution_mode": {"choice": "single_pass", "confidence": 0.9},
            }
        }
        mock_response.raise_for_status = MagicMock()
        mock_client.post.return_value = mock_response

        result = system1_guide(prompt, settings, mock_client)

        # Il risultato deve contenere il contatore
        self.assertIn("laya_call_count", result)
        self.assertEqual(result["laya_call_count"], 1)

    @patch("benchmark.runner.benchmark_models.analyze_prompt")
    @patch("benchmark.runner.benchmark_models.epub_text")
    @patch("benchmark.runner.benchmark_models.time.perf_counter")
    def test_laya_call_count_zero_when_skipped(
        self, mock_perf, mock_epub, mock_analyze
    ):
        """Quando Laya è saltata dal gateway, il contatore deve essere 0."""
        mock_perf.side_effect = [100.0, 100.5]
        mock_epub.return_value = ""

        settings = _make_settings()
        prompt = {"id": "test", "prompt": "ciao mondo"}

        # Prompt breve → _gateway_skip attiva → laya_recommended=False
        mock_analyze.return_value = {
            "task_family": "general",
            "execution_mode": "single_pass",
            "source_chars": 0,
            "has_source": False,
            "explicit_plan": False,
            "laya_recommended": False,
            "task_contract": {
                "family": "general",
                "required_strategy": "direct_answer",
            },
        }

        mock_client = MagicMock()
        result = system1_guide(prompt, settings, mock_client)

        # Laya non chiamata → contatore 0
        self.assertEqual(result["laya_call_count"], 0)
        mock_client.post.assert_not_called()

    @patch("benchmark.runner.benchmark_models.analyze_prompt")
    @patch("benchmark.runner.benchmark_models.epub_text")
    @patch("benchmark.runner.benchmark_models.time.perf_counter")
    def test_laya_call_count_with_retry(self, mock_perf, mock_epub, mock_analyze):
        """Con retry, il contatore conta tutti i tentativi."""
        mock_perf.side_effect = [100.0, 100.5, 101.0, 101.5]
        mock_epub.return_value = ""

        settings = _make_settings(laya_max_retries=1)
        prompt = {"id": "test", "prompt": "Analizza questo testo complesso"}

        mock_analyze.return_value = {
            "task_family": "general",
            "execution_mode": "source_chunks",
            "source_chars": 5000,
            "has_source": True,
            "explicit_plan": True,
            "laya_recommended": True,
            "task_contract": {
                "family": "general",
                "required_strategy": "direct_answer",
            },
        }

        low_resp = MagicMock()
        low_resp.json.return_value = {
            "answers": {
                "task_family": {"choice": "general", "confidence": 0.3},
                "strategy": {"choice": "direct_answer", "confidence": 0.3},
                "execution_mode": {"choice": "source_chunks", "confidence": 0.3},
            }
        }
        low_resp.raise_for_status = MagicMock()

        high_resp = MagicMock()
        high_resp.json.return_value = {
            "answers": {
                "task_family": {"choice": "general", "confidence": 0.9},
                "strategy": {"choice": "direct_answer", "confidence": 0.9},
                "execution_mode": {"choice": "single_pass", "confidence": 0.9},
            }
        }
        high_resp.raise_for_status = MagicMock()

        mock_client = MagicMock()
        mock_client.post.side_effect = [low_resp, high_resp]
        result = system1_guide(prompt, settings, mock_client)

        # 2 chiamate (iniziale + 1 retry)
        self.assertEqual(result["laya_call_count"], 2)
        self.assertEqual(mock_client.post.call_count, 2)


if __name__ == "__main__":
    unittest.main()

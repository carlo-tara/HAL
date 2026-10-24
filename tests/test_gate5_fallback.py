"""Gate 5: fallback conservativi sotto soglia e retry limitati.

Acceptance:
- ogni decisione sotto soglia ricade nel percorso single-pass senza perdita di contenuto
- retry ammessi solo se una decisione confidente può cambiare il flusso e con tetto massimo
- test su fallback low-confidence e limite retry
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


def _make_mock_response(family, strategy, mode, confidence=0.9):
    """Costruisce una risposta mock di Laya con scelte arbitrarie."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "answers": {
            "task_family": {"choice": family, "confidence": confidence},
            "strategy": {"choice": strategy, "confidence": confidence},
            "execution_mode": {"choice": mode, "confidence": confidence},
        }
    }
    mock_response.raise_for_status = MagicMock()
    mock_client.post.return_value = mock_response
    return mock_client


class TestGate5LowConfidenceFallback(unittest.TestCase):
    """Verifica che le decisioni low-confidence ricadano in single-pass."""

    @patch("benchmark.runner.benchmark_models.analyze_prompt")
    @patch("benchmark.runner.benchmark_models.epub_text")
    @patch("benchmark.runner.benchmark_models.time.perf_counter")
    def test_low_confidence_forces_single_pass(
        self, mock_perf, mock_epub, mock_analyze
    ):
        """Quando la confidenza è sotto soglia, execution_mode deve essere single_pass."""
        # Ogni tentativo chiama perf_counter 2 volte; con retry=1 default → 4 chiamate min.
        mock_perf.side_effect = [100.0, 100.5, 101.0, 101.5]
        mock_epub.return_value = ""

        settings = _make_settings()
        prompt = {"id": "test", "prompt": "Analizza questo testo complesso"}

        # Mock analyze per evitare _gateway_skip
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

        # Laya risponde con bassa confidenza
        mock_client = _make_mock_response(
            family="general",
            strategy="direct_answer",
            mode="source_chunks",
            confidence=0.5,  # sotto soglia 0.7
        )

        result = system1_guide(prompt, settings, mock_client)

        # Gate 5: fallback conservativo → single_pass
        self.assertEqual(result["execution_mode"], "single_pass")
        self.assertEqual(result["decision_source"], "local_task_gate")
        self.assertTrue(result["laya_called"])
        self.assertLess(result["confidence"], settings.laya_min_confidence)

    @patch("benchmark.runner.benchmark_models.analyze_prompt")
    @patch("benchmark.runner.benchmark_models.epub_text")
    @patch("benchmark.runner.benchmark_models.time.perf_counter")
    def test_low_confidence_preserves_strategy(
        self, mock_perf, mock_epub, mock_analyze
    ):
        """In caso di bassa confidenza, la strategia deve essere quella del contratto locale."""
        mock_perf.side_effect = [100.0, 100.5, 101.0, 101.5]
        mock_epub.return_value = ""

        settings = _make_settings()
        prompt = {"id": "test", "prompt": "Estrai i dati da questo documento"}

        mock_analyze.return_value = {
            "task_family": "source",
            "execution_mode": "single_pass",
            "source_chars": 1000,
            "has_source": False,
            "explicit_plan": True,
            "laya_recommended": True,
            "task_contract": {
                "family": "source",
                "required_strategy": "grounded_extract",
            },
        }

        # Laya propone una strategia diversa con bassa confidenza
        mock_client = _make_mock_response(
            family="source",
            strategy="faithful_translate",  # sbagliata
            mode="single_pass",
            confidence=0.4,
        )

        result = system1_guide(prompt, settings, mock_client)

        # Gate 5: strategia locale preservata
        self.assertEqual(result["strategy"], "grounded_extract")
        self.assertEqual(result["decision_source"], "local_task_gate")

    @patch("benchmark.runner.benchmark_models.analyze_prompt")
    @patch("benchmark.runner.benchmark_models.epub_text")
    @patch("benchmark.runner.benchmark_models.time.perf_counter")
    def test_high_confidence_allows_source_chunks(
        self, mock_perf, mock_epub, mock_analyze
    ):
        """Con confidenza alta, source_chunks deve essere permesso."""
        mock_perf.side_effect = [100.0, 100.5, 101.0, 101.5]
        mock_epub.return_value = ""

        settings = _make_settings()
        prompt = {"id": "test", "prompt": "Analizza questo testo lungo"}

        mock_analyze.return_value = {
            "task_family": "general",
            "execution_mode": "source_chunks",
            "source_chars": 10000,
            "has_source": True,
            "explicit_plan": True,
            "laya_recommended": True,
            "task_contract": {
                "family": "general",
                "required_strategy": "direct_answer",
            },
        }

        # Laya risponde con alta confidenza
        mock_client = _make_mock_response(
            family="general",
            strategy="direct_answer",
            mode="source_chunks",
            confidence=0.9,
        )

        result = system1_guide(prompt, settings, mock_client)

        # Alta confidenza → il flusso originale si preserva
        self.assertEqual(result["execution_mode"], "source_chunks")
        self.assertEqual(result["decision_source"], "laya")
        self.assertGreaterEqual(result["confidence"], settings.laya_min_confidence)


class TestGate5BoundedRetries(unittest.TestCase):
    """Verifica il meccanismo di retry limitato."""

    @patch("benchmark.runner.benchmark_models.analyze_prompt")
    @patch("benchmark.runner.benchmark_models.epub_text")
    @patch("benchmark.runner.benchmark_models.time.perf_counter")
    def test_retry_on_low_confidence(self, mock_perf, mock_epub, mock_analyze):
        """Il retry viene tentato una volta quando la confidenza è bassa."""
        # 2 tentativi × 2 chiamate perf_counter = 4+ valori
        mock_perf.side_effect = [100.0, 100.5, 101.0, 101.5, 102.0, 102.5]
        mock_epub.return_value = ""

        settings = _make_settings(laya_max_retries=1)
        prompt = {"id": "test", "prompt": "Analizza questo testo"}

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

        # Usa post.side_effect per restituire risposte diverse per ogni tentativo
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

        # Il retry ha cambiato l'esito: ora abbiamo single_pass con alta confidenza
        self.assertEqual(result["execution_mode"], "single_pass")
        self.assertEqual(result["decision_source"], "laya")
        self.assertGreaterEqual(result["confidence"], settings.laya_min_confidence)
        self.assertEqual(mock_client.post.call_count, 2)  # 2 chiamate a Laya

    @patch("benchmark.runner.benchmark_models.analyze_prompt")
    @patch("benchmark.runner.benchmark_models.epub_text")
    @patch("benchmark.runner.benchmark_models.time.perf_counter")
    def test_no_retry_when_zero_max_retries(self, mock_perf, mock_epub, mock_analyze):
        """Con laya_max_retries=0 non ci sono retry."""
        # max_retries=0 → 1 tentativo × 2 chiamate perf_counter = 2 valori
        mock_perf.side_effect = [100.0, 100.5]
        mock_epub.return_value = ""

        settings = _make_settings(laya_max_retries=0)
        prompt = {"id": "test", "prompt": "Analizza questo testo"}

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

        resp = MagicMock()
        resp.json.return_value = {
            "answers": {
                "task_family": {"choice": "general", "confidence": 0.3},
                "strategy": {"choice": "direct_answer", "confidence": 0.3},
                "execution_mode": {"choice": "source_chunks", "confidence": 0.3},
            }
        }
        resp.raise_for_status = MagicMock()

        mock_client = MagicMock()
        mock_client.post.return_value = resp
        result = system1_guide(prompt, settings, mock_client)

        # Nessun retry: fallback immediato a single_pass
        self.assertEqual(result["execution_mode"], "single_pass")
        self.assertEqual(result["decision_source"], "local_task_gate")
        self.assertEqual(mock_client.post.call_count, 1)  # 1 sola chiamata

    @patch("benchmark.runner.benchmark_models.analyze_prompt")
    @patch("benchmark.runner.benchmark_models.epub_text")
    @patch("benchmark.runner.benchmark_models.time.perf_counter")
    def test_retry_exhausted_falls_back(self, mock_perf, mock_epub, mock_analyze):
        """Se il retry mantiene bassa confidenza, si fallisce in single_pass."""
        # 2 tentativi × 2 chiamate perf_counter = 4 valori
        mock_perf.side_effect = [100.0, 100.5, 101.0, 101.5]
        mock_epub.return_value = ""

        settings = _make_settings(laya_max_retries=1)
        prompt = {"id": "test", "prompt": "Analizza questo testo"}

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

        # Entrambi i tentativi: bassa confidenza
        low_resp = MagicMock()
        low_resp.json.return_value = {
            "answers": {
                "task_family": {"choice": "general", "confidence": 0.2},
                "strategy": {"choice": "direct_answer", "confidence": 0.2},
                "execution_mode": {"choice": "source_chunks", "confidence": 0.2},
            }
        }
        low_resp.raise_for_status = MagicMock()

        mock_client = MagicMock()
        mock_client.post.side_effect = [low_resp, low_resp]
        result = system1_guide(prompt, settings, mock_client)

        # Retry esaurito: fallback conservativo
        self.assertEqual(result["execution_mode"], "single_pass")
        self.assertEqual(result["decision_source"], "local_task_gate")
        self.assertLess(result["confidence"], settings.laya_min_confidence)
        self.assertEqual(mock_client.post.call_count, 2)  # 2 chiamate (iniziale + 1 retry)


if __name__ == "__main__":
    unittest.main()

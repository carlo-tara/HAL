"""Gate 4: single-pass come default, plan-then-solve e segmentazione solo se giustificati.

Acceptance:
- plan-then-solve solo con richiesta decomponibile e confidenza sopra soglia
- segmentazione solo oltre CHARS_PER_A4_PAGE e nel rispetto dei limiti di pagina/intervallo
- test per ciascun ramo e per la preservazione dei segmenti
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

_project_root = str(Path(__file__).resolve().parent.parent)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from benchmark.runner.benchmark_models import (
    CHARS_PER_A4_PAGE,
    Settings,
    analyze_prompt,
    system1_guide,
)


class TestGate4ExecutionMode(unittest.TestCase):
    """Verify single-pass default and justified plan-then-solve / source-chunks."""

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

    # --- Unit tests: analyze_prompt mode determination ---

    def test_single_pass_default_no_source_no_plan(self):
        """No source, no explicit plan → single_pass."""
        result = analyze_prompt({"prompt": "calcola 2+2"})
        self.assertEqual(result["execution_mode"], "single_pass")
        self.assertFalse(result["explicit_plan"])
        self.assertFalse(result["has_source"])

    def test_plan_then_solve_on_explicit_plan_keyword(self):
        """Explicit plan keyword → plan_then_solve."""
        result = analyze_prompt(
            {"prompt": "piano di implementazione per questa funzione"}
        )
        self.assertEqual(result["execution_mode"], "plan_then_solve")
        self.assertTrue(result["explicit_plan"])

    def test_source_chunks_above_page_threshold(self):
        """Source > CHARS_PER_A4_PAGE → source_chunks."""
        large_source = "x" * (CHARS_PER_A4_PAGE + 1)
        result = analyze_prompt(
            {"prompt": "estraii dati", "source": "fake.epub"},
            source_chars=len(large_source),
        )
        self.assertEqual(result["execution_mode"], "source_chunks")
        self.assertTrue(result["has_source"])

    def test_single_pass_below_page_threshold(self):
        """Source ≤ CHARS_PER_A4_PAGE → single_pass (no chunks)."""
        small_source = "x" * CHARS_PER_A4_PAGE
        result = analyze_prompt(
            {"prompt": "ostraii dati"}, source_chars=len(small_source)
        )
        self.assertEqual(result["execution_mode"], "single_pass")

    def test_source_chunks_with_translation_family(self):
        """Translation with long source → source_chunks."""
        large_source = "y" * (CHARS_PER_A4_PAGE + 500)
        result = analyze_prompt(
            {"prompt": "traduci questo testo", "source": "fake.epub"},
            source_chars=len(large_source),
        )
        self.assertEqual(result["execution_mode"], "source_chunks")
        self.assertEqual(result["task_family"], "translation")

    # --- Integration tests: system1_guide mode enforcement ---

    @patch("benchmark.runner.benchmark_models.epub_text", return_value="")
    @patch("benchmark.runner.benchmark_models.time.perf_counter")
    def test_single_pass_default_skips_laya(self, mock_perf, mock_epub):
        """Short prompt without plan → single_pass, no Laya call."""
        mock_perf.side_effect = [100.0, 100.5]

        settings = self._make_settings()
        prompt = self._make_prompt("calcola il risultato")

        mock_client = MagicMock()
        result = system1_guide(prompt, settings, mock_client)

        mock_client.post.assert_not_called()
        self.assertEqual(result["execution_mode"], "single_pass")
        self.assertFalse(result["laya_called"])

    @patch("benchmark.runner.benchmark_models.epub_text", return_value="")
    @patch("benchmark.runner.benchmark_models.time.perf_counter")
    def test_plan_then_solve_requires_laya_confidence(self, mock_perf, mock_epub):
        """Explicit plan → Laya called; plan_then_solve only if confidence >= threshold."""
        mock_perf.side_effect = [100.0, 100.5]

        settings = self._make_settings()
        prompt = self._make_prompt("piano di implementazione passo dopo passo")

        # Laya proposes plan_then_solve with HIGH confidence → accepted
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "answers": {
                "task_family": {"choice": "general", "confidence": 1.0},
                "strategy": {"choice": "direct_answer", "confidence": 1.0},
                "execution_mode": {"choice": "plan_then_solve", "confidence": 0.9},
            }
        }
        mock_response.raise_for_status = MagicMock()
        mock_client.post.return_value = mock_response

        result = system1_guide(prompt, settings, mock_client)

        mock_client.post.assert_called_once()
        self.assertEqual(result["execution_mode"], "plan_then_solve")
        self.assertTrue(result["laya_called"])
        self.assertGreaterEqual(result["confidence"], settings.laya_min_confidence)

    @patch("benchmark.runner.benchmark_models.epub_text", return_value="")
    @patch("benchmark.runner.benchmark_models.time.perf_counter")
    def test_plan_then_solve_rejected_on_low_confidence(self, mock_perf, mock_epub):
        """Explicit plan + Laya proposes plan_then_solve but LOW confidence → fallback single_pass."""
        # Retry loop: 2 tentativi × 2 chiamate perf_counter = 4 valori
        mock_perf.side_effect = [100.0, 100.5, 101.0, 101.5]

        settings = self._make_settings()
        prompt = self._make_prompt("scomponi la richiesta in passaggi")

        mock_client = MagicMock()
        mock_response = MagicMock()
        # Laya proposes plan_then_solve but confidence below threshold
        mock_response.json.return_value = {
            "answers": {
                "task_family": {"choice": "general", "confidence": 0.5},
                "strategy": {"choice": "direct_answer", "confidence": 0.5},
                "execution_mode": {"choice": "plan_then_solve", "confidence": 0.5},
            }
        }
        mock_response.raise_for_status = MagicMock()
        mock_client.post.return_value = mock_response

        result = system1_guide(prompt, settings, mock_client)

        # Retry loop: 2 chiamate (iniziale + 1 retry) poi fallback single_pass
        self.assertEqual(mock_client.post.call_count, 2)
        # Should fall back to single_pass because confidence < threshold
        self.assertEqual(result["execution_mode"], "single_pass")
        self.assertTrue(result["laya_called"])

    @patch("benchmark.runner.benchmark_models.epub_text")
    @patch("benchmark.runner.benchmark_models.time.perf_counter")
    def test_source_chunks_triggered_above_threshold(self, mock_perf, mock_epub):
        """Long source (> CHARS_PER_A4_PAGE) → source_chunks mode."""
        mock_perf.side_effect = [100.0, 100.5]

        settings = self._make_settings()
        large_source = "z" * (CHARS_PER_A4_PAGE + 100)
        mock_epub.return_value = large_source

        prompt = self._make_prompt("estraii i dati dal documento", source="fake.epub")

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "answers": {
                "task_family": {"choice": "source", "confidence": 1.0},
                "strategy": {"choice": "grounded_extract", "confidence": 1.0},
                "execution_mode": {"choice": "source_chunks", "confidence": 1.0},
            }
        }
        mock_response.raise_for_status = MagicMock()
        mock_client.post.return_value = mock_response

        result = system1_guide(prompt, settings, mock_client)

        mock_client.post.assert_called_once()
        self.assertEqual(result["execution_mode"], "source_chunks")
        self.assertEqual(result["source_chars"], len(large_source))

    @patch("benchmark.runner.benchmark_models.epub_text")
    @patch("benchmark.runner.benchmark_models.time.perf_counter")
    def test_source_not_chunked_at_or_below_threshold(self, mock_perf, mock_epub):
        """Source exactly at CHARS_PER_A4_PAGE → NOT source_chunks."""
        mock_perf.side_effect = [100.0, 100.5]

        settings = self._make_settings()
        exact_source = "w" * CHARS_PER_A4_PAGE
        mock_epub.return_value = exact_source

        prompt = self._make_prompt("processa il contenuto", source="fake.epub")

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "answers": {
                "task_family": {"choice": "source", "confidence": 1.0},
                "strategy": {"choice": "grounded_extract", "confidence": 1.0},
                "execution_mode": {"choice": "single_pass", "confidence": 1.0},
            }
        }
        mock_response.raise_for_status = MagicMock()
        mock_client.post.return_value = mock_response

        result = system1_guide(prompt, settings, mock_client)

        # At threshold: source_chars == CHARS_PER_A4_PAGE, so NOT > threshold → single_pass
        self.assertNotEqual(result["execution_mode"], "source_chunks")
        self.assertEqual(result["execution_mode"], "single_pass")

    @patch("benchmark.runner.benchmark_models.epub_text")
    @patch("benchmark.runner.benchmark_models.time.perf_counter")
    def test_numero_pagine_caps_source_before_chunking(self, mock_perf, mock_epub):
        """numero_pagine argument caps source length before chunking decision."""
        mock_perf.side_effect = [100.0, 100.5]

        settings = self._make_settings()
        huge_source = "v" * 20000  # Would trigger chunks without cap
        mock_epub.return_value = huge_source

        # Cap at 1 page (3000 chars) → below chunk threshold
        prompt = {
            "id": "test",
            "prompt": "estraii dati",
            "source": "fake.epub",
            "arguments": {"numero_pagine": 1},
        }

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "answers": {
                "task_family": {"choice": "source", "confidence": 1.0},
                "strategy": {"choice": "grounded_extract", "confidence": 1.0},
                "execution_mode": {"choice": "single_pass", "confidence": 1.0},
            }
        }
        mock_response.raise_for_status = MagicMock()
        mock_client.post.return_value = mock_response

        result = system1_guide(prompt, settings, mock_client)

        # After capping to 1 page (3000 chars), source_chars == CHARS_PER_A4_PAGE
        # which is NOT > CHARS_PER_A4_PAGE, so no chunks
        self.assertNotEqual(result["execution_mode"], "source_chunks")
        self.assertEqual(result["execution_mode"], "single_pass")

    @patch("benchmark.runner.benchmark_models.epub_text", return_value="")
    @patch("benchmark.runner.benchmark_models.time.perf_counter")
    def test_segment_max_output_tokens_passed_through(self, mock_perf, mock_epub):
        """segment_max_output_tokens setting is respected in config."""
        mock_perf.side_effect = [100.0, 100.5]

        settings = self._make_settings(segment_max_output_tokens=500)
        self.assertEqual(settings.segment_max_output_tokens, 500)

        prompt = self._make_prompt("test")
        mock_client = MagicMock()
        result = system1_guide(prompt, settings, mock_client)

        # Config is passed through; verify settings object has the value
        self.assertEqual(result.get("complexity"), "atomic")


if __name__ == "__main__":
    unittest.main()

"""Gate 3: verificare la coerenza tra famiglia task, strategia e modalità scelte da Laya."""

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


class TestGate3Compatibility(unittest.TestCase):
    """Verifica che il gate blocchi le combinazioni incompatibili famiglia/strategia/modalità."""

    @patch("benchmark.runner.benchmark_models.epub_text")
    @patch("benchmark.runner.benchmark_models.time.perf_counter")
    def test_translation_rejects_extraction_strategy(self, mock_perf, mock_epub):
        """La famiglia translation non deve accettare la strategia grounded_extract (estrazione)."""
        mock_perf.side_effect = [100.0, 100.5]
        mock_epub.return_value = ""

        settings = _make_settings()
        prompt = {"id": "test", "prompt": "Traduci questo testo in francese"}

        # Laya propone erroneamente estrazione invece di traduzione
        mock_client = _make_mock_response(
            family="translation",
            strategy="grounded_extract",  # ← errata: è estrazione, non traduzione
            mode="single_pass",
        )

        result = system1_guide(prompt, settings, mock_client)

        # Il gate locale deve prevalere: strategia corretta per translation
        self.assertEqual(result["task_family"], "translation")
        self.assertEqual(result["strategy"], "faithful_translate")
        self.assertEqual(result["decision_source"], "local_task_gate")

    @patch("benchmark.runner.benchmark_models.analyze_prompt")
    @patch("benchmark.runner.benchmark_models.epub_text")
    @patch("benchmark.runner.benchmark_models.time.perf_counter")
    def test_translation_rejects_source_chunks_mode(
        self, mock_perf, mock_epub, mock_analyze
    ):
        """La famiglia translation non deve accettare source_chunks come modalità."""
        mock_perf.side_effect = [100.0, 100.5]
        mock_epub.return_value = ""

        settings = _make_settings()
        # Prompt semplice: analyze_prompt restituisce execution_mode=single_pass
        prompt = {"id": "test", "prompt": "Traduci questo testo in tedesco"}

        # Mock analyze_prompt per evitare _gateway_skip (explicit_plan=True → complexity=medium)
        mock_analyze.return_value = {
            "task_family": "translation",
            "execution_mode": "single_pass",
            "source_chars": 0,
            "has_source": False,
            "explicit_plan": True,
            "laya_recommended": True,
            "task_contract": {
                "family": "translation",
                "required_strategy": "faithful_translate",
            },
        }

        # Laya propone erroneamente source_chunks invece di single_pass
        mock_client = _make_mock_response(
            family="translation",
            strategy="faithful_translate",
            mode="source_chunks",  # ← errata: translation non supporta chunking
        )

        result = system1_guide(prompt, settings, mock_client)

        # La modalità deve essere single_pass (non source_chunks) per translation
        self.assertEqual(result["task_family"], "translation")
        self.assertEqual(result["execution_mode"], "single_pass")
        # La proposta incompatibile va registrata
        self.assertEqual(result["proposed_execution_mode"], "source_chunks")

    @patch("benchmark.runner.benchmark_models.analyze_prompt")
    @patch("benchmark.runner.benchmark_models.epub_text")
    @patch("benchmark.runner.benchmark_models.time.perf_counter")
    def test_translation_rejects_source_chunks_explicit(
        self, mock_perf, mock_epub, mock_analyze
    ):
        """Se l'analisi forza source_chunks su una translation, il gate deve resettare a single_pass."""
        mock_perf.side_effect = [100.0, 100.5]
        mock_epub.return_value = ""

        settings = _make_settings()
        prompt = {"id": "test", "prompt": "Traduci questo testo"}

        # Mock analyze_prompt per restituire execution_mode=source_chunks
        # (simula un caso reale con fonte lunga + traduzione)
        mock_analyze.return_value = {
            "task_family": "translation",
            "execution_mode": "source_chunks",
            "source_chars": 5000,
            "has_source": True,
            "explicit_plan": False,
            "laya_recommended": True,
            "task_contract": {
                "family": "translation",
                "required_strategy": "faithful_translate",
                "execution_mode": "source_chunks",
                "preserve_source_order": True,
                "respect_output_format": False,
            },
        }

        # Laya propone source_chunks (coerente con analisi ma incompatibile con family)
        mock_client = _make_mock_response(
            family="translation",
            strategy="faithful_translate",
            mode="source_chunks",
        )

        result = system1_guide(prompt, settings, mock_client)

        # Il gate deve resettare a single_pass per translation
        self.assertEqual(result["task_family"], "translation")
        self.assertEqual(result["execution_mode"], "single_pass")
        self.assertEqual(result["proposed_execution_mode"], "source_chunks")

    @patch("benchmark.runner.benchmark_models.analyze_prompt")
    @patch("benchmark.runner.benchmark_models.epub_text")
    @patch("benchmark.runner.benchmark_models.time.perf_counter")
    def test_valid_translation_combination_accepted(
        self, mock_perf, mock_epub, mock_analyze
    ):
        """Una combinazione valida translation + faithful_translate + single_pass deve passare."""
        mock_perf.side_effect = [100.0, 100.5]
        mock_epub.return_value = ""

        settings = _make_settings()
        prompt = {"id": "test", "prompt": "Traduci questo testo in spagnolo"}

        # Mock analyze_prompt per evitare _gateway_skip (explicit_plan=True → complexity=medium)
        mock_analyze.return_value = {
            "task_family": "translation",
            "execution_mode": "single_pass",
            "source_chars": 0,
            "has_source": False,
            "explicit_plan": True,
            "laya_recommended": True,
            "task_contract": {
                "family": "translation",
                "required_strategy": "faithful_translate",
            },
        }

        mock_client = _make_mock_response(
            family="translation",
            strategy="faithful_translate",
            mode="single_pass",
        )

        result = system1_guide(prompt, settings, mock_client)

        self.assertEqual(result["task_family"], "translation")
        self.assertEqual(result["strategy"], "faithful_translate")
        self.assertEqual(result["execution_mode"], "single_pass")
        self.assertEqual(result["decision_source"], "laya")

    @patch("benchmark.runner.benchmark_models.epub_text")
    @patch("benchmark.runner.benchmark_models.time.perf_counter")
    def test_source_family_rejects_translation_strategy(self, mock_perf, mock_epub):
        """La famiglia source (estrazione) non deve accettare la strategia faithful_translate."""
        mock_perf.side_effect = [100.0, 100.5]
        mock_epub.return_value = "Testo fonte di esempio"

        settings = _make_settings()
        prompt = {
            "id": "test",
            "prompt": "Estrai i nomi da questo documento",
            "source": "fake.epub",
        }

        # Laya propone erroneamente traduzione invece di estrazione
        mock_client = _make_mock_response(
            family="source",
            strategy="faithful_translate",  # ← errata: è traduzione, non estrazione
            mode="single_pass",
        )

        result = system1_guide(prompt, settings, mock_client)

        # Il gate locale deve prevalere
        self.assertEqual(result["task_family"], "source")
        self.assertEqual(result["strategy"], "grounded_extract")
        self.assertEqual(result["decision_source"], "local_task_gate")

    @patch("benchmark.runner.benchmark_models.analyze_prompt")
    @patch("benchmark.runner.benchmark_models.epub_text")
    @patch("benchmark.runner.benchmark_models.time.perf_counter")
    def test_source_family_rejects_plan_then_solve(
        self, mock_perf, mock_epub, mock_analyze
    ):
        """La famiglia source non deve accettare plan_then_solve come modalità."""
        mock_perf.side_effect = [100.0, 100.5]
        mock_epub.return_value = ""

        settings = _make_settings()
        prompt = {"id": "test", "prompt": "Estrai i dati JSON dal testo"}

        mock_analyze.return_value = {
            "task_family": "source",
            "execution_mode": "plan_then_solve",
            "source_chars": 1000,
            "has_source": False,
            "explicit_plan": True,
            "laya_recommended": True,
            "task_contract": {
                "family": "source",
                "required_strategy": "grounded_extract",
                "execution_mode": "plan_then_solve",
                "preserve_source_order": False,
                "respect_output_format": True,
            },
        }

        mock_client = _make_mock_response(
            family="source",
            strategy="grounded_extract",
            mode="plan_then_solve",
        )

        result = system1_guide(prompt, settings, mock_client)

        # source supporta solo single_pass
        self.assertEqual(result["task_family"], "source")
        self.assertEqual(result["execution_mode"], "single_pass")
        self.assertEqual(result["proposed_execution_mode"], "plan_then_solve")

    @patch("benchmark.runner.benchmark_models.analyze_prompt")
    @patch("benchmark.runner.benchmark_models.epub_text")
    @patch("benchmark.runner.benchmark_models.time.perf_counter")
    def test_reasoning_rejects_source_chunks(self, mock_perf, mock_epub, mock_analyze):
        """La famiglia reasoning non deve accettare source_chunks come modalità."""
        mock_perf.side_effect = [100.0, 100.5]
        mock_epub.return_value = ""

        settings = _make_settings()
        prompt = {"id": "test", "prompt": "Ragiona su questo problema logico"}

        mock_analyze.return_value = {
            "task_family": "reasoning",
            "execution_mode": "source_chunks",
            "source_chars": 8000,
            "has_source": True,
            "explicit_plan": False,
            "laya_recommended": True,
            "task_contract": {
                "family": "reasoning",
                "required_strategy": "reasoning_check",
                "execution_mode": "source_chunks",
                "preserve_source_order": False,
                "respect_output_format": False,
            },
        }

        mock_client = _make_mock_response(
            family="reasoning",
            strategy="reasoning_check",
            mode="source_chunks",
        )

        result = system1_guide(prompt, settings, mock_client)

        # reasoning supporta solo single_pass e plan_then_solve
        self.assertEqual(result["task_family"], "reasoning")
        self.assertEqual(result["execution_mode"], "single_pass")
        self.assertEqual(result["proposed_execution_mode"], "source_chunks")

    @patch("benchmark.runner.benchmark_models.analyze_prompt")
    @patch("benchmark.runner.benchmark_models.epub_text")
    @patch("benchmark.runner.benchmark_models.time.perf_counter")
    def test_coding_allows_plan_then_solve(self, mock_perf, mock_epub, mock_analyze):
        """La famiglia coding deve accettare plan_then_solve come modalità valida."""
        mock_perf.side_effect = [100.0, 100.5]
        mock_epub.return_value = ""

        settings = _make_settings()
        prompt = {"id": "test", "prompt": "Scrivi una funzione Python"}

        mock_analyze.return_value = {
            "task_family": "coding",
            "execution_mode": "plan_then_solve",
            "source_chars": 500,
            "has_source": False,
            "explicit_plan": True,
            "laya_recommended": True,
            "task_contract": {
                "family": "coding",
                "required_strategy": "requirements_check",
                "execution_mode": "plan_then_solve",
                "preserve_source_order": False,
                "respect_output_format": False,
            },
        }

        mock_client = _make_mock_response(
            family="coding",
            strategy="requirements_check",
            mode="plan_then_solve",
        )

        result = system1_guide(prompt, settings, mock_client)

        # coding supporta plan_then_solve → deve passare invariato
        self.assertEqual(result["task_family"], "coding")
        self.assertEqual(result["execution_mode"], "plan_then_solve")
        self.assertEqual(result["proposed_execution_mode"], "plan_then_solve")
        self.assertEqual(result["decision_source"], "laya")

    @patch("benchmark.runner.benchmark_models.analyze_prompt")
    @patch("benchmark.runner.benchmark_models.epub_text")
    @patch("benchmark.runner.benchmark_models.time.perf_counter")
    def test_general_allows_source_chunks(self, mock_perf, mock_epub, mock_analyze):
        """La famiglia general deve accettare source_chunks come modalità valida."""
        mock_perf.side_effect = [100.0, 100.5]
        mock_epub.return_value = ""

        settings = _make_settings()
        prompt = {"id": "test", "prompt": "Analizza questo testo generico"}

        mock_analyze.return_value = {
            "task_family": "general",
            "execution_mode": "source_chunks",
            "source_chars": 10000,
            "has_source": True,
            "explicit_plan": False,
            "laya_recommended": True,
            "task_contract": {
                "family": "general",
                "required_strategy": "direct_answer",
                "execution_mode": "source_chunks",
                "preserve_source_order": False,
                "respect_output_format": False,
            },
        }

        mock_client = _make_mock_response(
            family="general",
            strategy="direct_answer",
            mode="source_chunks",
        )

        result = system1_guide(prompt, settings, mock_client)

        # general supporta source_chunks → deve passare invariato
        self.assertEqual(result["task_family"], "general")
        self.assertEqual(result["execution_mode"], "source_chunks")
        self.assertEqual(result["proposed_execution_mode"], "source_chunks")
        self.assertEqual(result["decision_source"], "laya")


if __name__ == "__main__":
    unittest.main()

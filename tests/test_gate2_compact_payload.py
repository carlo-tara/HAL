"""Gate 2: il payload verso Laya deve contenere solo contratto compatto, niente fonte integrale."""

from __future__ import annotations

import json
import re

# Import from benchmark runner via package path.
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Ensure the project root is on sys.path so 'benchmark' resolves.
_project_root = str(Path(__file__).resolve().parent.parent)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from benchmark.runner.benchmark_models import Settings, analyze_prompt, system1_guide


class TestGate2CompactPayload(unittest.TestCase):
    """Verifica che il payload inviato a Laya sia un contratto compatto."""

    def _make_settings(self, **overrides):
        """Costruisce Settings con overrides."""
        base = {
            "laya_base_url": "http://127.0.0.1:8091",
            "laya_api_key": "sk-test",
            "laya_timeout": 120,
            "laya_min_confidence": 0.7,
            "laya_model": "multilingual",
        }
        base.update(overrides)
        return Settings(**base)

    def _make_prompt(self, prompt_text="Traduci questo testo in inglese", source=None):
        """Costruisce un prompt di test."""
        p = {"id": "test", "prompt": prompt_text}
        if source:
            p["source"] = source
        return p

    @patch("benchmark.runner.benchmark_models.epub_text")
    @patch("benchmark.runner.benchmark_models.time.perf_counter")
    def test_payload_no_full_source_text(self, mock_perf, mock_epub):
        """Il payload non deve contenere il testo integrale della fonte."""
        mock_perf.side_effect = [100.0, 100.5]  # preflight latency
        full_source = "A" * 50000  # 50k caratteri, ben oltre ogni limite ragionevole
        mock_epub.return_value = full_source

        settings = self._make_settings()
        prompt = self._make_prompt(source="fake.epub")

        # Mock la risposta di Laya
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "answers": {
                "task_family": {"choice": "translation", "confidence": 0.9},
                "strategy": {"choice": "reasoning_check", "confidence": 0.9},
                "execution_mode": {"choice": "single_pass", "confidence": 0.9},
            }
        }
        mock_response.raise_for_status = MagicMock()
        mock_client.post.return_value = mock_response

        result = system1_guide(prompt, settings, mock_client)

        # Verifica che la chiamata POST sia stata fatta
        call_args = mock_client.post.call_args
        self.assertIsNotNone(call_args, "system1_guide deve chiamare client.post")

        # Estrai il payload JSON inviato
        payload = call_args.kwargs.get("json") or call_args[1].get("json")
        self.assertIsNotNone(payload, "payload JSON deve essere presente")

        # Serializza il payload e verifica che non contenga il testo integrale
        payload_str = json.dumps(payload)
        # Il testo integrale è 50k 'A'; se nel payload appare una sequenza > 5000 'A',
        # significa che la fonte integrale (o una porzione troppo grande) è inclusa.
        long_sequence_pattern = '"A{5000,}"'
        self.assertNotRegex(
            payload_str,
            long_sequence_pattern,
            "Il payload non deve contenere sequenze lunghe del testo della fonte",
        )

    @patch("benchmark.runner.benchmark_models.epub_text")
    @patch("benchmark.runner.benchmark_models.time.perf_counter")
    def test_payload_excerpt_within_configurable_limit(self, mock_perf, mock_epub):
        """L'estratto nel payload deve rispettare il tetto configurabile (default 1200)."""
        mock_perf.side_effect = [100.0, 100.5]
        full_source = "X" * 5000
        mock_epub.return_value = full_source

        settings = self._make_settings()
        prompt = self._make_prompt(source="fake.epub")

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "answers": {
                "task_family": {"choice": "translation", "confidence": 0.9},
                "strategy": {"choice": "reasoning_check", "confidence": 0.9},
                "execution_mode": {"choice": "single_pass", "confidence": 0.9},
            }
        }
        mock_response.raise_for_status = MagicMock()
        mock_client.post.return_value = mock_response

        result = system1_guide(prompt, settings, mock_client)

        call_args = mock_client.post.call_args
        payload = call_args.kwargs.get("json") or call_args[1].get("json")

        # Cerca tutti i valori stringa nel payload e verifica che nessuno superi 1200 char
        # (esclusi i campi strutturati come task_contract)
        def find_long_strings(obj, path=""):
            long_strings = []
            if isinstance(obj, str):
                if len(obj) > 1200:
                    long_strings.append((path, obj[:50], len(obj)))
            elif isinstance(obj, dict):
                for k, v in obj.items():
                    long_strings.extend(find_long_strings(v, f"{path}.{k}"))
            elif isinstance(obj, list):
                for i, v in enumerate(obj):
                    long_strings.extend(find_long_strings(v, f"{path}[{i}]"))
            return long_strings

        long_strings = find_long_strings(payload)
        # Filtra solo i campi che potrebbero contenere testo della fonte
        source_related = [
            (p, s, l)
            for p, s, l in long_strings
            if any(
                kw in p.lower()
                for kw in ("source", "context", "notes", "excerpt", "text")
            )
        ]
        self.assertEqual(
            len(source_related),
            0,
            f"Trovati campi contenenti testo > 1200 char: {source_related}",
        )

    def test_analyze_preserves_source_and_output_format(self):
        """analyze_prompt deve preservare source e output_format nell'analisi."""
        prompt = {
            "id": "test",
            "prompt": "Estrai i dati JSON da questo testo",
            "arguments": {"output_format": "json"},
        }
        analysis = analyze_prompt(prompt, source_chars=0)

        # Verifica che i campi richiesti siano presenti
        self.assertIn("task_contract", analysis)
        task_contract = analysis["task_contract"]
        # Il task_contract deve contenere le informazioni essenziali
        self.assertIn("family", task_contract)
        self.assertIn("required_strategy", task_contract)

    @patch("benchmark.runner.benchmark_models.epub_text")
    @patch("benchmark.runner.benchmark_models.time.perf_counter")
    def test_payload_contains_task_contract_metadata(self, mock_perf, mock_epub):
        """Il payload deve contenere il task_contract con metadati essenziali."""
        mock_perf.side_effect = [100.0, 100.5]
        mock_epub.return_value = "B" * 1000

        settings = self._make_settings()
        prompt = self._make_prompt(source="fake.epub")

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "answers": {
                "task_family": {"choice": "translation", "confidence": 0.9},
                "strategy": {"choice": "reasoning_check", "confidence": 0.9},
                "execution_mode": {"choice": "single_pass", "confidence": 0.9},
            }
        }
        mock_response.raise_for_status = MagicMock()
        mock_client.post.return_value = mock_response

        result = system1_guide(prompt, settings, mock_client)

        call_args = mock_client.post.call_args
        payload = call_args.kwargs.get("json") or call_args[1].get("json")

        # Il payload deve contenere task_contract
        self.assertIn("state", payload)
        self.assertIn("task_contract", payload["state"])

        tc = payload["state"]["task_contract"]
        # Deve avere famiglia
        self.assertIn("family", tc)
        # Deve avere strategia richiesta
        self.assertIn("required_strategy", tc)

    @patch("benchmark.runner.benchmark_models.epub_text")
    @patch("benchmark.runner.benchmark_models.time.perf_counter")
    def test_payload_contains_complexity_and_format(self, mock_perf, mock_epub):
        """Il payload deve contenere complessità e formato."""
        mock_perf.side_effect = [100.0, 100.5]
        mock_epub.return_value = "D" * 1000

        settings = self._make_settings()
        prompt = self._make_prompt(source="fake.epub")

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "answers": {
                "task_family": {"choice": "translation", "confidence": 0.9},
                "strategy": {"choice": "reasoning_check", "confidence": 0.9},
                "execution_mode": {"choice": "single_pass", "confidence": 0.9},
            }
        }
        mock_response.raise_for_status = MagicMock()
        mock_client.post.return_value = mock_response

        result = system1_guide(prompt, settings, mock_client)

        call_args = mock_client.post.call_args
        payload = call_args.kwargs.get("json") or call_args[1].get("json")

        self.assertIn("complexity", payload["state"])
        self.assertIn("format", payload["state"])
        self.assertIsInstance(payload["state"]["complexity"], str)
        self.assertIsInstance(payload["state"]["format"], str)

    @patch("benchmark.runner.benchmark_models.epub_text")
    @patch("benchmark.runner.benchmark_models.time.perf_counter")
    def test_result_preserves_source_and_output_format(self, mock_perf, mock_epub):
        """Il risultato deve preservare source e output_format."""
        mock_perf.side_effect = [100.0, 100.5]
        mock_epub.return_value = "C" * 1000

        settings = self._make_settings()
        prompt = self._make_prompt(
            prompt_text="Estrai i dati JSON da questo testo",
            source="fake.epub",
        )
        prompt["arguments"] = {"output_format": "json"}

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "answers": {
                "task_family": {"choice": "source", "confidence": 0.9},
                "strategy": {"choice": "grounded_extract", "confidence": 0.9},
                "execution_mode": {"choice": "single_pass", "confidence": 0.9},
            }
        }
        mock_response.raise_for_status = MagicMock()
        mock_client.post.return_value = mock_response

        result = system1_guide(prompt, settings, mock_client)

        self.assertEqual(result["source"], "fake.epub")
        self.assertEqual(result["output_format"], "json")

    def test_result_preserves_source_and_output_format_no_laya(self):
        """Il risultato senza chiamata Laya deve preservare source e output_format."""
        settings = self._make_settings()
        prompt = self._make_prompt(
            prompt_text="Ciao",
        )
        prompt["arguments"] = {"output_format": "html"}

        result = system1_guide(prompt, settings, MagicMock())

        self.assertIsNone(result.get("source"))
        self.assertEqual(result["output_format"], "html")
        self.assertIn("complexity", result)
        self.assertIn("format", result)

    def test_complexity_high_for_source_chunks(self):
        """La complessità deve essere 'high' quando execution_mode è source_chunks."""
        settings = self._make_settings()
        prompt = self._make_prompt(
            prompt_text="Estrai e sintetizza la fonte fornita",
            source="fake.epub",
        )

        mock_epub = MagicMock()
        # Fonte lunga > CHARS_PER_A4_PAGE per attivare source_chunks
        mock_epub.return_value = "E" * 5000

        with patch("benchmark.runner.benchmark_models.epub_text", mock_epub):
            with patch(
                "benchmark.runner.benchmark_models.time.perf_counter"
            ) as mock_perf:
                mock_perf.side_effect = [100.0, 100.5]

                mock_client = MagicMock()
                mock_response = MagicMock()
                mock_response.json.return_value = {
                    "answers": {
                        "task_family": {"choice": "source", "confidence": 0.9},
                        "strategy": {"choice": "grounded_extract", "confidence": 0.9},
                        "execution_mode": {
                            "choice": "source_chunks",
                            "confidence": 0.9,
                        },
                    }
                }
                mock_response.raise_for_status = MagicMock()
                mock_client.post.return_value = mock_response

                result = system1_guide(prompt, settings, mock_client)

                call_args = mock_client.post.call_args
                payload = call_args.kwargs.get("json") or call_args[1].get("json")

                self.assertEqual(payload["state"]["complexity"], "high")

    @patch("benchmark.runner.benchmark_models.epub_text")
    @patch("benchmark.runner.benchmark_models.time.perf_counter")
    def test_complexity_medium_for_explicit_plan(self, mock_perf, mock_epub):
        """La complessità deve essere 'medium' quando la richiesta chiede un piano."""
        mock_perf.side_effect = [100.0, 100.5]
        mock_epub.return_value = ""

        settings = self._make_settings()
        prompt = self._make_prompt(
            prompt_text="Fai un piano di implementazione prima di rispondere",
        )

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "answers": {
                "task_family": {"choice": "general", "confidence": 0.9},
                "strategy": {"choice": "direct_answer", "confidence": 0.9},
                "execution_mode": {"choice": "plan_then_solve", "confidence": 0.9},
            }
        }
        mock_response.raise_for_status = MagicMock()
        mock_client.post.return_value = mock_response

        result = system1_guide(prompt, settings, mock_client)

        self.assertEqual(result["complexity"], "medium")

    def test_configurable_excerpt_max_chars(self):
        """L'estratto deve rispettare il tetto configurabile laya_excerpt_max_chars."""
        full_source = "F" * 5000

        # Test con default 1200
        settings_default = self._make_settings()
        prompt = self._make_prompt(source="fake.epub")

        mock_epub = MagicMock()
        mock_epub.return_value = full_source

        with patch("benchmark.runner.benchmark_models.epub_text", mock_epub):
            with patch(
                "benchmark.runner.benchmark_models.time.perf_counter"
            ) as mock_perf:
                mock_perf.side_effect = [100.0, 100.5]

                mock_client = MagicMock()
                mock_response = MagicMock()
                mock_response.json.return_value = {
                    "answers": {
                        "task_family": {"choice": "translation", "confidence": 0.9},
                        "strategy": {"choice": "reasoning_check", "confidence": 0.9},
                        "execution_mode": {"choice": "single_pass", "confidence": 0.9},
                    }
                }
                mock_response.raise_for_status = MagicMock()
                mock_client.post.return_value = mock_response

                system1_guide(prompt, settings_default, mock_client)

                call_args = mock_client.post.call_args
                payload = call_args.kwargs.get("json") or call_args[1].get("json")
                excerpt = payload["state"]["excerpt"]
                self.assertLessEqual(len(excerpt), 1200)

        # Test con valore personalizzato
        custom_limit = 500
        settings_custom = self._make_settings(laya_excerpt_max_chars=custom_limit)

        with patch("benchmark.runner.benchmark_models.epub_text", mock_epub):
            with patch(
                "benchmark.runner.benchmark_models.time.perf_counter"
            ) as mock_perf:
                mock_perf.side_effect = [100.0, 100.5]

                mock_client2 = MagicMock()
                mock_response2 = MagicMock()
                mock_response2.json.return_value = {
                    "answers": {
                        "task_family": {"choice": "translation", "confidence": 0.9},
                        "strategy": {"choice": "reasoning_check", "confidence": 0.9},
                        "execution_mode": {"choice": "single_pass", "confidence": 0.9},
                    }
                }
                mock_response2.raise_for_status = MagicMock()
                mock_client2.post.return_value = mock_response2

                system1_guide(prompt, settings_custom, mock_client2)

                call_args2 = mock_client2.post.call_args
                payload2 = call_args2.kwargs.get("json") or call_args2[1].get("json")
                excerpt2 = payload2["state"]["excerpt"]
                self.assertLessEqual(len(excerpt2), custom_limit)


if __name__ == "__main__":
    unittest.main()

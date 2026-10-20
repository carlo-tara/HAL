"""Guardia sulla copia del runner nel gateway (canonico: hal_system2/app/)."""

from __future__ import annotations

import json
import unittest
from unittest.mock import patch

import httpx

from benchmark.runner import benchmark_models as runner

MODEL = {"provider": "ollama", "model": "local:1b"}
SOURCE = "a" * 3000 + "b" * 3000 + "c" * 1000


def _guide(family: str, strategy: str) -> dict:
    return {
        "task_family": family,
        "execution_mode": "source_chunks",
        "guidance": runner.SYSTEM1_STRATEGIES[strategy],
    }


def _run(prompt: dict, guide: dict, answers: list[str] | None = None):
    messages: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        messages.append(json.loads(request.content)["messages"][0]["content"])
        text = (answers or [])[len(messages) - 1] if answers else f"out-{len(messages)}"
        return httpx.Response(
            200,
            json={
                "done": True,
                "message": {"content": text},
                "done_reason": "stop",
                "prompt_eval_count": 10,
                "eval_count": 5,
            },
        )

    with (
        patch.object(runner, "epub_text", return_value=SOURCE),
        httpx.Client(transport=httpx.MockTransport(handler)) as client,
    ):
        result = runner.system2_workflow_call(
            MODEL,
            prompt,
            runner.Settings(ollama_base_url="http://ollama:11434"),
            client,
            guide,
        )
    return result, messages


class TestLocalAssembly(unittest.TestCase):
    def test_translation_is_concatenated_without_assembly_call(self) -> None:
        prompt = {
            "id": "t",
            "prompt": "Traduci il libro.",
            "source": "x.epub",
            "arguments": {"lingua_destinazione": "spagnolo"},
        }

        result, messages = _run(prompt, _guide("translation", "faithful_translate"))

        self.assertEqual(len(messages), 3)
        self.assertFalse(any("Assembla i risultati parziali" in m for m in messages))
        self.assertEqual(result["response"], "out-1\n\nout-2\n\nout-3")
        self.assertEqual(result["tokens"]["total"], 45)

    def test_non_mechanical_extraction_still_assembles_with_model(self) -> None:
        prompt = {"id": "e", "prompt": "Riassumi il libro.", "source": "x.epub"}

        result, messages = _run(prompt, _guide("source", "grounded_extract"))

        self.assertEqual(len(messages), 4)
        self.assertIn("Assembla i risultati parziali", messages[-1])
        self.assertEqual(result["response"], "out-4")

    def test_json_extraction_with_valid_segments_is_merged_locally(self) -> None:
        prompt = {"id": "j", "prompt": "Estrai in JSON.", "source": "x.epub"}

        result, messages = _run(
            prompt,
            _guide("source", "grounded_extract"),
            answers=['[{"c": 1}]', '[{"c": 2}]', '{"c": 3}'],
        )

        self.assertEqual(len(messages), 3)
        self.assertEqual(json.loads(result["response"]), [{"c": 1}, {"c": 2}, {"c": 3}])

    def test_assemble_segments_locally_contract(self) -> None:
        assemble = runner.assemble_segments_locally

        self.assertIsNone(assemble("translation", "x", []))
        self.assertEqual(assemble("source", "x", ["solo"]), "solo")
        self.assertEqual(assemble("translation", "x", [" a ", "b"]), "a\n\nb")
        self.assertIsNone(assemble("source", "estrai json", ["[1]", "non json"]))
        self.assertIsNone(assemble("source", "riassumi", ["uno", "due"]))


class TestCooldown(unittest.TestCase):
    def _run(self, count: int, **kwargs) -> list[float]:
        import tempfile
        from pathlib import Path

        pauses: list[float] = []
        reply = httpx.Response(200, json={"done": True, "message": {"content": "ok"}})
        models = [{"provider": "ollama", "model": f"m:{i}"} for i in range(count)]
        with (
            tempfile.TemporaryDirectory() as tmp,
            httpx.Client(transport=httpx.MockTransport(lambda r: reply)) as client,
        ):
            runner.run_benchmark(
                models,
                [{"id": "math", "prompt": "Q"}],
                runner.Settings(ollama_base_url="http://ollama:11434"),
                Path(tmp) / "out.json",
                client=client,
                sleep=pauses.append,
                **kwargs,
            )
        return pauses

    def test_pause_only_between_models(self) -> None:
        self.assertEqual(self._run(3, cooldown=300), [300, 300])

    def test_no_pause_by_default_or_with_single_model(self) -> None:
        self.assertEqual(self._run(3), [])
        self.assertEqual(self._run(1, cooldown=300), [])


if __name__ == "__main__":
    unittest.main()

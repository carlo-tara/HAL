"""Contratto P1 (ToDo 2026-10-28, voce streaming SSE): il backend registrato
via ``SystemTwoEngine.register_backend`` ricostruisce una ``SystemTwoResponse``
dal flusso: accumulo ``delta.content``, chunk finale senza ``choices`` ma con
``usage``, terminazione alla sentinella ``data: [DONE]``.
"""

from __future__ import annotations

import json
import unittest

from global_config import SystemTwoEngine, SystemTwoResponse
from streaming_backend import (
    SSESystemTwoBackend,
    accumulate_stream,
    build_stream_payload,
    extract_sse_data,
)


def _chunk(content: str) -> str:
    return "data: " + json.dumps(
        {"choices": [{"delta": {"content": content}, "index": 0}]}
    )


class TestSseParsing(unittest.TestCase):
    def test_accumulo_delta_content(self) -> None:
        lines = [_chunk("Hel"), _chunk("lo "), _chunk("mondo"), "data: [DONE]"]
        resp = accumulate_stream(lines, "orcarouter/qwen/qwen3.8-flash", "orcarouter")
        self.assertEqual(str(resp), "Hello mondo")
        self.assertIsInstance(resp, SystemTwoResponse)

    def test_chunk_finale_usage_senza_choices(self) -> None:
        lines = [
            _chunk("ok"),
            "data: "
            + json.dumps(
                {
                    "choices": [],
                    "usage": {
                        "prompt_tokens": 12,
                        "completion_tokens": 3,
                        "total_tokens": 15,
                    },
                }
            ),
            "data: [DONE]",
        ]
        resp = accumulate_stream(lines, "m", "p")
        self.assertEqual(str(resp), "ok")
        self.assertEqual(resp.usage["total_tokens"], 15)  # type: ignore[attr-defined]

    def test_sentinella_conclude_il_flusso(self) -> None:
        lines = [
            _chunk("A"),
            "data: [DONE]",
            _chunk("NON_DEVE_APPARIRE"),
        ]
        resp = accumulate_stream(lines, "m", "p")
        self.assertEqual(str(resp), "A")

    def test_keep_alive_e_righe_vuote_ignorati(self) -> None:
        lines = [": keep-alive", "", _chunk("B"), "data: [DONE]"]
        resp = accumulate_stream(lines, "m", "p")
        self.assertEqual(str(resp), "B")

    def test_riga_malformata_saltata(self) -> None:
        lines = ["data: {non-json", _chunk("C"), "data: [DONE]"]
        resp = accumulate_stream(lines, "m", "p")
        self.assertEqual(str(resp), "C")

    def test_extract_sse_data(self) -> None:
        self.assertIsNone(extract_sse_data(""))
        self.assertIsNone(extract_sse_data(": ping"))
        self.assertEqual(extract_sse_data("data: [DONE]"), "[DONE]")
        self.assertEqual(extract_sse_data("data:  x "), "x")
        self.assertIsNone(extract_sse_data("event: msg"))


class TestPayload(unittest.TestCase):
    def test_include_usage_default(self) -> None:
        payload = build_stream_payload(
            "coding", "ciao", "orcarouter/qwen/qwen3.8-flash"
        )
        self.assertTrue(payload["stream"])
        self.assertEqual(payload["stream_options"], {"include_usage": True})

    def test_streaming_only_passa_la_frontiera(self) -> None:
        payload = build_stream_payload("coding", "ciao", "orcarouter/qwen/qwq-32b")
        self.assertTrue(payload["stream"])


class TestEngineIntegration(unittest.TestCase):
    def tearDown(self) -> None:
        SystemTwoEngine.register_backend(None)

    def test_execute_via_register_backend(self) -> None:
        def fake_lines(payload):
            assert payload["stream"] is True
            return [_chunk("ri"), _chunk("su"), "data: [DONE]"]

        backend = SSESystemTwoBackend(fake_lines)
        SystemTwoEngine.register_backend(backend)
        response = SystemTwoEngine.execute("coding", "testo")
        self.assertIsInstance(response, SystemTwoResponse)
        self.assertEqual(str(response), "risu")
        self.assertEqual(response.model, SystemTwoEngine.ACTIVE_MODEL_NAME)


if __name__ == "__main__":
    unittest.main()

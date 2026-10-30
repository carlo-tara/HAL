"""Contratto P2 (ToDo 2026-10-28, §Streaming with tool calls + JSON Mode):

gli argomenti dei tool arrivano come stringhe JSON parziali in
``tool_calls[i].function.arguments``, da concatenare per ``index`` e passare a
``json.loads`` solo a stream terminato. Con JSON Mode + streaming solo l'output
concatenato è JSON valido: in Cache L1 va messa la risposta completa, non i
chunk. Nessuna invocazione di parsing su chunk singolo.
"""

from __future__ import annotations

import json
import unittest

from streaming_backend import ToolCallAccumulator, accumulate_stream


def _tc_chunk(
    index: int,
    arg_fragment: str,
    name: str | None = None,
    tc_id: str | None = None,
) -> str:
    tc: dict = {"index": index, "function": {"arguments": arg_fragment}}
    if name:
        tc["function"]["name"] = name
    if tc_id:
        tc["id"] = tc_id
        tc["type"] = "function"
    return "data: " + json.dumps(
        {"choices": [{"delta": {"tool_calls": [tc]}, "index": 0}]}
    )


def _payload_of(line: str) -> dict:
    return json.loads(line[len("data: ") :])


class TestToolCallAccumulator(unittest.TestCase):
    def test_argomenti_frammentati_concatenati_per_index(self) -> None:
        acc = ToolCallAccumulator()
        # due tool call parallele, argomenti spezzati su piu' chunk
        acc.feed(_payload_of(_tc_chunk(0, '{"a":', name="search", tc_id="call_0")))
        acc.feed(_payload_of(_tc_chunk(1, '{"b":', name="fetch", tc_id="call_1")))
        acc.feed(_payload_of(_tc_chunk(0, " 1}")))
        acc.feed(_payload_of(_tc_chunk(1, " 2}")))
        calls = acc.final_tool_calls()
        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[0]["function"]["arguments"], {"a": 1})
        self.assertEqual(calls[1]["function"]["arguments"], {"b": 2})
        self.assertEqual(calls[0]["id"], "call_0")
        self.assertEqual(calls[0]["function"]["name"], "search")

    def test_nessun_parsing_su_chunk_singolo(self) -> None:
        acc = ToolCallAccumulator()
        # JSON parziale volutamente invalido nei primi chunk: feed non deve mai
        # sollevare; il parsing avviene solo a stream terminato (3 frammenti)
        acc.feed(_payload_of(_tc_chunk(0, '{"nested":', tc_id="c")))
        acc.feed(_payload_of(_tc_chunk(0, ' {"k":')))
        acc.feed(_payload_of(_tc_chunk(0, " 1}}")))
        self.assertEqual(acc.parse_count, 0)  # nulla parsato durante il feed
        calls = acc.final_tool_calls()
        self.assertEqual(calls[0]["function"]["arguments"], {"nested": {"k": 1}})
        self.assertEqual(acc.parse_count, 1)  # un solo parsing, a fine stream

    def test_usato_dal_backend_streaming(self) -> None:
        lines = [
            _tc_chunk(0, '{"x": 1}', name="tool", tc_id="call_0"),
            "data: " + json.dumps({"choices": [{"delta": {"content": "testo"}}]}),
            "data: [DONE]",
        ]
        resp = accumulate_stream(lines, "m", "p")
        self.assertEqual(str(resp), "testo")
        self.assertEqual(resp.tool_calls[0]["function"]["arguments"], {"x": 1})  # type: ignore[attr-defined]


if __name__ == "__main__":
    unittest.main()

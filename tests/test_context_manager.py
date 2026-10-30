"""Contratto P1 (ToDo 2026-10-28, doc QwenCloud multi-turn): ContextManager.

L'API e' stateless: il client mantiene l'array messages applicando tre
strategie — tenere gli ultimi N turni (troncamento), rolling summary a soglia
(~70% del contesto), retrieval on-demand. SystemTwoEngine.execute e' oggi
single-shot: il modulo fissa la rappresentazione di conversazione entro
max_context_tokens del profilo.
"""

from __future__ import annotations

import unittest

from context_manager import ContextManager, estimate_message_tokens


def _turns(n: int, size: int = 100) -> list[dict[str, str]]:
    msgs = [{"role": "system", "content": "sei HAL"}]
    for i in range(n):
        filler = "x" * size
        msgs.append({"role": "user", "content": f"domanda {i} {filler}"})
        msgs.append({"role": "assistant", "content": f"risposta {i} {filler}"})
    return msgs


class TestTruncation(unittest.TestCase):
    def test_tiene_gli_ultimi_turni_entro_budget(self) -> None:
        cm = ContextManager(max_context_tokens=120, keep_recent_turns=2)
        out = cm.compact(_turns(10))
        self.assertLessEqual(estimate_message_tokens(out), 120)
        joined = " ".join(m["content"] for m in out)
        self.assertIn("domanda 9", joined)
        self.assertNotIn("domanda 0", joined)

    def test_system_sempre_presente(self) -> None:
        cm = ContextManager(max_context_tokens=60, keep_recent_turns=1)
        out = cm.compact(_turns(10))
        self.assertEqual(out[0]["role"], "system")
        self.assertEqual(out[0]["content"], "sei HAL")

    def test_sotto_budget_invariato(self) -> None:
        msgs = _turns(1)
        cm = ContextManager(max_context_tokens=10_000)
        self.assertEqual(cm.compact(msgs), msgs)


class TestRollingSummary(unittest.TestCase):
    def test_summary_a_soglia_70_percento(self) -> None:
        calls: list[list[dict[str, str]]] = []

        def fake_summarizer(old: list[dict[str, str]]) -> str:
            calls.append(old)
            return "stub: " + old[0]["content"][:20]

        budget = 250
        cm = ContextManager(
            max_context_tokens=budget,
            keep_recent_turns=2,
            summarizer=fake_summarizer,
        )
        # conversazione sopra soglia (~70%) e sopra budget: compatta con summary
        out = cm.compact(_turns(4))
        self.assertEqual(len(calls), 1)
        self.assertEqual(out[1]["role"], "system")
        self.assertTrue(out[1]["content"].startswith("Riepilogo"))
        self.assertIn("stub:", out[1]["content"])
        self.assertLessEqual(estimate_message_tokens(out), budget)
        joined = " ".join(m["content"] for m in out)
        self.assertIn("domanda 3", joined)

    def test_senza_summarizer_cade_su_troncamento(self) -> None:
        budget = 120
        cm = ContextManager(max_context_tokens=budget, keep_recent_turns=2)
        out = cm.compact(_turns(6))
        self.assertLessEqual(estimate_message_tokens(out), budget)
        self.assertNotIn("Riepilogo", out[1]["content"])


class TestRetrieval(unittest.TestCase):
    def test_retrieval_on_demand_entro_budget(self) -> None:
        corpus = {"fix": ["nota lunga " + "y" * 400]}
        cm = ContextManager(
            max_context_tokens=300,
            keep_recent_turns=2,
            retriever=lambda q: corpus.get(q, []),
        )
        out = cm.compact(_turns(3), query="fix")
        self.assertLessEqual(estimate_message_tokens(out), 300)
        roles = [m["role"] for m in out]
        self.assertIn("system", roles)
        # il contesto recuperato precede la conversazione trattenuta
        context_msgs = [m for m in out if "nota lunga" in m["content"]]
        self.assertEqual(len(context_msgs), 1)
        history_start = next(
            i for i, m in enumerate(out) if m["content"].startswith("domanda")
        )
        self.assertLess(out.index(context_msgs[0]), history_start)

    def test_retriever_assente_nessun_blocco(self) -> None:
        cm = ContextManager(max_context_tokens=5_000, keep_recent_turns=2)
        out = cm.compact(_turns(2), query="fix")
        self.assertNotIn("nota lunga", " ".join(m["content"] for m in out))


class TestReasoningContentFilter(unittest.TestCase):
    def test_reasoning_content_eliminato_nella_ricostruzione(self) -> None:
        msgs = [
            {"role": "system", "content": "sei HAL"},
            {"role": "user", "content": "ciao"},
            {
                "role": "assistant",
                "content": "risposta",
                "reasoning_content": "pensiero lungo " + "z" * 300,
            },
        ]
        cm = ContextManager(max_context_tokens=5_000)
        out = cm.compact(msgs)
        self.assertTrue(all("reasoning_content" not in m for m in out))
        self.assertIn("risposta", out[-1]["content"])
        self.assertNotIn("pensiero", out[-1]["content"])

    def test_estima_non_conta_reasoning(self) -> None:
        with_thoughts = [
            {"role": "user", "content": "a", "reasoning_content": "b" * 800}
        ]
        plain = [{"role": "user", "content": "a"}]
        self.assertEqual(
            estimate_message_tokens(with_thoughts),
            estimate_message_tokens(plain),
        )


class TestToolMessageMerge(unittest.TestCase):
    def test_tool_consecutivi_fusi_in_un_messaggio_con_blocci(self) -> None:
        msgs = [
            {"role": "system", "content": "sei HAL"},
            {"role": "user", "content": "parallele"},
            {
                "role": "assistant",
                "content": "",
                "tool_calls": [{"id": "1"}, {"id": "2"}, {"id": "3"}],
            },
            {"role": "tool", "tool_call_id": "1", "content": "risultato uno"},
            {"role": "tool", "tool_call_id": "2", "content": "risultato due"},
            {"role": "tool", "tool_call_id": "3", "content": "risultato tre"},
        ]
        cm = ContextManager(max_context_tokens=5_000)
        out = cm.compact(msgs)
        tool_msgs = [m for m in out if m.get("role") == "tool"]
        self.assertEqual(len(tool_msgs), 1)
        blocks = tool_msgs[0]["content"]
        self.assertIsInstance(blocks, list)
        self.assertEqual(len(blocks), 3)
        self.assertEqual([b["tool_call_id"] for b in blocks], ["1", "2", "3"])
        self.assertTrue(all(b["type"] == "text" for b in blocks))

    def test_merge_riduce_i_blocchi_content(self) -> None:
        # il doc QwenCloud: troppi block tool consecutivi sforano il lookback
        # di 20 content block dal marker; il merge li comprime in un messaggio
        msgs = [
            {"role": "system", "content": "s"},
            *[
                {"role": "tool", "tool_call_id": str(i), "content": f"r{i}"}
                for i in range(30)
            ],
        ]
        cm = ContextManager(max_context_tokens=5_000)
        out = cm.compact(msgs)
        self.assertEqual(len([m for m in out if m.get("role") == "tool"]), 1)

    def test_tool_non_consecutivi_non_fusi(self) -> None:
        msgs = [
            {"role": "tool", "tool_call_id": "1", "content": "a"},
            {"role": "assistant", "content": " pausa "},
            {"role": "tool", "tool_call_id": "2", "content": "b"},
        ]
        cm = ContextManager(max_context_tokens=5_000)
        out = cm.compact(msgs)
        self.assertEqual(len([m for m in out if m.get("role") == "tool"]), 2)


if __name__ == "__main__":
    unittest.main()

"""Contratto P2 (ToDo 2026-10-28, voce System prompt come instructions).

normalize_prompt appiattiva i messaggi perdendo i ruoli e mischia il system
prompt nel transcript: il system entra così sia nell'hash sia nella parte
append-only, e non è possibile riusare il transcript con system diversi. Qui
system e transcript viaggiano separati con ruolo esplicito; lo stesso
transcript con system diverso deve produrre chiavi diverse. Include il
contrato di ordering static-first (lato code della voce P1 ordering).
"""

from __future__ import annotations

import unittest

from gateway_core import (
    L1RedisCacheManager,
    assemble_static_first_blocks,
    compute_cache_key,
    normalize_prompt,
)

TRANSCRIPT = [
    {"role": "user", "content": "spiega il bug"},
    {"role": "assistant", "content": "eccolo"},
]


class TestSystemSeparated(unittest.TestCase):
    def test_stesso_transcript_system_diverso_chiavi_diverse(self) -> None:
        key_a = compute_cache_key("s1", "coding", TRANSCRIPT, instructions="sei HAL")
        key_b = compute_cache_key("s1", "coding", TRANSCRIPT, instructions="sei altro")
        self.assertNotEqual(key_a, key_b)

    def test_system_non_entra_nel_transcript(self) -> None:
        with_msgs = [{"role": "system", "content": "sei HAL"}] + TRANSCRIPT
        via_instructions = normalize_prompt(with_msgs)
        explicit = normalize_prompt(TRANSCRIPT, instructions="sei HAL")
        self.assertEqual(via_instructions, explicit)
        # la parte transcript da sola non contiene il system
        transcript_only = normalize_prompt(TRANSCRIPT)
        self.assertNotIn("sei hal", transcript_only)

    def test_ruoli_preservati(self) -> None:
        user = normalize_prompt([{"role": "user", "content": "ciao"}])
        assistant = normalize_prompt([{"role": "assistant", "content": "ciao"}])
        self.assertNotEqual(user, assistant)

    def test_content_based_key_riflette_instructions(self) -> None:
        mgr = L1RedisCacheManager(backend="memory")
        key_a = mgr.compute_content_based_cache_key(
            "s1", "coding", TRANSCRIPT, [], instructions="A"
        )
        key_b = mgr.compute_content_based_cache_key(
            "s1", "coding", TRANSCRIPT, [], instructions="B"
        )
        self.assertNotEqual(key_a, key_b)


class TestStaticFirstOrdering(unittest.TestCase):
    def test_ordine_blocchi_fisso(self) -> None:
        blocks = assemble_static_first_blocks(
            instructions="sei HAL",
            declarations=[{"name": "fetch"}],
            context_files=["docs/x.md"],
            transcript=TRANSCRIPT,
            current_question={"role": "user", "content": "domanda"},
        )
        kinds = [b["block"] for b in blocks]
        self.assertEqual(
            kinds, ["system", "declarations", "context", "history", "question"]
        )

    def test_volatile_non_in_testa(self) -> None:
        blocks = assemble_static_first_blocks(
            instructions="sei HAL",
            declarations=[],
            context_files=[],
            transcript=TRANSCRIPT,
            current_question={"role": "user", "content": "q"},
            volatile={"session_id": "abc", "timestamp": "2026-10-28T00:00:00Z"},
        )
        self.assertEqual(blocks[0]["block"], "system")
        self.assertNotIn("session_id", str(blocks[0]))
        vol_index = next(i for i, b in enumerate(blocks) if b["block"] == "volatile")
        self.assertGreater(vol_index, 0)


if __name__ == "__main__":
    unittest.main()

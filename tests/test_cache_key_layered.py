"""Contratto P1 (ToDo 2026-10-28): chiave Cache L1 a due livelli.

La chiave esatta sull'intera richiesta invalida tutta la voce a ogni append
(skill iniettata, nuovo turno). Il livello prefix (system + tool core + primi
turni dichiarati stabili) deve restare invariato su append; il suffisso
assorisce il resto. Rispecchia il riuso parziale del prefix caching provider.
"""

from __future__ import annotations

import unittest

from gateway_core import L1RedisCacheManager, compute_layered_cache_key


class TestLayeredCacheKey(unittest.TestCase):
    def setUp(self) -> None:
        self.cache_mgr = L1RedisCacheManager(backend="memory")
        self.system = [{"role": "system", "content": "sei HAL"}]
        self.first_turn = self.system + [{"role": "user", "content": "ciao"}]

    def test_append_messaggio_non_invalida_prefix(self) -> None:
        k1 = compute_layered_cache_key("s1", "coding", self.first_turn)
        appended = self.first_turn + [
            {"role": "assistant", "content": "ok"},
            {"role": "user", "content": "e poi?"},
        ]
        k2 = compute_layered_cache_key("s1", "coding", appended)
        self.assertEqual(k1["prefix"], k2["prefix"])
        self.assertNotEqual(k1["full"], k2["full"])

    def test_append_dichiarazione_non_invalida_prefix(self) -> None:
        stable = [{"name": "fetch"}]
        k1 = compute_layered_cache_key(
            "s1",
            "coding",
            self.first_turn,
            declarations=stable,
            stable_declarations=stable,
        )
        injected = stable + [{"name": "skill_extra"}]
        k2 = compute_layered_cache_key(
            "s1",
            "coding",
            self.first_turn,
            declarations=injected,
            stable_declarations=stable,
        )
        self.assertEqual(k1["prefix"], k2["prefix"])
        self.assertNotEqual(k1["full"], k2["full"])

    def test_stable_turns_entra_nel_prefix(self) -> None:
        conv = self.first_turn + [{"role": "assistant", "content": "ok"}]
        k0 = compute_layered_cache_key("s1", "coding", conv, stable_turns=0)
        k1 = compute_layered_cache_key("s1", "coding", conv, stable_turns=1)
        self.assertNotEqual(k0["prefix"], k1["prefix"])

    def test_chiavi_distinte_per_sessione_e_use_case(self) -> None:
        a = compute_layered_cache_key("s1", "coding", self.first_turn)
        b = compute_layered_cache_key("s2", "coding", self.first_turn)
        c = compute_layered_cache_key("s1", "summarization", self.first_turn)
        self.assertEqual(a["prefix"], b["prefix"].replace("s2", "s1"))
        self.assertNotEqual(a["prefix"], b["prefix"])
        self.assertNotEqual(a["prefix"], c["prefix"])


class TestLayeredManager(unittest.TestCase):
    def setUp(self) -> None:
        self.cache_mgr = L1RedisCacheManager(backend="memory")
        self.messages = [
            {"role": "system", "content": "sei HAL"},
            {"role": "user", "content": "ciao"},
        ]

    def test_voce_originale_non_invalidata_dall_append(self) -> None:
        self.cache_mgr.set_layered("s1", "coding", self.messages, "risposta-1")
        appended = self.messages + [{"role": "user", "content": "grazie"}]
        self.cache_mgr.set_layered("s1", "coding", appended, "risposta-2")

        resp, state, prefix_state = self.cache_mgr.get_layered(
            "s1", "coding", self.messages
        )
        self.assertEqual((resp, state), ("risposta-1", "cache_hit"))
        self.assertEqual(prefix_state, "prefix_hit")

        resp2, state2, prefix_state2 = self.cache_mgr.get_layered(
            "s1", "coding", appended
        )
        self.assertEqual((resp2, state2), ("risposta-2", "cache_hit"))
        self.assertEqual(prefix_state2, "prefix_hit")

    def test_prefix_info_su_full_miss(self) -> None:
        self.cache_mgr.set_layered("s1", "coding", self.messages, "risposta-1")
        extended = self.messages + [{"role": "user", "content": "nuovo turno"}]
        resp, state, prefix_state = self.cache_mgr.get_layered("s1", "coding", extended)
        self.assertEqual((resp, state), (None, "cache_miss"))
        self.assertEqual(prefix_state, "prefix_hit")


if __name__ == "__main__":
    unittest.main()

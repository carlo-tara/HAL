"""Contratto P0 (ToDo 2026-10-28): dichiarazioni tool/skill nella chiave Cache L1.

normalize_prompt/compute_cache_key hashavano solo il campo `content`: due
richieste con stesso testo ma tool set diverso condividevano la chiave,
producendo falsi hit con risposta potenzialmente errata. Qui si fissa che le
dichiarazioni (tools, skill, tool_calls nei messaggi) entrano nella chiave.
"""

from __future__ import annotations

import unittest

from gateway_core import (
    L1RedisCacheManager,
    compute_cache_key,
    normalize_prompt,
)


class TestCacheKeyIncludesDeclarations(unittest.TestCase):
    def setUp(self) -> None:
        self.cache_mgr = L1RedisCacheManager(backend="memory")

    # -- compute_cache_key (chiave Redis L1) --------------------------------

    def test_stesso_testo_tool_diversi_chiavi_diverse(self) -> None:
        messages = [{"role": "user", "content": "genera il report"}]
        key_a = compute_cache_key(
            "s1", "coding", messages, declarations=[{"name": "fetch"}]
        )
        key_b = compute_cache_key(
            "s1", "coding", messages, declarations=[{"name": "search"}]
        )
        self.assertNotEqual(key_a, key_b)

    def test_dichiarazioni_assenti_vs_empty_stesso_hash(self) -> None:
        messages = [{"role": "user", "content": "ciao"}]
        key_none = compute_cache_key("s1", "coding", messages)
        key_empty = compute_cache_key("s1", "coding", messages, declarations=[])
        self.assertEqual(key_none, key_empty)

    def test_deterministico_indipendente_dallordine(self) -> None:
        messages = [{"role": "user", "content": "ciao"}]
        key_a = compute_cache_key(
            "s1",
            "coding",
            messages,
            declarations=[{"name": "beta"}, {"name": "alpha"}],
        )
        key_b = compute_cache_key(
            "s1",
            "coding",
            messages,
            declarations=[{"name": "alpha"}, {"name": "beta"}],
        )
        self.assertEqual(key_a, key_b)

    def test_skill_entry_nella_chiave(self) -> None:
        messages = [{"role": "user", "content": "ciao"}]
        key_a = compute_cache_key("s1", "coding", messages, declarations=["skill:a"])
        key_b = compute_cache_key("s1", "coding", messages, declarations=["skill:b"])
        self.assertNotEqual(key_a, key_b)

    # -- normalize_prompt ----------------------------------------------------

    def test_tool_calls_nei_messaggi_cambiano_la_normalizzazione(self) -> None:
        plain = [{"role": "assistant", "content": "ok"}]
        with_call = [
            {
                "role": "assistant",
                "content": "ok",
                "tool_calls": [{"id": "t1", "name": "fetch"}],
            }
        ]
        self.assertNotEqual(normalize_prompt(plain), normalize_prompt(with_call))

    # -- flusso get/set end-to-end -------------------------------------------

    def test_falso_hit_tra_tool_set_diversi(self) -> None:
        messages = [{"role": "user", "content": "stesso testo"}]
        self.cache_mgr.set(
            "s1",
            "coding",
            messages,
            "risposta-tools-A",
            declarations=[{"name": "tool_a"}],
        )
        hit_a, state_a = self.cache_mgr.get(
            "s1", "coding", messages, declarations=[{"name": "tool_a"}]
        )
        hit_b, state_b = self.cache_mgr.get(
            "s1", "coding", messages, declarations=[{"name": "tool_b"}]
        )
        self.assertEqual((hit_a, state_a), ("risposta-tools-A", "cache_hit"))
        self.assertEqual((hit_b, state_b), (None, "cache_miss"))

    def test_content_based_key_riflette_dichiarazioni(self) -> None:
        messages = [{"role": "user", "content": "x"}]
        key_a = self.cache_mgr.compute_content_based_cache_key(
            "s1", "coding", messages, [], declarations=[{"name": "tool_a"}]
        )
        key_b = self.cache_mgr.compute_content_based_cache_key(
            "s1", "coding", messages, [], declarations=[{"name": "tool_b"}]
        )
        self.assertNotEqual(key_a, key_b)


if __name__ == "__main__":
    unittest.main()

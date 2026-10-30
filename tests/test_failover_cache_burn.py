"""Contratto P2 (ToDo 2026-10-28, voce costo di refill nel failover):

la cache è isolata per modello oltre che per account: quando il breaker o il
fallback cambiano modello a sessione invariata, il prefisso riparte da zero e
la ricreazione costa 125%. Il costo del failover non è solo latenza: va
marcato come evento/metrica con il costo di creazione atteso.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from gateway_core import record_failover_cache_burn


class TestCacheBurnEvent(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.log = Path(self.tmp.name) / "events.jsonl"

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_evento_marca_cambio_modello_a_sessione_invariata(self) -> None:
        burn = record_failover_cache_burn(
            session_id="sess-abc",
            from_model="qwen/qwen3.8-flash",
            to_model="deepseek/deepseek-v4.1-flash",
            prompt_tokens=1000,
            log_path=self.log,
        )
        self.assertEqual(burn["event"], "cache_refill")
        self.assertEqual(burn["session_id"], "sess-abc")
        self.assertTrue(burn["session_unchanged"])
        self.assertEqual(burn["from_model"], "qwen/qwen3.8-flash")
        self.assertEqual(burn["to_model"], "deepseek/deepseek-v4.1-flash")
        # costo atteso: prefisso da ricostruire a 125%
        self.assertEqual(burn["expected_creation_cost"], 1250.0)
        self.assertEqual(burn["prompt_tokens"], 1000)

    def test_persistenza_nel_log_eventi(self) -> None:
        record_failover_cache_burn(
            session_id="s",
            from_model="a",
            to_model="b",
            prompt_tokens=400,
            log_path=self.log,
        )
        line = self.log.read_text(encoding="utf-8").strip()
        record = json.loads(line)
        self.assertEqual(record["event"], "cache_refill")

    def test_modello_identico_nessun_burn(self) -> None:
        burn = record_failover_cache_burn(
            session_id="s",
            from_model="qwen/qwen3.8-flash",
            to_model="qwen/qwen3.8-flash",
            prompt_tokens=1000,
            log_path=self.log,
        )
        self.assertIsNone(burn["expected_creation_cost"])
        self.assertFalse(burn["cache_invalidated"])

    def test_ratio_custom(self) -> None:
        burn = record_failover_cache_burn(
            session_id="s",
            from_model="a",
            to_model="b",
            prompt_tokens=100,
            log_path=self.log,
            creation_ratio=1.0,
        )
        self.assertEqual(burn["expected_creation_cost"], 100.0)


if __name__ == "__main__":
    unittest.main()

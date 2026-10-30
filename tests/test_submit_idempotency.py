"""Contratto P1 (ToDo 2026-10-28, doc QwenCloud async-task §duplicate work):

ogni POST crea un nuovo task anche con parametri identici; un retry di submit
fallito (rete, switching tra provider) può ri-creare lo stesso task pagandolo
due volte. Il registro mappa richiesta -> task_id in-flight con la chiave
``cache:v1:...`` come idempotency key: submit identico entro la finestra non
crea un nuovo task e restituisce il task_id esistente.
"""

from __future__ import annotations

import unittest

from gateway_core import SubmitIdempotencyRegistry, compute_cache_key


class TestSubmitIdempotencyRegistry(unittest.TestCase):
    def setUp(self) -> None:
        self.registry = SubmitIdempotencyRegistry(window_s=60.0)
        self.calls = 0

    def _submit(self) -> str:
        self.calls += 1
        return f"task-{self.calls}"

    def test_doppio_submit_stessa_richiesta_un_solo_task(self) -> None:
        key = compute_cache_key("s1", "coding", [{"role": "user", "content": "x"}])
        first = self.registry.submit_once(key, self._submit, now=100.0)
        second = self.registry.submit_once(key, self._submit, now=120.0)
        self.assertEqual(first, second)
        self.assertEqual(self.calls, 1)

    def test_fuori_dalla_finestra_nuovo_task(self) -> None:
        key = compute_cache_key("s1", "coding", [{"role": "user", "content": "x"}])
        self.registry.submit_once(key, self._submit, now=100.0)
        later = self.registry.submit_once(key, self._submit, now=200.0)
        self.assertEqual(later, "task-2")
        self.assertEqual(self.calls, 2)

    def test_richieste_diverse_task_diversi(self) -> None:
        key_a = compute_cache_key("s1", "coding", [{"role": "user", "content": "a"}])
        key_b = compute_cache_key("s1", "coding", [{"role": "user", "content": "b"}])
        self.assertNotEqual(
            self.registry.submit_once(key_a, self._submit, now=100.0),
            self.registry.submit_once(key_b, self._submit, now=100.0),
        )
        self.assertEqual(self.calls, 2)

    def test_lookup_esistente_senza_submit(self) -> None:
        key = compute_cache_key("s1", "coding", [{"role": "user", "content": "x"}])
        self.registry.submit_once(key, self._submit, now=100.0)
        self.assertEqual(self.registry.get_task_id(key, now=130.0), "task-1")
        self.assertIsNone(self.registry.get_task_id(key, now=500.0))

    def test_dichiarazioni_partecipano_alla_chiave(self) -> None:
        messages = [{"role": "user", "content": "x"}]
        key_a = compute_cache_key(
            "s1", "coding", messages, declarations=[{"name": "a"}]
        )
        key_b = compute_cache_key(
            "s1", "coding", messages, declarations=[{"name": "b"}]
        )
        self.registry.submit_once(key_a, self._submit, now=100.0)
        self.registry.submit_once(key_b, self._submit, now=100.0)
        self.assertEqual(self.calls, 2)


if __name__ == "__main__":
    unittest.main()

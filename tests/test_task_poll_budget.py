"""Contratto P2 (ToDo 2026-10-28, doc QwenCloud §async management):

query, list e cancel condividono 20 QPS per account e il doc prescrive di
batchare i check di stato quando i task concorrenti sono molti, con
``Throttling.RateQuota`` come segnale di ridurre la frequenza / aumentare
l'intervallo. HAL ha CircuitBreaker e LayaCallBudget ma nessun budget di
frequenza sui poll LLM: molti polling paralleli saturerebbero il limite.
"""

from __future__ import annotations

import unittest

from gateway_core import TaskPollBudget


class TestTaskPollBudget(unittest.TestCase):
    def test_restsotto_il_limit_concorrente(self) -> None:
        budget = TaskPollBudget(rate_per_s=20.0)
        now = 1000.0
        granted = sum(1 for _ in range(40) if budget.acquire(now=now))
        self.assertEqual(granted, 20)

    def test_il_bucket_si_ricarica(self) -> None:
        budget = TaskPollBudget(rate_per_s=20.0)
        self.assertTrue(budget.acquire(now=1000.0))
        # esauro il bucket nello stesso istante
        while budget.acquire(now=1000.0):
            pass
        # dopo un secondo il refill consente altri 20 poll
        granted = sum(1 for _ in range(20) if budget.acquire(now=1001.0))
        self.assertEqual(granted, 20)
        self.assertFalse(budget.acquire(now=1001.0))

    def test_attesa_al_slot_successivo(self) -> None:
        budget = TaskPollBudget(rate_per_s=20.0)
        budget.drain(now=1000.0)
        self.assertAlmostEqual(budget.wait_time(now=1000.0), 0.05, places=2)

    def test_throttling_aumenta_l_intervallo(self) -> None:
        budget = TaskPollBudget(rate_per_s=20.0, base_interval=3.0, max_interval=15.0)
        i0 = budget.poll_interval()
        budget.note_throttled()  # 429 / Throttling.RateQuota
        i1 = budget.poll_interval()
        self.assertAlmostEqual(i1, i0 * 1.5)
        budget.note_throttled()
        budget.note_throttled()
        self.assertLessEqual(budget.poll_interval(), 15.0)

    def test_successo_ripristina_l_intervallo_base(self) -> None:
        budget = TaskPollBudget(rate_per_s=20.0, base_interval=3.0)
        budget.note_throttled()
        budget.note_success()
        self.assertEqual(budget.poll_interval(), 3.0)

    def test_validazione_parametri(self) -> None:
        with self.assertRaises(ValueError):
            TaskPollBudget(rate_per_s=0)
        with self.assertRaises(ValueError):
            TaskPollBudget(rate_per_s=20, base_interval=20, max_interval=10)


if __name__ == "__main__":
    unittest.main()

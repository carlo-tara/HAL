"""Contratto P1 (ToDo 2026-10-28, doc QwenCloud §Production checklist): retry
Laya con exponential backoff e jitter.

Il loop di ``_call`` ritentava senza alcuna attesa (``continue`` stretto): con
Laya degradata il gateway la martella e amplifica l'incidente. Il budget
limita il numero di tentativi, non ne distanzia il timing.
"""

from __future__ import annotations

import unittest
from unittest.mock import Mock, patch

import requests

from laya_service import LayaSystemOneService, compute_backoff_delay
from system1_preflight import LayaCallBudget


class _RetryablePost:
    """Fa fallire i primi ``failures`` POST con Timeout, poi risponde ok."""

    def __init__(self, failures: int) -> None:
        self.calls = 0
        self.failures = failures

    def __call__(self, *args, **kwargs):
        self.calls += 1
        if self.calls <= self.failures:
            raise requests.exceptions.Timeout("connect timeout")
        response = Mock()
        response.status_code = 200
        response.raise_for_status = Mock()
        response.json = Mock(return_value={"result": {"choice": "ok"}})
        return response


class TestComputeBackoffDelay(unittest.TestCase):
    def test_crescita_esponenziale_con_cap(self) -> None:
        d0 = compute_backoff_delay(0, base=0.3, cap=4.0, rng=lambda frac: 1.0)
        d1 = compute_backoff_delay(1, base=0.3, cap=4.0, rng=lambda frac: 1.0)
        d2 = compute_backoff_delay(2, base=0.3, cap=4.0, rng=lambda frac: 1.0)
        self.assertAlmostEqual(d0, 0.3)
        self.assertAlmostEqual(d1, 0.6)
        self.assertAlmostEqual(d2, 1.2)
        big = compute_backoff_delay(30, base=0.3, cap=4.0, rng=lambda frac: 1.0)
        self.assertAlmostEqual(big, 4.0)

    def test_jitter_presente_e_positivo(self) -> None:
        delays = [compute_backoff_delay(1, base=0.3, cap=4.0) for _ in range(50)]
        self.assertTrue(all(0.0 < d <= 4.0 for d in delays))
        self.assertGreater(len(set(delays)), 1)


class TestRetrySpacing(unittest.TestCase):
    def test_tentativi_distanziati_entro_budget(self) -> None:
        post = _RetryablePost(failures=1)
        sleeps: list[float] = []
        budget = LayaCallBudget(max_calls=2, max_retries=1, retry_reason="transient")
        with patch("laya_service._session.post", side_effect=post), patch(
            "laya_service._sleep", side_effect=sleeps.append
        ), LayaSystemOneService.budget(budget):
            result = LayaSystemOneService._call({"op": "routing"})
        self.assertEqual(result, {"choice": "ok"})
        self.assertEqual(post.calls, 2)
        self.assertEqual(len(sleeps), 1)
        self.assertGreater(sleeps[0], 0.0)

    def test_nessun_retry_oltre_il_budget(self) -> None:
        post = _RetryablePost(failures=10)
        sleeps: list[float] = []
        with (
            patch("laya_service._session.post", side_effect=post),
            patch("laya_service._sleep", side_effect=sleeps.append),
            self.assertRaises(Exception) as ctx,
        ):
            LayaSystemOneService._call({"op": "routing"})
        self.assertIn("unavailable", str(ctx.exception))
        self.assertEqual(post.calls, 1)
        self.assertEqual(sleeps, [])


if __name__ == "__main__":
    unittest.main()

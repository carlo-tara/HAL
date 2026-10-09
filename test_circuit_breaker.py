import time  # noqa: I001
import unittest

from gateway_core import CircuitBreaker, ProviderResolverWithBreaker

class TestCircuitBreakerIntegration(unittest.TestCase):
    def test_breaker_states_and_single_probe(self) -> None:
        cb = CircuitBreaker(provider_name="test-provider", failure_threshold=2, open_s=1)
        self.assertEqual(cb.state, "CLOSED")
        self.assertTrue(cb.allow_request(time.time()))

        # Record failures to open breaker
        now = time.time()
        cb.record_failure(now)
        cb.record_failure(now)
        self.assertEqual(cb.state, "OPEN")

        # Request while open -> rejected
        self.assertFalse(cb.allow_request(now + 0.5))

        # Time passes beyond open_s -> transitions to HALF-OPEN
        probe_time = now + 1.5
        self.assertTrue(cb.allow_request(probe_time))
        self.assertEqual(cb.state, "HALF-OPEN")

        # Second concurrent probe in HALF-OPEN should be blocked to prevent flooding
        self.assertFalse(cb.allow_request(probe_time))

    def test_resolver_skips_open_and_falls_back(self) -> None:
        resolver = ProviderResolverWithBreaker()
        resolver.register_provider("primary", lambda t, d: "primary-res")
        resolver.register_provider("fallback", lambda t, d: "fallback-res")

        # Force primary breaker open
        cb_primary = resolver.get_breaker("primary")
        self.assertIsNotNone(cb_primary)
        assert cb_primary is not None
        now = time.time()
        cb_primary.record_failure(now)
        cb_primary.record_failure(now)
        self.assertEqual(cb_primary.state, "OPEN")

        # Resolve request -> should skip primary and use fallback
        res, provider_used = resolver.resolve_and_execute("coding", "test data")
        self.assertEqual(res, "fallback-res")
        self.assertEqual(provider_used, "fallback")

if __name__ == "__main__":
    unittest.main()

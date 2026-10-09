import unittest  # noqa
from global_config import SystemEvaluationEngine

class TestSystemEvaluationEngine(unittest.TestCase):
    def test_offline_replay(self) -> None:
        requests = [
            {"task": "summarization", "text": "test content 1", "expected_outcome": "success"},
            {"task": "coding", "text": "def foo(): pass", "expected_outcome": "success"},
            {"task": "text_editing", "text": "edit text", "expected_outcome": "success"}
        ]
        candidate_config = {"model": "orcarouter/deepseek/deepseek-v4.1-flash", "profile": "coding"}
        metrics = SystemEvaluationEngine.replay(requests, candidate_config)

        self.assertEqual(metrics["total_requests"], 3)
        self.assertIn("success_rate", metrics)
        self.assertIn("avg_latency_ms", metrics)
        self.assertIn("estimated_cost", metrics)
        self.assertEqual(metrics["success_rate"], 1.0)

    def test_shadow_evaluation(self) -> None:
        primary = {"response": "Hello world", "latency_ms": 120}
        shadow = {"response": "Hello world (shadow)", "latency_ms": 110}
        comparison = SystemEvaluationEngine.shadow_evaluate(primary, shadow)

        self.assertIn("match", comparison)
        self.assertIn("latency_delta_ms", comparison)
        self.assertEqual(comparison["latency_delta_ms"], -10)

    def test_promotion_gate_and_rollback(self) -> None:
        good_metrics = {"success_rate": 0.99, "error_rate": 0.01, "avg_latency_ms": 150}
        thresholds = {"min_success_rate": 0.95, "max_error_rate": 0.05, "max_latency_ms": 500}

        passed, reason = SystemEvaluationEngine.promote_with_rollback(good_metrics, thresholds)
        self.assertTrue(passed)
        self.assertEqual(reason, "Gate passed successfully")

        bad_metrics = {"success_rate": 0.85, "error_rate": 0.15, "avg_latency_ms": 600}
        passed_fail, reason_fail = SystemEvaluationEngine.promote_with_rollback(bad_metrics, thresholds)
        self.assertFalse(passed_fail)
        self.assertIn("Rollback triggered", reason_fail)

if __name__ == "__main__":
    unittest.main()

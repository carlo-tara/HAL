import unittest  # noqa
from global_config import SystemEvaluationEngine


class TestSystemEvaluationEngine(unittest.TestCase):
    def test_offline_replay(self) -> None:
        requests = [
            {
                "task": "summarization",
                "text": "test content 1",
                "expected_outcome": "success",
            },
            {
                "task": "coding",
                "text": "def foo(): pass",
                "expected_outcome": "success",
            },
            {
                "task": "text_editing",
                "text": "edit text",
                "expected_outcome": "success",
            },
        ]
        candidate_config = {
            "model": "orcarouter/deepseek/deepseek-v4.1-flash",
            "profile": "coding",
        }
        metrics = SystemEvaluationEngine.replay(requests, candidate_config)

        self.assertEqual(metrics["total_requests"], 3)
        self.assertIn("success_rate", metrics)
        self.assertIn("avg_latency_ms", metrics)
        self.assertIn("estimated_cost", metrics)
        self.assertEqual(metrics["success_rate"], 1.0)
        self.assertEqual(metrics["error_rate"], 0.0)
        self.assertEqual(metrics["latency_samples"], 0)
        self.assertEqual(metrics["cost_samples"], 0)
        self.assertEqual(metrics["avg_latency_ms"], 0.0)
        self.assertEqual(metrics["estimated_cost"], 0)

    def test_replay_aggregates_measured_metrics_without_prompt_content(self) -> None:
        requests = [
            {
                "text": "private prompt",
                "expected_outcome": "success",
                "latency_ms": 100,
                "estimated_cost": 0.02,
            },
            {
                "text": "another private prompt",
                "expected_outcome": "error",
                "latency_ms": 300,
                "estimated_cost": 0.03,
            },
            {
                "expected_outcome": "success",
                "latency_ms": float("nan"),
                "estimated_cost": "unknown",
            },
        ]

        metrics = SystemEvaluationEngine.replay(requests, {"model": "candidate"})

        self.assertEqual(metrics["total_requests"], 3)
        self.assertEqual(metrics["successes"], 2)
        self.assertAlmostEqual(metrics["success_rate"], 2 / 3)
        self.assertAlmostEqual(metrics["error_rate"], 1 / 3)
        self.assertEqual(metrics["avg_latency_ms"], 200)
        self.assertEqual(metrics["latency_samples"], 2)
        self.assertEqual(metrics["estimated_cost"], 0.05)
        self.assertEqual(metrics["cost_samples"], 2)
        self.assertNotIn("text", metrics)

    def test_replay_uses_benchmark_status_and_keeps_duration_separate(self) -> None:
        requests = [
            {
                "test_id": "reasoning",
                "status": "ok",
                "quality": {"score": 1.0, "passed": 4, "total": 4},
                "seconds": 45,
                "response": "private output",
            },
            {
                "test_id": "math",
                "status": "truncated",
                "quality": {"score": 0.8, "passed": 4, "total": 5},
                "seconds": 60,
                "response": "another private output",
            },
        ]

        metrics = SystemEvaluationEngine.replay(requests, {"model": "candidate"})

        self.assertEqual(metrics["successes"], 1)
        self.assertEqual(metrics["success_rate"], 0.5)
        self.assertEqual(metrics["truncated_requests"], 1)
        self.assertEqual(metrics["quality_score"], 0.9)
        self.assertEqual(metrics["quality_samples"], 2)
        self.assertEqual(metrics["quality_coverage"], 1.0)
        self.assertEqual(metrics["semantic_quality_samples"], 0)
        self.assertEqual(metrics["semantic_quality_coverage"], 0.0)
        self.assertEqual(metrics["task_quality"]["math"]["score"], 0.8)
        self.assertEqual(metrics["latency_samples"], 0)
        self.assertEqual(metrics["avg_end_to_end_seconds"], 52.5)
        self.assertNotIn("response", metrics)

    def test_empty_replay_returns_zeroed_metrics(self) -> None:
        metrics = SystemEvaluationEngine.replay([], {"model": "candidate"})

        self.assertEqual(metrics["total_requests"], 0)
        self.assertEqual(metrics["success_rate"], 0.0)
        self.assertEqual(metrics["error_rate"], 0.0)
        self.assertEqual(metrics["avg_latency_ms"], 0.0)
        self.assertEqual(metrics["quality_coverage"], 0.0)
        self.assertEqual(metrics["estimated_cost"], 0)

    def test_shadow_evaluation(self) -> None:
        primary = {"response": "Hello world", "latency_ms": 120}
        shadow = {"response": "Hello world (shadow)", "latency_ms": 110}
        comparison = SystemEvaluationEngine.shadow_evaluate(primary, shadow)

        self.assertIn("match", comparison)
        self.assertIn("latency_delta_ms", comparison)
        self.assertEqual(comparison["latency_delta_ms"], -10)

    def test_promotion_gate_and_rollback(self) -> None:
        good_metrics = {
            "success_rate": 0.99,
            "error_rate": 0.01,
            "avg_latency_ms": 150,
            "latency_samples": 20,
            "quality_score": 0.92,
            "quality_samples": 20,
            "quality_coverage": 1.0,
            "semantic_quality_score": 0.95,
            "semantic_quality_samples": 20,
            "semantic_quality_coverage": 1.0,
            "truncated_requests": 0,
            "task_quality": {"coding": {"score": 0.9, "samples": 20}},
        }
        thresholds = {
            "min_success_rate": 0.95,
            "max_error_rate": 0.05,
            "max_latency_ms": 500,
            "min_quality_score": 0.8,
            "min_quality_coverage": 0.9,
            "min_task_quality_score": 0.8,
        }

        passed, reason = SystemEvaluationEngine.promote_with_rollback(
            good_metrics, thresholds
        )
        self.assertTrue(passed)
        self.assertEqual(reason, "Gate passed successfully")

        bad_metrics = {
            **good_metrics,
            "success_rate": 0.85,
            "error_rate": 0.15,
            "avg_latency_ms": 600,
        }
        passed_fail, reason_fail = SystemEvaluationEngine.promote_with_rollback(
            bad_metrics, thresholds
        )
        self.assertFalse(passed_fail)
        self.assertIn("Rollback triggered", reason_fail)

    def test_gate_fails_closed_when_quality_or_latency_evidence_is_missing(
        self,
    ) -> None:
        passed, reason = SystemEvaluationEngine.promote_with_rollback(
            {
                "success_rate": 1.0,
                "error_rate": 0.0,
                "avg_latency_ms": 0.0,
                "latency_samples": 0,
                "quality_score": 0.0,
                "quality_samples": 0,
                "quality_coverage": 0.0,
                "semantic_quality_score": 0.0,
                "semantic_quality_samples": 0,
                "semantic_quality_coverage": 0.0,
                "truncated_requests": 0,
            },
            {},
        )

        self.assertFalse(passed)
        self.assertIn("no quality samples", reason)
        self.assertIn("no independent semantic-quality samples", reason)
        self.assertIn("quality_coverage", reason)
        self.assertIn("no comparable serving-latency samples", reason)

    def test_gate_rejects_a_weak_task_even_when_aggregate_quality_passes(self) -> None:
        metrics = {
            "success_rate": 1.0,
            "error_rate": 0.0,
            "avg_latency_ms": 120,
            "latency_samples": 5,
            "quality_score": 0.82,
            "quality_samples": 5,
            "quality_coverage": 1.0,
            "semantic_quality_score": 0.9,
            "semantic_quality_samples": 5,
            "semantic_quality_coverage": 1.0,
            "truncated_requests": 0,
            "task_quality": {
                "coding": {"score": 0.98, "samples": 4},
                "matematica": {"score": 0.18, "samples": 1},
            },
        }

        passed, reason = SystemEvaluationEngine.promote_with_rollback(metrics, {})

        self.assertFalse(passed)
        self.assertIn("task_quality[matematica]=0.180", reason)

    def test_gate_rejects_truncated_benchmark_outputs(self) -> None:
        metrics = {
            "success_rate": 0.99,
            "error_rate": 0.01,
            "avg_latency_ms": 120,
            "latency_samples": 10,
            "quality_score": 0.95,
            "quality_samples": 10,
            "quality_coverage": 1.0,
            "semantic_quality_score": 0.9,
            "semantic_quality_samples": 10,
            "semantic_quality_coverage": 1.0,
            "truncated_requests": 1,
            "task_quality": {"coding": {"score": 0.95, "samples": 10}},
        }

        passed, reason = SystemEvaluationEngine.promote_with_rollback(metrics, {})

        self.assertFalse(passed)
        self.assertIn("truncated_requests=1.0 (max 0.0)", reason)


if __name__ == "__main__":
    unittest.main()

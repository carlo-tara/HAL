import unittest  # noqa: I001
from global_config import SystemRoutingPolicy, augment_response_with_wysiati

class TestKahnemanEvolution(unittest.TestCase):
    def test_wysiati_completeness_flag(self) -> None:
        raw_response = {"result": "success", "data": "test"}
        augmented = augment_response_with_wysiati(raw_response, text_length=150, missing_context_indicators=0)
        self.assertIn("wysiati_complete", augmented)
        self.assertIn("evidence_completeness_score", augmented)
        self.assertTrue(augmented["wysiati_complete"])

        incomplete_response = augment_response_with_wysiati(raw_response, text_length=5, missing_context_indicators=3)
        self.assertFalse(incomplete_response["wysiati_complete"])

    def test_cognitive_tension_monitoring_escalation(self) -> None:
        policy_res = SystemRoutingPolicy.evaluate_routing(
            task_type="summarization",
            text="Very complex ambiguous architecture security audit across multi-cloud clusters...",
            laya_assessment={"decision_status": "ok", "risk_score": 0.2},
            cognitive_tension=0.85
        )
        self.assertEqual(policy_res["tier"], "s2_full")
        self.assertFalse(policy_res["budget_reduction"])

if __name__ == "__main__":
    unittest.main()

import os  # noqa: I001
import unittest

from global_config import SystemRoutingPolicy, SystemTwoEngine, resolve_model_for_profile

class TestSystemTwoProvider(unittest.TestCase):
    def setUp(self) -> None:
        SystemTwoEngine.register_backend(None, None)
        if "LLM_EXTERNAL_MODE" in os.environ:
            del os.environ["LLM_EXTERNAL_MODE"]

    def tearDown(self) -> None:
        SystemTwoEngine.register_backend(None, None)
        if "LLM_EXTERNAL_MODE" in os.environ:
            del os.environ["LLM_EXTERNAL_MODE"]

    def test_default_execution_metadata(self) -> None:
        res = SystemTwoEngine.execute("coding", "hello world")
        self.assertIn(SystemTwoEngine.ACTIVE_MODEL_NAME, res)
        self.assertEqual(res.model, SystemTwoEngine.ACTIVE_MODEL_NAME)
        self.assertEqual(res.provider, "system2_default")
        self.assertFalse(res.fallback_used)

    def test_mock_backend_invocation(self) -> None:
        def mock_backend(task, text, model, agent, **kwargs):
            return {
                "response": f"Mocked response for {text} on {model}",
                "model": model,
                "provider": "mock_provider"
            }

        SystemTwoEngine.register_backend(mock_backend)
        res = SystemTwoEngine.execute("reasoning_planning", "plan architecture", agent="a-product")
        self.assertEqual(res.response, f"Mocked response for plan architecture on {SystemTwoEngine.ACTIVE_MODEL_NAME}")
        self.assertEqual(res.provider, "mock_provider")
        self.assertFalse(res.fallback_used)

    def test_backend_fallback(self) -> None:
        def failing_backend(task, text, model, agent, **kwargs):
            raise RuntimeError("Provider connection error")

        def fallback_backend(task, text, model, agent, error, **kwargs):
            return {
                "response": f"Fallback executed due to {error}",
                "model": "fallback-model"
            }

        SystemTwoEngine.register_backend(failing_backend, fallback_backend)
        res = SystemTwoEngine.execute("summarization", "summarize this", agent="a-harness")
        self.assertIn("Fallback executed", res.response)
        self.assertEqual(res.model, "fallback-model")
        self.assertTrue(res.fallback_used)

    def test_profile_model_resolution(self) -> None:
        model_off = resolve_model_for_profile(profile="coding")
        self.assertEqual(model_off, SystemTwoEngine.ACTIVE_MODEL_NAME)

        os.environ["LLM_EXTERNAL_MODE"] = "1"
        model_coding = resolve_model_for_profile(profile="coding")
        self.assertEqual(model_coding, "orcarouter/deepseek/deepseek-v4.1-flash")

        model_editing = resolve_model_for_profile(profile="text_editing")
        self.assertEqual(model_editing, "orcarouter/openai/gpt-4o-mini")

        os.environ["LLM_EXTERNAL_MODE"] = "0"
        arbitrary_model = resolve_model_for_profile(profile="coding", requested_model="malicious-arbitrary-model")
        self.assertEqual(arbitrary_model, SystemTwoEngine.ACTIVE_MODEL_NAME)

        valid_model = resolve_model_for_profile(profile="coding", requested_model="orcarouter/deepseek/deepseek-v4.1-flash")
        self.assertEqual(valid_model, "orcarouter/deepseek/deepseek-v4.1-flash")

    def test_system_routing_policy(self) -> None:
        # 1. Closed decision with low risk -> System 1 (s1)
        res_s1 = SystemRoutingPolicy.evaluate_routing("choice", "choose option A", {"decision_status": "ok", "risk_score": 0.1})
        self.assertEqual(res_s1["tier"], "s1")
        self.assertFalse(res_s1["budget_reduction"])

        # 2. Simple low-risk generation -> System 2 Reduced (s2_reduced)
        res_reduced = SystemRoutingPolicy.evaluate_routing("summarization", "long text", {"decision_status": "ok", "risk_score": 0.15})
        self.assertEqual(res_reduced["tier"], "s2_reduced")
        self.assertTrue(res_reduced["budget_reduction"])
        self.assertEqual(res_reduced["max_tokens"], 1024)

        # 3. Abstention prevents reduction -> System 2 Full (s2_full)
        res_abstain = SystemRoutingPolicy.evaluate_routing("summarization", "long text", {"decision_status": "abstain", "risk_score": 0.15})
        self.assertEqual(res_abstain["tier"], "s2_full")
        self.assertFalse(res_abstain["budget_reduction"])

        # 4. High risk or side-effects prevents reduction -> System 2 Full (s2_full)
        res_risk = SystemRoutingPolicy.evaluate_routing("text_editing", "edit text", {"decision_status": "ok", "risk_score": 0.8})
        self.assertEqual(res_risk["tier"], "s2_full")
        self.assertFalse(res_risk["budget_reduction"])

        res_side = SystemRoutingPolicy.evaluate_routing("text_editing", "edit text", {"decision_status": "ok", "risk_score": 0.1}, has_side_effects=True)
        self.assertEqual(res_side["tier"], "s2_full")
        self.assertFalse(res_side["budget_reduction"])

        # 5. Complex reasoning task -> System 2 Full (s2_full)
        res_complex = SystemRoutingPolicy.evaluate_routing("reasoning_planning", "complex plan", {"decision_status": "ok", "risk_score": 0.1})
        self.assertEqual(res_complex["tier"], "s2_full")
        self.assertFalse(res_complex["budget_reduction"])

if __name__ == "__main__":
    unittest.main()

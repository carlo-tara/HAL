from __future__ import annotations

import unittest
from collections.abc import Mapping
from functools import partial
from unittest.mock import Mock, patch

import requests

import system1_preflight
from global_config import GlobalLayaHandler
from laya_service import LayaSystemOneService
from router import handle_batch_routing, handle_batch_score, triage_request


class TestLayaService(unittest.TestCase):
    @staticmethod
    def _response(payload: Mapping[str, object]) -> Mock:
        response = Mock()
        response.status_code = 200
        response.json.return_value = payload
        return response

    def test_unavailable_routing_abstains_and_is_not_cached(self) -> None:
        prompt = f"routing recovery {self.id()}"
        routes = ["a-harness", "a-product"]

        with patch("laya_service._session.post", side_effect=requests.ConnectionError):
            unavailable = LayaSystemOneService.routing(prompt, routes)

        self.assertEqual(unavailable.status, "abstain")
        self.assertIsNone(unavailable.value)
        self.assertEqual(unavailable.reason, "unavailable")

        with patch(
            "laya_service._session.post",
            return_value=self._response({"route": "a-product"}),
        ) as post:
            recovered = LayaSystemOneService.routing(prompt, routes)

        self.assertEqual(recovered.status, "ok")
        self.assertEqual(recovered.value, "a-product")
        post.assert_called_once()

    def test_invalid_route_abstains_and_is_not_cached(self) -> None:
        prompt = f"invalid route recovery {self.id()}"
        routes = ["a-harness", "a-product"]

        with patch(
            "laya_service._session.post",
            return_value=self._response({"route": "not-a-route"}),
        ):
            invalid = LayaSystemOneService.routing(prompt, routes)

        self.assertEqual(invalid.status, "abstain")
        self.assertIsNone(invalid.value)
        self.assertEqual(invalid.reason, "invalid_route")

        with patch(
            "laya_service._session.post",
            return_value=self._response({"route": "a-product"}),
        ) as post:
            recovered = LayaSystemOneService.routing(prompt, routes)

        self.assertEqual(recovered.status, "ok")
        self.assertEqual(recovered.value, "a-product")
        post.assert_called_once()

    def test_score_does_not_fabricate_confidence_on_failure_or_invalid_response(
        self,
    ) -> None:
        text = f"score failure {self.id()}"

        with patch("laya_service._session.post", side_effect=requests.ConnectionError):
            unavailable = LayaSystemOneService.score(text, "relevance")

        self.assertEqual(unavailable.status, "abstain")
        self.assertIsNone(unavailable.value)

        with patch(
            "laya_service._session.post",
            return_value=self._response({"score": "not-a-number"}),
        ):
            invalid = LayaSystemOneService.score(text, "relevance")

        self.assertEqual(invalid.status, "abstain")
        self.assertIsNone(invalid.value)
        self.assertEqual(invalid.reason, "invalid_score")

    def test_triage_abstains_instead_of_routing_on_outage(self) -> None:
        with patch("laya_service._session.post", side_effect=requests.ConnectionError):
            result = triage_request(f"triage outage {self.id()}")

        self.assertEqual(result["decision_status"], "abstain")
        self.assertEqual(result["agent"], "none")
        self.assertFalse(result["is_routed"])

    def test_atomic_low_risk_single_choice_skips_laya_and_preserves_context(
        self,
    ) -> None:
        contract = {
            "risk_level": "low",
            "complexity": "atomic",
            "source": "original source text",
            "output_format": "json",
        }

        with patch("laya_service._session.post") as post:
            result = GlobalLayaHandler.evaluate(
                "choice", f"one option {self.id()}", ["only"], task_contract=contract
            )

        post.assert_not_called()
        self.assertIsInstance(result.value, dict)
        self.assertEqual(result.value["result"], "only")
        self.assertEqual(result.value["source"], "original source text")
        self.assertEqual(result.value["output_format"], "json")

    def test_non_atomic_task_sends_compact_metadata_without_source(self) -> None:
        source = "private source content that must remain local"
        contract = {
            "risk_level": "high",
            "complexity": "complex",
            "source": source,
            "output_format": "json",
            "constraints": ["preserve all records"],
        }
        prompt = f"route request {self.id()}"

        with patch(
            "laya_service._session.post",
            return_value=self._response({"route": "a-product"}),
        ) as post:
            result = GlobalLayaHandler.evaluate(
                "routing", prompt, ["a-product", "a-harness"], task_contract=contract
            )

        payload = post.call_args.kwargs["json"]
        self.assertNotIn(source, str(payload))
        self.assertIn(f"source_chars={len(source)}", payload["text"])
        self.assertIn("format=json", payload["text"])
        self.assertIn("preserve all records", payload["text"])
        self.assertIsInstance(result.value, dict)
        self.assertEqual(result.value["source"], source)
        self.assertEqual(result.value["output_format"], "json")

    def test_unknown_risk_does_not_enable_local_shortcut(self) -> None:
        contract = {
            "risk_level": "unknown",
            "complexity": "atomic",
            "source": "source",
        }

        with patch(
            "laya_service._session.post",
            return_value=self._response({"route": "a-product"}),
        ) as post:
            result = GlobalLayaHandler.evaluate(
                "routing", f"route {self.id()}", ["a-product"], task_contract=contract
            )

        post.assert_called_once()
        self.assertEqual(result.status, "ok")

    def test_coherence_gate_executes_local_coherence(self) -> None:
        contract = {
            "risk_level": "low",
            "complexity": "atomic",
            "source": "orig",
            "output_format": "json",
        }

        with patch("laya_service._session.post") as post:
            result = GlobalLayaHandler.evaluate(
                "coherence", "check", [], task_contract=contract
            )

        self.assertIsInstance(result.value, dict)
        self.assertEqual(result.value["result"], "coherence_ok")
        self.assertEqual(result.value["origin"], "local_coherence")
        post.assert_not_called()


class TestLayaBudget(unittest.TestCase):
    def setUp(self) -> None:
        self.contract = {
            "risk_level": "unknown",
            "source": "segment one\nsegment two\nsegment three",
            "output_format": "json",
        }

    def budget(self, **kwargs):
        return system1_preflight.LayaCallBudget(**kwargs)

    def evaluate(self, budget=None, **metadata):
        return GlobalLayaHandler.evaluate(
            "routing",
            self.id(),
            ["a-product"],
            task_contract={**self.contract, **metadata},
            laya_budget=budget,
        )

    def assert_context_preserved(self, outcome) -> None:
        self.assertEqual(outcome.value["source"], self.contract["source"])
        self.assertEqual(outcome.value["output_format"], "json")

    def test_shared_budget_stops_second_gateway_call(self) -> None:
        budget = self.budget(max_calls=1)
        with patch(
            "laya_service._session.post",
            return_value=TestLayaService._response({"route": "a-product"}),
        ) as post:
            first = self.evaluate(budget)
            second = self.evaluate(budget)
        self.assertEqual(first.status, "ok")
        self.assertEqual(second.status, "abstain")
        self.assertEqual(second.reason, "call_budget_exhausted")
        self.assert_context_preserved(second)
        self.assertEqual(budget.calls, 1)
        post.assert_called_once()

    def test_zero_budget_abstains_without_losing_segments(self) -> None:
        with patch("laya_service._session.post") as post:
            result = self.evaluate(self.budget(max_calls=0))
        post.assert_not_called()
        self.assertEqual(result.status, "abstain")
        self.assertEqual(result.reason, "call_budget_exhausted")
        self.assert_context_preserved(result)

    def test_local_preflight_does_not_consume_budget(self) -> None:
        budget = self.budget(max_calls=0)
        with patch("laya_service._session.post") as post:
            result = self.evaluate(budget, risk_level="low", complexity="atomic")
        self.assertEqual(result.status, "ok")
        self.assertEqual(result.value["origin"], "local_preflight")
        self.assertEqual(budget.calls, 0)
        self.assert_context_preserved(result)
        post.assert_not_called()

    def test_flow_neutral_intermediate_decision_skips_laya(self) -> None:
        with patch("laya_service._session.post") as post:
            result = self.evaluate(is_intermediate=True)
        self.assertEqual(result.status, "abstain")
        self.assertEqual(result.reason, "no_flow_change")
        self.assert_context_preserved(result)
        post.assert_not_called()

    def test_flow_changing_intermediate_decision_uses_budget(self) -> None:
        with patch(
            "laya_service._session.post",
            return_value=TestLayaService._response({"route": "a-product"}),
        ) as post:
            result = self.evaluate(is_intermediate=True, changes_flow=True)
        post.assert_called_once()
        self.assertEqual(result.status, "ok")
        self.assert_context_preserved(result)
        self.assertNotIn(self.contract["source"], str(post.call_args.kwargs["json"]))

    def test_default_has_no_retry(self) -> None:
        with patch("laya_service._session.post", side_effect=requests.Timeout) as post:
            result = self.evaluate()
        self.assertEqual(result.reason, "unavailable")
        self.assert_context_preserved(result)
        post.assert_called_once()

    def test_one_justified_transient_retry_can_recover(self) -> None:
        budget = self.budget(
            max_calls=2, max_retries=1, retry_reason="transient timeout"
        )
        with patch(
            "laya_service._session.post",
            side_effect=[
                requests.Timeout(),
                TestLayaService._response({"route": "a-product"}),
            ],
        ) as post:
            result = self.evaluate(budget)
        self.assertEqual(result.status, "ok")
        self.assertEqual(post.call_count, 2)
        self.assertEqual((budget.calls, budget.retries), (2, 1))
        self.assert_context_preserved(result)

    def test_retry_never_exceeds_total_or_retry_limits(self) -> None:
        for limit, expected_calls in ((1, 1), (3, 2)):
            with self.subTest(limit=limit):
                budget = self.budget(
                    max_calls=limit, max_retries=1, retry_reason="transient failure"
                )
                with patch(
                    "laya_service._session.post", side_effect=requests.ConnectionError
                ) as post:
                    result = self.evaluate(budget)
                self.assertEqual(result.status, "abstain")
                self.assertEqual(post.call_count, expected_calls)
                self.assertLessEqual(budget.calls, limit)
                self.assert_context_preserved(result)

    def test_invalid_result_and_http_error_are_not_retried(self) -> None:
        for failure in (
            TestLayaService._response({"route": "invalid"}),
            requests.HTTPError(),
        ):
            with self.subTest(failure=type(failure).__name__):
                budget = self.budget(
                    max_calls=2, max_retries=1, retry_reason="transient failure"
                )
                with patch("laya_service._session.post") as post:
                    if isinstance(failure, Exception):
                        post.side_effect = failure
                    else:
                        post.return_value = failure
                    result = self.evaluate(budget)
                self.assertEqual(result.status, "abstain")
                self.assertEqual(budget.retries, 0)
                post.assert_called_once()
                self.assert_context_preserved(result)

    def test_context_budget_covers_direct_service_and_resets_after_run(self) -> None:
        budget = self.budget(max_calls=1)
        prompt = f"direct {self.id()}"
        with patch(
            "laya_service._session.post",
            return_value=TestLayaService._response({"route": "a-product"}),
        ) as post:
            with LayaSystemOneService.budget(budget):
                first = LayaSystemOneService.routing(prompt, ["a-product"])
                cached = LayaSystemOneService.routing(prompt, ["a-product"])
                blocked = self.evaluate()
            fresh_run = self.evaluate()
        self.assertEqual(
            (first.status, cached.status, fresh_run.status), ("ok", "ok", "ok")
        )
        self.assertEqual(blocked.reason, "call_budget_exhausted")
        self.assertEqual(budget.calls, 1)
        self.assertEqual(post.call_count, 2)

    def test_redirect_is_not_followed_or_accepted(self) -> None:
        response = TestLayaService._response({"route": "a-product"})
        response.status_code = 307
        with patch("laya_service._session.post", return_value=response) as post:
            result = self.evaluate()
        self.assertEqual(result.status, "abstain")
        self.assertEqual(result.reason, "redirect_not_allowed")
        self.assertFalse(post.call_args.kwargs["allow_redirects"])
        post.assert_called_once()
        self.assert_context_preserved(result)

    def test_explicit_nested_budget_cannot_replace_active_budget(self) -> None:
        with (
            patch("laya_service._session.post") as post,
            LayaSystemOneService.budget(self.budget(max_calls=0)),
            self.assertRaises(ValueError),
        ):
            self.evaluate(self.budget(max_calls=1))
        post.assert_not_called()

    def test_triage_agent_and_skill_share_one_bounded_run(self) -> None:
        seen = []
        responses = [{"route": "a-product"}, {"choice": "jtbd"}]

        def reply(*args, **kwargs):
            with LayaSystemOneService.budget() as active:
                seen.append(active)
            return TestLayaService._response(responses[len(seen) - 1])

        with patch("laya_service._session.post", side_effect=reply) as post:
            result = triage_request(self.id())
        self.assertEqual((result["agent"], result["skill"]), ("a-product", "jtbd"))
        self.assertEqual(post.call_count, 2)
        self.assertIs(seen[0], seen[1])
        self.assertEqual((seen[0].max_calls, seen[0].calls), (2, 2))

    def test_triage_explicit_cap_abstains_without_dropping_request(self) -> None:
        source = self.contract["source"] + self.id()
        with patch(
            "laya_service._session.post",
            return_value=TestLayaService._response({"route": "a-product"}),
        ) as post:
            result = triage_request(source, laya_budget=self.budget(max_calls=1))
        self.assertEqual(result["decision_status"], "abstain")
        self.assertFalse(result["is_routed"])
        self.assertEqual(result["request"], source)
        post.assert_called_once()

    def test_triage_inherits_exhausted_enclosing_budget(self) -> None:
        with (
            patch("laya_service._session.post") as post,
            LayaSystemOneService.budget(self.budget(max_calls=0)),
        ):
            result = triage_request(self.id())
        self.assertEqual(result["decision_status"], "abstain")
        self.assertEqual(result["request"], self.id())
        post.assert_not_called()

    def test_batch_uses_one_run_and_retains_exhausted_output_positions(self) -> None:
        for label, operation, response in (
            (
                "router_routing",
                partial(handle_batch_routing, routes=["a-product"]),
                {"route": "a-product"},
            ),
            (
                "router_score",
                partial(handle_batch_score, criteria="criterion"),
                {"score": 0.9},
            ),
            (
                "service_routing",
                partial(LayaSystemOneService.batch_routing, routes=["a-product"]),
                {"route": "a-product"},
            ),
            (
                "service_score",
                partial(LayaSystemOneService.batch_score, criteria="criterion"),
                {"score": 0.9},
            ),
        ):
            with self.subTest(operation=label):
                seen = []

                def reply(*args, seen=seen, response=response, **kwargs):
                    with LayaSystemOneService.budget() as active:
                        seen.append(active)
                    return TestLayaService._response(response)

                texts = [f"{self.id()} {label} {i}" for i in range(2)]
                with patch("laya_service._session.post", side_effect=reply):
                    results = operation(texts)
                self.assertEqual([r.status for r in results], ["ok", "ok"])
                self.assertIs(seen[0], seen[1])
                self.assertEqual((seen[0].max_calls, seen[0].calls), (2, 2))

                with (
                    patch("laya_service._session.post", side_effect=reply) as post,
                    LayaSystemOneService.budget(self.budget(max_calls=1)),
                ):
                    capped = operation([text + " capped" for text in texts])
                self.assertEqual([r.status for r in capped], ["ok", "abstain"])
                self.assertEqual(capped[1].reason, "call_budget_exhausted")
                post.assert_called_once()

    def test_local_ceiling_cannot_be_enlarged_by_parent_budget(self) -> None:
        parent = self.budget(max_calls=5)
        with (
            patch(
                "laya_service._session.post",
                return_value=TestLayaService._response({"route": "a-product"}),
            ) as post,
            LayaSystemOneService.budget(parent),
            LayaSystemOneService.budget(max_calls=1),
        ):
            first = self.evaluate()
            blocked = self.evaluate()
        self.assertEqual(first.status, "ok")
        self.assertEqual(blocked.reason, "call_budget_exhausted")
        self.assertEqual(parent.calls, 1)
        post.assert_called_once()

    def test_triage_does_not_inherit_parent_retries(self) -> None:
        parent = self.budget(
            max_calls=5, max_retries=1, retry_reason="transient failure"
        )
        with (
            patch(
                "laya_service._session.post",
                side_effect=[
                    requests.Timeout(),
                    TestLayaService._response({"route": "a-product"}),
                ],
            ) as post,
            LayaSystemOneService.budget(parent),
        ):
            result = triage_request(self.id())
        self.assertEqual(result["decision_status"], "abstain")
        self.assertEqual(parent.retries, 0)
        post.assert_called_once()

    def test_batches_do_not_inherit_parent_retries(self) -> None:
        for label, operation, response in (
            (
                "router_routing",
                partial(handle_batch_routing, routes=["a-product"]),
                {"route": "a-product"},
            ),
            (
                "router_score",
                partial(handle_batch_score, criteria="criterion"),
                {"score": 0.9},
            ),
            (
                "service_routing",
                partial(LayaSystemOneService.batch_routing, routes=["a-product"]),
                {"route": "a-product"},
            ),
            (
                "service_score",
                partial(LayaSystemOneService.batch_score, criteria="criterion"),
                {"score": 0.9},
            ),
        ):
            with self.subTest(operation=label):
                parent = self.budget(
                    max_calls=5, max_retries=1, retry_reason="transient failure"
                )
                with (
                    patch(
                        "laya_service._session.post",
                        side_effect=[
                            requests.Timeout(),
                            TestLayaService._response(response),
                        ],
                    ) as post,
                    LayaSystemOneService.budget(parent),
                ):
                    results = operation([f"{self.id()} {label} {i}" for i in range(2)])
                self.assertEqual([r.status for r in results], ["abstain", "ok"])
                self.assertEqual(parent.retries, 0)
                self.assertEqual(post.call_count, 2)

    def test_budget_and_flow_flags_reject_invalid_configuration(self) -> None:
        for invalid in (
            {"max_calls": -1},
            {"max_calls": True},
            {"max_calls": 1.5},
            {"max_retries": 2},
            {"max_retries": True},
            {"max_retries": 1},
            {"retry_reason": None},
        ):
            with (
                self.subTest(invalid=invalid),
                self.assertRaises((TypeError, ValueError)),
            ):
                self.budget(**invalid)
        with patch("laya_service._session.post") as post:
            with self.assertRaises(TypeError):
                self.evaluate("unlimited")
            with self.assertRaises(TypeError):
                self.evaluate(is_intermediate="false")
            with self.assertRaises(TypeError):
                self.evaluate(changes_flow="true")
        post.assert_not_called()


if __name__ == "__main__":
    unittest.main()

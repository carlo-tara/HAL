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
            return_value=self._response({"result": {"choice": "a-product"}}),
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
            return_value=self._response({"result": {"choice": "not-a-route"}}),
        ):
            invalid = LayaSystemOneService.routing(prompt, routes)

        self.assertEqual(invalid.status, "abstain")
        self.assertIsNone(invalid.value)
        self.assertEqual(invalid.reason, "invalid_route")

        with patch(
            "laya_service._session.post",
            return_value=self._response({"result": {"choice": "a-product"}}),
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
            return_value=self._response({"result": {"score": "not-a-number"}}),
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
            return_value=self._response({"result": {"choice": "a-product"}}),
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
            return_value=self._response({"result": {"choice": "a-product"}}),
        ) as post:
            result = GlobalLayaHandler.evaluate(
                "routing", f"route {self.id()}", ["a-product"], task_contract=contract
            )

        post.assert_called_once()
        self.assertEqual(result.status, "ok")

    def _evaluate_atomic(self, task, candidates, source, **extra):
        contract = {
            "risk_level": "low",
            "complexity": "atomic",
            "source": source,
            "output_format": "json",
            **extra,
        }
        return GlobalLayaHandler.evaluate(
            task, f"short request {self.id()}", candidates, task_contract=contract
        )

    def test_atomic_short_low_risk_multi_choice_skips_preflight(self) -> None:
        budget = system1_preflight.LayaCallBudget(max_calls=0)

        with patch("laya_service._session.post") as post:
            result = self._evaluate_atomic(
                "choice", ["a", "b", "c"], "short source", laya_budget=budget
            )

        post.assert_not_called()
        self.assertEqual(result.status, "abstain")
        self.assertEqual(result.reason, "preflight_skipped_atomic")
        self.assertEqual(result.value["source"], "short source")
        self.assertEqual(result.value["output_format"], "json")
        self.assertEqual(budget.calls, 0)

    def test_atomic_short_low_risk_score_skips_preflight(self) -> None:
        with patch("laya_service._session.post") as post:
            result = self._evaluate_atomic("score", [], "short source", criteria="fit")

        post.assert_not_called()
        self.assertEqual(result.reason, "preflight_skipped_atomic")

    def test_atomic_low_risk_long_request_still_calls_laya(self) -> None:
        source = "x" * system1_preflight.PREFLIGHT_SHORT_MAX_CHARS

        with patch(
            "laya_service._session.post",
            return_value=self._response({"result": {"choice": "b"}}),
        ) as post:
            result = self._evaluate_atomic("choice", ["a", "b"], source)

        post.assert_called_once()
        self.assertEqual(result.status, "ok")
        self.assertEqual(result.value["origin"], "laya")

    def test_preflight_length_threshold_is_exclusive(self) -> None:
        limit = system1_preflight.PREFLIGHT_SHORT_MAX_CHARS

        def contract(source_len: int, **overrides):
            instruction = "pick"
            return system1_preflight.TaskContract(
                task_type="choice",
                instruction=instruction,
                source="x" * source_len,
                output_format="json",
                candidates=("a", "b"),
                risk_level=overrides.get("risk_level", "low"),
                complexity=overrides.get("complexity", "atomic"),
            )

        below = contract(limit - len("pick") - 1)
        at_limit = contract(limit - len("pick"))
        self.assertTrue(system1_preflight.is_atomic_short_low_risk(below))
        self.assertFalse(system1_preflight.is_atomic_short_low_risk(at_limit))
        self.assertFalse(
            system1_preflight.is_atomic_short_low_risk(contract(5, risk_level="high"))
        )
        self.assertFalse(
            system1_preflight.is_atomic_short_low_risk(
                contract(5, complexity="complex")
            )
        )

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
            return_value=TestLayaService._response({"result": {"choice": "a-product"}}),
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
            return_value=TestLayaService._response({"result": {"choice": "a-product"}}),
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
                TestLayaService._response({"result": {"choice": "a-product"}}),
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
            TestLayaService._response({"result": {"choice": "invalid"}}),
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
            return_value=TestLayaService._response({"result": {"choice": "a-product"}}),
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
        response = TestLayaService._response({"result": {"choice": "a-product"}})
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
        responses = [
            {"result": {"choice": "a-product"}},
            {"result": {"choice": "jtbd"}},
        ]

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
            return_value=TestLayaService._response({"result": {"choice": "a-product"}}),
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
                {"result": {"choice": "a-product"}},
            ),
            (
                "router_score",
                partial(handle_batch_score, criteria="criterion"),
                {"result": {"score": 0.9}},
            ),
            (
                "service_routing",
                partial(LayaSystemOneService.batch_routing, routes=["a-product"]),
                {"result": {"choice": "a-product"}},
            ),
            (
                "service_score",
                partial(LayaSystemOneService.batch_score, criteria="criterion"),
                {"result": {"score": 0.9}},
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
                return_value=TestLayaService._response(
                    {"result": {"choice": "a-product"}}
                ),
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
                    TestLayaService._response({"result": {"choice": "a-product"}}),
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
                {"result": {"choice": "a-product"}},
            ),
            (
                "router_score",
                partial(handle_batch_score, criteria="criterion"),
                {"result": {"score": 0.9}},
            ),
            (
                "service_routing",
                partial(LayaSystemOneService.batch_routing, routes=["a-product"]),
                {"result": {"choice": "a-product"}},
            ),
            (
                "service_score",
                partial(LayaSystemOneService.batch_score, criteria="criterion"),
                {"result": {"score": 0.9}},
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


class TestSystemOneContract(unittest.TestCase):
    """Endpoint canonico dei task: POST /systemone {task_type,text,params} → envelope {"result": {choice,...}}."""

    @staticmethod
    def _response(payload: Mapping[str, object]) -> Mock:
        response = Mock()
        response.status_code = 200
        response.json.return_value = payload
        return response

    def test_routing_uses_systemone_envelope(self) -> None:
        routes = ["cache-cost-tokeni", "rete-non-tokeni"]
        text = f"marker cache_control {self.id()}"
        envelope = self._response(
            {
                "result": {
                    "type": "choice",
                    "choice": "cache-cost-tokeni",
                    "confidence": 0.65,
                },
                "request_hash": "h1",
            }
        )
        with patch("laya_service._session.post", return_value=envelope) as post:
            outcome = LayaSystemOneService.routing(text, routes)
        self.assertEqual(outcome.status, "ok")
        self.assertEqual(outcome.value, "cache-cost-tokeni")
        self.assertTrue(str(post.call_args.args[0]).endswith("/systemone"))
        sent = post.call_args.kwargs["json"]
        self.assertEqual(sent["task_type"], "routing")
        self.assertEqual(sent["params"], routes)
        self.assertEqual(sent["text"], text)

    def test_choice_uses_systemone_envelope(self) -> None:
        options = ["a-harness", "a-product"]
        text = f"quale agente {self.id()}"
        envelope = self._response(
            {"result": {"type": "choice", "choice": "a-product", "confidence": 0.9}}
        )
        with patch("laya_service._session.post", return_value=envelope) as post:
            outcome = LayaSystemOneService.choice(text, options)
        self.assertEqual(outcome.status, "ok")
        self.assertEqual(outcome.value, "a-product")
        sent = post.call_args.kwargs["json"]
        self.assertEqual(sent["task_type"], "choice")
        self.assertEqual(sent["params"], options)

    def test_score_bypass_abstains_with_documented_reason(self) -> None:
        envelope = self._response(
            {"result": {"bypass": True, "reason": "score_not_discriminative"}}
        )
        with patch("laya_service._session.post", return_value=envelope):
            outcome = LayaSystemOneService.score(f"testo {self.id()}", "rischio")
        self.assertEqual(outcome.status, "abstain")
        self.assertEqual(outcome.reason, "score_not_discriminative")
        self.assertIsNone(outcome.value)

    def test_noul_returns_intent_choice_string(self) -> None:
        envelope = self._response(
            {
                "result": {"type": "choice", "choice": "answer", "confidence": 0.8},
                "request_hash": "h2",
            }
        )
        with patch("laya_service._session.post", return_value=envelope):
            outcome = LayaSystemOneService.noul(f"ciao mamma {self.id()}")
        self.assertEqual(outcome.status, "ok")
        self.assertEqual(outcome.value, "answer")

    def test_noul_bypass_surfaces_reason(self) -> None:
        """Il servizio by-passa noul (noul_gpu_excluded): il motivo documentato
        deve arrivare nel LayaOutcome, non un generico invalid_result."""
        envelope = self._response(
            {"result": {"bypass": True, "reason": "noul_gpu_excluded"}}
        )
        with patch("laya_service._session.post", return_value=envelope):
            outcome = LayaSystemOneService.noul(f"ciao {self.id()}")
        self.assertEqual(outcome.status, "abstain")
        self.assertEqual(outcome.reason, "noul_gpu_excluded")

    def test_preflight_routing_parses_envelope_choice(self) -> None:
        contract = system1_preflight.TaskContract(
            task_type="routing",
            instruction="instrada",
            source="x" * 500,
            output_format="json",
            candidates=("a-product", "a-harness"),
            risk_level="high",
            complexity="complex",
        )
        envelope = self._response(
            {"result": {"type": "choice", "choice": "a-product", "confidence": 0.7}}
        )
        with patch("laya_service._session.post", return_value=envelope) as post:
            result = LayaSystemOneService.preflight(contract)
        self.assertEqual(result.status, "ok")
        self.assertEqual(result.value["result"], "a-product")
        self.assertEqual(result.value["origin"], "laya")
        sent = post.call_args.kwargs["json"]
        self.assertEqual(sent["task_type"], "routing")
        self.assertEqual(sent["params"], ["a-product", "a-harness"])


class KAwareGateGatewayTests(unittest.TestCase):
    """Gate k-aware (telemetria laya_calls): mirrored from hal_system1 — a k>=4 il
    solo margin non basta, e i verdetti senza speranza si astengono subito."""

    @staticmethod
    def _response(payload: Mapping[str, object]) -> Mock:
        response = Mock()
        response.status_code = 200
        response.json.return_value = payload
        return response

    def test_clear_margin_routing_single_call(self) -> None:
        prompt = f"gate clear {self.id()}"
        env = self._response(
            {
                "result": {"choice": "a", "probabilities": {"a": 0.9, "b": 0.1}},
                "request_hash": "h",
            }
        )
        with patch("laya_service._session.post", return_value=env) as post:
            outcome = LayaSystemOneService.routing(prompt, ["a", "b"])
        self.assertEqual(outcome.status, "ok")
        self.assertEqual(outcome.value, "a")
        post.assert_called_once()

    def test_no_probabilities_still_trusted(self) -> None:
        prompt = f"gate noprob {self.id()}"
        env = self._response({"result": {"choice": "b"}, "request_hash": "h"})
        with patch("laya_service._session.post", return_value=env) as post:
            outcome = LayaSystemOneService.choice(prompt, ["a", "b"])
        self.assertEqual(outcome.status, "ok")
        self.assertEqual(outcome.value, "b")
        post.assert_called_once()

    def test_deeply_unclear_abstains_with_single_call(self) -> None:
        prompt = f"gate unclear {self.id()}"
        env = self._response(
            {
                "result": {"choice": "a", "probabilities": {"a": 0.52, "b": 0.48}},
                "request_hash": "h1",
            }
        )
        with patch("laya_service._session.post", return_value=env) as post:
            outcome = LayaSystemOneService.routing(prompt, ["a", "b"])
        self.assertEqual(outcome.status, "abstain")
        self.assertEqual(outcome.reason, "low_margin")
        post.assert_called_once()

    def test_k4_high_margin_low_top1_forces_reversed_verification(self) -> None:
        prompt = f"gate k4 {self.id()}"
        probs = {"a": 0.65, "b": 0.10, "c": 0.125, "d": 0.125}
        first = self._response(
            {"result": {"choice": "a", "probabilities": probs}, "request_hash": "h1"}
        )
        second = self._response(
            {"result": {"choice": "a", "probabilities": probs}, "request_hash": "h2"}
        )
        with patch("laya_service._session.post", side_effect=[first, second]) as post:
            outcome = LayaSystemOneService.choice(prompt, ["a", "b", "c", "d"])
        self.assertEqual(outcome.status, "ok")
        self.assertEqual(outcome.value, "a")
        self.assertEqual(post.call_count, 2)
        self.assertEqual(
            post.call_args_list[1].kwargs["json"]["params"], ["d", "c", "b", "a"]
        )

    def test_gate_helpers_shared_with_laya_gate(self) -> None:
        """Anti-drift: il gateway non duplica più il gate, importa il canonico."""
        import laya_gate
        import laya_service as gw

        self.assertIs(gw._top_and_margin, laya_gate._top_and_margin)
        self.assertIs(gw.verdict_directly_acceptable, laya_gate.verdict_directly_acceptable)
        self.assertEqual(gw.FAST_MARGIN, laya_gate.FAST_MARGIN)

    def test_preflight_abstains_on_unclear_verdict(self) -> None:
        contract = system1_preflight.TaskContract(
            task_type="choice",
            instruction="Scegli lagente corretto per la richiesta di enrichment",
            source="x" * 500,
            output_format="md",
            candidates=("docs", "infra", "agents", "product"),
            risk_level="medium",
            complexity="complex",
        )
        env = self._response(
            {
                "result": {
                    "choice": "docs",
                    "probabilities": {
                        "docs": 0.40,
                        "infra": 0.30,
                        "agents": 0.15,
                        "product": 0.15,
                    },
                },
                "request_hash": "h",
            }
        )
        with patch("laya_service._session.post", return_value=env):
            outcome = LayaSystemOneService.preflight(contract)
        self.assertEqual(outcome.status, "abstain")
        self.assertEqual(outcome.reason, "low_margin")


if __name__ == "__main__":
    unittest.main()

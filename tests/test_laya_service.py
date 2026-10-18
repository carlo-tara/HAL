from __future__ import annotations

import unittest
from unittest.mock import Mock, patch

import requests

from global_config import GlobalLayaHandler
from laya_service import LayaSystemOneService
from router import triage_request


class TestLayaService(unittest.TestCase):
    @staticmethod
    def _response(payload: dict[str, object]) -> Mock:
        response = Mock()
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


if __name__ == "__main__":
    unittest.main()

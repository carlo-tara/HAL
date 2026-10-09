from __future__ import annotations

import unittest
from unittest.mock import Mock, patch

import requests

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

    def test_score_does_not_fabricate_confidence_on_failure_or_invalid_response(self) -> None:
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


if __name__ == "__main__":
    unittest.main()

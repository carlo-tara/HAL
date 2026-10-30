"""Contratto wire /systemone (verificato sul deployment laya-gpu 2026-10-30):

- POST {base}/systemone con {task_type, text, params} — NON /predict, che è il
  passthrough nativo {state,questions} e ignora i campi task HAL (risponde solo
  answers.intent);
- verdetto nell'envelope ``result``: choice/route/intent = ``result.choice``;
  score = diniego esplicito ``{"bypass": true, "reason": ...}`` (task non
  discriminativo, misurato server-side) → astensione con quel reason, mai un
  numero fabricato.
"""

from __future__ import annotations

import unittest
from collections.abc import Mapping
from unittest.mock import Mock, patch

from laya_service import LayaSystemOneService


def _response(envelope: Mapping[str, object]) -> Mock:
    response = Mock()
    response.status_code = 200
    response.json.return_value = dict(envelope)
    return response


class TestSystemOneContract(unittest.TestCase):
    def test_routing_chiama_systemone_con_task_type_e_params(self) -> None:
        prompt = f"wire routing {self.id()}"
        routes = ["cache-costo", "routing-batch"]
        with patch(
            "laya_service._session.post",
            return_value=_response({"result": {"choice": "cache-costo"}}),
        ) as post:
            outcome = LayaSystemOneService.routing(prompt, routes)
        self.assertEqual(outcome.status, "ok")
        self.assertEqual(outcome.value, "cache-costo")
        url = post.call_args.args[0]
        self.assertTrue(url.endswith("/systemone"), url)
        self.assertEqual(
            post.call_args.kwargs["json"],
            {"task_type": "routing", "text": prompt, "params": routes},
        )

    def test_choice_chiama_systemone_con_options_come_params(self) -> None:
        prompt = f"wire choice {self.id()}"
        with patch(
            "laya_service._session.post",
            return_value=_response({"result": {"choice": "b"}}),
        ) as post:
            outcome = LayaSystemOneService.choice(prompt, ["a", "b"])
        self.assertEqual((outcome.status, outcome.value), ("ok", "b"))
        self.assertEqual(
            post.call_args.kwargs["json"],
            {"task_type": "choice", "text": prompt, "params": ["a", "b"]},
        )

    def test_noul_non_invia_params(self) -> None:
        text = f"wire noul {self.id()}"
        with patch(
            "laya_service._session.post",
            return_value=_response({"result": {"type": "choice", "choice": "clarify"}}),
        ) as post:
            outcome = LayaSystemOneService.noul(text)
        self.assertEqual((outcome.status, outcome.value), ("ok", "clarify"))
        payload = post.call_args.kwargs["json"]
        self.assertEqual(payload["task_type"], "noul")
        self.assertNotIn("params", payload)

    def test_score_bypass_server_diventa_astensione_con_reason(self) -> None:
        text = f"wire score {self.id()}"
        with patch(
            "laya_service._session.post",
            return_value=_response(
                {"result": {"bypass": True, "reason": "score_not_discriminative"}}
            ),
        ):
            outcome = LayaSystemOneService.score(text, "relevance")
        self.assertEqual(outcome.status, "abstain")
        self.assertIsNone(outcome.value)
        self.assertEqual(outcome.reason, "score_not_discriminative")

    def test_envelope_senza_result_dict_e_invalid_response(self) -> None:
        with patch(
            "laya_service._session.post", return_value=_response({"answers": {}})
        ):
            outcome = LayaSystemOneService.noul(f"wire broken {self.id()}")
        self.assertEqual((outcome.status, outcome.reason), ("abstain", "invalid_response"))


if __name__ == "__main__":
    unittest.main()

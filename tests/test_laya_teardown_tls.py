"""Contratto P2 (ToDo 2026-10-28, doc QwenCloud §best practices HTTP):

- T29 teardown della _session: ``close()`` sul servizio che rilascia l'adapter,
  invocato dai runner batch nel ``finally`` (le connessioni non restano aperte
  fino al termine del processo);
- T30 verify configurabile: ``LAYA_CA_BUNDLE`` (path CA) o ``LAYA_TLS_VERIFY``;
  ``verify=False`` resta solo fallback esplicito documentato in docs/.
"""

from __future__ import annotations

import os
import unittest
from unittest.mock import Mock, patch

import laya_service
from laya_service import LayaSystemOneService, get_tls_verify


def _ok_response() -> Mock:
    response = Mock()
    response.status_code = 200
    response.raise_for_status = Mock()
    response.json = Mock(return_value={"result": {"choice": "ok", "score": 0.7}})
    return response


class TestTeardown(unittest.TestCase):
    def test_close_rilascia_la_session(self) -> None:
        with patch.object(laya_service._session, "close") as close:
            LayaSystemOneService.close()
        close.assert_called_once()

    def test_batch_invoca_close_nel_finally(self) -> None:
        with patch("laya_service._session.post", return_value=_ok_response()), patch(
            "laya_service._session.close"
        ) as close:
            LayaSystemOneService.batch_score(["a", "b"], "criterio")
        close.assert_called()

    def test_batch_invoca_close_anche_su_fallimento_laya(self) -> None:
        import requests

        with patch(
            "laya_service._session.post", side_effect=requests.ConnectionError
        ), patch("laya_service._session.close") as close:
            outcomes = LayaSystemOneService.batch_score(["a"], "criterio")
        self.assertEqual(outcomes[0].status, "abstain")
        close.assert_called()

    def test_context_manager_run_chiude(self) -> None:
        with patch("laya_service._session.close") as close, LayaSystemOneService.run():
            pass
        close.assert_called_once()


class TestTlsVerify(unittest.TestCase):
    def test_ca_bundle_preferito(self) -> None:
        env = {"LAYA_CA_BUNDLE": "/etc/ssl/laya-ca.pem", "LAYA_TLS_VERIFY": "1"}
        with patch.dict(os.environ, env, clear=True):
            self.assertEqual(get_tls_verify(), "/etc/ssl/laya-ca.pem")

    def test_flag_verifica(self) -> None:
        with patch.dict(os.environ, {"LAYA_TLS_VERIFY": "1"}, clear=True):
            self.assertIs(get_tls_verify(), True)
        with patch.dict(os.environ, {"LAYA_TLS_VERIFY": "0"}, clear=True):
            self.assertIs(get_tls_verify(), False)

    def test_fallback_off_documentato(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            self.assertIs(get_tls_verify(), False)

    def test_post_riceve_verify(self) -> None:
        with (
            patch.dict(os.environ, {"LAYA_CA_BUNDLE": "/x/ca.pem"}),
            patch("laya_service._session.post", return_value=_ok_response()) as post,
        ):
            LayaSystemOneService._call({"op": "noul"})
        self.assertEqual(post.call_args.kwargs["verify"], "/x/ca.pem")


if __name__ == "__main__":
    unittest.main()

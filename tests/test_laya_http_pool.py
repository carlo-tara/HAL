"""Contratto P1 (ToDo 2026-10-28, doc QwenCloud §connection reuse e parametri):

- HTTPAdapter con pool dimensionato sulla _session Laya, env configurabili,
  retry di trasporto disattivato per non sommare due forme di retry;
- timeout disaccoppiati connect/read in tupla a Session.post + pool_timeout
  esplicito, con env dedicate e parsing difensivo.
"""

from __future__ import annotations

import os
import unittest
from unittest.mock import Mock, patch

from requests.adapters import HTTPAdapter

import laya_service
from laya_service import (
    LayaSystemOneService,
    build_laya_adapter,
    get_pool_settings,
    get_pool_timeout,
    get_timeout_tuple,
)


class TestPoolSettings(unittest.TestCase):
    def test_defaults_documentati(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            settings = get_pool_settings()
        self.assertEqual(settings["pool_connections"], 10)
        # >= massimo atteso di chiamate batch concorrenti (len(texts) tipico)
        self.assertGreaterEqual(settings["pool_maxsize"], 32)
        self.assertEqual(get_pool_timeout(), 2.0)

    def test_env_configurabili(self) -> None:
        env = {
            "LAYA_POOL_CONNECTIONS": "5",
            "LAYA_POOL_MAXSIZE": "50",
            "LAYA_POOL_TIMEOUT": "1.5",
        }
        with patch.dict(os.environ, env, clear=True):
            settings = get_pool_settings()
            self.assertEqual(settings["pool_connections"], 5)
            self.assertEqual(settings["pool_maxsize"], 50)
            self.assertEqual(get_pool_timeout(), 1.5)

    def test_valori_non_validi_alle_defaults(self) -> None:
        with patch.dict(os.environ, {"LAYA_POOL_CONNECTIONS": "abc"}, clear=True):
            self.assertEqual(get_pool_settings()["pool_connections"], 10)

    def test_adapter_monta_pool_e_disattiva_retry_trasporto(self) -> None:
        with patch.dict(os.environ, {"LAYA_POOL_MAXSIZE": "40"}, clear=True):
            adapter = build_laya_adapter()
        self.assertIsInstance(adapter, HTTPAdapter)
        self.assertEqual(adapter._pool_maxsize, 40)
        self.assertEqual(adapter.max_retries.total, 0)
        self.assertEqual(adapter.poolmanager.connection_pool_kw.get("timeout"), 2.0)

    def test_session_monta_ladapter(self) -> None:
        mounted = laya_service._session.get_adapter("http://laya.local:8091/v1/systemone")
        self.assertIsInstance(mounted, HTTPAdapter)


class TestTimeoutTuple(unittest.TestCase):
    def test_defaults(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            connect, read = get_timeout_tuple()
        # connect corto per servizio locale (1-2 s), read sul budget storico
        self.assertEqual(connect, 2.0)
        self.assertEqual(read, laya_service.LAYA_TIMEOUT)

    def test_env_dedicati(self) -> None:
        with patch.dict(
            os.environ,
            {"LAYA_CONNECT_TIMEOUT": "1.5", "LAYA_READ_TIMEOUT": "8.0"},
            clear=True,
        ):
            self.assertEqual(get_timeout_tuple(), (1.5, 8.0))

    def test_parsing_difensivo_alle_defaults(self) -> None:
        with patch.dict(
            os.environ, {"LAYA_CONNECT_TIMEOUT": "-3", "LAYA_READ_TIMEOUT": "x"}
        ):
            connect, read = get_timeout_tuple()
        self.assertEqual(connect, 2.0)
        self.assertEqual(read, laya_service.LAYA_TIMEOUT)

    def test_post_riceve_la_tupla(self) -> None:
        response = Mock()
        response.status_code = 200
        response.raise_for_status = Mock()
        response.json = Mock(return_value={"result": {"choice": "ok"}})
        with (
            patch.dict(
                os.environ, {"LAYA_CONNECT_TIMEOUT": "1.25", "LAYA_READ_TIMEOUT": "6.5"}
            ),
            patch("laya_service._session.post", return_value=response) as post,
        ):
            LayaSystemOneService._call({"op": "noul"})
        self.assertEqual(post.call_args.kwargs["timeout"], (1.25, 6.5))


class TestAuthHeader(unittest.TestCase):
    """Il client invia sempre Bearer <LAYA_API_KEY>: /predict lo esige (401
    senza header) e /systemone lo tollera (forward-compat con futuri proxy)."""

    @staticmethod
    def _ok_response() -> Mock:
        response = Mock()
        response.status_code = 200
        response.raise_for_status = Mock()
        response.json = Mock(return_value={"result": {"choice": "ok"}})
        return response

    def test_post_invia_authorization(self) -> None:
        with (
            patch.dict(os.environ, {"LAYA_API_KEY": "sk-test"}),
            patch(
                "laya_service._session.post", return_value=self._ok_response()
            ) as post,
        ):
            LayaSystemOneService._call({"op": "noul"})
        self.assertEqual(
            post.call_args.kwargs["headers"]["Authorization"], "Bearer sk-test"
        )

    def test_default_sk_local_senza_env(self) -> None:
        env = {k: v for k, v in os.environ.items() if k != "LAYA_API_KEY"}
        with (
            patch.dict(os.environ, env, clear=True),
            patch(
                "laya_service._session.post", return_value=self._ok_response()
            ) as post,
        ):
            LayaSystemOneService._call({"op": "noul"})
        self.assertEqual(
            post.call_args.kwargs["headers"]["Authorization"], "Bearer sk-local"
        )


if __name__ == "__main__":
    unittest.main()

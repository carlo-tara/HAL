"""Contratto N24 (ToDo 2026-10-28, doc QwenCloud §HTTP connection reuse):

- `generate-image.py`: un'unica connessione keep-alive riusata tra le chiamate di
  `http_json` (il loop di polling non deve aprire una TCP+TLS nuova a ogni poll);
  contratto errori preservato: `RuntimeError` su HTTP >= 400, `URLError` su
  fallimento di rete;
- `extract.py`: nessun `httpx.Client` istanziato dentro funzioni invocate in loop
  — un solo client per timeout, riusato (factory `laya_client`);
- `cf_analytics_export.py`: niente `requests.post` nudo — una `Session` per run
  passata a `fetch_http_requests`.
"""

from __future__ import annotations

import http.server
import importlib.util
import json
import re
import sys
import threading
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parent.parent

GI_PATH = ROOT / "agents" / "a-design" / "illustrator" / "scripts" / "generate-image.py"
EXTRACT_PATH = ROOT / "agents" / "a-knowledge" / "scripts" / "extract.py"
CF_PATH = ROOT / "agents" / "a-seozoom" / "scripts" / "cf_analytics_export.py"


def _load_script(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class _CountingHandler(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"  # keep-alive lato server: riutilizza la TCP
    conns = 0
    reqs = 0

    def setup(self) -> None:  # una volta per TCP connection accettata
        type(self).conns += 1
        super().setup()

    def do_GET(self) -> None:
        type(self).reqs += 1
        body = json.dumps({"ok": True}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args) -> None:  # quiet
        pass


class _ErrorHandler(_CountingHandler):
    def do_GET(self) -> None:
        type(self).reqs += 1
        body = b"boom"
        self.send_response(404)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


class TestGenerateImageReuse(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.gi = _load_script(GI_PATH, "generate_image_reuse")

    def _serve(self, handler_cls):
        handler_cls.conns = 0
        handler_cls.reqs = 0
        server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler_cls)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(lambda: (server.shutdown(), server.server_close()))
        return f"http://127.0.0.1:{server.server_address[1]}/tasks/x"

    def test_due_chiamate_una_sola_connessione(self) -> None:
        url = self._serve(_CountingHandler)
        first = self.gi.http_json("GET", url, {}, timeout=10)
        second = self.gi.http_json("GET", url, {}, timeout=10)
        self.assertEqual(first, {"ok": True})
        self.assertEqual(second, {"ok": True})
        self.assertEqual(_CountingHandler.reqs, 2)
        self.assertEqual(_CountingHandler.conns, 1)

    def test_http_error_puo_raise_runtime(self) -> None:
        url = self._serve(_ErrorHandler)
        with self.assertRaises(RuntimeError) as ctx:
            self.gi.http_json("GET", url, {}, timeout=10)
        self.assertIn("HTTP 404", str(ctx.exception))

    def test_rete_giu_url_error(self) -> None:
        dead = "http://127.0.0.1:1/tasks/x"
        with self.assertRaises(urllib.error.URLError):
            self.gi.http_json("GET", dead, {}, timeout=5)


class TestSourceContracts(unittest.TestCase):
    def test_extract_un_solo_httpx_client(self) -> None:
        src = EXTRACT_PATH.read_text()
        self.assertEqual(src.count("httpx.Client("), 1)
        self.assertIn("def laya_client(", src)
        self.assertIn("client = laya_client(", src)

    def test_cf_niente_requests_post_nudo(self) -> None:
        src = CF_PATH.read_text()
        self.assertNotIn("requests.post(", src)
        self.assertIn("session: requests.Session", src)

    def test_generate_image_senza_cjk(self) -> None:
        src = GI_PATH.read_text()
        self.assertIsNone(re.search(r"[\u4e00-\u9fff]", src))

    def test_laya_client_identita(self) -> None:
        ex = _load_script(EXTRACT_PATH, "a_knowledge_extract_reuse")
        a = ex.laya_client(3.0)
        b = ex.laya_client(3.0)
        self.assertIs(a, b)


class TestCfSessionParam(unittest.TestCase):
    def test_fetch_usa_session_passata(self) -> None:
        cf = _load_script(CF_PATH, "cf_export_reuse")
        session = Mock()
        resp = Mock()
        resp.raise_for_status = Mock()
        resp.json.return_value = {"data": {"viewer": {"zones": []}}}
        session.post.return_value = resp
        out = cf.fetch_http_requests("z", "t", "a", "b", session=session)
        self.assertEqual(out, [])
        session.post.assert_called_once()


if __name__ == "__main__":
    unittest.main()

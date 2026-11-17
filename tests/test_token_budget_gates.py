"""Gate strutturali di token_budget.py (strategie token-minimization 2026-11).

Copre:
- S1-as-gate: ogni `s2_call` senza almeno una `s1_call` nella sessione registra
  la violazione `s1_skipped_before_s2` (telemetria: `s1_s2_ratio` 0.0).
- Lazy-load strutturale: `file_read` oltre la soglia di righe registra
  `file_read_full_over_limit` (protocollo: mai file interi > 100 righe).
- Entrambi i gate sono opt-out via env.
"""

from __future__ import annotations

import importlib.util
import json
import os
import re
import tempfile
import unittest
from pathlib import Path

_project_root = str(Path(__file__).resolve().parents[1])


def _load_tb():
    spec = importlib.util.spec_from_file_location(
        "token_budget",
        Path(_project_root) / "agents" / "a-agentzero" / "scripts" / "token_budget.py",
    )
    tb = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tb)
    return tb


class TokenBudgetGateTest(unittest.TestCase):
    def setUp(self):
        ctx = tempfile.TemporaryDirectory()
        self.addCleanup(ctx.cleanup)
        self.tmp = ctx.name
        self.old_env = {}
        for key in ("TOKEN_BUDGET_S1_GATE", "TOKEN_BUDGET_LAZY_MAX_LINES"):
            self.old_env[key] = os.environ.pop(key, None)
        self.addCleanup(
            lambda: [
                os.environ.__setitem__(k, v) if v is not None else os.environ.pop(k, None)
                for k, v in self.old_env.items()
            ]
        )

    def _session_after(self, tb, commands):
        """Esegue una sequenza di log in una tmpdir e ritorna la sessione."""
        old_cwd = os.getcwd()
        os.chdir(self.tmp)
        try:
            tb.cmd_init()
            for args in commands:
                tb.cmd_log(args)
            return json.loads(
                (Path("events") / "token-budget-session.json").read_text()
            )
        finally:
            os.chdir(old_cwd)

    def test_s2_senza_s1_registra_violazione(self):
        session = self._session_after(_load_tb(), [["s2_call"]])
        self.assertIn("s1_skipped_before_s2", session["violations"])

    def test_s1_prima_di_s2_nessuna_violazione(self):
        session = self._session_after(_load_tb(), [["s1_call"], ["s2_call"]])
        self.assertEqual(session["violations"], [])

    def test_s1_gate_opt_out(self):
        os.environ["TOKEN_BUDGET_S1_GATE"] = "0"
        session = self._session_after(_load_tb(), [["s2_call"]])
        self.assertEqual(session["violations"], [])

    def test_file_read_oltre_soglia_registra_violazione(self):
        session = self._session_after(_load_tb(), [["file_read", "app/main.py", "150"]])
        self.assertEqual(len(session["violations"]), 1)
        self.assertTrue(
            session["violations"][0].startswith("file_read_full_over_limit:")
        )

    def test_file_read_sotto_soglia_pulito(self):
        session = self._session_after(_load_tb(), [["file_read", "app/main.py", "80"]])
        self.assertEqual(session["violations"], [])

    def test_lazy_threshold_env_override(self):
        os.environ["TOKEN_BUDGET_LAZY_MAX_LINES"] = "20"
        session = self._session_after(_load_tb(), [["file_read", "README.md", "25"]])
        self.assertEqual(len(session["violations"]), 1)

    def test_violazione_automatica_finisce_nel_jsonl(self):
        tb = _load_tb()
        old_cwd = os.getcwd()
        os.chdir(self.tmp)
        try:
            tb.cmd_init()
            tb.cmd_log(["s2_call"])
            events = [
                json.loads(line)
                for line in (Path("events") / "token-budget.jsonl")
                .read_text()
                .splitlines()
            ]
            auto = [e for e in events if e.get("auto")]
            self.assertEqual(auto[0]["type"], "s1_skipped_before_s2")
            self.assertEqual(auto[0]["total"], 1)
        finally:
            os.chdir(old_cwd)


class TokenBudgetSessionIdTest(unittest.TestCase):
    """Contratto A1/A2: `session_id` in init + campo `session` su OGNI evento.

    Motiva: la coorte dell'esperimento `impersonate` (ToDo P1 hal_mcp_tools)
    deve essere contabile per sessioni DISTINTE, non per cluster orari (proxy).
    """

    def setUp(self):
        ctx = tempfile.TemporaryDirectory()
        self.addCleanup(ctx.cleanup)
        self.tmp = ctx.name

    def _chdir(self):
        old_cwd = os.getcwd()
        os.chdir(self.tmp)
        return old_cwd

    def _events(self):
        return [
            json.loads(line)
            for line in (Path("events") / "token-budget.jsonl")
            .read_text(encoding="utf-8")
            .splitlines()
            if line.strip()
        ]

    def test_init_genera_session_id_valido(self):
        tb = _load_tb()
        old = self._chdir()
        try:
            tb.cmd_init()
            session = json.loads(
                (Path("events") / "token-budget-session.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertRegex(session["session_id"], r"^[0-9a-f]{16}$")
        finally:
            os.chdir(old)

    def test_log_stampa_session_su_ogni_evento(self):
        tb = _load_tb()
        old = self._chdir()
        try:
            tb.cmd_init()
            sid = json.loads(
                (Path("events") / "token-budget-session.json").read_text(
                    encoding="utf-8"
                )
            )["session_id"]
            tb.cmd_log(["s2_call"])
            tb.cmd_log(["output", "120"])
            events = self._events()
            self.assertGreaterEqual(len(events), 2)
            for e in events:
                self.assertIn("session", e)
                self.assertEqual(e["session"], sid)
        finally:
            os.chdir(old)

    def test_due_sessioni_distinte_contano_due(self):
        """Coorte esatta: due cicli init+log → esattamente 2 session id distinti."""
        tb = _load_tb()
        old = self._chdir()
        try:
            tb.cmd_init()
            tb.cmd_log(["s2_call"])
            tb.cmd_init()
            tb.cmd_log(["s2_call"])
            sids = {
                e["session"] for e in self._events() if e.get("type") == "s2_call"
            }
            self.assertEqual(len(sids), 2)
            self.assertTrue(all(re.fullmatch(r"[0-9a-f]{16}", s or "") for s in sids))
        finally:
            os.chdir(old)

    def test_sessione_legacy_senza_id_degrada_a_none(self):
        """A2: SESSION_FILE pre-bump (senza session_id) → log non crasha, `session` null."""
        tb = _load_tb()
        old = self._chdir()
        try:
            tb.cmd_init()
            sfile = Path("events") / "token-budget-session.json"
            legacy = json.loads(sfile.read_text(encoding="utf-8"))
            legacy.pop("session_id", None)
            sfile.write_text(json.dumps(legacy), encoding="utf-8")
            tb.cmd_log(["s2_call"])
            events = self._events()
            last = events[-1]
            self.assertIsNone(last["session"])
        finally:
            os.chdir(old)


if __name__ == "__main__":
    unittest.main()

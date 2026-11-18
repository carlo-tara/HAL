"""Contratto HT-010 — runner pred.jsonl sul percorso prod Laya.

Il runner legge il gold set (validato via `scripts.gold_set_scoring.load_gold`,
fonte unica del contratto oro) e produce righe {id, choice, margin} chiamate
attraverso `LayaSystemOneService._call` (mockato nei test: nessuna rete). Il
margin NON è duplicato: viene da `laya_gate._top_and_margin` sulle
probabilities del servizio, come fa il gateway in produzione.

Regole lockate nel Plan HT-010 (accept 2026-11-18):
- choice/routing: choice = verdetto del servizio; margin = top1-top2 se il
  servizio riporta probabilities, altrimenti null;
- score: la numerica [0,1] va in banda {alto >=0.66, medio >=0.33, basso} con
  COSTANTI DI MODULO (non soglie gate — il gate misura margini, qui si misura
  una score); margin da probabilities se presenti, altrimenti null;
- noul: choice = intent stringa; margin null se il servizio non porta probs;
- astensione (_LayaAbstention): riga {choice: null, margin: null} + contatore
  nel summary per reason;
- resume idempotente: id gia presenti in pred.jsonl non vengono richiamati
  (salvo --fresh);
- regressione: se benchmark/gold_set/pred.jsonl esiste, gold+pred vengono
  misurati da score_gold_set e ogni id gold deve essere coperto (missing==0).
"""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

_ROOT = Path(__file__).resolve().parent.parent
_RUNNER_PATH = _ROOT / "benchmark" / "scripts" / "gold_set_pred_runner.py"
_spec = importlib.util.spec_from_file_location("gold_set_pred_runner", _RUNNER_PATH)
runner = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(runner)

from laya_service import _LayaAbstention  # noqa: E402

GOLD = [
    {
        "id": "c1",
        "family": "choice",
        "instruction": "Scegli A",
        "label": "a",
        "candidates": ["a", "b"],
    },
    {
        "id": "r1",
        "family": "routing",
        "instruction": "Instrada",
        "label": "x",
        "candidates": ["x", "y"],
    },
    {
        "id": "s1",
        "family": "score",
        "instruction": "Valuta",
        "label": "alto",
        "criteria": "rischio_regressione",
    },
    {"id": "n1", "family": "noul", "instruction": "Pre-filtro", "label": "intent"},
]


def _write_jsonl(path: Path, items: list[dict]) -> None:
    path.write_text("".join(json.dumps(i) + "\n" for i in items), encoding="utf-8")


class TestBandaScore(unittest.TestCase):
    """C: bucket {alto>=0.66, medio>=0.33, basso} — soglie di modulo, testate."""

    def test_boundary(self) -> None:
        self.assertEqual(runner._score_band(0.66), "alto")
        self.assertEqual(runner._score_band(0.9), "alto")
        self.assertEqual(runner._score_band(0.659), "medio")
        self.assertEqual(runner._score_band(0.33), "medio")
        self.assertEqual(runner._score_band(0.329), "basso")
        self.assertEqual(runner._score_band(0.0), "basso")

    def test_costanti_dichiarate(self) -> None:
        self.assertEqual(runner.BAND_ALTO_MIN, 0.66)
        self.assertEqual(runner.BAND_MEDIO_MIN, 0.33)


class TestPredRighe(unittest.TestCase):
    """A+B: righe {id, choice, margin} con margin single-source e astensioni nulle."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.gold = Path(self.tmp.name) / "gold.jsonl"
        self.pred = Path(self.tmp.name) / "pred.jsonl"
        _write_jsonl(self.gold, GOLD)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _run(self, fake_call, fresh: bool = False) -> dict:
        with mock.patch.object(
            runner.LayaSystemOneService, "_call", side_effect=fake_call
        ):
            return runner.build_predictions(self.gold, self.pred, fresh=fresh)

    def test_choice_con_probabilities_riprende_margin_vero(self) -> None:
        calls = []

        def fake(payload):
            calls.append(payload)
            return {"choice": "a", "probabilities": {"a": 0.6, "b": 0.25}}

        self._run(fake)
        rows = {
            json.loads(l)["id"]: json.loads(l)
            for l in self.pred.read_text().splitlines()
            if l.strip()
        }
        # _answer_probs rinormalizza sulle sole candidate (comportamento prod
        # del gate): margin = (0.6-0.25)/(0.6+0.25), non la grezza 0.35
        self.assertEqual(rows["c1"]["id"], "c1")
        self.assertEqual(rows["c1"]["choice"], "a")
        self.assertAlmostEqual(rows["c1"]["margin"], 0.35 / 0.85, places=12)
        self.assertEqual(calls[0]["task"], "choice")
        self.assertEqual(calls[0]["options"], ["a", "b"])

    def test_routing_senza_probabilities_margin_nullo(self) -> None:
        def fake(payload):
            return {"route": "y"}

        self._run(fake)
        row = json.loads(self.pred.read_text().splitlines()[1])
        self.assertEqual(row, {"id": "r1", "choice": "y", "margin": None})

    def test_score_banda_pi_probabilities(self) -> None:
        def fake(payload):
            if payload["task"] == "score":
                return {
                    "score": 0.9,
                    "probabilities": {"alto": 0.5, "medio": 0.3, "basso": 0.2},
                }
            return {"choice": "a", "probabilities": {"a": 0.6, "b": 0.25}}

        self._run(fake)
        row = json.loads(self.pred.read_text().splitlines()[2])
        self.assertEqual(row["id"], "s1")
        self.assertEqual(row["choice"], "alto")
        self.assertEqual(row["margin"], 0.2)

    def test_score_numerica_secca_banda_senza_margin(self) -> None:
        def fake(payload):
            if payload["task"] == "score":
                return {"score": 0.42}
            return {"choice": "a", "probabilities": {"a": 0.6, "b": 0.25}}

        self._run(fake)
        row = json.loads(self.pred.read_text().splitlines()[2])
        self.assertEqual(row["choice"], "medio")
        self.assertIsNone(row["margin"])

    def test_astensione_riga_null_e_contatore(self) -> None:
        def fake(payload):
            t = payload["task"]
            if t == "noul":
                raise _LayaAbstention("noul_gpu_excluded")
            if t == "score":
                return {"score": 0.5}
            opts = payload.get("options") or payload.get("routes") or ["a"]
            return {"choice": opts[0], "probabilities": {opts[0]: 0.6, opts[1]: 0.25}}

        summary = self._run(fake)
        rows = {
            json.loads(l)["id"]: json.loads(l)
            for l in self.pred.read_text().splitlines()
            if l.strip()
        }
        self.assertEqual(rows["n1"], {"id": "n1", "choice": None, "margin": None})
        self.assertEqual(summary["abstain_by_reason"], {"noul_gpu_excluded": 1})
        self.assertEqual(summary["requested"], 4)

    def test_bypass_servizio_e_astensione(self) -> None:
        """Il by-pass onesto (inner.bypass) non e un verdetto: va in abstain."""

        def fake(payload):
            t = payload["task"]
            if t == "score":
                return {"bypass": True, "reason": "score_not_discriminative"}
            opts = payload.get("options") or payload.get("routes")
            if not opts:
                return {"result": "intent"}
            return {"choice": opts[0], "probabilities": {opts[0]: 0.6, opts[1]: 0.25}}

        summary = self._run(fake)
        rows = {
            json.loads(l)["id"]: json.loads(l)
            for l in self.pred.read_text().splitlines()
            if l.strip()
        }
        self.assertEqual(rows["s1"]["choice"], None)
        self.assertEqual(rows["n1"]["choice"], "intent")
        self.assertEqual(
            summary["abstain_by_reason"], {"bypass:score_not_discriminative": 1}
        )

    def test_oro_invalido_esce_due(self) -> None:
        bad = Path(self.tmp.name) / "bad.jsonl"
        _write_jsonl(
            bad, [{"id": "x", "family": "nope", "instruction": "i", "label": "l"}]
        )
        rc = runner.main([str(bad), str(self.pred)])
        self.assertEqual(rc, 2)


class TestResumeFresh(unittest.TestCase):
    """D: resume idempotente; --fresh rigenera tutto."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.gold = Path(self.tmp.name) / "gold.jsonl"
        self.pred = Path(self.tmp.name) / "pred.jsonl"
        _write_jsonl(self.gold, GOLD)
        _write_jsonl(self.pred, [{"id": "c1", "choice": "a", "margin": 0.35}])

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_resume_non_richiama_id_esistenti(self) -> None:
        seen = []

        def fake(payload):
            seen.append(payload["text"])
            return {"choice": "a", "probabilities": {"a": 0.6, "b": 0.25}}

        with mock.patch.object(runner.LayaSystemOneService, "_call", side_effect=fake):
            summary = runner.build_predictions(self.gold, self.pred, fresh=False)
        self.assertNotIn("Scegli A", seen)
        self.assertEqual(summary["skipped_existing"], 1)
        rows = [json.loads(l) for l in self.pred.read_text().splitlines() if l.strip()]
        self.assertEqual([r["id"] for r in rows], ["c1", "r1", "s1", "n1"])
        self.assertEqual(rows[0]["margin"], 0.35)

    def test_fresh_richiama_anche_id_esistenti(self) -> None:
        seen = []

        def fake(payload):
            seen.append(payload["text"])
            return {"choice": "b", "probabilities": {"b": 0.7, "a": 0.2}}

        with mock.patch.object(runner.LayaSystemOneService, "_call", side_effect=fake):
            summary = runner.build_predictions(self.gold, self.pred, fresh=True)
        self.assertIn("Scegli A", seen)
        self.assertEqual(summary["skipped_existing"], 0)
        row = json.loads(self.pred.read_text().splitlines()[0])
        self.assertEqual(row["choice"], "b")


class TestRegressioneReale(unittest.TestCase):
    """Acceptance HT-010: run scoring inclusa in test-unit via discovery.

    Esegue sul gold set versionato (123 label confermate 2026-11-18) quando
    pred.jsonl esiste; skip VISIBILE se assente (mai green silenzioso).
    """

    GOLD_PATH = _ROOT / "benchmark" / "gold_set" / "gold_set.jsonl"
    PRED_PATH = _ROOT / "benchmark" / "gold_set" / "pred.jsonl"

    def setUp(self) -> None:
        from scripts.gold_set_scoring import load_gold

        self.gold = load_gold(self.GOLD_PATH)

    def test_pred_assente_skip_visibile(self) -> None:
        if not self.PRED_PATH.exists():
            self.skipTest("pred.jsonl assente: run reale HT-010 non ancora eseguito")

    def test_oro_e_pred_coperti_e_struttura_sintesi(self) -> None:
        from scripts.gold_set_scoring import load_predictions, score_gold_set

        if not self.PRED_PATH.exists():
            self.skipTest("pred.jsonl assente: run reale HT-010 non ancora eseguito")
        predictions = load_predictions(self.PRED_PATH)
        summary = score_gold_set(self.gold, predictions)
        self.assertEqual(summary["total"], len(self.gold))
        self.assertEqual(summary["missing"], 0)
        self.assertIsInstance(summary["hit_rate"], float)
        self.assertGreaterEqual(summary["hit_rate"], 0.0)
        self.assertLessEqual(summary["hit_rate"], 1.0)
        self.assertEqual(set(summary["by_band"]), {"direct", "caution", "escalate"})
        for band in summary["by_band"].values():
            self.assertIsInstance(band["n"], int)
            self.assertIsInstance(band["accuracy"], float)


if __name__ == "__main__":
    unittest.main()

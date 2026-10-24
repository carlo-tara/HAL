"""Gate BENCH: confronto baseline vs middleware con overhead Laya.

Acceptance:
- report per coppia con overhead Laya in latenza e token
- status tecnico, rubriche euristiche, validazione semantica separati
- promozione bloccata con output troncati o evidenza mancante
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

_project_root = str(Path(__file__).resolve().parent.parent)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from benchmark.scripts.bench_comparison import (
    build_bench_report,
    calculate_laya_overhead,
    check_promotion,
    render_bench_report,
    separate_status,
)


class TestBenchPromotion(unittest.TestCase):
    """Verifica i criteri di promozione."""

    def test_promotion_blocked_by_truncation(self):
        """Promozione bloccata se >10% stage troncati."""
        rows = []
        metrics_rows = [
            {"system": "system2", "status": "ok"},
            {"system": "system2", "status": "truncated"},
            {"system": "system2", "status": "truncated"},
        ]
        result = check_promotion(rows, metrics_rows)
        self.assertFalse(result["promoted"])
        self.assertTrue(len(result["issues"]) > 0)

    def test_promotion_passed_clean(self):
        """Promozione passata se nessun problema."""
        rows = []
        metrics_rows = [
            {"system": "system2", "status": "ok"},
            {"system": "system2", "status": "ok"},
        ]
        result = check_promotion(rows, metrics_rows)
        self.assertTrue(result["promoted"])
        self.assertEqual(result["issues"], [])

    def test_promotion_blocked_by_high_overhead(self):
        """Promozione bloccata se overhead token >3×."""
        rows = [
            {
                "model": "phi3:mini",
                "base_total": 1000,
                "run_total": 4000,
                "has_source": False,
            }
        ]
        metrics_rows = [{"system": "system2", "status": "ok"}]
        result = check_promotion(rows, metrics_rows)
        self.assertFalse(result["promoted"])
        self.assertTrue(any("eccessivo" in i for i in result["issues"]))


class TestBenchOverhead(unittest.TestCase):
    """Verifica il calcolo dell'overhead Laya."""

    def test_overhead_calculation(self):
        """L'overhead deve calcolare delta token medio per modello."""
        rows = [
            {"model": "phi3:mini", "base_input": 100, "run_input": 180},
            {"model": "phi3:mini", "base_input": 200, "run_input": 290},
            {"model": "llama3.2:1b", "base_input": 150, "run_input": 240},
        ]
        metrics_rows = []
        result = calculate_laya_overhead(rows, metrics_rows)
        self.assertIn("phi3:mini", result)
        self.assertEqual(result["phi3:mini"]["samples"], 2)
        # Delta medio: (80 + 90) / 2 = 85
        self.assertEqual(result["phi3:mini"]["avg_token_overhead"], 85.0)
        self.assertEqual(result["phi3:mini"]["max_token_overhead"], 90)
        self.assertEqual(result["phi3:mini"]["min_token_overhead"], 80)


class TestBenchStatus(unittest.TestCase):
    """Verifica la separazione dello status."""

    def test_separate_status_structure(self):
        """Lo status deve avere tre sezioni distinte."""
        rows = [
            {
                "model": "phi3:mini",
                "test_id": "matematica",
                "base_total": 1000,
                "run_total": 3500,
                "has_source": False,
                "stages": 1,
            },
            {
                "model": "phi3:mini",
                "test_id": "programmazione",
                "base_total": None,
                "run_total": 2000,
                "has_source": True,
                "stages": 3,
            },
        ]
        metrics_rows = []
        result = separate_status(rows, metrics_rows)
        self.assertIn("technical", result)
        self.assertIn("heuristic", result)
        self.assertIn("semantic", result)

    def test_technical_counts(self):
        """I conteggi tecnici devono essere corretti."""
        rows = [
            {
                "model": "m",
                "test_id": "t1",
                "base_total": 100,
                "run_total": 200,
                "has_source": False,
                "stages": 1,
            },
            {
                "model": "m",
                "test_id": "t2",
                "base_total": None,
                "run_total": 300,
                "has_source": True,
                "stages": 2,
            },
        ]
        metrics_rows = []
        result = separate_status(rows, metrics_rows)
        tech = result["technical"]
        self.assertEqual(tech["total_pairs"], 2)
        self.assertEqual(tech["pairs_with_both_totals"], 1)
        self.assertEqual(tech["pairs_with_source"], 1)


class TestBenchReport(unittest.TestCase):
    """Verifica la generazione del report completo."""

    def setUp(self):
        # Crea cartelle temporanee con dati fittizi
        self.tmpdir = Path(tempfile.mkdtemp())
        self.baseline_dir = self.tmpdir / "baseline"
        self.run_dir = self.tmpdir / "run"
        self.baseline_dir.mkdir()
        self.run_dir.mkdir()

        # Baseline: file <n>_<test>_<model>.json
        (self.baseline_dir / "1_matematica_phi3:mini.json").write_text(
            json.dumps(
                {
                    "model": "phi3:mini",
                    "test_id": "matematica",
                    "tokens": {"input": 100, "output": 200, "total": 300},
                }
            )
        )
        (self.baseline_dir / "1_programmazione_phi3:mini.json").write_text(
            json.dumps(
                {
                    "model": "phi3:mini",
                    "test_id": "programmazione",
                    "tokens": {"input": 150, "output": 300, "total": 450},
                }
            )
        )

        # Run: results.json
        (self.run_dir / "results.json").write_text(
            json.dumps(
                {
                    "results": [
                        {
                            "model": "phi3:mini",
                            "test_id": "matematica",
                            "tokens": {"input": 180, "output": 220, "total": 400},
                            "workflow": [{"stage": "risposta_finale"}],
                            "system1": {"has_source": False},
                        },
                        {
                            "model": "phi3:mini",
                            "test_id": "programmazione",
                            "tokens": {"input": 240, "output": 350, "total": 590},
                            "workflow": [
                                {"stage": "piano_iniziale"},
                                {"stage": "risposta_finale"},
                            ],
                            "system1": {"has_source": True},
                        },
                    ]
                }
            )
        )

    def tearDown(self):
        import shutil

        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_build_report_succeeds(self):
        """build_bench_report deve restituire un dict con tutte le sezioni."""
        report = build_bench_report(self.baseline_dir, self.run_dir)
        self.assertIn("rows", report)
        self.assertIn("summary", report)
        self.assertIn("overhead", report)
        self.assertIn("status", report)
        self.assertIn("promotion", report)
        self.assertEqual(len(report["rows"]), 2)

    def test_render_report_contains_sections(self):
        """render_bench_report deve contenere tutte le sezioni."""
        report = build_bench_report(self.baseline_dir, self.run_dir)
        text = render_bench_report(report)
        self.assertIn("LAYA OVERHEAD", text)
        self.assertIn("STATUS TECNICO", text)
        self.assertIn("RUBRICHE EURISTICHE", text)
        self.assertIn("VALIDAZIONE SEMANTICA", text)
        self.assertIn("PROMOZIONE", text)
        self.assertIn("DETTAGLIO COPPIE", text)


if __name__ == "__main__":
    unittest.main()

"""Rilevamento ripetizione blocco <strategia_system1_laya> in output modello.

Acceptance:
- percentuale di risposte che riportano il blocco nell'output
- valori scritti nella voce
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

_project_root = str(Path(__file__).resolve().parent.parent)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from benchmark.runner.system2_metrics import (
    STRATEGIA_BLOCK_MARKER,
    count_strategy_block_occurrences,
    detect_strategy_block_in_output,
)


class TestStrategyBlockDetection(unittest.TestCase):
    """Verifica rilevamento blocco strategia in output."""

    def test_block_present_returns_true(self):
        """Marker presente → True."""
        response = "Risposta.\n\n<strategia_system1_laya>\nGuida...\n</strategia_system1_laya>\nFine."
        self.assertTrue(detect_strategy_block_in_output(response))

    def test_block_absent_returns_false(self):
        """Marker assente → False."""
        response = "Risposta normale senza blocchi."
        self.assertFalse(detect_strategy_block_in_output(response))

    def test_multiple_occurrences_counted(self):
        """Più occorrenze contate correttamente."""
        response = "<strategia_system1_laya>A</strategia_system1_laya> x <strategia_system1_laya>B</strategia_system1_laya>"
        self.assertEqual(count_strategy_block_occurrences(response), 2)

    def test_empty_response_returns_false(self):
        """Response vuota → False."""
        self.assertFalse(detect_strategy_block_in_output(""))

    def test_marker_constant_defined(self):
        """Il marker deve essere definito."""
        self.assertEqual(STRATEGIA_BLOCK_MARKER, "<strategia_system1_laya>")


if __name__ == "__main__":
    unittest.main()

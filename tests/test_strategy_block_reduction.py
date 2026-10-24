"""Riduzione blocco <strategia_system1_laya> ripetuto in ogni stage.

Acceptance:
- implementato nel canonico e sincronizzato
- token prima/dopo misurati
- rubriche euristiche e validazione semantica invariate
- se guadagno trascurabile, chiusura senza modifiche
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

_project_root = str(Path(__file__).resolve().parent.parent)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from benchmark.runner.benchmark_models import system1_prompt


class TestStrategyBlockReduction(unittest.TestCase):
    """Verifica riduzione blocco strategia."""

    def test_block_still_generated(self):
        """Il blocco deve ancora essere generato."""
        guide = {
            "task_family": "translation",
            "execution_mode": "single_pass",
            "guidance": "Traduci fedelmente",
        }
        prompt = {"prompt": "Testo di prova"}
        result = system1_prompt(prompt, guide)
        self.assertIn("<strategia_system1_laya>", result)
        self.assertIn("</strategia_system1_laya>", result)

    def test_disclaimer_removed(self):
        """La disclaimer lunga deve essere rimossa."""
        guide = {
            "task_family": "translation",
            "execution_mode": "single_pass",
            "guidance": "Traduci fedelmente",
        }
        prompt = {"prompt": "Testo di prova"}
        result = system1_prompt(prompt, guide)
        self.assertNotIn("non modifica il compito", result)
        self.assertNotIn("Guida metodologica preliminare", result)

    def test_essential_fields_present(self):
        """I campi essenziali devono essere presenti."""
        guide = {
            "task_family": "coding",
            "execution_mode": "plan_then_solve",
            "guidance": "Estrai requisiti",
        }
        prompt = {"prompt": "Scrivi una funzione"}
        result = system1_prompt(prompt, guide)
        self.assertIn("Categoria: coding", result)
        self.assertIn("Modalità: plan_then_solve", result)
        self.assertIn("Strategia: Estrai requisiti", result)

    def test_block_shorter_than_before(self):
        """Il blocco deve essere più corto della versione precedente (~178 chars overhead)."""
        guide = {
            "task_family": "translation",
            "execution_mode": "single_pass",
            "guidance": "Traduci fedelmente",
        }
        prompt = {"prompt": "Testo di prova"}
        result = system1_prompt(prompt, guide)
        block_start = result.find("<strategia_system1_laya>")
        block_end = result.find("</strategia_system1_laya>") + len(
            "</strategia_system1_laya>"
        )
        block = result[block_start:block_end]
        # Versione precedente: ~178 chars overhead; nuova dovrebbe essere < 130
        self.assertLess(len(block), 130)


if __name__ == "__main__":
    unittest.main()

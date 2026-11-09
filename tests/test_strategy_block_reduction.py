"""Riduzione blocco <strategia_system1_laya> ripetuto in ogni stage.

Acceptance:
- implementato nel canonico e sincronizzato
- token prima/dopo misurati
- rubriche euristiche e validazione semantica invariate
- se guadagno trascurabile, chiusura senza modifiche

2026-11-09 (reverse port rv7): la rimozione della disclaimer e il tetto <130
char erano deviazioni gateway; il canonico (mirror byte-identico, guardia
test_sync_hal_system2.py) mantiene la riga di disclaimer e il test canonico
asserta esplicitamente "guida metodologica" presente. Riduzione oggi = una
sola copia del blocco per stage (verificata in
test_strategy_block_repetition.py); qui si pinna la forma canonica.
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

    def test_disclaimer_not_repeated(self):
        """La disclaimer canonica compare una sola copia nel blocco per stage.

        2026-11-09: riallineato al canonico (test_disclaimer_removed -> qui):
        la riga "Guida metodologica preliminare..." e' parte del contratto
        canonico (test canonico: "guida metodologica" in enriched). Il gate
        prova che non risulti duplicata dentro il blocco di stage.
        """
        guide = {
            "task_family": "translation",
            "execution_mode": "single_pass",
            "guidance": "Traduci fedelmente",
        }
        prompt = {"prompt": "Testo di prova"}
        result = system1_prompt(prompt, guide)
        self.assertEqual(result.count("Guida metodologica preliminare"), 1)
        self.assertEqual(result.count("non modifica il compito"), 1)

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

    def test_block_matches_canonical_shape(self):
        """Il blocco e' esattamente il template canonico (guardia anti-deriva).

        2026-11-09: il vecchio budget <130 char era una deviazione gateway poi
        sovrascritta dal reverse port; il canonico produce il blocco completo
        (~215 char con questa guida) e la guardia byte-identica lo impone.
        Pinnare il template esatto e' la copertura rappresentabile: qualsiasi
        rigonfiamento o divergenza dal canonico fa fallire questo test.
        """
        guide = {
            "task_family": "translation",
            "execution_mode": "single_pass",
            "guidance": "Traduci fedelmente",
        }
        prompt = {"prompt": "Testo di prova"}
        result = system1_prompt(prompt, guide)
        expected_block = (
            "<strategia_system1_laya>\n"
            "Guida metodologica preliminare; non modifica il compito, i dati o il formato richiesto.\n"
            "Categoria: translation.\n"
            "Modalità: single_pass.\n"
            "Strategia: Traduci fedelmente\n"
            "</strategia_system1_laya>"
        )
        self.assertIn(expected_block, result)
        self.assertEqual(result.count("<strategia_system1_laya>"), 1)


if __name__ == "__main__":
    unittest.main()

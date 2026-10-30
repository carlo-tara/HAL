"""Contratto P2 (ToDo 2026-10-28, voce prezzi cache effettivi):

``qwen3.8-flash`` e ``qwen3.8-max`` non rispettano i rapporti fissi 10%/125%
(variano per regione, doc QwenCloud §billing); stime basate su costanti
darebbero classifiche errate sui profili cost-oriented. Test con fixture a
rapporti alterati.
"""

from __future__ import annotations

import unittest

from benchmark.runner.cache_pricing import (
    DEFAULT_RATIOS,
    cache_cost_summary,
    effective_input_tokens,
    resolve_ratios,
)


class TestResolveRatios(unittest.TestCase):
    def test_regione_alternata_rispetta_tabella(self) -> None:
        eu = resolve_ratios("orcarouter/qwen/qwen3.8-flash", "eu-central-1")
        self.assertEqual(eu["hit_ratio"], 0.20)  # fixture a rapporto alterato
        ap = resolve_ratios("qwen3.8-flash")
        self.assertEqual(ap["hit_ratio"], 0.10)
        self.assertNotEqual(eu["hit_ratio"], ap["hit_ratio"])

    def test_default_documentato_per_regione_mancante(self) -> None:
        ratios = resolve_ratios("qwen3.8-flash", "us-east-1")
        self.assertEqual(ratios, resolve_ratios("qwen3.8-flash", None))

    def test_modello_noto_usa_default_del_modello(self) -> None:
        # deepseek: rapporto diverso dalle costanti globali
        self.assertEqual(resolve_ratios("deepseek-v4.1-flash")["hit_ratio"], 0.02)

    def test_modello_sconosciuto_alle_costanti_globali(self) -> None:
        self.assertEqual(resolve_ratios("modello-che-non-c-e"), DEFAULT_RATIOS)


class TestEffectiveCost(unittest.TestCase):
    def test_eu_hit_raddoppiato(self) -> None:
        # 1000 input: 500 cached + 100 creation + 400 freschi
        eff = effective_input_tokens(
            1000, 500, 100, model="qwen3.8-flash", region="eu-central-1"
        )
        # 400 + 100*1.25 + 500*0.20 = 625
        self.assertAlmostEqual(eff, 625.0)

    def test_cached_maggiore_di_input_e_saturato(self) -> None:
        eff = effective_input_tokens(100, 500, 0, model="qwen3.8-flash")
        self.assertLessEqual(eff, 100 * DEFAULT_RATIOS["hit_ratio"] * 2)

    def test_savings_su_eventi(self) -> None:
        summary = cache_cost_summary(
            [
                {"tokens_in": 1000, "cached_tokens": 500, "model": "qwen3.8-flash"},
                {"tokens_in": 0, "cached_tokens": None, "model": "qwen3.8-flash"},
            ]
        )
        self.assertEqual(summary["nominal_input_total"], 1000)
        self.assertAlmostEqual(summary["effective_input_total"], 550.0)
        self.assertAlmostEqual(summary["savings_pct"], 45.0)


if __name__ == "__main__":
    unittest.main()

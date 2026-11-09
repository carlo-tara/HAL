"""Contratto HT-008 — infrastruttura gold set System 1 (scoring, schema, CLI).

Estratto ciclabile di HT-005: schema del dataset, funzione di scoring
(hit-rate + accuracy per fascia di margine) e validazione; l'etichettatura
vera resta umana in HT-005. Le soglie di fascia vengono da `laya_gate`
(fonte unica delle soglie System 1), non duplicate.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from laya_gate import ESCALATE_MARGIN, FAST_MARGIN
from scripts.gold_set_scoring import (
    GOLD_FAMILIES,
    load_gold,
    load_predictions,
    main,
    score_gold_set,
    validate_gold_item,
)

SCHEMA_PATH = (
    Path(__file__).resolve().parent.parent / "benchmark/config/gold_set.schema.json"
)


def _gold_items() -> list[dict]:
    return [
        {
            "id": "c1",
            "family": "choice",
            "instruction": "Scegli A",
            "label": "a",
            "candidates": ["a", "b"],
        },
        {
            "id": "c2",
            "family": "choice",
            "instruction": "Scegli B",
            "label": "b",
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
            "instruction": "Valuta rischio",
            "label": "alto",
            "criteria": "rischio_regressione",
        },
        {"id": "n1", "family": "noul", "instruction": "Pre-filtro", "label": "intent"},
    ]


def _predictions() -> dict[str, dict]:
    return {
        "c1": {"choice": "a", "margin": 0.6},  # direct, hit
        "c2": {"choice": "b", "margin": 0.2},  # caution, hit
        "r1": {"choice": "y", "margin": 0.05},  # escalate, miss
        "n1": {"choice": "intent", "margin": 0.7},  # direct, hit
        # s1 senza previsione → missing
    }


class TestValidation(unittest.TestCase):
    def test_item_valid_passa(self) -> None:
        for item in _gold_items():
            validate_gold_item(item)

    def test_famiglia_sconosciuta_errore(self) -> None:
        with self.assertRaises(ValueError):
            validate_gold_item(
                {"id": "x", "family": "summarize", "instruction": "i", "label": "l"}
            )

    def test_label_mancante_o_vuota_errore(self) -> None:
        base = {"id": "x", "family": "noul", "instruction": "i"}
        with self.assertRaises(ValueError):
            validate_gold_item({**base, "label": ""})
        with self.assertRaises(ValueError):
            validate_gold_item(base)

    def test_choice_richiede_candidati_e_label_al_loro_interno(self) -> None:
        with self.assertRaises(ValueError):
            validate_gold_item(
                {"id": "x", "family": "choice", "instruction": "i", "label": "a"}
            )
        with self.assertRaises(ValueError):
            validate_gold_item(
                {
                    "id": "x",
                    "family": "choice",
                    "instruction": "i",
                    "label": "c",
                    "candidates": ["a", "b"],
                }
            )
        with self.assertRaises(ValueError):
            validate_gold_item(
                {
                    "id": "x",
                    "family": "choice",
                    "instruction": "i",
                    "label": "a",
                    "candidates": ["a"],
                }
            )

    def test_score_richiede_criteria(self) -> None:
        with self.assertRaises(ValueError):
            validate_gold_item(
                {"id": "x", "family": "score", "instruction": "i", "label": "alto"}
            )

    def test_id_duplicato_in_caricamento_errore(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "gold.jsonl"
            path.write_text(
                "\n".join(json.dumps(i) for i in [_gold_items()[4], _gold_items()[4]])
                + "\n"
            )
            with self.assertRaises(ValueError):
                load_gold(path)


class TestScoring(unittest.TestCase):
    def setUp(self) -> None:
        self.summary = score_gold_set(_gold_items(), _predictions())

    def test_hit_rate_ed_conteggi(self) -> None:
        self.assertEqual(self.summary["total"], 5)
        self.assertEqual(self.summary["evaluated"], 4)
        self.assertEqual(self.summary["matched"], 3)
        self.assertEqual(self.summary["missing"], 1)
        self.assertAlmostEqual(self.summary["hit_rate"], 0.75)

    def test_fasce_di_margin_usano_le_soglie_laya_gate(self) -> None:
        bands = self.summary["by_band"]
        self.assertEqual(bands["direct"]["n"], 2)
        self.assertAlmostEqual(bands["direct"]["accuracy"], 1.0)
        self.assertEqual(bands["caution"]["n"], 1)
        self.assertAlmostEqual(bands["caution"]["accuracy"], 1.0)
        self.assertEqual(bands["escalate"]["n"], 1)
        self.assertAlmostEqual(bands["escalate"]["accuracy"], 0.0)
        self.assertAlmostEqual(FAST_MARGIN, 0.5)
        self.assertAlmostEqual(ESCALATE_MARGIN, 0.15)

    def test_predizioni_senza_oro_sono_ignorate(self) -> None:
        preds = {**_predictions(), "zz": {"choice": "q", "margin": 0.9}}
        summary = score_gold_set(_gold_items(), preds)
        self.assertEqual(summary["ignored"], 1)
        self.assertEqual(summary["evaluated"], 4)

    def test_load_predictions_normalizza_righe(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "pred.jsonl"
            path.write_text(
                '{"id": "a", "choice": "x", "margin": 0.6, "extra": 1}\n\n'
                '{"id": "b", "choice": "y"}\n'
            )
            preds = load_predictions(path)
        self.assertEqual(preds["a"], {"choice": "x", "margin": 0.6})
        self.assertEqual(preds["b"], {"choice": "y", "margin": None})


class TestCli(unittest.TestCase):
    def test_main_scrive_json_ed_esce_zero(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            gold = Path(tmp) / "gold.jsonl"
            gold.write_text("\n".join(json.dumps(i) for i in _gold_items()) + "\n")
            pred = Path(tmp) / "pred.jsonl"
            pred.write_text(
                "\n".join(json.dumps({"id": k, **v}) for k, v in _predictions().items())
                + "\n"
            )
            exit_code = main([str(gold), str(pred)])
            self.assertEqual(exit_code, 0)

    def test_main_oro_invalido_esce_due(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            gold = Path(tmp) / "gold.jsonl"
            gold.write_text(
                json.dumps(
                    {"id": "x", "family": "nope", "instruction": "i", "label": "l"}
                )
                + "\n"
            )
            pred = Path(tmp) / "pred.jsonl"
            pred.write_text("")
            self.assertEqual(main([str(gold), str(pred)]), 2)


class TestSchemaFile(unittest.TestCase):
    def test_schema_presente_e_coerente_col_script(self) -> None:
        schema = json.loads(SCHEMA_PATH.read_text())
        self.assertEqual(
            set(schema["properties"]["family"]["enum"]), set(GOLD_FAMILIES)
        )
        self.assertIn("label", schema["required"])
        self.assertIn("instruction", schema["required"])


if __name__ == "__main__":
    unittest.main()

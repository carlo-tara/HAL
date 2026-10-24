"""Confronto token baseline vs middleware per (modello, test)."""

from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from benchmark.scripts import compare_tokens as ct


def tokens(input_: int | None, output: int | None) -> dict:
    total = None if input_ is None or output is None else input_ + output
    return {"input": input_, "output": output, "reasoning": None, "total": total}


def write_baseline(folder: Path, entries: list[tuple[str, str, dict]]) -> None:
    for index, (model, test_id, tok) in enumerate(entries, start=1):
        name = f"{index:02d}_{test_id}_{model.replace(':', '_')}.json"
        payload = {"model": model, "test_id": test_id, "tokens": tok, "status": "ok"}
        (folder / name).write_text(json.dumps(payload), encoding="utf-8")


def result(model: str, test_id: str, tok: dict, stages: int, has_source: bool) -> dict:
    return {
        "model": model,
        "test_id": test_id,
        "tokens": tok,
        "status": "ok" if tok["total"] is not None else "error",
        "workflow": [{"stage": f"s{n}"} for n in range(stages)],
        "system1": {"has_source": has_source},
    }


def write_run(folder: Path, results: list[dict]) -> None:
    (folder / "results.json").write_text(
        json.dumps({"results": results}), encoding="utf-8"
    )


class CompareTokensTest(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.baseline = Path(tmp.name) / "baseline"
        self.run_dir = Path(tmp.name) / "run"
        self.baseline.mkdir()
        self.run_dir.mkdir()

    def rows(self, **kwargs) -> list[dict]:
        return ct.compare(
            ct.load_baseline(self.baseline), ct.load_run(self.run_dir), **kwargs
        )

    def test_row_reports_tokens_stages_and_ratio(self) -> None:
        write_baseline(self.baseline, [("phi3:mini", "estrazione", tokens(2050, 500))])
        write_run(
            self.run_dir,
            [result("phi3:mini", "estrazione", tokens(10000, 5000), 11, True)],
        )
        (row,) = self.rows()
        self.assertEqual(row["model"], "phi3:mini")
        self.assertEqual(row["test_id"], "estrazione")
        self.assertEqual((row["base_input"], row["base_total"]), (2050, 2550))
        self.assertEqual((row["run_input"], row["run_total"]), (10000, 15000))
        self.assertEqual(row["stages"], 11)
        self.assertAlmostEqual(row["ratio_total"], 15000 / 2550)

    def test_unavailable_tokens_are_not_summed_and_have_no_ratio(self) -> None:
        write_baseline(
            self.baseline,
            [
                ("qwen", "a", tokens(100, 100)),
                ("qwen", "b", tokens(100, 100)),
            ],
        )
        write_run(
            self.run_dir,
            [
                result("qwen", "a", tokens(300, 100), 1, False),
                result("qwen", "b", tokens(None, None), 6, True),
            ],
        )
        rows = {row["test_id"]: row for row in self.rows()}
        self.assertIsNone(rows["b"]["run_total"])
        self.assertIsNone(rows["b"]["ratio_total"])
        summary = ct.summarize(list(rows.values()))["qwen"]
        self.assertEqual(summary["base_total"], 200)
        self.assertEqual(summary["run_total"], 400)
        self.assertEqual(summary["excluded"], 1)
        self.assertAlmostEqual(summary["ratio_total"], 2.0)

    def test_flags_identical_baseline_input_on_source_test(self) -> None:
        write_baseline(
            self.baseline,
            [(m, "sintesi", tokens(2050, 100)) for m in ("a", "b", "c")],
        )
        write_run(
            self.run_dir,
            [result(m, "sintesi", tokens(5000, 100), 6, True) for m in ("a", "b", "c")],
        )
        self.assertTrue(all(row["baseline_input_sospetto"] for row in self.rows()))

    def test_no_flag_when_inputs_differ_or_two_models_only(self) -> None:
        write_baseline(
            self.baseline,
            [
                ("a", "sintesi", tokens(2050, 100)),
                ("b", "sintesi", tokens(2050, 100)),
                ("a", "logica", tokens(80, 100)),
                ("b", "logica", tokens(80, 100)),
                ("c", "logica", tokens(80, 100)),
            ],
        )
        write_run(
            self.run_dir,
            [
                result("a", "sintesi", tokens(5000, 100), 6, True),
                result("b", "sintesi", tokens(5000, 100), 6, True),
                result("a", "logica", tokens(190, 100), 1, False),
            ],
        )
        self.assertFalse(any(row["baseline_input_sospetto"] for row in self.rows()))

    def test_flag_uses_whole_baseline_even_when_models_filtered(self) -> None:
        write_baseline(
            self.baseline,
            [(m, "sintesi", tokens(2050, 100)) for m in ("a", "b", "c")],
        )
        write_run(self.run_dir, [result("a", "sintesi", tokens(5000, 9), 6, True)])
        (row,) = self.rows(models=["a"])
        self.assertTrue(row["baseline_input_sospetto"])

    def test_strategy_block_cost_from_single_stage_tests_without_source(self) -> None:
        write_baseline(
            self.baseline,
            [
                ("a", "logica", tokens(87, 600)),
                ("a", "matematica", tokens(126, 800)),
                ("a", "sintesi", tokens(2050, 800)),
            ],
        )
        write_run(
            self.run_dir,
            [
                result("a", "logica", tokens(199, 900), 1, False),
                result("a", "matematica", tokens(238, 900), 1, False),
                result("a", "sintesi", tokens(5600, 900), 6, True),
            ],
        )
        self.assertEqual(ct.strategy_block_cost(self.rows()), {"a": 112.0})

    def test_models_filter_limits_rows(self) -> None:
        write_baseline(
            self.baseline,
            [("a", "t", tokens(1, 1)), ("b", "t", tokens(1, 1))],
        )
        write_run(
            self.run_dir,
            [
                result("a", "t", tokens(2, 2), 1, False),
                result("b", "t", tokens(2, 2), 1, False),
            ],
        )
        self.assertEqual([r["model"] for r in self.rows(models=["b"])], ["b"])

    def test_cli_prints_table_with_nd_and_flag(self) -> None:
        write_baseline(
            self.baseline,
            [(m, "sintesi", tokens(2050, 100)) for m in ("a", "b", "c")],
        )
        write_run(
            self.run_dir,
            [
                result("a", "sintesi", tokens(5000, 100), 6, True),
                result("b", "sintesi", tokens(None, None), 6, True),
            ],
        )
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = ct.main(
                [
                    "--baseline",
                    str(self.baseline),
                    "--run",
                    str(self.run_dir),
                    "--models",
                    "a",
                    "b",
                ]
            )
        text = out.getvalue()
        self.assertEqual(code, 0)
        self.assertIn("n/d", text)
        self.assertIn("baseline_input_sospetto", text)
        self.assertIn("sintesi", text)

    def test_cli_fails_on_missing_folder(self) -> None:
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            code = ct.main(
                ["--baseline", str(self.baseline / "x"), "--run", str(self.run_dir)]
            )
        self.assertNotEqual(code, 0)


if __name__ == "__main__":
    unittest.main()

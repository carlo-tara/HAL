#!/usr/bin/env python3
"""Confronta i token di una run baseline con quelli di una run middleware.

Per ogni coppia (modello, test) mostra token di input/output/totale, numero di
stage e rapporto. I token non disponibili (`None`) restano `n/d` e non entrano
nelle somme. Il flag `baseline_input_sospetto` segnala un input baseline
identico in almeno `SUSPECT_MIN_MODELS` modelli su un test con fonte: indizio di
una fonte tagliata al contesto, non una prova.

Uso:
    python3 benchmark/scripts/compare_tokens.py \
        --baseline benchmark/history/20261017_all \
        --run benchmark/history/20261021_1 --models phi3:mini llama3.2:1b
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from statistics import mean

SUSPECT_MIN_MODELS = 3
ND = "n/d"
FLAG = "baseline_input_sospetto"

Key = tuple[str, str]


def _token(tokens: dict | None, name: str) -> int | None:
    value = (tokens or {}).get(name)
    return value if isinstance(value, int) and not isinstance(value, bool) else None


def load_baseline(folder: Path) -> dict[Key, dict]:
    """Legge un JSON per test (`<n>_<test>_<modello>.json`); ignora gli altri file."""
    entries: dict[Key, dict] = {}
    for path in sorted(folder.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if isinstance(data, dict) and "model" in data and "test_id" in data:
            entries[(data["model"], data["test_id"])] = {
                "tokens": data.get("tokens") or {}
            }
    return entries


def load_run(folder: Path) -> dict[Key, dict]:
    """Legge `results.json` di una run middleware."""
    data = json.loads((folder / "results.json").read_text(encoding="utf-8"))
    entries: dict[Key, dict] = {}
    for item in data.get("results", []):
        entries[(item["model"], item["test_id"])] = {
            "tokens": item.get("tokens") or {},
            "stages": len(item.get("workflow") or []),
            "has_source": bool((item.get("system1") or {}).get("has_source")),
        }
    return entries


def _suspect_inputs(baseline: dict[Key, dict]) -> set[tuple[str, int]]:
    models_by_value: dict[tuple[str, int], set[str]] = defaultdict(set)
    for (model, test_id), entry in baseline.items():
        value = _token(entry["tokens"], "input")
        if value is not None:
            models_by_value[(test_id, value)].add(model)
    return {
        key
        for key, models in models_by_value.items()
        if len(models) >= SUSPECT_MIN_MODELS
    }


def compare(
    baseline: dict[Key, dict],
    run: dict[Key, dict],
    models: list[str] | None = None,
) -> list[dict]:
    suspects = _suspect_inputs(baseline)
    rows = []
    for (model, test_id), entry in sorted(run.items()):
        if models and model not in models:
            continue
        base = (baseline.get((model, test_id)) or {}).get("tokens", {})
        run_tokens = entry["tokens"]
        base_total = _token(base, "total")
        run_total = _token(run_tokens, "total")
        ratio = run_total / base_total if base_total and run_total is not None else None
        base_input = _token(base, "input")
        rows.append(
            {
                "model": model,
                "test_id": test_id,
                "base_input": base_input,
                "base_output": _token(base, "output"),
                "base_total": base_total,
                "run_input": _token(run_tokens, "input"),
                "run_output": _token(run_tokens, "output"),
                "run_total": run_total,
                "stages": entry["stages"],
                "has_source": entry["has_source"],
                "ratio_total": ratio,
                FLAG: bool(
                    entry["has_source"]
                    and base_input is not None
                    and (test_id, base_input) in suspects
                ),
            }
        )
    return rows


def summarize(rows: list[dict]) -> dict[str, dict]:
    """Somma per modello solo le coppie con totali noti da entrambi i lati."""
    summary: dict[str, dict] = {}
    for row in rows:
        item = summary.setdefault(
            row["model"], {"base_total": 0, "run_total": 0, "excluded": 0}
        )
        if row["base_total"] is None or row["run_total"] is None:
            item["excluded"] += 1
            continue
        item["base_total"] += row["base_total"]
        item["run_total"] += row["run_total"]
    for item in summary.values():
        item["ratio_total"] = (
            item["run_total"] / item["base_total"] if item["base_total"] else None
        )
    return summary


def strategy_block_cost(rows: list[dict]) -> dict[str, float]:
    """Delta medio di input sui test senza fonte e a stage singolo.

    Senza fonte e con un solo stage l'unica differenza di prompt è il blocco
    `<strategia_system1_laya>`: il delta ne misura il costo in token di input.
    """
    deltas: dict[str, list[int]] = defaultdict(list)
    for row in rows:
        if row["has_source"] or row["stages"] != 1:
            continue
        if row["base_input"] is None or row["run_input"] is None:
            continue
        deltas[row["model"]].append(row["run_input"] - row["base_input"])
    return {model: float(mean(values)) for model, values in deltas.items()}


def _fmt(value: int | None) -> str:
    return ND if value is None else str(value)


def _fmt_ratio(value: float | None) -> str:
    return ND if value is None else f"{value:.2f}x"


def render(rows: list[dict]) -> str:
    header = "modello | test | base in/out/tot | middleware in/out/tot | stage | rapporto | note"
    lines = [header, "-" * len(header)]
    for row in rows:
        base = "/".join(
            _fmt(row[k]) for k in ("base_input", "base_output", "base_total")
        )
        run = "/".join(_fmt(row[k]) for k in ("run_input", "run_output", "run_total"))
        note = FLAG if row[FLAG] else ""
        lines.append(
            f"{row['model']} | {row['test_id']} | {base} | {run} | "
            f"{row['stages']} | {_fmt_ratio(row['ratio_total'])} | {note}".rstrip()
        )
    lines += ["", "Totali per modello (solo coppie con token noti da entrambi i lati):"]
    for model, item in summarize(rows).items():
        lines.append(
            f"- {model}: base {item['base_total']} -> middleware {item['run_total']} "
            f"({_fmt_ratio(item['ratio_total'])}); coppie escluse (n/d): {item['excluded']}"
        )
    costs = strategy_block_cost(rows)
    if costs:
        lines += [
            "",
            "Costo del blocco strategia (delta input, test senza fonte, 1 stage):",
        ]
        lines += [f"- {model}: {cost:.0f} token" for model, cost in costs.items()]
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--models", nargs="*", default=None)
    args = parser.parse_args(argv)
    for folder in (args.baseline, args.run):
        if not folder.is_dir():
            print(f"cartella non trovata: {folder}", file=sys.stderr)
            return 2
    try:
        baseline = load_baseline(args.baseline)
        run = load_run(args.run)
    except (OSError, ValueError, KeyError) as error:
        print(f"input non valido: {error}", file=sys.stderr)
        return 2
    print(render(compare(baseline, run, args.models)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

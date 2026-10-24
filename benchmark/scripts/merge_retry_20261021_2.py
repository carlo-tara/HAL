#!/usr/bin/env python3
"""Fonde la run 20261021_2 con il retry delle celle HAL 504 ed esclude Haiku.

Uso:
    python3 benchmark/scripts/merge_retry_20261021_2.py \
        --run benchmark/history/20261021_2/run \
        --retry benchmark/history/20261021_2/run_retry_hal \
        --out benchmark/history/20261021_2/run_merged

Le celle sostituite mantengono traccia in `superseded_error`; l'output è
compatibile con generate_comparison_report.py.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_orcarouter_comparison import summarize, utc_now

EXCLUDE_PREFIX = "anthropic/claude-haiku"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", required=True, type=Path)
    parser.add_argument("--retry", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    source = json.loads((args.run / "results.json").read_text(encoding="utf-8"))
    retry = json.loads((args.retry / "results.json").read_text(encoding="utf-8"))
    args.out.mkdir(parents=True, exist_ok=True)

    replacements = {
        (r["model_requested"], r["path"], r["prompt_id"]): r for r in retry["results"]
    }
    merged_results = []
    replaced = 0
    for r in source["results"]:
        if r["model_requested"].startswith(EXCLUDE_PREFIX):
            continue  # Haiku rimosso dal benchmark
        key = (r["model_requested"], r["path"], r["prompt_id"])
        if key in replacements:
            new = dict(replacements[key])
            new["superseded_error"] = {
                "status": r["status"],
                "http_status": r.get("http_status"),
                "seconds": r.get("seconds"),
                "reason": "504 al vecchio timeout upstream di 60 s",
            }
            merged_results.append(new)
            replaced += 1
            # copia il file dettaglio nella cartella fusa
            shutil.copy(args.retry / new["result_file"], args.out / new["result_file"])
        else:
            merged_results.append(r)

    models = [
        m for m in source["method"]["model_order"] if not m.startswith(EXCLUDE_PREFIX)
    ]
    out = dict(source)
    out["results"] = merged_results
    out["status"] = (
        "completed"
        if all(r["status"] == "ok" for r in merged_results)
        else "completed_with_errors"
    )
    out["finished_at"] = retry.get("finished_at") or utc_now()
    out["run_id"] = "20261021_2_merged"
    method = dict(source["method"])
    method["model_order"] = models
    method["retry_merge"] = {
        "merged_at": utc_now(),
        "retry_run": str(args.retry),
        "cells_replaced": replaced,
        "excluded_models": ["anthropic/claude-haiku-4.5 (rimosso su richiesta 23/10)"],
        "hal_upstream_timeout_seconds": 600,
    }
    out["method"] = method
    out["summary"] = summarize(merged_results)

    # copia anche i file dettaglio non sostituiti
    for f in args.run.glob("*.json"):
        if f.name == "results.json":
            continue
        dest = args.out / f.name
        if not dest.exists():
            shutil.copy(f, dest)
    (args.out / "results.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"merged: {len(merged_results)} risultati, {replaced} celle sostituite")
    print(f"status: {out['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

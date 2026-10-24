#!/usr/bin/env python3
"""Rilancia le celle HAL fallite con 504 al vecchio timeout upstream di 60 s.

Uso:
    python3 benchmark/scripts/retry_hal_cells.py \
        --run-dir benchmark/history/20261021_2/run_retry_hal \
        --source benchmark/history/20261021_2/run/results.json

Seleziona automaticamente i risultati con status=error, path=hal_system2 e
http_status=504 nella run sorgente e li riesegue via HAL con il timeout
aggiornato (600 s). Pausa 180 s quando cambia il modello, come nel runner
principale.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_orcarouter_comparison import (
    EPUB_PATH,
    PROMPTS_PATH,
    build_message,
    evaluate_quality,
    extract_epub_text,
    response_payload,
    utc_now,
)

HAL_BASE_URL = "http://127.0.0.1:8910/v1"
TEMPERATURE = 0.6
COOLDOWN_SECONDS = 180


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", required=True, type=Path)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--hal-base-url", default=HAL_BASE_URL)
    args = parser.parse_args()

    source = json.loads(args.source.read_text(encoding="utf-8"))
    cells = [
        (r["model_requested"], r["prompt_id"])
        for r in source["results"]
        if r["path"] == "hal_system2"
        and r["status"] == "error"
        and r.get("http_status") == 504
    ]
    if not cells:
        raise SystemExit("Nessuna cella HAL 504 da rilanciare")
    print(f"CELLA DA RILANCIARE: {len(cells)} -> {cells}", flush=True)

    prompts = {p["id"]: p for p in json.loads(PROMPTS_PATH.read_text())["prompts"]}
    epub_text = extract_epub_text(EPUB_PATH)
    headers = {
        "Authorization": "Bearer dev-token",
        "Content-Type": "application/json",
        "Cache-Control": "no-cache",
    }
    args.run_dir.mkdir(parents=True, exist_ok=True)
    report_path = args.run_dir / "results.json"
    report = {
        "benchmark": "hal_retry_504_cells",
        "source_run": str(args.source),
        "started_at": utc_now(),
        "finished_at": None,
        "status": "running",
        "method": {
            "hal_endpoint": args.hal_base_url,
            "cells": [list(c) for c in cells],
            "temperature": TEMPERATURE,
            "cooldown_seconds_between_models": COOLDOWN_SECONDS,
            "notes": "Stesse celle fallite con 504 al timeout upstream di 60 s; rilanciate dopo aver reso il timeout configurabile (600 s).",
        },
        "results": [],
    }

    client = httpx.Client(timeout=900.0)
    try:
        for index, (model, prompt_id) in enumerate(cells):
            if index and model != cells[index - 1][0]:
                print(f"COOLDOWN {COOLDOWN_SECONDS}s", flush=True)
                time.sleep(COOLDOWN_SECONDS)
            prompt = prompts[prompt_id]
            message = build_message(prompt, epub_text)
            payload = {
                "model": model,
                "messages": [{"role": "user", "content": message}],
                "stream": False,
                "temperature": TEMPERATURE,
            }
            started = time.perf_counter()
            result = {
                "model_requested": model,
                "model_served": None,
                "path": "hal_system2",
                "prompt_id": prompt_id,
                "status": "error",
                "http_status": None,
                "seconds": None,
                "usage": {},
                "response": "",
                "quality": None,
                "error_type": None,
                "cache_hit": False,
                "started_at": utc_now(),
                "retry_of": "504 at 60s upstream timeout (run 2026-10-22)",
            }
            print(f"START {model} {prompt_id}", flush=True)
            try:
                response = client.post(
                    f"{args.hal_base_url.rstrip('/')}/chat/completions",
                    headers=headers,
                    json=payload,
                )
                result["http_status"] = response.status_code
                response.raise_for_status()
                text, served_model, usage = response_payload(response)
                result.update(
                    status="ok" if text else "empty_response",
                    model_served=served_model,
                    response=text,
                    usage=usage,
                    quality=evaluate_quality(prompt, text),
                    cache_hit=response.headers.get("X-Cache", "").lower() == "hit",
                )
            except httpx.HTTPStatusError as exc:
                result["error_type"] = "http_error"
                result["error_detail"] = exc.response.text[:1000]
            except httpx.TimeoutException:
                result["error_type"] = "timeout"
            except httpx.RequestError as exc:
                result["error_type"] = type(exc).__name__
            except (ValueError, KeyError, TypeError) as exc:
                result["error_type"] = type(exc).__name__
            result["seconds"] = round(time.perf_counter() - started, 3)
            result["finished_at"] = utc_now()
            name = (
                f"{index + 1:02d}_{prompt_id}_{model.replace('/', '_')}"
                "_hal_system2_retry.json"
            )
            (args.run_dir / name).write_text(
                json.dumps(result, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            result["result_file"] = name
            report["results"].append(result)
            report["updated_at"] = utc_now()
            report_path.write_text(
                json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            print(
                f"  {index + 1}/{len(cells)} {model} {prompt_id}: "
                f"{result['status']} ({result['seconds']:.1f}s)",
                flush=True,
            )
    finally:
        client.close()

    report["finished_at"] = utc_now()
    report["status"] = (
        "completed"
        if all(r["status"] == "ok" for r in report["results"])
        else "completed_with_errors"
    )
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report["status"], ensure_ascii=False), flush=True)
    return 0 if report["status"] == "completed" else 1


if __name__ == "__main__":
    raise SystemExit(main())

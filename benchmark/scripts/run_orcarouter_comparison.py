#!/usr/bin/env python3
"""Compare HAL System 2 and direct OrcaRouter calls using benchmark prompts."""

from __future__ import annotations

import argparse
import json
import os
import posixpath
import re
import time
import xml.etree.ElementTree as ET
import zipfile
from datetime import UTC, datetime
from html.parser import HTMLParser
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
PROMPTS_PATH = ROOT / "config" / "benchmark-prompts.json"
EPUB_PATH = Path("/var/www/hal_system2/docs/Pensieri_lenti_e_veloci.epub")
CHARS_PER_A4_PAGE = 3000
MODELS = [
    "anthropic/claude-sonnet-5.5",
    "anthropic/claude-opus-5.5",
    "openai/gpt-6-luna",
    "openai/gpt-6.1-sol",
]
HAL_BASE_URL = "http://127.0.0.1:8910/v1"
ORCA_BASE_URL_DEFAULT = "https://api.orcarouter.ai/v1"
TEMPERATURE = 0.6


class TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        if data.strip():
            self.parts.append(data.strip())


def load_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def extract_epub_text(path: Path) -> str:
    with zipfile.ZipFile(path) as book:
        container = ET.fromstring(book.read("META-INF/container.xml"))
        rootfile = next(
            node.attrib["full-path"]
            for node in container.iter()
            if node.tag.endswith("rootfile") and node.attrib.get("full-path")
        )
        opf = ET.fromstring(book.read(rootfile))
        base = posixpath.dirname(rootfile)
        manifest = {
            node.attrib.get("id"): node.attrib.get("href")
            for node in opf.iter()
            if node.tag.endswith("item")
        }
        sections: list[str] = []
        for ref in opf.iter():
            if not ref.tag.endswith("itemref"):
                continue
            href = manifest.get(ref.attrib.get("idref"))
            if not href:
                continue
            parser = TextExtractor()
            parser.feed(book.read(posixpath.join(base, href)).decode("utf-8", "ignore"))
            sections.append(" ".join(parser.parts))
    text = "\n".join(sections)
    text = re.sub(r"[ \t\u00a0]+", " ", text)
    return re.sub(r"\n\s*\n+", "\n\n", text).strip()


def build_message(prompt: dict, epub_text: str) -> str:
    arguments = prompt.get("arguments", {})
    instructions = prompt["prompt"]
    if "lingua_destinazione" in arguments:
        instructions = f"Lingua di destinazione: {arguments['lingua_destinazione']}.\n{instructions}"
    if "source" not in prompt:
        return instructions
    source = epub_text
    if "numero_pagine" in arguments:
        source = source[: arguments["numero_pagine"] * CHARS_PER_A4_PAGE]
    return f"<libro>\n{source}\n</libro>\n\n{instructions}"


def quality_check(check: dict, text: str) -> bool:
    kind = check["type"]
    folded = text.casefold()
    if kind == "contains_any":
        return any(value.casefold() in folded for value in check["values"])
    if kind == "absent":
        return not any(value.casefold() in folded for value in check["values"])
    if kind == "min_chars":
        return len(text.strip()) >= check["value"]
    if kind == "json":
        candidate = re.search(r"```(?:json)?(.*?)```", text, re.IGNORECASE | re.DOTALL)
        candidate_text = candidate.group(1) if candidate else text
        starts = [
            i for i in (candidate_text.find("["), candidate_text.find("{")) if i >= 0
        ]
        if not starts:
            return False
        try:
            json.JSONDecoder().raw_decode(candidate_text, min(starts))
            return True
        except ValueError:
            return False
    if kind == "html":
        return bool(re.search(r"<!doctype\s+html|<html\b", text, re.IGNORECASE))
    return False


def evaluate_quality(prompt: dict, text: str) -> dict:
    checks = [
        {
            "label": check.get("label", check["type"]),
            "passed": quality_check(check, text),
        }
        for check in prompt.get("quality", [])
    ]
    passed = sum(check["passed"] for check in checks)
    return {
        "passed": passed,
        "total": len(checks),
        "score": round(passed / len(checks), 2) if checks else None,
        "checks": checks,
    }


def normalize_model_id(model: str | None) -> str:
    if not model:
        return ""
    return model.rsplit("/", 1)[-1].replace(".", "-").casefold()


def response_payload(response: httpx.Response) -> tuple[str, str | None, dict]:
    data = response.json()
    choice = (data.get("choices") or [{}])[0]
    message = choice.get("message") or {}
    content = message.get("content") or ""
    if isinstance(content, list):
        content = "".join(
            part.get("text", "") for part in content if isinstance(part, dict)
        )
    usage = data.get("usage") if isinstance(data.get("usage"), dict) else {}
    return str(content), data.get("model"), usage


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", required=True, type=Path)
    parser.add_argument(
        "--models-file",
        type=Path,
        default=None,
        help="JSON con models[].model (slug OrcaRouter); default: MODELS hardcoded",
    )
    parser.add_argument("--cooldown", type=int, default=180)
    parser.add_argument(
        "--env-file", type=Path, default=Path("/var/www/hal_system2/.env")
    )
    parser.add_argument("--hal-base-url", default=HAL_BASE_URL)
    args = parser.parse_args()

    if args.run_dir.exists():
        raise SystemExit(f"Run directory already exists: {args.run_dir}")
    env = load_env(args.env_file)
    orca_key = os.environ.get("ORCAROUTER_API_KEY") or env.get("ORCAROUTER_API_KEY")
    if not orca_key:
        raise SystemExit("ORCAROUTER_API_KEY is not configured")
    orca_base = (env.get("ORCAROUTER_API_URI") or ORCA_BASE_URL_DEFAULT).rstrip("/")
    models = MODELS
    if args.models_file:
        cfg = json.loads(args.models_file.read_text(encoding="utf-8"))
        models = [entry["model"] for entry in cfg["models"]]
    prompts = json.loads(PROMPTS_PATH.read_text(encoding="utf-8"))["prompts"]
    if len(prompts) != 5:
        raise SystemExit("Expected exactly five configured benchmark prompts")
    if not EPUB_PATH.is_file():
        raise SystemExit(f"Required EPUB is missing: {EPUB_PATH}")
    epub_text = extract_epub_text(EPUB_PATH)

    args.run_dir.mkdir(parents=True)
    report_path = args.run_dir / "results.json"
    report = {
        "benchmark": "hal_system2_vs_direct_orcarouter",
        "started_at": utc_now(),
        "finished_at": None,
        "status": "running",
        "method": {
            "hal_endpoint": args.hal_base_url,
            "direct_endpoint": orca_base,
            "model_order": models,
            "prompts_file": str(PROMPTS_PATH.relative_to(ROOT)),
            "prompt_count_per_model_path": len(prompts),
            "total_runs": len(models) * 2,
            "total_requests": len(models) * 2 * len(prompts),
            "cooldown_seconds_between_runs": args.cooldown,
            "temperature": TEMPERATURE,
            "cache_control": "no-cache on both paths; disables HAL response cache",
            "source_handling": "Original benchmark EPUB extraction and 3000 chars per page; identical user message sent to both paths",
            "notes": "HAL applies its Laya preflight, routing and telemetry; direct OrcaRouter bypasses those HAL layers. Both calls use the same requested model, user message and temperature.",
        },
        "results": [],
        "runs": [],
    }

    direct_headers = {
        "Authorization": f"Bearer {orca_key}",
        "Content-Type": "application/json",
        "Cache-Control": "no-cache",
    }
    hal_headers = {
        "Authorization": "Bearer dev-token",
        "Content-Type": "application/json",
        "Cache-Control": "no-cache",
    }
    timeout = httpx.Timeout(900.0, connect=20.0)
    client = httpx.Client(timeout=timeout)
    try:
        for model_index, model in enumerate(models):
            paths = (
                ["hal_system2", "orcarouter_direct"]
                if model_index % 2 == 0
                else ["orcarouter_direct", "hal_system2"]
            )
            for path_index, path_name in enumerate(paths):
                run_started = utc_now()
                run_record = {
                    "model": model,
                    "path": path_name,
                    "started_at": run_started,
                    "prompt_results": [],
                }
                report["runs"].append(run_record)
                print(f"START {model} {path_name} ({len(prompts)} prompts)", flush=True)
                for prompt_index, prompt in enumerate(prompts, start=1):
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
                        "path": path_name,
                        "prompt_id": prompt["id"],
                        "status": "error",
                        "http_status": None,
                        "seconds": None,
                        "usage": {},
                        "response": "",
                        "quality": None,
                        "error_type": None,
                        "cache_hit": False,
                    }
                    try:
                        if path_name == "hal_system2":
                            url = f"{args.hal_base_url.rstrip('/')}/chat/completions"
                            headers = hal_headers
                        else:
                            url = f"{orca_base}/chat/completions"
                            headers = direct_headers
                        response = client.post(url, headers=headers, json=payload)
                        result["http_status"] = response.status_code
                        response.raise_for_status()
                        text, served_model, usage = response_payload(response)
                        result.update(
                            status="ok" if text else "empty_response",
                            model_served=served_model,
                            response=text,
                            usage=usage,
                            quality=evaluate_quality(prompt, text),
                            cache_hit=response.headers.get("X-Cache", "").lower()
                            == "hit",
                        )
                        if (
                            path_name == "hal_system2"
                            and served_model
                            and normalize_model_id(served_model)
                            != normalize_model_id(model)
                        ):
                            result["status"] = "wrong_model_served"
                    except httpx.HTTPStatusError as exc:
                        result["http_status"] = exc.response.status_code
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
                    result_name = f"{len(report['results']) + 1:02d}_{prompt['id']}_{model.replace('/', '_')}_{path_name}.json"
                    result_file = args.run_dir / result_name
                    result_file.write_text(
                        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8",
                    )
                    result["result_file"] = result_name
                    report["results"].append(result)
                    run_record["prompt_results"].append(result_name)
                    report["updated_at"] = utc_now()
                    report_path.write_text(
                        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8",
                    )
                    print(
                        f"  {prompt_index}/5 {prompt['id']}: {result['status']} ({result['seconds']:.1f}s) model={result['model_served']}",
                        flush=True,
                    )
                run_record["finished_at"] = utc_now()
                run_record["status"] = (
                    "completed"
                    if all(
                        next(r for r in report["results"] if r["result_file"] == name)[
                            "status"
                        ]
                        == "ok"
                        for name in run_record["prompt_results"]
                    )
                    else "completed_with_errors"
                )
                report["runs"][-1] = run_record
                report["updated_at"] = utc_now()
                report_path.write_text(
                    json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                )
                if model_index != len(models) - 1 or path_index == 0:
                    print(f"COOLDOWN {args.cooldown}s", flush=True)
                    time.sleep(args.cooldown)
    finally:
        client.close()

    report["finished_at"] = utc_now()
    report["status"] = (
        "completed"
        if all(result["status"] == "ok" for result in report["results"])
        else "completed_with_errors"
    )
    report["summary"] = summarize(report["results"])
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report["summary"], ensure_ascii=False, indent=2), flush=True)
    return 0 if report["status"] == "completed" else 1


def summarize(results: list[dict]) -> dict:
    summary: dict[str, dict] = {}
    for result in results:
        key = f"{result['model_requested']} | {result['path']}"
        entry = summary.setdefault(
            key,
            {
                "successful": 0,
                "failed": 0,
                "seconds": 0.0,
                "prompt_results": 0,
                "quality_passed": 0,
                "quality_total": 0,
                "usage": {},
            },
        )
        entry["prompt_results"] += 1
        if result["status"] == "ok":
            entry["successful"] += 1
        else:
            entry["failed"] += 1
        entry["seconds"] = round(entry["seconds"] + (result.get("seconds") or 0), 3)
        quality = result.get("quality") or {}
        entry["quality_passed"] += quality.get("passed", 0)
        entry["quality_total"] += quality.get("total", 0)
        usage = result.get("usage") or {}
        for field in (
            "prompt_tokens",
            "completion_tokens",
            "total_tokens",
            "input_tokens",
            "output_tokens",
        ):
            if isinstance(usage.get(field), (int, float)):
                entry["usage"][field] = entry["usage"].get(field, 0) + usage[field]
    for entry in summary.values():
        total = entry["quality_total"]
        entry["quality_score"] = (
            round(entry["quality_passed"] / total, 4) if total else None
        )
    return summary


if __name__ == "__main__":
    raise SystemExit(main())

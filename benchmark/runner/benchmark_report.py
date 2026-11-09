"""Riepiloghi e output leggibile del benchmark (T2-09, rv7 N28).

Spostamento meccanico di codice da `app/benchmark_models.py` (nessun
riscrittura).
"""

from __future__ import annotations

import sys
from pathlib import Path

from .benchmark_calls import openai_compatible_google
from .benchmark_settings import Settings


def common_benchmark_dir(output: Path, date_str: str) -> Path:
    base = output.parent / f"{date_str}_all"
    base.mkdir(parents=True, exist_ok=True)
    return base

def summary(results: list[dict]) -> dict:
    counts = [result["tokens"]["total"] for result in results]
    return {
        "completed": len(results),
        "successful": sum(r["status"] == "ok" for r in results),
        "failed": sum(r["status"] != "ok" for r in results),
        "seconds": round(sum(r["seconds"] for r in results), 6),
        "total_tokens": sum(counts)
        if counts and all(n is not None for n in counts)
        else None,
        "known_total_tokens": sum(n for n in counts if n is not None),
        "usage_missing": sum(n is None for n in counts),
    }

def apply_llm_model_override(models: list[dict], config: Settings) -> list[dict]:
    if not config.llm_provider:
        return models
    if not openai_compatible_google(config):
        raise ValueError(
            "LLM_PROVIDER deve essere openai_compa oppure openai_compatible"
        )
    if not config.llm_model:
        return models
    # Replace existing Google entries only: never add one, so provider filters stay exact.
    first_google = next(
        (i for i, model in enumerate(models) if model["provider"] == "google"), None
    )
    if first_google is None:
        return models
    others = [model for model in models if model["provider"] != "google"]
    others.insert(first_google, {"provider": "google", "model": config.llm_model})
    return others

def log(message: str = "") -> None:
    print(message, file=sys.stderr, flush=True)

def describe_result(result: dict) -> str:
    if result["status"] == "error":
        error = result.get("error", {})
        detail = error.get("type", "errore")
        if error.get("http_status"):
            detail += f" HTTP {error['http_status']}"
            if error["http_status"] == 500 and result["provider"] == "ollama":
                detail += " (spesso memoria insufficiente per il modello)"
        return f"✗ errore: {detail}"
    tokens = result["tokens"]
    counts = " · ".join(
        f"{label} {value if value is not None else 'n/d'}"
        for label, value in (
            ("in", tokens["input"]),
            ("out", tokens["output"]),
            ("tot", tokens["total"]),
        )
    )
    icon = "✓" if result["status"] == "ok" else "⚠"
    quality = result.get("quality")
    score = f" | qualità {quality['passed']}/{quality['total']}" if quality else ""
    return f"{icon} {result['status']} | token {counts}{score}"

def log_final_summary(report: dict) -> None:
    per_model: dict[tuple[str, str], list[dict]] = {}
    for result in report["results"]:
        per_model.setdefault((result["provider"], result["model"]), []).append(result)
    log()
    log("Riepilogo per modello:")
    for (provider, model), results in per_model.items():
        ok = sum(r["status"] == "ok" for r in results)
        known = sum(r["tokens"]["total"] or 0 for r in results)
        seconds = sum(r["seconds"] for r in results)
        scored = [r["quality"] for r in results if r.get("quality")]
        quality = (
            f" | qualità {sum(q['passed'] for q in scored)}/{sum(q['total'] for q in scored)}"
            if scored
            else ""
        )
        log(
            f"  {provider}/{model}: {ok}/{len(results)} ok | token {known} | {seconds:.1f}s{quality}"
        )
    s = report["summary"]
    log(
        f"Totale: {s['successful']} ok, {s['failed']} errori, "
        f"token {s['known_total_tokens']}, tempo {s['seconds']:.1f}s"
    )

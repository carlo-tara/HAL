"""Orchestrazione dell'esecuzione benchmark (T2-09, rv7 N28).

Spostamento meccanico di codice da `app/benchmark_models.py` (nessun
riscrittura).
"""

from __future__ import annotations

import os
import sqlite3
import time
import uuid
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Any

import httpx

from .benchmark_calls import benchmark_call, local_translation, translation_result
from .benchmark_parsing import extract_html_document, prompt_message, safe_path_component
from .benchmark_quality import evaluate_quality
from .benchmark_report import (
    apply_llm_model_override,
    common_benchmark_dir,
    describe_result,
    log,
    log_final_summary,
    summary,
)
from .benchmark_settings import Settings, utc_now, write_json
from .benchmark_system2 import system2_workflow_call
from .system2_metrics import System2Metrics


def run_benchmark(
    models: list[dict],
    prompts: list[dict],
    config: Settings,
    output: Path,
    *,
    client: httpx.Client,
    run_dir: Path | None = None,
    system1_guides: dict[str, dict] | None = None,
    metrics_db: Path | None = None,
    clock: Callable[[], float] = time.perf_counter,
    cooldown: float = 0.0,
    sleep: Callable[[float], None] = time.sleep,
) -> dict:
    models = apply_llm_model_override(models, config)
    log(
        f"Benchmark: {len(models)} modelli x {len(prompts)} test "
        f"= {len(models) * len(prompts)} chiamate"
    )
    if config.llm_provider:
        log(
            f"Google: openai-compatible su {config.llm_base_url} "
            f"(modello {config.llm_model or 'da catalogo'})"
        )
    log(f"Ollama: {config.ollama_base_url}")
    log(f"Timeout per chiamata: {config.timeout:g}s")
    log(f"Output: {output}")
    report: dict[str, Any] = {
        "started_at": utc_now(),
        "finished_at": None,
        "status": "running",
        "expected_results": len(models) * len(prompts),
        "timing": "end_to_end_including_model_load",
        "results": [],
        "result_directories": [],
        "summary": summary([]),
    }
    if run_dir is not None:
        common_base = run_dir
        common_base.mkdir(parents=True, exist_ok=False)
    else:
        date_str = datetime.now().strftime("%Y%m%d")
        common_base = common_benchmark_dir(output, date_str)
    # A2: la telemetria e un artefatto del run, non del gate System 1: nasce
    # ogni qualvolta un db e richiesto, con o senza --system1.
    metrics = System2Metrics(metrics_db) if metrics_db is not None else None
    run_id = uuid.uuid4().hex
    if system1_guides:
        report["system1"] = dict(system1_guides)
        write_json(common_base / "system1.json", report["system1"])
    if metrics is not None:
        report["system2_metrics"] = {"run_id": run_id, "db_path": str(metrics_db)}
        prompt_by_id = {prompt["id"]: prompt for prompt in prompts}
        for prompt_id, guide in (system1_guides or {}).items():
            try:
                metrics.record_event(
                    run_id=run_id,
                    prompt_id=prompt_id,
                    task_family=guide.get("task_family", "general"),
                    execution_mode=guide.get("execution_mode", "single_pass"),
                    system="system1",
                    stage="preflight_laya"
                    if guide.get("laya_called")
                    else "preflight_local_gate",
                    status="ok",
                    latency_ms=guide.get("preflight_latency_ms", 0),
                    input_chars=len(prompt_by_id.get(prompt_id, {}).get("prompt", "")),
                    decision=guide.get("decision_source"),
                    confidence=guide.get("confidence"),
                    fallback_used=guide.get("decision_source") == "local_task_gate",
                )
            except (OSError, sqlite3.Error, ValueError, TypeError) as exc:
                log(f"Metriche SQLite non registrate: {type(exc).__name__}")
    write_json(output, report)
    for model_index, model in enumerate(models, start=1):
        if model_index > 1 and cooldown > 0:
            log()
            log(f"Pausa di {cooldown:g}s prima del modello successivo…")
            sleep(cooldown)
        log()
        log(
            f"━━ [{model_index}/{len(models)}] {model['provider']}/{model['model']} "
            f"→ cartella {common_base.name}"
        )
        report["result_directories"].append(
            {
                "provider": model["provider"],
                "model": model["model"],
                "directory": str(common_base.relative_to(output.parent)),
            }
        )
        write_json(output, report)
        for test_index, prompt in enumerate(prompts, start=1):
            filename = f"{test_index:02d}_{safe_path_component(prompt['id'])}_{safe_path_component(model['model'])}.json"
            result = {
                **model,
                "test_id": prompt["id"],
                "started_at": utc_now(),
                "quality": None,
                "tokens": {
                    "input": None,
                    "output": None,
                    "reasoning": None,
                    "total": None,
                },
            }
            start = clock()
            translation = local_translation(prompt, config, client)
            # Latenza misurata attorno alla sola chiamata di traduzione: il
            # clock non va consumato quando il prompt passa al provider.
            translation_ms = (
                round((clock() - start) * 1000) if translation is not None else 0
            )
            log(
                f"  → test {test_index}/{len(prompts)} {prompt['id']}: "
                + (
                    f"traduzione locale ({translation.result.backend})…"
                    if translation is not None
                    else f"invio richiesta ({len(prompt_message(prompt)):,} caratteri)…"
                )
            )
            try:
                if translation is not None:
                    result.update(translation_result(translation.result))
                    if metrics is not None:
                        try:
                            # Stadio locale della catena: gli stessi nomi di campo
                            # di run_stage. Il backend e codificato nel nome stage
                            # e lo schema system2_workflow_events non ammette un
                            # value 'translation' (CHECK su system), quindi la riga
                            # resta nel system2 con stage traduzione_{backend}.
                            metrics.record_event(
                                run_id=run_id,
                                prompt_id=prompt["id"],
                                provider=model["provider"],
                                model=model["model"],
                                system="system2",
                                stage=f"traduzione_{translation.result.backend}",
                                status=result["status"],
                                latency_ms=translation_ms,
                                input_chars=len(translation.source),
                                output_chars=len(translation.result.text),
                                tokens_in=0,
                                tokens_out=0,
                                tokens_total=0,
                            )
                        except (OSError, sqlite3.Error, ValueError, TypeError) as exc:
                            log(
                                f"    Metriche SQLite non registrate: {type(exc).__name__}"
                            )
                else:
                    guide = (system1_guides or {}).get(prompt["id"])
                    if guide is None:
                        result.update(benchmark_call(model, prompt, config, client))
                    else:
                        result.update(
                            system2_workflow_call(
                                model,
                                prompt,
                                config,
                                client,
                                guide,
                                metrics=metrics,
                                run_id=run_id,
                            )
                        )
            except httpx.HTTPStatusError as exc:
                result.update(
                    status="error",
                    error={
                        "type": "http_error",
                        "http_status": exc.response.status_code,
                    },
                )
            except httpx.TimeoutException:
                result.update(status="error", error={"type": "timeout"})
            except httpx.RequestError:
                result.update(status="error", error={"type": "network_error"})
            except (ValueError, KeyError, TypeError, AttributeError, IndexError) as exc:
                # Never serialize exception messages: URLs/payloads may contain credentials.
                log(f"    Errore middleware: {type(exc).__name__}")
                error_type = (
                    "configuration_error"
                    if model["provider"] == "google" and not config.google_api_key
                    else "invalid_response"
                )
                result.update(status="error", error={"type": error_type})
            result["seconds"] = round(clock() - start, 6)
            if "response" in result:
                result["quality"] = evaluate_quality(prompt, result["response"])
            result["result_file"] = os.path.relpath(
                common_base / filename, output.parent
            )
            system1_result = (system1_guides or {}).get(prompt["id"])
            if system1_result is not None:
                result["system1"] = system1_result
            report["results"].append(result)
            report["summary"] = summary(report["results"])
            write_json(common_base / filename, result)
            if result["status"] == "ok":
                html = extract_html_document(result["response"])
                if html:
                    (common_base / filename).with_suffix(".htm").write_text(
                        html, encoding="utf-8"
                    )
            write_json(output, report)
            log(
                f"    {describe_result(result)} | {result['seconds']:.1f}s "
                f"[{len(report['results'])}/{report['expected_results']}]"
            )
    report.update(finished_at=utc_now(), status="completed")
    if metrics is not None:
        report["system2_metrics"] = {
            "run_id": run_id,
            "db_path": str(metrics_db),
            "summary": metrics.get_summary(run_id=run_id),
        }
    write_json(output, report)
    log_final_summary(report)
    return report

def filter_models(
    models: list[dict], provider: str | None, names: list[str] | None
) -> list[dict]:
    selected = [
        model
        for model in models
        if (provider is None or model["provider"] == provider)
        and (not names or model["model"] in names)
    ]
    if not selected:
        raise ValueError("Nessun modello corrisponde ai filtri --provider/--model")
    return selected

def filter_prompts(prompts: list[dict], ids: list[str] | None) -> list[dict]:
    if not ids:
        return prompts
    known = {prompt["id"] for prompt in prompts}
    unknown = [prompt_id for prompt_id in ids if prompt_id not in known]
    if unknown:
        raise ValueError("Test sconosciuto nei filtri --prompt/--only-id")
    return [prompt for prompt in prompts if prompt["id"] in ids]

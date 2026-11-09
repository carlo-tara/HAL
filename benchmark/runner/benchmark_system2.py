"""Chiamata workflow System 2 del benchmark (T2-09, rv7 N28).

Spostamento meccanico di codice da `app/benchmark_models.py` (nessun
riscrittura).
"""

from __future__ import annotations

import sqlite3
import time
from typing import Any

import httpx

from . import benchmark_parsing as parsing
from .benchmark_calls import benchmark_call
from .benchmark_parsing import _prompt_min_chars
from .benchmark_report import log
from .benchmark_settings import (
    CHARS_PER_A4_PAGE,
    MAX_PROMPT_EXCERPT,
    ROOT,
    Settings,
    resolve_output_cap,
)
from .benchmark_workflow import (
    assemble_segments_locally,
    system1_decision,
    system1_prompt,
)
from .system2_metrics import System2Metrics


def system2_workflow_call(
    model: dict,
    prompt: dict,
    config: Settings,
    client: httpx.Client,
    guide: dict,
    *,
    metrics: System2Metrics | None = None,
    run_id: str = "",
) -> dict:
    """Alternate Laya's bounded decisions with small, ordered System 2 calls."""
    mode = guide.get("execution_mode", "single_pass")
    if mode == "source_chunks" and "source" not in prompt:
        mode = "plan_then_solve"
    family = guide.get("task_family", "general")
    trace: list[dict] = []

    def record_metric(**event: Any) -> None:
        if metrics is None:
            return
        try:
            metrics.record_event(
                run_id=run_id,
                prompt_id=prompt["id"],
                provider=model["provider"],
                model=model["model"],
                task_family=guide.get("task_family", "general"),
                execution_mode=mode,
                **event,
            )
        except (OSError, sqlite3.Error, ValueError, TypeError) as exc:
            log(f"    Metriche SQLite non registrate: {type(exc).__name__}")

    def run_stage(
        stage_prompt: dict,
        stage: str,
        max_output_tokens: int | None = None,
        *,
        _system_message: str | None = None,
    ) -> dict:
        started = time.perf_counter()
        input_chars = len(stage_prompt.get("prompt", ""))
        result: dict | None = None
        failure: Exception | None = None
        try:
            result = benchmark_call(
                model,
                stage_prompt,
                config,
                client,
                system1=guide,
                system_message=_system_message,
                max_output_tokens=max_output_tokens,
            )
        except Exception as exc:
            failure = exc
            raise
        finally:
            # HT-004: registrazione unica nel finally — uno stage fallito o in
            # timeout deve avere il costo già speso a catalogo, altrimenti il
            # retry resta invisibile nei totali.
            fields: dict[str, Any]
            if result is not None and failure is None:
                tokens = result.get("tokens", {})
                trace.append(
                    {
                        "system": "system2",
                        "stage": stage,
                        "status": result.get("status"),
                        "tokens": tokens,
                    }
                )
                fields = {
                    "status": result.get("status", "error"),
                    "output_chars": len(result.get("response", "")),
                    "tokens_in": tokens.get("input"),
                    "tokens_out": tokens.get("output"),
                    "tokens_total": tokens.get("total"),
                    "cached_tokens": tokens.get("cached"),
                    "cache_creation_input_tokens": tokens.get("cache_creation"),
                }
            else:
                # Nessuna usage ricostruibile dalla risposta d'errore: non si
                # inventano token; si registrano char-in (input_chars) e i char
                # del messaggio wire dopo il collasso (input_collapsed) come
                # proxy dichiarati nel campo evento.
                input_collapsed = (
                    input_chars + len(_system_message)
                    if _system_message is not None
                    else len(system1_prompt(stage_prompt, guide))
                )
                exc_name = type(failure).__name__ if failure else "StageInterrupted"
                fields = {
                    "status": "failed",
                    "output_chars": 0,
                    "input_collapsed": input_collapsed,
                    "error_message": (
                        f"{exc_name}: "
                        f"proxy char_in={input_chars} "
                        f"input_collapsed={input_collapsed}"
                    ),
                }
            record_metric(
                system="system2",
                stage=stage,
                latency_ms=round((time.perf_counter() - started) * 1000),
                input_chars=input_chars,
                **fields,
            )
        if result is None:  # unreachable: senza eccezione benchmark_call ritorna
            raise AssertionError(f"stage {stage!r} terminato senza risultato")
        return result

    def decide(stage: str, artifact: str, choices: dict[str, str]) -> str:
        started = time.perf_counter()
        decision = system1_decision(
            prompt,
            config,
            client,
            phase=stage,
            artifact=artifact,
            choices=choices,
        )
        fallback_used = decision["confidence"] < config.laya_min_confidence
        chosen = decision["decision"]
        if fallback_used:
            chosen = next(
                (
                    option
                    for option in ("proceed", "accept", "process")
                    if option in choices
                ),
                next(iter(choices)),
            )
        trace.append(
            {"system": "system1_laya", **decision, "fallback_used": fallback_used}
        )
        record_metric(
            system="system1",
            stage=stage,
            status="ok",
            latency_ms=round((time.perf_counter() - started) * 1000),
            input_chars=len(artifact),
            decision=chosen,
            confidence=decision["confidence"],
            fallback_used=fallback_used,
        )
        return chosen

    def user_prompt(text: str) -> dict:
        return {"id": prompt["id"], "prompt": text}

    if mode == "source_chunks":
        source = parsing.epub_text(ROOT / prompt["source"])
        arguments = prompt.get("arguments", {})
        if "numero_pagine" in arguments:
            source = source[: arguments["numero_pagine"] * CHARS_PER_A4_PAGE]
        chunks = [
            source[index : index + CHARS_PER_A4_PAGE]
            for index in range(0, len(source), CHARS_PER_A4_PAGE)
        ]
        instructions = prompt["prompt"]
        language = arguments.get("lingua_destinazione")
        if language:
            instructions = f"Lingua di destinazione: {language}.\n{instructions}"
        # Prefisso invariante costruito una volta sola per tutti i segmenti.
        strategy_block = (
            "<strategia_system1_laya>\n"
            "Guida metodologica preliminare; non modifica il compito, i dati o il formato richiesto.\n"
            f"Categoria: {guide['task_family']}.\n"
            f"Modalità: {guide.get('execution_mode', 'single_pass')}.\n"
            f"Strategia: {guide['guidance']}\n"
            "</strategia_system1_laya>"
        )
        segment_system_message = f"{strategy_block}\n\n{instructions}"
        artifacts: list[str] = []
        truncated_part: dict | None = None
        for index, chunk in enumerate(chunks, start=1):
            # Preserve every in-scope source segment: a generic relevance classifier
            # must not silently drop content needed for extraction or translation.
            part_prompt = user_prompt(
                f"{instructions}\n\nElabora soltanto il segmento {index}/{len(chunks)}. "
                "Non completare il lavoro sugli altri segmenti e non dichiarare che questa è la risposta complessiva. "
                f"Mantieni informazioni utili all'assemblaggio finale.\n\n<segmento_fonte>\n{chunk}\n</segmento_fonte>"
            )
            part = run_stage(
                part_prompt,
                f"segmento_{index}",
                resolve_output_cap("segment", family, config.segment_max_output_tokens),
                _system_message=segment_system_message,
            )
            if part.get("status") == "truncated":
                # The prompt can no longer succeed: do not spend tokens on the rest.
                truncated_part = part
                break
            if part.get("response"):
                artifacts.append(part["response"])
        local_text = (
            None
            if truncated_part is not None
            else assemble_segments_locally(
                guide.get("task_family", "general"),
                instructions,
                artifacts,
                output_format=guide.get("output_format", ""),
            )
        )
        if truncated_part is not None:
            final = truncated_part
        elif local_text is not None:
            zero_tokens = {"input": 0, "output": 0, "reasoning": 0, "total": 0}
            trace.append(
                {
                    "system": "system2_local",
                    "stage": "assemblaggio_locale",
                    "status": "ok",
                    "tokens": zero_tokens,
                }
            )
            record_metric(
                system="system2",
                stage="assemblaggio_locale",
                status="ok",
                output_chars=len(local_text),
                tokens_in=0,
                tokens_out=0,
                tokens_total=0,
            )
            final = {
                "status": "ok" if local_text.strip() else "empty_response",
                "tokens": zero_tokens,
                "finish_reason": "local_assembly",
                "response": local_text,
            }
        else:
            # Troncare ogni risultato parziale per evitare che l'assemblaggio
            # superi il tetto configurabile; il modello System 2 può integrare
            # i bordi con contesto locale.
            _max_artifact = getattr(
                config, "laya_excerpt_max_chars", MAX_PROMPT_EXCERPT
            )
            truncated = [artifact[:_max_artifact] for artifact in artifacts]
            assembled = "\n\n---\n\n".join(
                f"<risultato_segmento_{index}>\n{artifact}\n</risultato_segmento_{index}>"
                for index, artifact in enumerate(truncated, start=1)
            )
            final_prompt = user_prompt(
                f"{instructions}\n\nAssembla i risultati parziali seguenti in un'unica risposta completa. "
                "Rimuovi duplicazioni introdotte dai confini dei segmenti, preserva l'ordine e rispetta esattamente il formato richiesto. "
                f"Non aggiungere fatti non presenti nei risultati.\n\n<risultati_parziali>\n{assembled}\n</risultati_parziali>"
            )
            final = run_stage(
                final_prompt,
                "assemblaggio_finale",
                resolve_output_cap(
                    "assembly", family, config.assembly_max_output_tokens
                ),
            )
    else:
        plan = None
        if mode == "plan_then_solve":
            plan_prompt = user_prompt(
                "Scomponi la richiesta seguente in requisiti verificabili e passaggi ordinati. "
                "Non dare ancora la risposta finale né generare l'artefatto.\n\n"
                f"{prompt['prompt']}"
            )
            plan = run_stage(
                plan_prompt, "piano_iniziale", resolve_output_cap("plan", family)
            )
            plan_action = decide(
                "valutazione piano",
                plan.get("response", f"stato={plan.get('status')}"),
                {
                    "proceed": "Il piano copre i requisiti principali e si può procedere alla risposta.",
                    "revise": "Il piano omette requisiti o passaggi; rifarlo una volta.",
                },
            )
            if plan_action == "revise":
                plan_prompt = user_prompt(
                    f"{plan_prompt['prompt']}\n\nLaya ha rilevato omissioni: rivedi il piano e includi tutti i requisiti espliciti."
                )
                plan = run_stage(
                    plan_prompt, "piano_revisionato", resolve_output_cap("plan", family)
                )
                decide(
                    "verifica piano revisionato",
                    plan.get("response", f"stato={plan.get('status')}"),
                    {
                        "proceed": "Il piano revisionato è sufficientemente completo per procedere.",
                        "incomplete": "Il piano revisionato resta incompleto.",
                    },
                )
        final_text = prompt["prompt"]
        if plan is not None:
            final_text = (
                f"Richiesta originale:\n{prompt['prompt']}\n\n"
                f"Piano prodotto da System 2 e instradato da Laya:\n{plan.get('response', '')}"
            )
        elif "source" in prompt:
            # Un task con fonte eseguito in single pass senza la fonte produrrebbe
            # una risposta non ancorata al documento (misurato in 20261023_6:
            # risposte da 651/639 caratteri e min_chars 7500 fallito su entrambi
            # i modelli): la fonte segue la richiesta come nella baseline.
            arguments = prompt.get("arguments", {})
            source = parsing.epub_text(ROOT / prompt["source"])
            if "numero_pagine" in arguments:
                source = source[: arguments["numero_pagine"] * CHARS_PER_A4_PAGE]
            language = arguments.get("lingua_destinazione")
            if language:
                source = f"Lingua di destinazione: {language}.\n{source}"
            final_text = f"{prompt['prompt']}\n\n<fonte>\n{source}\n</fonte>"
        final = run_stage(
            user_prompt(final_text),
            "risposta_finale",
            resolve_output_cap(
                "final",
                family,
                config.final_max_output_tokens,
                min_chars=_prompt_min_chars(prompt),
            ),
        )

    system2_tokens = [
        entry["tokens"] for entry in trace if entry.get("system") == "system2"
    ]
    final["tokens"] = {
        key: (
            sum(tokens[key] for tokens in system2_tokens)
            if system2_tokens
            and all(type(tokens.get(key)) is int for tokens in system2_tokens)
            else None
        )
        for key in ("input", "output", "reasoning", "total")
    }
    final["workflow"] = trace
    final["workflow_summary"] = {
        "system1_decisions": sum(
            entry.get("system") == "system1_laya" for entry in trace
        ),
        "system2_stages": sum(entry.get("system") == "system2" for entry in trace),
        "execution_mode": mode,
    }
    return final

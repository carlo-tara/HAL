"""Workflow System 1: guida, decisione, prompt e assemble locale (T2-09, rv7 N28).

Spostamento meccanico di codice da `app/benchmark_models.py` (nessun
riscrittura).
"""

from __future__ import annotations

import json
import math
import os
import time
from typing import Any

import httpx

from . import benchmark_parsing as parsing
from .benchmark_parsing import (
    _NO_JSON,
    _json_merge_items,
    _wants_json_merge,
    parse_json_document,
    prompt_message,
)
from .benchmark_quality import _mode_allowed_for_family, analyze_prompt
from .benchmark_settings import CHARS_PER_A4_PAGE, MAX_ARTIFACT_SNAPSHOT, ROOT, Settings

SYSTEM1_TASK_FAMILIES = {
    "reasoning": "Deduzione, logica o risoluzione di un problema con vincoli.",
    "math": "Calcoli quantitativi, formule, unità o verifica aritmetica.",
    "coding": "Progettazione o generazione di codice/artefatti software.",
    "source": "Estrazione o sintesi vincolata a una fonte fornita.",
    "translation": "Traduzione fedele di una fonte in una lingua richiesta.",
    "general": "Altra richiesta testuale: risposta diretta e verificabile.",
}

SYSTEM1_EXECUTION_MODES = {
    "single_pass": "Richiesta atomica: il gate iniziale instrada e System 2 risponde direttamente.",
    "plan_then_solve": "Scomponi prima requisiti e passaggi, poi risolvi con una seconda chiamata System 2.",
    "source_chunks": "Elabora una fonte lunga in segmenti ordinati, poi assembla i risultati.",
}

SYSTEM1_STRATEGIES = {
    "reasoning_check": (
        "Elenca i vincoli e i fatti, deriva la risposta per passaggi e verifica la conclusione."
    ),
    "math_check": (
        "Formalizza dati e unità, mostra i calcoli essenziali e controlla il risultato numericamente."
    ),
    "requirements_check": (
        "Estrai i requisiti espliciti, produci un artefatto completo e controlla vincoli e casi limite. "
        "Output essenziale: codice funzionante senza spiegazioni verbose a meno che non siano richieste. "
        "Usa nomi significativi, evita boilerplate non necessario."
    ),
    "grounded_extract": (
        "Usa solo la fonte fornita, rispetta esattamente formato e intervallo richiesti, "
        "non inventare dettagli. Output compatto: elenchi strutturati, valori essenziali, "
        "senza introduzioni o commenti ridondanti. Preserva solo le informazioni necessarie."
    ),
    "faithful_translate": (
        "Traduci solo il testo richiesto, preservando significato, completezza e ordine; "
        "non aggiungere sintesi."
    ),
    "direct_answer": "Rispondi direttamente alla richiesta e verifica che ogni vincolo esplicito sia rispettato.",
}

def system1_guide(prompt: dict, config: Settings, client: httpx.Client) -> dict:
    """Gate and align Laya's routing against a local, task-specific contract."""
    source = ""
    arguments = prompt.get("arguments", {})
    if "source" in prompt:
        source = parsing.epub_text(ROOT / prompt["source"])
        if "numero_pagine" in arguments:
            source = source[: arguments["numero_pagine"] * CHARS_PER_A4_PAGE]
    analysis = analyze_prompt(prompt, source_chars=len(source))
    expected_family = analysis["task_family"]
    required_strategy = analysis["task_contract"]["required_strategy"]

    # Complessità e formato per il contratto compatto (Gate 2).
    text = prompt["prompt"].lower()
    if analysis["execution_mode"] == "source_chunks":
        complexity = "high"
    elif analysis["explicit_plan"]:
        complexity = "medium"
    else:
        complexity = "atomic"

    output_format = arguments.get("output_format", "")
    if not output_format:
        for fmt in ("json", "html", "xml", "csv"):
            if fmt in text:
                output_format = fmt
                break
    if not output_format:
        output_format = "text"

    if not analysis["laya_recommended"]:
        return {
            **analysis,
            "task_family": expected_family,
            "family_confidence": 1.0,
            "strategy": required_strategy,
            "strategy_confidence": 1.0,
            "execution_mode": analysis["execution_mode"],
            "execution_confidence": 1.0,
            "confidence": 1.0,
            "guidance": SYSTEM1_STRATEGIES[required_strategy],
            "laya_called": False,
            "decision_source": "local_task_gate",
            "preflight_latency_ms": 0,
            "complexity": complexity,
            "format": output_format,
            "source": prompt.get("source"),
            "output_format": output_format,
        }

    # Gate 2: il payload verso Laya deve contenere solo contratto compatto.
    # "notes" trasmette solo le istruzioni (prompt); la fonte viene inviata
    # come estratto numerato (source_chars) e blocco excerpt con tetto
    # configurabile (config.laya_excerpt_max_chars, default 1200).
    laya_excerpt_max_chars = getattr(config, "laya_excerpt_max_chars", 1200)
    notes = prompt["prompt"]
    state = {
        "notes": notes,
        "language": "italian",
        "task_contract": analysis["task_contract"],
        "complexity": complexity,
        "format": output_format,
    }
    if source:
        state["source"] = prompt["source"]
        state["source_chars"] = len(source)
        state["excerpt"] = source[:laya_excerpt_max_chars]
    else:
        state["source_chars"] = 0
    payload = {
        "state": state,
        "questions": {
            "task_family": {
                "type": "choice",
                "instructions": (
                    f"Classifica il compito principale rispettando il contratto locale: {expected_family}. "
                    "Non confondere traduzione fedele con estrazione o sintesi."
                ),
                "criteria": SYSTEM1_TASK_FAMILIES,
            },
            "strategy": {
                "type": "choice",
                "instructions": (
                    f"Scegli la strategia coerente con il task e il formato. Strategia richiesta dal gate: "
                    f"{required_strategy}."
                ),
                "criteria": SYSTEM1_STRATEGIES,
            },
            "execution_mode": {
                "type": "choice",
                "instructions": (
                    f"Scegli una modalità compatibile col contratto: {analysis['execution_mode']}. "
                    "Non pianificare richieste atomiche e non scartare segmenti di fonte."
                ),
                "criteria": SYSTEM1_EXECUTION_MODES,
            },
        },
        "model": config.laya_model,
    }
    started = time.perf_counter()
    response = client.post(
        f"{config.laya_base_url}/predict",
        headers={"Authorization": f"Bearer {config.laya_api_key}"},
        json=payload,
        timeout=config.laya_timeout,
    )
    preflight_latency_ms = round((time.perf_counter() - started) * 1000)
    response.raise_for_status()
    data = response.json()
    answers = data.get("answers") if isinstance(data, dict) else None
    if not isinstance(answers, dict):
        raise TypeError("Laya response has no structured answers")

    def answer_for(key: str, allowed: dict[str, str]) -> tuple[str, float]:
        answer = answers.get(key)
        if not isinstance(answer, dict):
            raise TypeError(f"Laya response is missing {key}")
        choice = answer.get("choice", answer.get("prediction"))
        if not isinstance(choice, str) or choice not in allowed:
            raise ValueError(f"Laya returned an unknown {key}")
        try:
            confidence = float(answer.get("confidence", 0.0))
        except (TypeError, ValueError):
            confidence = 0.0
        if not math.isfinite(confidence) or not 0.0 <= confidence <= 1.0:
            confidence = 0.0
        return choice, confidence

    proposed_family, family_confidence = answer_for(
        "task_family", SYSTEM1_TASK_FAMILIES
    )
    proposed_strategy, strategy_confidence = answer_for("strategy", SYSTEM1_STRATEGIES)
    proposed_mode, execution_confidence = answer_for(
        "execution_mode", SYSTEM1_EXECUTION_MODES
    )
    confidence = min(family_confidence, strategy_confidence, execution_confidence)
    coherent = (
        proposed_family == expected_family
        and proposed_strategy == required_strategy
        and confidence >= config.laya_min_confidence
    )
    # The local contract is authoritative; Laya may refine only compatible choices.
    task_family = expected_family
    strategy = proposed_strategy if coherent else required_strategy
    execution_mode = analysis["execution_mode"]
    if analysis["explicit_plan"]:
        execution_mode = (
            "plan_then_solve"
            if proposed_mode == "plan_then_solve"
            and confidence >= config.laya_min_confidence
            else "single_pass"
        )
    # Gate 3: blocca modalit\u00e0 incompatibili con la famiglia task.
    if not _mode_allowed_for_family(expected_family, execution_mode):
        execution_mode = "single_pass"
    guidance = SYSTEM1_STRATEGIES[strategy]
    if confidence < config.laya_min_confidence:
        guidance = (
            "Classificazione Laya incerta: segui il contratto locale, estrai i requisiti "
            "dal prompt e rispetta rigorosamente fonte e formato."
        )
        strategy = required_strategy
    return {
        **analysis,
        "task_family": task_family,
        "family_confidence": family_confidence,
        "strategy": strategy,
        "strategy_confidence": strategy_confidence,
        "execution_mode": execution_mode,
        "execution_confidence": execution_confidence,
        "confidence": confidence,
        "guidance": guidance,
        "laya_called": True,
        "decision_source": "laya" if coherent else "local_task_gate",
        "proposed_task_family": proposed_family,
        "proposed_strategy": proposed_strategy,
        "proposed_execution_mode": proposed_mode,
        "preflight_latency_ms": preflight_latency_ms,
        "complexity": complexity,
        "source": prompt.get("source"),
        "output_format": output_format,
    }

def system1_decision(
    prompt: dict,
    config: Settings,
    client: httpx.Client,
    *,
    phase: str,
    artifact: str,
    choices: dict[str, str],
) -> dict:
    """Delegate a bounded workflow decision to Laya and preserve its choice."""
    payload = {
        "state": {
            "notes": (
                f"Richiesta: {prompt['prompt']}\nFase: {phase}\n"
                f"Output System 2 da valutare:\n{artifact[:MAX_ARTIFACT_SNAPSHOT]}"
            ),
            "language": "italian",
        },
        "questions": {
            "decision": {
                "type": "choice",
                "instructions": "Classifica il risultato e scegli l'azione successiva.",
                "criteria": choices,
            }
        },
        "model": config.laya_model,
    }
    response = client.post(
        f"{config.laya_base_url}/predict",
        headers={"Authorization": f"Bearer {config.laya_api_key}"},
        json=payload,
        timeout=config.laya_timeout,
    )
    response.raise_for_status()
    data = response.json()
    answers = data.get("answers") if isinstance(data, dict) else None
    answer = answers.get("decision") if isinstance(answers, dict) else None
    if not isinstance(answer, dict):
        raise TypeError("Laya response has no workflow decision")
    choice = answer.get("choice", answer.get("prediction"))
    if not isinstance(choice, str) or choice not in choices:
        raise ValueError("Laya returned an unknown workflow decision")
    try:
        confidence = float(answer.get("confidence", 0.0))
    except (TypeError, ValueError):
        confidence = 0.0
    if not math.isfinite(confidence) or not 0.0 <= confidence <= 1.0:
        confidence = 0.0
    return {"phase": phase, "decision": choice, "confidence": confidence}

def system1_prompt(prompt: dict, guide: dict) -> str:
    strategy = (
        "<strategia_system1_laya>\n"
        "Guida metodologica preliminare; non modifica il compito, i dati o il formato richiesto.\n"
        f"Categoria: {guide['task_family']}.\n"
        f"Modalità: {guide.get('execution_mode', 'single_pass')}.\n"
        f"Strategia: {guide['guidance']}\n"
        "</strategia_system1_laya>"
    )
    message = prompt_message(prompt)
    if "source" not in prompt:
        return f"{strategy}\n\n{message}"
    instructions = prompt["prompt"]
    language = prompt.get("arguments", {}).get("lingua_destinazione")
    if language:
        instructions = f"Lingua di destinazione: {language}.\n{instructions}"
    source = message.removesuffix(f"\n\n{instructions}")
    return f"{source}\n\n{strategy}\n\n{instructions}"

def assemble_segments_locally(
    task_family: str,
    instructions: str,
    artifacts: list[str],
    *,
    output_format: str = "",
) -> str | None:
    """Combine segment results without a model call when the merge is mechanical.

    Telemetry showed the model-based assembly stage costing ~18% of all tokens while
    shrinking the output (translations lost most of their text) and being the stage
    that most often timed out. Segments never overlap, so translations are plain
    concatenation, a single segment needs no merge, and a JSON extraction whose
    segments are all valid JSON is merged into one array. Returns None when only a
    model can assemble the result.
    HT-007 braccio B: con ``BENCHMARK_LOCAL_ASSEMBLY=0`` nell'ambiente del
    processo il merge meccanico e' disabilitato del tutto e l'assemblaggio passa
    via modello, cosi' le run A/B dei due bracci sono producibili senza toccare
    i test. Default invariato: merge locale attivo.
    """
    if os.environ.get("BENCHMARK_LOCAL_ASSEMBLY", "1").strip() == "0":
        return None
    if not artifacts:
        return None
    if len(artifacts) == 1:
        return artifacts[0]
    if task_family == "translation":
        return "\n\n".join(artifact.strip() for artifact in artifacts)
    if _wants_json_merge(instructions, output_format):
        merged: list[Any] = []
        all_json = True
        for artifact in artifacts:
            value = parse_json_document(artifact)
            if value is _NO_JSON:
                all_json = False
                break
            merged.extend(_json_merge_items(value))
        if all_json:
            return json.dumps(merged, ensure_ascii=False, indent=2)
    # Generic text: every segment is self-contained (non-overlapping source
    # chunks). Concatenate with numbered tags so the consumer can still
    # distinguish boundaries when needed.
    parts: list[str] = []
    for index, artifact in enumerate(artifacts, start=1):
        stripped = artifact.strip()
        if stripped:
            parts.append(
                f"<risultato_segmento_{index}>\n{stripped}\n</risultato_segmento_{index}>"
            )
    if parts:
        return "\n\n---\n\n".join(parts)
    return None

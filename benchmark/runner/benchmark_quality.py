"""Analisi prompt e quality-check delle risposte benchmark (T2-09, rv7 N28).

Spostamento meccanico di codice da `app/benchmark_models.py` (nessun
riscrittura).
"""

from __future__ import annotations

from .benchmark_parsing import extract_html_document, json_document
from .benchmark_settings import CHARS_PER_A4_PAGE

# Gate 3: modalità ammesse per ciascuna famiglia task.
# Alcune combinazioni sono semanticamente incompatibili (es. traduzione + chunking).
TASK_FAMILY_ALLOWED_MODES: dict[str, list[str]] = {
    "translation": ["single_pass", "source_chunks"],
    "source": ["single_pass", "source_chunks"],
    "reasoning": ["single_pass", "plan_then_solve"],
    "math": ["single_pass", "plan_then_solve"],
    "coding": ["single_pass", "plan_then_solve"],
    "general": ["single_pass", "plan_then_solve", "source_chunks"],
}

def _mode_allowed_for_family(family: str, mode: str) -> bool:
    """Verifica se una modalit\u00e0 di esecuzione \u00e8 ammessa per una famiglia task."""
    allowed = TASK_FAMILY_ALLOWED_MODES.get(family)
    if allowed is None:
        return True  # famiglie sconosciute non bloccano
    return mode in allowed

def analyze_prompt(prompt: dict, *, source_chars: int = 0) -> dict:
    """Apply a cheap task contract before deciding whether Laya can add value."""
    text = prompt["prompt"].lower()
    arguments = prompt.get("arguments", {})
    has_source = "source" in prompt
    is_translation = bool(arguments.get("lingua_destinazione")) or any(
        term in text for term in ("traduci", "tradurre", "translation", "translate")
    )
    if is_translation:
        family = "translation"
    elif has_source or any(
        term in text
        for term in ("estrai", "estrazione", "riassumi", "summarize", "extract")
    ):
        family = "source"
    elif any(
        term in text
        for term in ("html", "javascript", "python", "codice", "programma", "funzione")
    ):
        family = "coding"
    elif any(
        term in text
        for term in (
            "calcola",
            "calcolare",
            "calculation",
            "calculate",
            "percentuale",
            "ricavo",
            "utile",
        )
    ):
        family = "math"
    elif any(
        term in text
        for term in (
            "logica",
            "logico",
            "deduci",
            "deduzione",
            "vincoli",
            "puzzle",
            "scatole",
        )
    ):
        family = "reasoning"
    else:
        family = "general"

    explicit_plan = any(
        term in text
        for term in (
            "piano di implementazione",
            "scomponi la richiesta",
            "passaggi ordinati prima",
        )
    )
    if family == "source" and has_source and source_chars > CHARS_PER_A4_PAGE:
        mode = "source_chunks"
    else:
        mode = "plan_then_solve" if explicit_plan else "single_pass"
    # Tiny, atomic general prompts gain little from a remote preflight call.
    laya_recommended = family != "general" or len(text) >= 400 or explicit_plan
    return {
        "task_family": family,
        "execution_mode": mode,
        "source_chars": source_chars,
        "has_source": has_source,
        "explicit_plan": explicit_plan,
        "laya_recommended": laya_recommended,
        "task_contract": {
            "family": family,
            "required_strategy": {
                "reasoning": "reasoning_check",
                "math": "math_check",
                "coding": "requirements_check",
                "source": "grounded_extract",
                "translation": "faithful_translate",
                "general": "direct_answer",
            }[family],
            "execution_mode": mode,
            "preserve_source_order": has_source,
            "respect_output_format": any(
                term in text for term in ("json", "html", "solo il codice", "formato")
            ),
        },
    }

def quality_check_passes(check: dict, text: str) -> bool:
    kind = check["type"]
    folded = text.casefold()
    if kind == "contains_any":
        return any(value.casefold() in folded for value in check["values"])
    if kind == "absent":
        return not any(value.casefold() in folded for value in check["values"])
    if kind == "json":
        return json_document(text)
    if kind == "html":
        return extract_html_document(text) is not None
    return len(text.strip()) >= check["value"]

def evaluate_quality(prompt: dict, text: str) -> dict | None:
    checks = prompt.get("quality")
    if not checks:
        return None
    results = [
        {
            "label": check.get("label", check["type"]),
            "passed": quality_check_passes(check, text),
        }
        for check in checks
    ]
    passed = sum(result["passed"] for result in results)
    return {
        "passed": passed,
        "total": len(results),
        "score": round(passed / len(results), 2),
        "checks": results,
    }

"""Sequential Ollama/Google text benchmark with provider-reported token usage.

Facciata pubblica del benchmark (T2-09, rv7 N28): il codice vive nei moduli
`app/benchmark_settings|parsing|quality|workflow|calls|system2|report|runner|cli`.
Questo modulo ri-esporta i nomi (import path storici invariati) e resta
l'entry point `python -m app.benchmark_models`.
"""

from __future__ import annotations

from .benchmark_calls import (
    LocalTranslation,
    benchmark_call,
    discover_models,
    headers_for,
    local_translation,
    openai_compatible_google,
    parse_response,
    token_count,
    translation_result,
)
from .benchmark_cli import main
from .benchmark_parsing import (
    _NO_JSON,
    QUALITY_TYPES,
    _HtmlText,
    _json_merge_items,
    _prompt_min_chars,
    _wants_json_merge,
    epub_text,
    extract_html_document,
    json_document,
    load_inputs,
    parse_json_document,
    prompt_message,
    safe_path_component,
    validate_quality,
)
from .benchmark_quality import (
    TASK_FAMILY_ALLOWED_MODES,
    _mode_allowed_for_family,
    analyze_prompt,
    evaluate_quality,
    quality_check_passes,
)
from .benchmark_report import (
    apply_llm_model_override,
    common_benchmark_dir,
    describe_result,
    log,
    log_final_summary,
    summary,
)
from .benchmark_runner import filter_models, filter_prompts, run_benchmark
from .benchmark_settings import (
    CHARS_PER_A4_PAGE,
    CONTRACT_CHARS_PER_TOKEN,
    DEFAULT_OUTPUT_CAPS,
    FINAL_OUTPUT_CAP_BY_FAMILY,
    MAX_ARTIFACT_SNAPSHOT,
    MAX_PROMPT_EXCERPT,
    ROOT,
    Settings,
    _env_flag,
    resolve_output_cap,
    utc_now,
    write_json,
)
from .benchmark_system2 import system2_workflow_call
from .benchmark_workflow import (
    SYSTEM1_EXECUTION_MODES,
    SYSTEM1_STRATEGIES,
    SYSTEM1_TASK_FAMILIES,
    assemble_segments_locally,
    system1_decision,
    system1_guide,
    system1_prompt,
)

__all__ = [
    "CHARS_PER_A4_PAGE",
    "CONTRACT_CHARS_PER_TOKEN",
    "DEFAULT_OUTPUT_CAPS",
    "FINAL_OUTPUT_CAP_BY_FAMILY",
    "MAX_ARTIFACT_SNAPSHOT",
    "MAX_PROMPT_EXCERPT",
    "QUALITY_TYPES",
    "ROOT",
    "SYSTEM1_EXECUTION_MODES",
    "SYSTEM1_STRATEGIES",
    "SYSTEM1_TASK_FAMILIES",
    "TASK_FAMILY_ALLOWED_MODES",
    "_NO_JSON",
    "LocalTranslation",
    "Settings",
    "_HtmlText",
    "_env_flag",
    "_json_merge_items",
    "_mode_allowed_for_family",
    "_prompt_min_chars",
    "_wants_json_merge",
    "analyze_prompt",
    "apply_llm_model_override",
    "assemble_segments_locally",
    "benchmark_call",
    "common_benchmark_dir",
    "describe_result",
    "discover_models",
    "epub_text",
    "evaluate_quality",
    "extract_html_document",
    "filter_models",
    "filter_prompts",
    "headers_for",
    "json_document",
    "load_inputs",
    "local_translation",
    "log",
    "log_final_summary",
    "main",
    "openai_compatible_google",
    "parse_json_document",
    "parse_response",
    "prompt_message",
    "quality_check_passes",
    "resolve_output_cap",
    "run_benchmark",
    "safe_path_component",
    "summary",
    "system1_decision",
    "system1_guide",
    "system1_prompt",
    "system2_workflow_call",
    "token_count",
    "translation_result",
    "utc_now",
    "validate_quality",
    "write_json",
]

if __name__ == "__main__":
    raise SystemExit(main())

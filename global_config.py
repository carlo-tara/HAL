from __future__ import annotations

import math
import os
from collections.abc import Callable
from typing import Any, ClassVar

from laya_service import LayaSystemOneService
from system1_preflight import TaskContract

DEFAULT_LAYA_BASE_URL = "http://laya.local:8091/v1"
DEFAULT_LAYA_TIMEOUT = "10.0"

DEFAULT_LLM_EXTERNAL_MODE = 0
DEFAULT_LLM_EXTERNAL_URI = "https://api.orcarouter.com/v1"


# Modelli OrcaRouter associati per ciascun agente di HAL
AGENT_EXTERNAL_MODELS: dict[str, str] = {
    "a-agentzero": "orcarouter/deepseek/deepseek-v4-flash-free",
    "a-b2b": "orcarouter/z-ai/glm-5.3-flash",
    "a-copywriter": "orcarouter/openai/gpt-4o-mini",
    "a-design": "orcarouter/qwen/qwen3.8-flash",
    "a-harness": "orcarouter/deepseek/deepseek-v4.1-flash",
    "a-product": "orcarouter/deepseek/deepseek-v4-flash-free",
    "a-seozoom": "orcarouter/deepseek/deepseek-v4-flash-free",
    "a-wordpress": "orcarouter/z-ai/glm-5.3-flash",
    "enrichment": "orcarouter/deepseek/deepseek-v4-flash-free",
    "personas": "orcarouter/openai/gpt-4o-mini",
    "jtbd": "orcarouter/openai/gpt-4o-mini",
    "gherkin": "orcarouter/qwen/qwen3.8-flash",
    "charts": "orcarouter/qwen/qwen3.8-flash",
    "illustrator": "orcarouter/qwen/qwen3.8-flash",
    "uiux": "orcarouter/qwen/qwen3.8-flash",
    "harness-agentfactory": "orcarouter/deepseek/deepseek-v4.1-flash",
    "learn": "orcarouter/openai/gpt-4o-mini",
    "sync": "orcarouter/deepseek/deepseek-v4-flash",
}


def get_agent_llm_config(agent_name: str) -> dict[str, Any]:
    """
    Risolve la configurazione LLM per un agente specifico condizionata dal feature flag:
      - LLM_EXTERNAL_MODE: 0 (default spento) | 1 (attivo)
      - LLM_EXTERNAL_URI: endpoint OrcaRouter
      - LLM_EXTERNAL_MODEL: modello esterno associato
    Se LLM_EXTERNAL_MODE == 0, l'esecuzione ricade sul modello predefinito System 2.
    """
    env_prefix = agent_name.upper().replace("-", "_")

    # Flag per-agente con fallback sul flag globale (default: 0 = spento)
    mode_raw = os.getenv(
        f"{env_prefix}_LLM_EXTERNAL_MODE",
        os.getenv("LLM_EXTERNAL_MODE", str(DEFAULT_LLM_EXTERNAL_MODE)),
    )
    try:
        mode = int(mode_raw)
    except ValueError:
        mode = DEFAULT_LLM_EXTERNAL_MODE

    uri = os.getenv(
        f"{env_prefix}_LLM_EXTERNAL_URI",
        os.getenv("LLM_EXTERNAL_URI", DEFAULT_LLM_EXTERNAL_URI),
    )
    default_model = AGENT_EXTERNAL_MODELS.get(
        agent_name, "orcarouter/deepseek/deepseek-v4-flash-free"
    )
    model = os.getenv(f"{env_prefix}_LLM_EXTERNAL_MODEL", default_model)

    active_model = model if mode == 1 else SystemTwoEngine.ACTIVE_MODEL_NAME
    provider = "orcarouter" if mode == 1 else "system2_default"

    return {
        "agent": agent_name,
        "LLM_EXTERNAL_MODE": mode,
        "LLM_EXTERNAL_URI": uri,
        "LLM_EXTERNAL_MODEL": model,
        "active_model": active_model,
        "provider": provider,
    }


def resolve_agent_model(agent_name: str) -> str:
    """Restituisce il nome del modello attivo per l'agente (OrcaRouter se mode=1, altrimenti System 2)."""
    cfg = get_agent_llm_config(agent_name)
    return str(cfg["active_model"])


def configure_laya_defaults() -> None:
    """
    Configura le variabili d'ambiente di default per garantire che ogni nuova esecuzione
    e chat utilizzi laya.local per i task System 1.
    """
    os.environ.setdefault("LAYA_BASE_URL", DEFAULT_LAYA_BASE_URL)
    os.environ.setdefault("LAYA_TIMEOUT", DEFAULT_LAYA_TIMEOUT)


configure_laya_defaults()

# Profili d'uso e capability per la risoluzione del modello System 2 indipendentemente dall'agente
SYSTEM_TWO_PROFILES: dict[str, dict[str, Any]] = {
    "coding": {
        "min_context": 8192,
        "code_capable": True,
        "preferred_models": [
            "orcarouter/deepseek/deepseek-v4.1-flash",
            "orcarouter/kimi/kimi-k2.7-code",
            "Gemini 3.5 Flash-Lite",
        ],
    },
    "reasoning_planning": {
        "min_context": 16384,
        "code_capable": True,
        "preferred_models": [
            "orcarouter/deepseek/deepseek-v4.1-flash",
            "Gemini 3.5 Flash-Lite",
        ],
    },
    "text_editing": {
        "min_context": 4096,
        "code_capable": False,
        "preferred_models": ["orcarouter/openai/gpt-4o-mini", "Gemini 3.5 Flash-Lite"],
    },
    "default": {
        "min_context": 4096,
        "code_capable": False,
        "preferred_models": ["Gemini 3.5 Flash-Lite"],
    },
}


def resolve_model_for_profile(
    profile: str = "default",
    required_capabilities: list[str] | None = None,
    requested_model: str | None = None,
) -> str:
    """
    Seleziona il modello System 2 basandosi sul profilo d'uso e sulle capability,
    indipendentemente dall'identità dell'agente. Mantiene il fallback condiviso
    (ACTIVE_MODEL_NAME) e impedisce l'accettazione di nomi modello arbitrari o non validati da input esterni/Laya.
    """
    required_capabilities = required_capabilities or []
    profile_cfg = SYSTEM_TWO_PROFILES.get(profile, SYSTEM_TWO_PROFILES["default"])

    if requested_model:
        allowed_models = set(profile_cfg["preferred_models"]) | {
            SystemTwoEngine.ACTIVE_MODEL_NAME,
            "orcarouter/deepseek/deepseek-v4.1-flash",
            "orcarouter/deepseek/deepseek-v4-flash-free",
            "orcarouter/openai/gpt-4o-mini",
            "orcarouter/z-ai/glm-5.3-flash",
            "orcarouter/qwen/qwen3.8-flash",
            "orcarouter/anthropic/claude-haiku-5.5",
            "orcarouter/anthropic/claude-sonnet-5.5",
            "orcarouter/anthropic/claude-opus-5.5",
            "orcarouter/openai/gpt-6-luna",
            "orcarouter/openai/gpt-6-sol",
            "orcarouter/openai/gpt-5-nano",
            "orcarouter/google/gemini-3.5-flash-lite",
            "orcarouter/google/gemini-3.8-flash",
            "orcarouter/z-ai/glm-5.3-flash-free",
            "orcarouter/deepseek/deepseek-v4.1-flash-free",
            "orcarouter/tencent/hy3-free",
            "orcarouter/orca/orcaverify-text1.0-free",
            "orcarouter/tencent/hy4-preview-free",
            "orcarouter/qwen/qwen3.7-flash",
            "anthropic/claude-haiku-5.5",
            "anthropic/claude-sonnet-5.5",
            "anthropic/claude-opus-5.5",
            "openai/gpt-6-luna",
            "openai/gpt-6-sol",
            "openai/gpt-5-nano",
            "google/gemini-3.5-flash-lite",
            "google/gemini-3.8-flash",
            "z-ai/glm-5.3-flash-free",
            "deepseek/deepseek-v4.1-flash-free",
            "tencent/hy3-free",
            "orca/orcaverify-text1.0-free",
            "tencent/hy4-preview-free",
            "deepseek/deepseek-v4-flash-free",
            "qwen/qwen3.7-flash",
        }
        if requested_model not in allowed_models:
            return SystemTwoEngine.ACTIVE_MODEL_NAME
        return requested_model

    external_mode = int(os.getenv("LLM_EXTERNAL_MODE", str(DEFAULT_LLM_EXTERNAL_MODE)))
    preferred = profile_cfg.get("preferred_models", [SystemTwoEngine.ACTIVE_MODEL_NAME])
    if external_mode == 1 and preferred:
        return preferred[0]

    return SystemTwoEngine.ACTIVE_MODEL_NAME


class SystemTwoResponse(str):
    model: str
    provider: str
    fallback_used: bool
    response: str

    def __new__(cls, text: str, model: str, provider: str, fallback_used: bool = False):
        obj = super().__new__(cls, text)
        obj.model = model
        obj.provider = provider
        obj.fallback_used = fallback_used
        obj.response = text
        return obj


class SystemTwoEngine:
    """
    Motore System 2 gestito dal modello di interfaccia corrente (es. Gemini 3.5 Flash-Lite)
    con supporto estensibile per futuri motori System 2, backend reali/mock e routing condizionato (OrcaRouter).
    """

    ACTIVE_MODEL_NAME: ClassVar[str] = "Gemini 3.5 Flash-Lite"
    _custom_backend: ClassVar[Callable[..., Any] | None] = None
    _fallback_backend: ClassVar[Callable[..., Any] | None] = None

    @classmethod
    def register_backend(
        cls,
        backend: Callable[..., Any] | None,
        fallback: Callable[..., Any] | None = None,
    ) -> None:
        cls._custom_backend = backend
        cls._fallback_backend = fallback

    @classmethod
    def resolve_model(cls, agent_name: str | None = None) -> str:
        if agent_name:
            return resolve_agent_model(agent_name)
        return cls.ACTIVE_MODEL_NAME

    @classmethod
    def execute(
        cls, task: str, text: str, *args: Any, agent: str | None = None, **kwargs: Any
    ) -> Any:
        model = cls.resolve_model(agent)
        cfg = get_agent_llm_config(agent) if agent else {"provider": "system2_default"}
        provider = cfg.get("provider", "system2_default")

        try:
            if cls._custom_backend is not None:
                res = cls._custom_backend(
                    task, text, *args, model=model, agent=agent, **kwargs
                )
                if isinstance(res, dict):
                    resp_text = res.get("response", str(res))
                    served_model = res.get("model", model)
                    prov = res.get("provider", provider)
                    return SystemTwoResponse(
                        resp_text, served_model, prov, fallback_used=False
                    )
                elif isinstance(res, str):
                    return SystemTwoResponse(res, model, provider, fallback_used=False)
                else:
                    return SystemTwoResponse(
                        str(res), model, provider, fallback_used=False
                    )

            resp_text = f"[{model} - System 2: {task}] Processed: {text}"
            return SystemTwoResponse(resp_text, model, provider, fallback_used=False)
        except Exception as e:
            if cls._fallback_backend is not None:
                res = cls._fallback_backend(
                    task, text, *args, model=model, agent=agent, error=e, **kwargs
                )
                resp_text = (
                    res.get("response", f"[Fallback] Error: {e}")
                    if isinstance(res, dict)
                    else str(res)
                )
                fallback_model = (
                    res.get("model", model) if isinstance(res, dict) else model
                )
                return SystemTwoResponse(
                    resp_text, fallback_model, provider, fallback_used=True
                )
            raise


class GlobalLayaHandler:
    """
    Handler centralizzato che distingue tra task System 1 (Laya)
    e task System 2 (Modello di interfaccia / motori estensibili).
    """

    # Task System 1 (affidati a Laya)
    _SYSTEM_ONE_TABLE: ClassVar[dict[str, Callable[[tuple], Any]]] = {
        "choice": lambda args: LayaSystemOneService.choice(args[0], args[1]),
        "routing": lambda args: LayaSystemOneService.routing(args[0], args[1]),
        "score": lambda args: LayaSystemOneService.score(args[0], args[1]),
        "noul": lambda args: LayaSystemOneService.noul(args[0]),
    }

    # Task System 2 (tradotti in inglese, gestiti dal modello di interfaccia / System 2 engines)
    _SYSTEM_TWO_TASKS: ClassVar[set[str]] = {
        "coding",
        "text_editing",
        "image_generation",
        "summarization",
        "translation",
        "extraction",
        "classification",
        "security_check",
        "reasoning_planning",
    }

    @classmethod
    def evaluate(cls, task_type: str, *args: Any, **kwargs: Any) -> Any:
        configure_laya_defaults()

        # Quick path for coherence gate (System 1)
        if task_type == "coherence":
            task_contract = kwargs.get("task_contract")
            if task_contract is None:
                # Fallback: construct a minimal TaskContract for coherence gate
                contract = TaskContract(
                    task_type=task_type,
                    instruction="coherence gate",
                    source="",
                    output_format="",
                )
            else:
                contract = TaskContract(
                    task_type=task_type,
                    instruction="coherence gate",
                    source="",
                    output_format="",
                )
            return LayaSystemOneService.coherence(contract)

        # Check System 1
        if task_type in cls._SYSTEM_ONE_TABLE:
            with LayaSystemOneService.budget(kwargs.get("laya_budget")):
                task_contract = kwargs.get("task_contract")
                if task_contract is not None:
                    contract = TaskContract.from_request(task_type, args, task_contract)
                    return LayaSystemOneService.preflight(contract)
                return cls._SYSTEM_ONE_TABLE[task_type](args)

        # Check System 2
        if task_type in cls._SYSTEM_TWO_TASKS:
            text_arg = args[0] if args else ""
            return SystemTwoEngine.execute(task_type, text_arg, *args[1:], **kwargs)

        supported = list(cls._SYSTEM_ONE_TABLE.keys()) + list(cls._SYSTEM_TWO_TASKS)
        raise ValueError(f"Task sconosciuto: {task_type}. Task supportati: {supported}")


def augment_response_with_wysiati(
    response: dict[str, Any],
    text_length: int = 100,
    missing_context_indicators: int = 0,
) -> dict[str, Any]:
    """
    Aggiunge flag di completezza informativa (WYSIATI - What You See Is All There Is)
    ai payload di risposta di Laya Service e Gateway.
    """
    completeness_score = max(0.0, min(1.0, 1.0 - (missing_context_indicators * 0.25)))
    if text_length < 20:
        completeness_score *= 0.5

    wysiati_complete = completeness_score >= 0.7 and missing_context_indicators == 0

    augmented = dict(response)
    augmented["wysiati_complete"] = wysiati_complete
    augmented["evidence_completeness_score"] = round(completeness_score, 2)
    return augmented


class SystemRoutingPolicy:
    """
    Policy di instradamento System 1 / System 2 e riduzione del budget System 2
    basata su rischio, complessità, tool, tensione cognitiva e affidabilità dell'esito Laya (WYSIATI / astensione).
    """

    @classmethod
    def evaluate_routing(
        cls,
        task_type: str,
        text: str,
        laya_assessment: dict | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        laya_assessment = laya_assessment or {}
        decision_status = laya_assessment.get("decision_status", "ok")
        risk_score = laya_assessment.get("risk_score", 0.0)
        has_side_effects = kwargs.get("has_side_effects", False)
        cognitive_tension = kwargs.get("cognitive_tension", 0.0)
        is_closed_decision = task_type in {"choice", "routing", "score", "noul"}

        # Regola 0: Tensione cognitiva elevata o task complesso → Impedisce pigrizia di System 2, forza S2 Full
        if cognitive_tension >= 0.7:
            return {
                "tier": "s2_full",
                "executor": "system_two_engine",
                "budget_reduction": False,
                "max_tokens": 4096,
                "context_window": 16384,
                "allow_tools": True,
                "cognitive_tension_triggered": True,
            }

        # Regola 1: Decisioni chiuse con esito Laya valido e basso rischio → System 1 (S1)
        if (
            is_closed_decision
            and decision_status == "ok"
            and risk_score < 0.5
            and not has_side_effects
        ):
            return {
                "tier": "s1",
                "executor": "laya_system_one",
                "budget_reduction": False,
                "max_tokens": 256,
                "context_window": 1024,
                "allow_tools": False,
            }

        # Regola 2: Astensione, errore o rischio elevato → System 2 Completo (S2 Full), mai riduzione
        if (
            decision_status == "abstain"
            or risk_score >= 0.7
            or has_side_effects
            or task_type in {"security_check", "reasoning_planning"}
        ):
            return {
                "tier": "s2_full",
                "executor": "system_two_engine",
                "budget_reduction": False,
                "max_tokens": 4096,
                "context_window": 16384,
                "allow_tools": True,
            }

        # Regola 3: Generazione semplice a basso rischio con esito sicuro → System 2 Ridotto (S2 Reduced)
        if (
            decision_status == "ok"
            and risk_score < 0.3
            and task_type
            in {"text_editing", "summarization", "translation", "extraction"}
        ):
            return {
                "tier": "s2_reduced",
                "executor": "system_two_engine",
                "budget_reduction": True,
                "max_tokens": 1024,
                "context_window": 4096,
                "allow_tools": False,
            }

        # Default fallback: System 2 Standard / Full
        return {
            "tier": "s2_full",
            "executor": "system_two_engine",
            "budget_reduction": False,
            "max_tokens": 2048,
            "context_window": 8192,
            "allow_tools": True,
        }


class SystemEvaluationEngine:
    """
    Motore di evaluation offline (replay), shadow mode e metriche di gate con rollback
    per configurazioni e policy di routing System 2.
    """

    @classmethod
    def replay(
        cls, requests: list[dict[str, Any]], candidate_config: dict[str, Any]
    ) -> dict[str, Any]:
        """Aggregate benchmark records without conflating quality or timing signals.

        ``quality`` is the benchmark's automated checklist; ``semantic_quality_score``
        must come from an independent validator. ``seconds`` is end-to-end duration,
        not serving latency.
        """
        total = len(requests)

        def finite_non_negative(raw_value: Any) -> float | None:
            if raw_value is None or isinstance(raw_value, bool):
                return None
            try:
                value = float(raw_value)
            except (TypeError, ValueError):
                return None
            return value if math.isfinite(value) and value >= 0 else None

        def quality_for(request: dict[str, Any]) -> float | None:
            quality = request.get("quality")
            if isinstance(quality, dict):
                score = finite_non_negative(quality.get("score"))
                if score is None or score > 1:
                    passed = finite_non_negative(quality.get("passed"))
                    checks = finite_non_negative(quality.get("total"))
                    if passed is not None and checks is not None and checks > 0:
                        score = passed / checks
            else:
                score = finite_non_negative(request.get("quality_score"))
            return score if score is not None and score <= 1 else None

        successes = 0
        truncated_requests = 0
        latencies: list[float] = []
        durations: list[float] = []
        costs: list[float] = []
        quality_scores: list[float] = []
        semantic_quality_scores: list[float] = []
        task_scores: dict[str, list[float]] = {}

        for request in requests:
            status = request.get("status")
            if isinstance(status, str):
                successes += status in {"ok", "success"}
                truncated_requests += status == "truncated"
            else:
                successes += request.get("expected_outcome") == "success"

            latency = finite_non_negative(request.get("latency_ms"))
            if latency is not None:
                latencies.append(latency)
            duration = finite_non_negative(request.get("seconds"))
            if duration is not None:
                durations.append(duration)
            cost = finite_non_negative(request.get("estimated_cost"))
            if cost is not None:
                costs.append(cost)

            quality_score = quality_for(request)
            if quality_score is not None:
                quality_scores.append(quality_score)
                task = str(request.get("test_id") or request.get("task") or "unknown")
                task_scores.setdefault(task, []).append(quality_score)
            semantic_score = finite_non_negative(request.get("semantic_quality_score"))
            if semantic_score is not None and semantic_score <= 1:
                semantic_quality_scores.append(semantic_score)

        task_quality = {
            task: {"score": sum(scores) / len(scores), "samples": len(scores)}
            for task, scores in task_scores.items()
        }
        return {
            "total_requests": total,
            "successes": successes,
            "success_rate": successes / total if total else 0.0,
            "error_rate": (total - successes) / total if total else 0.0,
            "truncated_requests": truncated_requests,
            "avg_latency_ms": sum(latencies) / len(latencies) if latencies else 0.0,
            "latency_samples": len(latencies),
            "avg_end_to_end_seconds": sum(durations) / len(durations)
            if durations
            else 0.0,
            "duration_samples": len(durations),
            "estimated_cost": sum(costs) if costs else 0.0,
            "cost_samples": len(costs),
            "quality_score": sum(quality_scores) / len(quality_scores)
            if quality_scores
            else 0.0,
            "quality_samples": len(quality_scores),
            "quality_coverage": len(quality_scores) / total if total else 0.0,
            "semantic_quality_score": (
                sum(semantic_quality_scores) / len(semantic_quality_scores)
                if semantic_quality_scores
                else 0.0
            ),
            "semantic_quality_samples": len(semantic_quality_scores),
            "semantic_quality_coverage": (
                len(semantic_quality_scores) / total if total else 0.0
            ),
            "task_quality": task_quality,
            "candidate_config": candidate_config,
        }

    @classmethod
    def shadow_evaluate(
        cls,
        primary_response: dict[str, Any],
        shadow_response: dict[str, Any],
        tolerances: dict[str, float] | None = None,
    ) -> dict[str, Any]:
        primary_text = primary_response.get("response", "")
        shadow_text = shadow_response.get("response", "")
        match = primary_text.strip().lower() == shadow_text.strip().lower()
        primary_lat = primary_response.get("latency_ms", 100)
        shadow_lat = shadow_response.get("latency_ms", 100)
        delta_ms = shadow_lat - primary_lat
        return {
            "match": match,
            "primary_latency_ms": primary_lat,
            "shadow_latency_ms": shadow_lat,
            "latency_delta_ms": delta_ms,
        }

    @classmethod
    def promote_with_rollback(
        cls, metrics: dict[str, Any], gate_thresholds: dict[str, Any]
    ) -> tuple[bool, str]:
        """Promote only with complete, independent quality and serving evidence."""

        def number(name: str) -> float | None:
            raw_value = metrics.get(name)
            if raw_value is None or isinstance(raw_value, bool):
                return None
            try:
                value = float(raw_value)
            except (TypeError, ValueError):
                return None
            return value if math.isfinite(value) else None

        required = (
            "success_rate",
            "error_rate",
            "avg_latency_ms",
            "latency_samples",
            "quality_score",
            "quality_samples",
            "quality_coverage",
            "semantic_quality_score",
            "semantic_quality_samples",
            "semantic_quality_coverage",
            "truncated_requests",
        )
        missing = [name for name in required if number(name) is None]
        if missing:
            return False, (
                "Gate failed: missing or invalid evidence: "
                + ", ".join(missing)
                + ". Rollback triggered to previous stable config."
            )

        success_rate = number("success_rate")
        error_rate = number("error_rate")
        avg_latency_ms = number("avg_latency_ms")
        latency_samples = number("latency_samples")
        quality_score = number("quality_score")
        quality_samples = number("quality_samples")
        quality_coverage = number("quality_coverage")
        semantic_quality_score = number("semantic_quality_score")
        semantic_quality_samples = number("semantic_quality_samples")
        semantic_quality_coverage = number("semantic_quality_coverage")
        truncated_requests = number("truncated_requests")
        assert success_rate is not None
        assert error_rate is not None
        assert avg_latency_ms is not None
        assert latency_samples is not None
        assert quality_score is not None
        assert quality_samples is not None
        assert quality_coverage is not None
        assert semantic_quality_score is not None
        assert semantic_quality_samples is not None
        assert semantic_quality_coverage is not None
        assert truncated_requests is not None

        def threshold(name: str, default: float) -> float | None:
            raw_value = gate_thresholds.get(name, default)
            if isinstance(raw_value, bool):
                return None
            try:
                value = float(raw_value)
            except (TypeError, ValueError):
                return None
            return value if math.isfinite(value) else None

        threshold_defaults = {
            "min_success_rate": 0.95,
            "max_error_rate": 0.05,
            "max_latency_ms": 500.0,
            "min_quality_score": 0.8,
            "min_quality_coverage": 0.8,
            "min_semantic_quality_score": 0.8,
            "min_semantic_quality_coverage": 0.8,
            "min_task_quality_score": 0.5,
            "max_truncated_requests": 0,
        }
        parsed_thresholds = {
            name: threshold(name, default)
            for name, default in threshold_defaults.items()
        }
        invalid_thresholds = [
            name for name, value in parsed_thresholds.items() if value is None
        ]
        if invalid_thresholds:
            return False, (
                "Gate failed: invalid thresholds: "
                + ", ".join(invalid_thresholds)
                + ". Rollback triggered to previous stable config."
            )

        min_success = parsed_thresholds["min_success_rate"]
        max_error = parsed_thresholds["max_error_rate"]
        max_latency = parsed_thresholds["max_latency_ms"]
        min_quality = parsed_thresholds["min_quality_score"]
        min_quality_coverage = parsed_thresholds["min_quality_coverage"]
        min_semantic_quality = parsed_thresholds["min_semantic_quality_score"]
        min_semantic_coverage = parsed_thresholds["min_semantic_quality_coverage"]
        min_task_quality = parsed_thresholds["min_task_quality_score"]
        max_truncated = parsed_thresholds["max_truncated_requests"]
        assert min_success is not None
        assert max_error is not None
        assert max_latency is not None
        assert min_quality is not None
        assert min_quality_coverage is not None
        assert min_semantic_quality is not None
        assert min_semantic_coverage is not None
        assert min_task_quality is not None
        assert max_truncated is not None
        failures: list[str] = []

        for name, value in (
            ("success_rate", success_rate),
            ("error_rate", error_rate),
            ("quality_score", quality_score),
            ("quality_coverage", quality_coverage),
            ("semantic_quality_score", semantic_quality_score),
            ("semantic_quality_coverage", semantic_quality_coverage),
        ):
            if not 0 <= value <= 1:
                failures.append(f"{name}={value} is outside [0, 1]")
        for name, value in (
            ("latency_samples", latency_samples),
            ("quality_samples", quality_samples),
            ("semantic_quality_samples", semantic_quality_samples),
            ("truncated_requests", truncated_requests),
        ):
            if value < 0 or not value.is_integer():
                failures.append(f"{name}={value} is not a non-negative count")
        if avg_latency_ms < 0:
            failures.append(f"avg_latency_ms={avg_latency_ms} is negative")

        if quality_samples < 1:
            failures.append("no quality samples")
        if quality_coverage < min_quality_coverage:
            failures.append(
                f"quality_coverage={quality_coverage:.3f} (min {min_quality_coverage})"
            )
        if quality_score < min_quality:
            failures.append(f"quality_score={quality_score:.3f} (min {min_quality})")
        if semantic_quality_samples < 1:
            failures.append("no independent semantic-quality samples")
        if semantic_quality_coverage < min_semantic_coverage:
            failures.append(
                "semantic_quality_coverage="
                f"{semantic_quality_coverage:.3f} (min {min_semantic_coverage})"
            )
        if semantic_quality_score < min_semantic_quality:
            failures.append(
                f"semantic_quality_score={semantic_quality_score:.3f} "
                f"(min {min_semantic_quality})"
            )
        if latency_samples < 1:
            failures.append("no comparable serving-latency samples")
        if truncated_requests > max_truncated:
            failures.append(
                f"truncated_requests={truncated_requests} (max {max_truncated})"
            )
        if success_rate < min_success:
            failures.append(f"success_rate={success_rate:.3f} (min {min_success})")
        if error_rate > max_error:
            failures.append(f"error_rate={error_rate:.3f} (max {max_error})")
        if avg_latency_ms > max_latency:
            failures.append(f"avg_latency_ms={avg_latency_ms:.1f} (max {max_latency})")

        task_quality = metrics.get("task_quality", {})
        task_thresholds = gate_thresholds.get("min_task_quality", {})
        if isinstance(task_quality, dict):
            for task, result in task_quality.items():
                if not isinstance(result, dict):
                    failures.append(f"task_quality[{task}] is invalid")
                    continue
                score = result.get("score")
                if score is None or isinstance(score, bool):
                    failures.append(f"task_quality[{task}] is missing a valid score")
                    continue
                try:
                    score = float(score)
                except (TypeError, ValueError):
                    failures.append(f"task_quality[{task}] is missing a valid score")
                    continue
                if not math.isfinite(score):
                    failures.append(f"task_quality[{task}] is not finite")
                    continue
                floor = task_thresholds.get(task, min_task_quality)
                if score < floor:
                    failures.append(f"task_quality[{task}]={score:.3f} (min {floor})")
            for task in task_thresholds:
                if task not in task_quality:
                    failures.append(f"task_quality[{task}] has no samples")
        elif task_thresholds:
            failures.append("task_quality evidence is invalid")

        max_duration = gate_thresholds.get("max_end_to_end_seconds")
        if max_duration is not None:
            duration_samples = number("duration_samples")
            avg_duration = number("avg_end_to_end_seconds")
            if duration_samples is None or avg_duration is None or duration_samples < 1:
                failures.append("no end-to-end duration samples")
            elif avg_duration > max_duration:
                failures.append(
                    f"avg_end_to_end_seconds={avg_duration:.1f} (max {max_duration})"
                )

        if failures:
            reason = "Gate failed: " + "; ".join(failures)
            return False, reason + ". Rollback triggered to previous stable config."
        return True, "Gate passed successfully"

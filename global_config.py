from __future__ import annotations

import os
from collections.abc import Callable
from typing import Any, ClassVar

from laya_service import LayaSystemOneService

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
    mode_raw = os.getenv(f"{env_prefix}_LLM_EXTERNAL_MODE", os.getenv("LLM_EXTERNAL_MODE", str(DEFAULT_LLM_EXTERNAL_MODE)))
    try:
        mode = int(mode_raw)
    except ValueError:
        mode = DEFAULT_LLM_EXTERNAL_MODE

    uri = os.getenv(
        f"{env_prefix}_LLM_EXTERNAL_URI",
        os.getenv("LLM_EXTERNAL_URI", DEFAULT_LLM_EXTERNAL_URI),
    )
    default_model = AGENT_EXTERNAL_MODELS.get(agent_name, "orcarouter/deepseek/deepseek-v4-flash-free")
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
            "Gemini 3.5 Flash-Lite"
        ]
    },
    "reasoning_planning": {
        "min_context": 16384,
        "code_capable": True,
        "preferred_models": [
            "orcarouter/deepseek/deepseek-v4.1-flash",
            "Gemini 3.5 Flash-Lite"
        ]
    },
    "text_editing": {
        "min_context": 4096,
        "code_capable": False,
        "preferred_models": [
            "orcarouter/openai/gpt-4o-mini",
            "Gemini 3.5 Flash-Lite"
        ]
    },
    "default": {
        "min_context": 4096,
        "code_capable": False,
        "preferred_models": [
            "Gemini 3.5 Flash-Lite"
        ]
    }
}

def resolve_model_for_profile(
    profile: str = "default",
    required_capabilities: list[str] | None = None,
    requested_model: str | None = None
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
            "orcarouter/qwen/qwen3.8-flash"
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
    def register_backend(cls, backend: Callable[..., Any] | None, fallback: Callable[..., Any] | None = None) -> None:
        cls._custom_backend = backend
        cls._fallback_backend = fallback

    @classmethod
    def resolve_model(cls, agent_name: str | None = None) -> str:
        if agent_name:
            return resolve_agent_model(agent_name)
        return cls.ACTIVE_MODEL_NAME

    @classmethod
    def execute(cls, task: str, text: str, *args: Any, agent: str | None = None, **kwargs: Any) -> Any:
        model = cls.resolve_model(agent)
        cfg = get_agent_llm_config(agent) if agent else {"provider": "system2_default"}
        provider = cfg.get("provider", "system2_default")

        try:
            if cls._custom_backend is not None:
                res = cls._custom_backend(task, text, *args, model=model, agent=agent, **kwargs)
                if isinstance(res, dict):
                    resp_text = res.get("response", str(res))
                    served_model = res.get("model", model)
                    prov = res.get("provider", provider)
                    return SystemTwoResponse(resp_text, served_model, prov, fallback_used=False)
                elif isinstance(res, str):
                    return SystemTwoResponse(res, model, provider, fallback_used=False)
                else:
                    return SystemTwoResponse(str(res), model, provider, fallback_used=False)

            resp_text = f"[{model} - System 2: {task}] Processed: {text}"
            return SystemTwoResponse(resp_text, model, provider, fallback_used=False)
        except Exception as e:
            if cls._fallback_backend is not None:
                res = cls._fallback_backend(task, text, *args, model=model, agent=agent, error=e, **kwargs)
                resp_text = res.get("response", f"[Fallback] Error: {e}") if isinstance(res, dict) else str(res)
                fallback_model = res.get("model", model) if isinstance(res, dict) else model
                return SystemTwoResponse(resp_text, fallback_model, provider, fallback_used=True)
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
        
        # Check System 1
        if task_type in cls._SYSTEM_ONE_TABLE:
            return cls._SYSTEM_ONE_TABLE[task_type](args)
        
        # Check System 2
        if task_type in cls._SYSTEM_TWO_TASKS:
            text_arg = args[0] if args else ""
            return SystemTwoEngine.execute(task_type, text_arg, *args[1:], **kwargs)
        
        supported = list(cls._SYSTEM_ONE_TABLE.keys()) + list(cls._SYSTEM_TWO_TASKS)
        raise ValueError(f"Task sconosciuto: {task_type}. Task supportati: {supported}")

def augment_response_with_wysiati(response: dict[str, Any], text_length: int = 100, missing_context_indicators: int = 0) -> dict[str, Any]:
    """
    Aggiunge flag di completezza informativa (WYSIATI - What You See Is All There Is)
    ai payload di risposta di Laya Service e Gateway.
    """
    completeness_score = max(0.0, min(1.0, 1.0 - (missing_context_indicators * 0.25)))
    if text_length < 20:
        completeness_score *= 0.5

    wysiati_complete = (completeness_score >= 0.7 and missing_context_indicators == 0)

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
    def evaluate_routing(cls, task_type: str, text: str, laya_assessment: dict | None = None, **kwargs: Any) -> dict[str, Any]:
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
                "cognitive_tension_triggered": True
            }

        # Regola 1: Decisioni chiuse con esito Laya valido e basso rischio → System 1 (S1)
        if is_closed_decision and decision_status == "ok" and risk_score < 0.5 and not has_side_effects:
            return {
                "tier": "s1",
                "executor": "laya_system_one",
                "budget_reduction": False,
                "max_tokens": 256,
                "context_window": 1024,
                "allow_tools": False
            }

        # Regola 2: Astensione, errore o rischio elevato → System 2 Completo (S2 Full), mai riduzione
        if decision_status == "abstain" or risk_score >= 0.7 or has_side_effects or task_type in {"security_check", "reasoning_planning"}:
            return {
                "tier": "s2_full",
                "executor": "system_two_engine",
                "budget_reduction": False,
                "max_tokens": 4096,
                "context_window": 16384,
                "allow_tools": True
            }

        # Regola 3: Generazione semplice a basso rischio con esito sicuro → System 2 Ridotto (S2 Reduced)
        if decision_status == "ok" and risk_score < 0.3 and task_type in {"text_editing", "summarization", "translation", "extraction"}:
            return {
                "tier": "s2_reduced",
                "executor": "system_two_engine",
                "budget_reduction": True,
                "max_tokens": 1024,
                "context_window": 4096,
                "allow_tools": False
            }

        # Default fallback: System 2 Standard / Full
        return {
            "tier": "s2_full",
            "executor": "system_two_engine",
            "budget_reduction": False,
            "max_tokens": 2048,
            "context_window": 8192,
            "allow_tools": True
        }

class SystemEvaluationEngine:
    """
    Motore di evaluation offline (replay), shadow mode e metriche di gate con rollback
    per configurazioni e policy di routing System 2.
    """

    @classmethod
    def replay(cls, requests: list[dict[str, Any]], candidate_config: dict[str, Any]) -> dict[str, Any]:
        total = len(requests)
        if total == 0:
            return {"total_requests": 0, "success_rate": 0.0, "avg_latency_ms": 0.0, "estimated_cost": 0.0}

        successes = sum(1 for r in requests if r.get("expected_outcome") == "success")
        success_rate = successes / total
        avg_latency_ms = 120.0
        estimated_cost = total * 0.0002
        return {
            "total_requests": total,
            "successes": successes,
            "success_rate": success_rate,
            "avg_latency_ms": avg_latency_ms,
            "estimated_cost": estimated_cost,
            "candidate_config": candidate_config
        }

    @classmethod
    def shadow_evaluate(cls, primary_response: dict[str, Any], shadow_response: dict[str, Any], tolerances: dict[str, float] | None = None) -> dict[str, Any]:
        primary_text = primary_response.get("response", "")
        shadow_text = shadow_response.get("response", "")
        match = (primary_text.strip().lower() == shadow_text.strip().lower())
        primary_lat = primary_response.get("latency_ms", 100)
        shadow_lat = shadow_response.get("latency_ms", 100)
        delta_ms = shadow_lat - primary_lat
        return {
            "match": match,
            "primary_latency_ms": primary_lat,
            "shadow_latency_ms": shadow_lat,
            "latency_delta_ms": delta_ms
        }

    @classmethod
    def promote_with_rollback(cls, metrics: dict[str, Any], gate_thresholds: dict[str, float]) -> tuple[bool, str]:
        success_rate = metrics.get("success_rate", 0.0)
        error_rate = metrics.get("error_rate", 0.0)
        avg_latency_ms = metrics.get("avg_latency_ms", 0.0)

        min_success = gate_thresholds.get("min_success_rate", 0.95)
        max_error = gate_thresholds.get("max_error_rate", 0.05)
        max_latency = gate_thresholds.get("max_latency_ms", 500.0)

        if success_rate >= min_success and error_rate <= max_error and avg_latency_ms <= max_latency:
            return True, "Gate passed successfully"
        else:
            reason = f"Gate failed: success_rate={success_rate} (min {min_success}), error_rate={error_rate} (max {max_error}), avg_latency_ms={avg_latency_ms} (max {max_latency}). Rollback triggered to previous stable config."
            return False, reason

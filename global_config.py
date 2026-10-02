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

class SystemTwoEngine:
    """
    Motore System 2 gestito dal modello di interfaccia corrente (es. Gemini 3.5 Flash-Lite)
    con supporto estensibile per futuri motori System 2 e routing condizionato (OrcaRouter).
    """
    ACTIVE_MODEL_NAME: ClassVar[str] = "Gemini 3.5 Flash-Lite"

    @classmethod
    def resolve_model(cls, agent_name: str | None = None) -> str:
        if agent_name:
            return resolve_agent_model(agent_name)
        return cls.ACTIVE_MODEL_NAME

    @classmethod
    def execute(cls, task: str, text: str, *args: Any, agent: str | None = None, **kwargs: Any) -> Any:
        model = cls.resolve_model(agent)
        return f"[{model} - System 2: {task}] Processed: {text}"

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

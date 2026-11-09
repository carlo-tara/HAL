"""Chiamate provider del benchmark: discovery, header, parse response, token, traduzione locale (T2-09, rv7 N28).

Spostamento meccanico di codice da `app/benchmark_models.py` (nessun
riscrittura).
"""

from __future__ import annotations

from typing import Any, NamedTuple

import httpx

from . import benchmark_parsing as parsing
from .benchmark_parsing import prompt_message
from .benchmark_settings import CHARS_PER_A4_PAGE, ROOT, Settings, utc_now
from .benchmark_workflow import system1_prompt
from .translation import TranslationResult, TranslationSettings, translate_text


def openai_compatible_google(config: Settings) -> bool:
    return config.llm_provider in {
        "openai",
        "openai_compat",
        "openai_compatible",
        "openai-compatible",
        "openai_compa",
    }


def headers_for(
    provider: str, config: Settings, *, native_google: bool = False
) -> dict:
    if provider == "google":
        if not config.google_api_key:
            raise ValueError(
                "Configurare LLM_API_KEY, GOOGLE_API_KEY oppure GEMINI_API_KEY"
            )
        if openai_compatible_google(config) and not native_google:
            return {"Authorization": f"Bearer {config.google_api_key}"}
        return {"x-goog-api-key": config.google_api_key}
    return (
        {"Authorization": f"Bearer {config.ollama_api_key}"}
        if config.ollama_api_key
        else {}
    )


def discover_models(
    config: Settings, *, client: httpx.Client, providers=("ollama", "google")
) -> dict:
    models = []
    excluded = []
    for provider in providers:
        headers = (
            headers_for(provider, config, native_google=True)
            if provider == "google"
            else headers_for(provider, config)
        )
        if provider == "ollama":
            response = client.get(f"{config.ollama_base_url}/api/tags", headers=headers)
            response.raise_for_status()
            for model in response.json()["models"]:
                capabilities = model.get("capabilities")
                if capabilities is None:
                    details = client.post(
                        f"{config.ollama_base_url}/api/show",
                        headers=headers,
                        json={"model": model["name"]},
                    )
                    details.raise_for_status()
                    capabilities = details.json().get("capabilities")
                if capabilities is not None and "completion" not in capabilities:
                    excluded.append({"provider": provider, "model": model["name"]})
                    continue
                models.append({"provider": provider, "model": model["name"]})
        else:
            token = None
            seen_pages = set()
            while True:
                params = {"pageSize": 1000}
                if token:
                    params["pageToken"] = token
                response = client.get(
                    f"{config.google_base_url}/models", headers=headers, params=params
                )
                response.raise_for_status()
                page = response.json()
                for model in page.get("models", []):
                    name = model["name"].removeprefix("models/")
                    # Audio/image-only endpoints cannot run the same five text tests.
                    if "generateContent" not in model.get(
                        "supportedGenerationMethods", []
                    ) or any(
                        marker in name.lower()
                        for marker in ("-tts", "-image", "-audio", "nano-banana")
                    ):
                        excluded.append({"provider": provider, "model": name})
                        continue
                    models.append({"provider": provider, "model": name})
                token = page.get("nextPageToken")
                if not token:
                    break
                if token in seen_pages:
                    raise ValueError(
                        "Il catalogo Google ripete il token di paginazione"
                    )
                seen_pages.add(token)
    # Preserve order and avoid aliases repeated across catalog pages.
    models = list({(m["provider"], m["model"]): m for m in models}.values())
    if not models:
        raise ValueError("Nessun modello testuale disponibile")
    return {
        "generated_at": utc_now(),
        "source": "live_provider_apis",
        "models": models,
        "excluded": excluded,
    }


def token_count(usage: dict, field: str) -> int | None:
    value = usage.get(field)
    return value if type(value) is int and value >= 0 else None


def parse_response(provider: str, data: dict) -> dict:
    if not isinstance(data, dict) or "error" in data:
        raise ValueError("Risposta provider non valida")
    if provider == "ollama":
        message = data.get("message", {})
        if not isinstance(message, dict) or not data.get("done"):
            raise ValueError("Risposta Ollama incompleta")
        input_tokens = token_count(data, "prompt_eval_count")
        output_tokens = token_count(data, "eval_count")
        tokens = {
            "input": input_tokens,
            "output": output_tokens,
            "reasoning": None,
            "cached": None,
            "cache_creation": None,
            "total": input_tokens + output_tokens
            if input_tokens is not None and output_tokens is not None
            else None,
        }
        text = message.get("content", "")
        finish = data.get("done_reason")
        status = (
            "truncated" if finish == "length" else "ok" if text else "empty_response"
        )
    elif provider == "google_openai":
        usage = data.get("usage") or {}
        details = usage.get("completion_tokens_details") or {}
        prompt_details = usage.get("prompt_tokens_details") or {}
        # Campi cache uniformi su tutti i path provider cache-abilitati (doc
        # QwenCloud 2026-10-28): prompt_tokens_details.cached_tokens + il campo
        # piatto Anthropic-style cache_creation_input_tokens
        cached = token_count(prompt_details, "cached_tokens")
        if cached is None:
            cached = token_count(usage, "cached_tokens")
        tokens = {
            "input": token_count(usage, "prompt_tokens"),
            "output": token_count(usage, "completion_tokens"),
            "reasoning": token_count(details, "reasoning_tokens"),
            "cached": cached,
            "cache_creation": token_count(usage, "cache_creation_input_tokens"),
            "total": token_count(usage, "total_tokens"),
        }
        choices = data.get("choices") or []
        candidate = choices[0] if choices else {}
        finish = candidate.get("finish_reason")
        message = candidate.get("message") or {}
        content = message.get("content", "")
        text = (
            content
            if isinstance(content, str)
            else "".join(
                part.get("text", "") for part in content if isinstance(part, dict)
            )
            if isinstance(content, list)
            else ""
        )
        status = (
            "truncated" if finish == "length" else "ok" if text else "empty_response"
        )
    else:
        usage = data.get("usageMetadata") or {}
        tokens = {
            "input": token_count(usage, "promptTokenCount"),
            "output": token_count(usage, "candidatesTokenCount"),
            "reasoning": token_count(usage, "thoughtsTokenCount"),
            "cached": token_count(usage, "cachedContentTokenCount"),
            "cache_creation": None,
            "total": token_count(usage, "totalTokenCount"),
        }
        candidates = data.get("candidates") or []
        candidate = candidates[0] if candidates else {}
        finish = candidate.get("finishReason") or (
            data.get("promptFeedback") or {}
        ).get("blockReason")
        text = "".join(
            part.get("text", "")
            for part in (candidate.get("content") or {}).get("parts", [])
            if not part.get("thought")
        )
        status = (
            "truncated"
            if finish == "MAX_TOKENS"
            else "blocked"
            if finish not in (None, "STOP")
            else "ok"
            if text
            else "empty_response"
        )
    return {
        "status": status,
        "tokens": tokens,
        "finish_reason": finish,
        "response": text,
    }


def benchmark_call(
    model: dict,
    prompt: dict,
    config: Settings,
    client: httpx.Client,
    *,
    system1: dict | None = None,
    system_message: str | None = None,
    max_output_tokens: int | None = None,
) -> dict:
    provider = model["provider"]
    headers = headers_for(provider, config)
    if system_message is not None:
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt.get("prompt", "")},
        ]
    elif system1 is not None:
        messages = [{"role": "user", "content": system1_prompt(prompt, system1)}]
    else:
        messages = [{"role": "user", "content": prompt_message(prompt)}]
    payload: dict[str, Any]
    if provider == "ollama":
        url = f"{config.ollama_base_url}/api/chat"
        payload = {
            "model": model["model"],
            "messages": messages,
            "stream": False,
            # Unload the runner after generation instead of retaining its KV cache.
            "keep_alive": 0,
            "options": {
                "num_predict": -1 if max_output_tokens is None else max_output_tokens,
                "num_ctx": config.ollama_num_ctx,
            },
        }
    elif openai_compatible_google(config):
        url = f"{config.llm_base_url}/chat/completions"
        payload = {
            "model": config.llm_model or model["model"],
            "messages": messages,
        }
        if config.llm_temperature is not None:
            payload["temperature"] = config.llm_temperature
        if max_output_tokens is not None:
            payload["max_tokens"] = max_output_tokens
        provider = "google_openai"
    else:
        url = f"{config.google_base_url}/models/{model['model']}:generateContent"
        if len(messages) > 1 and messages[0].get("role") == "system":
            sys_msg = messages[0]["content"]
            user_msg = messages[1]["content"]
            payload = {
                "contents": [{"role": "user", "parts": [{"text": user_msg}]}],
                "systemInstruction": {"role": "user", "parts": [{"text": sys_msg}]},
            }
        else:
            contents = [
                {"role": m["role"], "parts": [{"text": m["content"]}]} for m in messages
            ]
            payload = {"contents": contents}
        if max_output_tokens is not None:
            payload["generationConfig"] = {"maxOutputTokens": max_output_tokens}
    response = client.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return parse_response(provider, response.json())


class LocalTranslation(NamedTuple):
    """Esito della traduzione locale con il testo sorgente effettivamente usato.

    Il sorgente accompagna il risultato perche la registrazione metriche dello
    stadio in run_benchmark conta input_chars senza rileggere la fonte.
    """

    result: TranslationResult
    source: str


def local_translation(
    prompt: dict, config: Settings, client: httpx.Client
) -> LocalTranslation | None:
    """Traduce localmente la fonte quando il prompt chiede una traduzione.

    Restituisce None se la catena e disattivata, il prompt non e una traduzione
    o nessun backend locale e disponibile: in questi casi si usa l-LLM.
    """
    if not config.translation_enabled or "source" not in prompt:
        return None
    arguments = prompt.get("arguments", {})
    target_language = arguments.get("lingua_destinazione")
    if not target_language:
        return None
    source = parsing.epub_text(ROOT / prompt["source"])
    if "numero_pagine" in arguments:
        source = source[: arguments["numero_pagine"] * CHARS_PER_A4_PAGE]
    settings = TranslationSettings(
        argos_enabled=config.translation_argos_enabled,
        libretranslate_enabled=config.translation_libretranslate_enabled,
        libretranslate_url=config.libretranslate_url,
        libretranslate_api_key=config.libretranslate_api_key,
        timeout=config.translation_timeout,
        max_chars_per_request=config.translation_max_chars,
    )
    source_language = arguments.get(
        "lingua_sorgente", config.translation_source_language
    )
    result = translate_text(
        source,
        target_language,
        source_language=source_language,
        settings=settings,
        client=client,
    )
    if result is None:
        return None
    return LocalTranslation(result=result, source=source)


def translation_result(result: TranslationResult) -> dict:
    """Risultato di benchmark con 0 token e traccia della traduzione locale."""
    zero = {"input": 0, "output": 0, "reasoning": 0, "total": 0}
    return {
        "status": "ok" if result.text.strip() else "empty_response",
        "tokens": dict(zero),
        "finish_reason": f"translation_{result.backend}",
        "response": result.text,
        "workflow": [
            {
                "system": "translation",
                "stage": f"traduzione_{result.backend}",
                "backend": result.backend,
                "source_language": result.source_language,
                "target_language": result.target_language,
                "status": "ok",
                "tokens": dict(zero),
            }
        ],
        "workflow_summary": {
            "system1_decisions": 0,
            "system2_stages": 0,
            "execution_mode": "single_pass",
            "translation_backend": result.backend,
        },
    }

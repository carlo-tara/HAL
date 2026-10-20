"""Sequential Ollama/Google text benchmark with provider-reported token usage."""

from __future__ import annotations

import argparse
import json
import math
import os
import posixpath
import re
import sqlite3
import sys
import tempfile
import time
import uuid
import zipfile
from collections.abc import Callable
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from functools import lru_cache
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, ClassVar
from xml.etree import ElementTree as ET

import httpx
from dotenv import dotenv_values

from .system2_metrics import DEFAULT_METRICS_DB, System2Metrics

ROOT = Path(__file__).resolve().parent.parent
# Media indicativa di caratteri per pagina A4 a interlinea singola, spazi inclusi.
CHARS_PER_A4_PAGE = 3000


@dataclass(frozen=True)
class Settings:
    ollama_base_url: str = "http://127.0.0.1:11434"
    ollama_api_key: str = ""
    ollama_num_ctx: int = 4096
    google_base_url: str = "https://generativelanguage.googleapis.com/v1beta"
    google_api_key: str = ""
    llm_provider: str = ""
    llm_base_url: str = "https://generativelanguage.googleapis.com/v1beta/openai"
    llm_model: str = ""
    llm_temperature: float | None = None
    timeout: float = 600
    laya_base_url: str = "http://127.0.0.1:8091"
    laya_api_key: str = "sk-local"
    laya_timeout: float = 120
    laya_min_confidence: float = 0.7
    laya_model: str = "multilingual"

    @classmethod
    def from_env(cls, env_file: Path) -> Settings:
        file_env = {
            key: value
            for key, value in dotenv_values(env_file).items()
            if value is not None
        }
        env = {**file_env, **os.environ}
        environment_google_key = (
            os.environ.get("LLM_API_KEY")
            or os.environ.get("GOOGLE_API_KEY")
            or os.environ.get("GEMINI_API_KEY")
            or file_env.get("LLM_API_KEY")
            or file_env.get("GOOGLE_API_KEY")
            or file_env.get("GEMINI_API_KEY")
        )
        ollama_url = env.get("OLLAMA_BASE_URL", cls.ollama_base_url).rstrip("/")
        ollama_url = ollama_url.removesuffix("/v1")
        return cls(
            ollama_base_url=ollama_url,
            ollama_api_key=env.get("OLLAMA_API_KEY", ""),
            ollama_num_ctx=int(env.get("OLLAMA_NUM_CTX", "4096")),
            google_base_url=env.get("GOOGLE_BASE_URL", cls.google_base_url).rstrip("/"),
            google_api_key=environment_google_key or "",
            llm_provider=env.get("LLM_PROVIDER", "").strip().lower(),
            llm_base_url=env.get(
                "LLM_BASE_URL",
                "https://generativelanguage.googleapis.com/v1beta/openai",
            ).rstrip("/"),
            llm_model=env.get("LLM_MODEL", "").strip(),
            llm_temperature=(
                float(env["LLM_TEMPERATURE"]) if env.get("LLM_TEMPERATURE") else None
            ),
            timeout=float(env.get("BENCHMARK_TIMEOUT_SECONDS", "600")),
            laya_base_url=env.get(
                "LAYA_URL", env.get("LAYA_BASE_URL", "http://127.0.0.1:8091")
            )
            .rstrip("/")
            .removesuffix("/v1"),
            laya_api_key=env.get("LAYA_API_KEY", "sk-local"),
            laya_timeout=float(env.get("LAYA_TIMEOUT", "120")),
            laya_min_confidence=float(env.get("LAYA_MIN_CONFIDENCE", "0.7")),
            laya_model=env.get("LAYA_MODEL", "multilingual"),
        )


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    # Keep a complete, parseable checkpoint even if the process is interrupted.
    name = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=path.parent, delete=False
        ) as handle:
            name = handle.name
            json.dump(value, handle, ensure_ascii=False, indent=2, allow_nan=False)
            handle.write("\n")
        os.replace(name, path)
    finally:
        if name and os.path.exists(name):
            os.unlink(name)


class _HtmlText(HTMLParser):
    BLOCK_TAGS: ClassVar[set[str]] = {
        "p",
        "div",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "li",
        "br",
        "tr",
    }

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.skip = 0

    def handle_starttag(self, tag: str, attrs: list) -> None:
        if tag in {"script", "style"}:
            self.skip += 1
        elif tag in self.BLOCK_TAGS:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style"} and self.skip:
            self.skip -= 1

    def handle_data(self, data: str) -> None:
        if not self.skip:
            self.parts.append(data)


@lru_cache(maxsize=4)
def epub_text(path: Path) -> str:
    """Testo dei capitoli di un EPUB, nell'ordine di lettura (spine)."""
    opf_ns = "{http://www.idpf.org/2007/opf}"
    with zipfile.ZipFile(path) as book:
        container = ET.fromstring(book.read("META-INF/container.xml"))
        rootfile = container.find(
            ".//{urn:oasis:names:tc:opendocument:xmlns:container}rootfile"
        )
        if rootfile is None or not rootfile.get("full-path"):
            raise ValueError("EPUB senza rootfile OPF")
        opf_path = rootfile.get("full-path")
        if not opf_path:
            raise ValueError("EPUB senza rootfile OPF")
        opf = ET.fromstring(book.read(opf_path))
        base = posixpath.dirname(opf_path)
        manifest = {
            item.get("id"): item.get("href") for item in opf.iter(f"{opf_ns}item")
        }
        chapters = []
        for ref in opf.iter(f"{opf_ns}itemref"):
            href = manifest.get(ref.get("idref"))
            if not href:
                continue
            parser = _HtmlText()
            parser.feed(book.read(posixpath.join(base, href)).decode("utf-8", "ignore"))
            chapters.append("".join(parser.parts))
    text = "\n".join(chapters)
    text = re.sub(r"[ \t\u00a0]+", " ", text)
    return re.sub(r"\n\s*\n+", "\n\n", text).strip()


def prompt_message(prompt: dict) -> str:
    """Messaggio utente: l'eventuale fonte precede le istruzioni, così il troncamento
    lato server (es. num_ctx di Ollama) tocca il testo del libro, non le istruzioni."""
    arguments = prompt.get("arguments", {})
    instructions = prompt["prompt"]
    if "lingua_destinazione" in arguments:
        language = arguments["lingua_destinazione"]
        instructions = f"Lingua di destinazione: {language}.\n{instructions}"
    if "source" not in prompt:
        return instructions
    book = epub_text(ROOT / prompt["source"])
    if "numero_pagine" in arguments:
        book = book[: arguments["numero_pagine"] * CHARS_PER_A4_PAGE]
    return f"<libro>\n{book}\n</libro>\n\n{instructions}"


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
        "Estrai i requisiti espliciti, produci un artefatto completo e controlla vincoli e casi limite."
    ),
    "grounded_extract": (
        "Usa solo la fonte fornita, rispetta esattamente formato e intervallo richiesti, "
        "non inventare dettagli."
    ),
    "faithful_translate": (
        "Traduci solo il testo richiesto, preservando significato, completezza e ordine; "
        "non aggiungere sintesi."
    ),
    "direct_answer": "Rispondi direttamente alla richiesta e verifica che ogni vincolo esplicito sia rispettato.",
}


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
    if has_source and source_chars > CHARS_PER_A4_PAGE:
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


def system1_guide(prompt: dict, config: Settings, client: httpx.Client) -> dict:
    """Gate and align Laya's routing against a local, task-specific contract."""
    source = ""
    if "source" in prompt:
        source = epub_text(ROOT / prompt["source"])
        arguments = prompt.get("arguments", {})
        if "numero_pagine" in arguments:
            source = source[: arguments["numero_pagine"] * CHARS_PER_A4_PAGE]
    analysis = analyze_prompt(prompt, source_chars=len(source))
    expected_family = analysis["task_family"]
    required_strategy = analysis["task_contract"]["required_strategy"]
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
        }

    context = prompt["prompt"]
    if source:
        context += f"\nFonte {prompt['source']} (estratto iniziale):\n{source[:1200]}"
    payload = {
        "state": {
            "notes": context,
            "language": "italian",
            "task_contract": analysis["task_contract"],
        },
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
                f"Output System 2 da valutare:\n{artifact[:12000]}"
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


def load_inputs(models_path: Path, prompts_path: Path) -> tuple[list[dict], list[dict]]:
    with models_path.open(encoding="utf-8") as handle:
        catalog = json.load(handle)
    with prompts_path.open(encoding="utf-8") as handle:
        suite = json.load(handle)
    models = catalog.get("models") if isinstance(catalog, dict) else None
    prompts = suite.get("prompts") if isinstance(suite, dict) else None
    if not isinstance(models, list) or not models:
        raise ValueError("models deve contenere un elenco non vuoto")
    seen = set()
    clean_models = []
    for model in models:
        if not isinstance(model, dict) or model.get("provider") not in {
            "ollama",
            "google",
        }:
            raise ValueError("Ogni modello richiede provider ollama o google")
        name = model.get("model")
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Identificativo modello vuoto o non valido")
        if model["provider"] == "google":
            name = name.removeprefix("models/")
            if not re.fullmatch(r"[A-Za-z0-9._-]+", name):
                raise ValueError("Identificativo modello Google non valido")
        key = (model["provider"], name)
        if key in seen:
            raise ValueError("Modello duplicato")
        seen.add(key)
        # Deliberately do not forward arbitrary configuration, including token caps.
        clean_models.append({"provider": key[0], "model": name})
    if not isinstance(prompts, list) or len(prompts) != 5:
        raise ValueError("prompts deve contenere esattamente 5 test")
    seen = set()
    for prompt in prompts:
        if not isinstance(prompt, dict) or any(
            not isinstance(prompt.get(field), str) or not prompt[field].strip()
            for field in ("id", "prompt")
        ):
            raise ValueError("Ogni test richiede id e prompt non vuoti")
        if "source" in prompt and (
            not isinstance(prompt["source"], str) or not prompt["source"].strip()
        ):
            raise ValueError("source deve essere un percorso non vuoto")
        arguments = prompt.get("arguments", {})
        if not isinstance(arguments, dict):
            raise TypeError("arguments deve essere un oggetto")
        if "numero_pagine" in arguments and (
            "source" not in prompt
            or isinstance(arguments["numero_pagine"], bool)
            or not isinstance(arguments["numero_pagine"], int)
            or arguments["numero_pagine"] < 1
        ):
            raise ValueError("numero_pagine richiede source e un intero positivo")
        if "lingua_destinazione" in arguments and (
            not isinstance(arguments["lingua_destinazione"], str)
            or not arguments["lingua_destinazione"].strip()
        ):
            raise ValueError("lingua_destinazione deve essere un testo non vuoto")
        if "quality" in prompt:
            validate_quality(prompt["quality"])
        if prompt["id"] in seen:
            raise ValueError("Gli id dei test devono essere univoci")
        seen.add(prompt["id"])
    return clean_models, prompts


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
        tokens = {
            "input": token_count(usage, "prompt_tokens"),
            "output": token_count(usage, "completion_tokens"),
            "reasoning": token_count(details, "reasoning_tokens"),
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
) -> dict:
    provider = model["provider"]
    headers = headers_for(provider, config)
    message = system1_prompt(prompt, system1) if system1 else prompt_message(prompt)
    if provider == "ollama":
        url = f"{config.ollama_base_url}/api/chat"
        payload = {
            "model": model["model"],
            "messages": [{"role": "user", "content": message}],
            "stream": False,
            # Unload the runner after generation instead of retaining its KV cache.
            "keep_alive": 0,
            "options": {"num_predict": -1, "num_ctx": config.ollama_num_ctx},
        }
    elif openai_compatible_google(config):
        url = f"{config.llm_base_url}/chat/completions"
        payload = {
            "model": config.llm_model or model["model"],
            "messages": [{"role": "user", "content": message}],
        }
        if config.llm_temperature is not None:
            payload["temperature"] = config.llm_temperature
        provider = "google_openai"
    else:
        url = f"{config.google_base_url}/models/{model['model']}:generateContent"
        payload = {"contents": [{"role": "user", "parts": [{"text": message}]}]}
    response = client.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return parse_response(provider, response.json())


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

    def run_stage(stage_prompt: dict, stage: str) -> dict:
        started = time.perf_counter()
        try:
            result = benchmark_call(model, stage_prompt, config, client, system1=guide)
        except Exception:
            record_metric(
                system="system2",
                stage=stage,
                status="error",
                latency_ms=round((time.perf_counter() - started) * 1000),
                input_chars=len(stage_prompt.get("prompt", "")),
            )
            raise
        tokens = result.get("tokens", {})
        trace.append(
            {
                "system": "system2",
                "stage": stage,
                "status": result.get("status"),
                "tokens": tokens,
            }
        )
        record_metric(
            system="system2",
            stage=stage,
            status=result.get("status", "error"),
            latency_ms=round((time.perf_counter() - started) * 1000),
            input_chars=len(stage_prompt.get("prompt", "")),
            output_chars=len(result.get("response", "")),
            tokens_in=tokens.get("input"),
            tokens_out=tokens.get("output"),
            tokens_total=tokens.get("total"),
        )
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
        source = epub_text(ROOT / prompt["source"])
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
        artifacts: list[str] = []
        for index, chunk in enumerate(chunks, start=1):
            # Preserve every in-scope source segment: a generic relevance classifier
            # must not silently drop content needed for extraction or translation.
            part_prompt = user_prompt(
                f"{instructions}\n\nElabora soltanto il segmento {index}/{len(chunks)}. "
                "Non completare il lavoro sugli altri segmenti e non dichiarare che questa è la risposta complessiva. "
                f"Mantieni informazioni utili all'assemblaggio finale.\n\n<segmento_fonte>\n{chunk}\n</segmento_fonte>"
            )
            part = run_stage(part_prompt, f"segmento_{index}")
            if part.get("response"):
                artifacts.append(part["response"])
        assembled = "\n\n---\n\n".join(
            f"<risultato_segmento_{index}>\n{artifact}\n</risultato_segmento_{index}>"
            for index, artifact in enumerate(artifacts, start=1)
        )
        final_prompt = user_prompt(
            f"{instructions}\n\nAssembla i risultati parziali seguenti in un'unica risposta completa. "
            "Rimuovi duplicazioni introdotte dai confini dei segmenti, preserva l'ordine e rispetta esattamente il formato richiesto. "
            f"Non aggiungere fatti non presenti nei risultati.\n\n<risultati_parziali>\n{assembled}\n</risultati_parziali>"
        )
        final = run_stage(final_prompt, "assemblaggio_finale")
    else:
        plan = None
        if mode == "plan_then_solve":
            plan_prompt = user_prompt(
                "Scomponi la richiesta seguente in requisiti verificabili e passaggi ordinati. "
                "Non dare ancora la risposta finale né generare l'artefatto.\n\n"
                f"{prompt['prompt']}"
            )
            plan = run_stage(plan_prompt, "piano_iniziale")
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
                plan = run_stage(plan_prompt, "piano_revisionato")
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
        final = run_stage(user_prompt(final_text), "risposta_finale")

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


def safe_path_component(value: str) -> str:
    component = re.sub(r"[^A-Za-z0-9._-]+", "_", value).strip("._-")
    return component or "model"


def extract_html_document(text: str) -> str | None:
    fenced = re.search(r"```html\s*(.*?)```", text, re.DOTALL | re.IGNORECASE)
    if fenced:
        return fenced.group(1).strip() + "\n"
    document = re.search(r"<!DOCTYPE html>.*</html>", text, re.DOTALL | re.IGNORECASE)
    return document.group(0) + "\n" if document else None


QUALITY_TYPES = frozenset({"contains_any", "absent", "json", "html", "min_chars"})


def validate_quality(checks: object) -> None:
    if not isinstance(checks, list) or not checks:
        raise ValueError("quality deve essere un elenco non vuoto di controlli")
    for check in checks:
        if not isinstance(check, dict) or check.get("type") not in QUALITY_TYPES:
            raise ValueError("Tipo di controllo di qualità sconosciuto")
        if "label" in check and (
            not isinstance(check["label"], str) or not check["label"].strip()
        ):
            raise ValueError("label deve essere un testo non vuoto")
        if check["type"] in {"contains_any", "absent"} and (
            not isinstance(check.get("values"), list)
            or not check["values"]
            or any(not isinstance(v, str) or not v.strip() for v in check["values"])
        ):
            raise ValueError("values deve essere un elenco di testi non vuoti")
        if check["type"] == "min_chars" and (
            isinstance(check.get("value"), bool)
            or not isinstance(check.get("value"), int)
            or check["value"] < 1
        ):
            raise ValueError("min_chars richiede value intero positivo")


def json_document(text: str) -> bool:
    fenced = re.search(r"```(?:json)?(.*?)```", text, re.DOTALL | re.IGNORECASE)
    candidate = fenced.group(1) if fenced else text
    starts = [i for i in (candidate.find("["), candidate.find("{")) if i >= 0]
    if not starts:
        return False
    try:
        json.JSONDecoder().raw_decode(candidate, min(starts))
    except ValueError:
        return False
    return True


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
) -> dict:
    models = apply_llm_model_override(models, config)
    log(
        f"Benchmark: {len(models)} modelli × {len(prompts)} test "
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
    metrics = (
        System2Metrics(metrics_db)
        if system1_guides is not None and metrics_db is not None
        else None
    )
    run_id = uuid.uuid4().hex
    if system1_guides:
        report["system1"] = {
            prompt_id: guide for prompt_id, guide in system1_guides.items()
        }
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
            log(
                f"  → test {test_index}/{len(prompts)} {prompt['id']}: "
                f"invio richiesta ({len(prompt_message(prompt)):,} caratteri)…"
            )
            start = clock()
            try:
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
        raise ValueError("Test sconosciuto nei filtri --prompt")
    return [prompt for prompt in prompts if prompt["id"] in ids]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--models", type=Path, default=ROOT / "config/benchmark-models.json"
    )
    parser.add_argument(
        "--prompts", type=Path, default=ROOT / "config/benchmark-prompts.json"
    )
    parser.add_argument(
        "--output", type=Path, default=ROOT / "events/benchmarks/results.json"
    )
    parser.add_argument(
        "--run-dir",
        type=Path,
        help="Cartella dedicata a tutti i risultati dei modelli della run; deve non esistere",
    )
    parser.add_argument(
        "--system1",
        action="store_true",
        help="Usa il gate task-aware Laya/System 2 e registra le metriche SQLite",
    )
    parser.add_argument(
        "--metrics-db",
        type=Path,
        default=Path(os.getenv("SYSTEM2_METRICS_DB_PATH", DEFAULT_METRICS_DB)),
        help="File SQLite per telemetria System 1/System 2 (default: events/benchmarks/system2_metrics.sqlite3)",
    )
    parser.add_argument("--env-file", type=Path, default=ROOT / ".env")
    parser.add_argument(
        "--provider",
        choices=("ollama", "google"),
        help="Esegue solo i modelli del provider indicato",
    )
    parser.add_argument(
        "--model",
        action="append",
        dest="model_names",
        help="Esegue solo il modello indicato (ripetibile)",
    )
    parser.add_argument(
        "--prompt",
        action="append",
        dest="prompt_ids",
        help="Esegue solo il test indicato per id (ripetibile)",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        help="Timeout HTTP per operazione in secondi (default: 600)",
    )
    parser.add_argument(
        "--refresh-models",
        action="store_true",
        help="Aggiorna solo il catalogo, senza generazione",
    )
    parser.add_argument(
        "--providers",
        nargs="+",
        choices=("ollama", "google"),
        default=["ollama", "google"],
        help="Provider da interrogare durante --refresh-models",
    )
    args = parser.parse_args(argv)
    try:
        config = Settings.from_env(args.env_file)
        timeout = config.timeout if args.timeout is None else args.timeout
        if not math.isfinite(timeout) or timeout <= 0:
            raise ValueError("Il timeout deve essere un numero positivo finito")
        config = replace(config, timeout=timeout)
        if args.system1 and (
            not math.isfinite(config.laya_timeout)
            or config.laya_timeout <= 0
            or not math.isfinite(config.laya_min_confidence)
            or not 0 <= config.laya_min_confidence <= 1
        ):
            raise ValueError("Configurazione timeout/confidenza Laya non valida")
        if args.refresh_models:
            if args.models.resolve() in {
                args.env_file.resolve(),
                args.prompts.resolve(),
            }:
                raise ValueError("Il catalogo non può sovrascrivere prompt o .env")
            with httpx.Client(timeout=timeout) as client:
                catalog = discover_models(
                    config, client=client, providers=args.providers
                )
            write_json(args.models, catalog)
            print(
                f"Catalogo aggiornato: {len(catalog['models'])} modelli in {args.models}"
            )
            return 0
        if args.output.resolve() in {
            args.models.resolve(),
            args.prompts.resolve(),
            args.env_file.resolve(),
        }:
            raise ValueError("L'output non può sovrascrivere input o .env")
        models, prompts = load_inputs(args.models, args.prompts)
        prompts = filter_prompts(prompts, args.prompt_ids)
        for prompt in prompts:
            if "source" in prompt:
                log(
                    f"Fonte per {prompt['id']}: {prompt['source']} "
                    f"({len(epub_text(ROOT / prompt['source'])):,} caratteri)"
                )
        models = filter_models(
            apply_llm_model_override(models, config), args.provider, args.model_names
        )
        if args.run_dir is not None:
            if args.run_dir.exists():
                raise ValueError(f"La cartella di run esiste già: {args.run_dir}")
            if args.output.resolve().parent != args.run_dir.resolve():
                raise ValueError("--output deve essere direttamente dentro --run-dir")
        with httpx.Client(timeout=timeout) as client:
            guides = None
            if args.system1:
                log(
                    f"System 1 Laya: preflight su {len(prompts)} prompt "
                    f"({config.laya_base_url}, modello {config.laya_model})"
                )
                guides = {}
                for prompt in prompts:
                    log(f"  → classificazione Laya: {prompt['id']}")
                    guides[prompt["id"]] = system1_guide(prompt, config, client)
            report = run_benchmark(
                models,
                prompts,
                config,
                args.output,
                client=client,
                run_dir=args.run_dir,
                system1_guides=guides,
                metrics_db=args.metrics_db if args.system1 else None,
            )
        print(
            f"Risultati: {args.output}; successi: {report['summary']['successful']}; errori: {report['summary']['failed']}"
        )
        return 1 if report["summary"]["failed"] else 0
    except httpx.HTTPStatusError as exc:
        print(
            f"Errore HTTP {exc.response.status_code} durante discovery o System 1 Laya",
            file=sys.stderr,
        )
    except httpx.RequestError:
        print(
            "Errore di rete/timeout durante discovery o inferenza System 1 Laya",
            file=sys.stderr,
        )
    except FileNotFoundError as exc:
        print(f"File non trovato: {exc.filename}", file=sys.stderr)
        return 2
    except (OSError, ValueError, KeyError, TypeError):
        print(
            "Configurazione/input non validi o file non accessibile: verificare JSON, percorsi, chiave Google e timeout",
            file=sys.stderr,
        )
    except KeyboardInterrupt:
        print(
            "Interrotto: i risultati già completati restano nel checkpoint JSON",
            file=sys.stderr,
        )
        return 130
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

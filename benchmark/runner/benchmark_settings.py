"""Settings e utilità di configurazione/output del benchmark (T2-09, rv7 N28).

Spostamento meccanico di codice da `app/benchmark_models.py` (nessun
riscrittura).
"""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from dotenv import dotenv_values

ROOT = Path(__file__).resolve().parent.parent

# Media indicativa di caratteri per pagina A4 a interlinea singola, spazi inclusi.
CHARS_PER_A4_PAGE = 3000

# Tetti massimi per i payload System 1 / System 2. Mantenuti centralizzati
# affinché ogni chiamata passi attraverso la stessa logica di troncamento.
MAX_ARTIFACT_SNAPSHOT = 1200  # caratteri max nell'artifact passato a Laya (decision)

MAX_PROMPT_EXCERPT = 1200  # caratteri max per estratto fonte nei prompt

# Tetti di output (guardrail) per tipo di stage, attivi per default per evitare
# generazioni fuori misura sui modelli cloud. I valori stanno sopra il massimo
# osservato nei benchmark reali (segmenti ≤ ~1,2k token su estrazione JSON,
# assemblaggio ≤ ~2,7k, risposta finale ≤ ~2,3k), quindi non troncano gli output
# normali e limitano solo la coda. None = nessun tetto per quello stage.
DEFAULT_OUTPUT_CAPS: dict[str, int | None] = {
    "segment": 2048,
    "assembly": 3072,
    "final": 2048,
    "plan": 1024,
}

# Famiglie con artefatti intrinsecamente lunghi (codice) alzano il tetto finale.
FINAL_OUTPUT_CAP_BY_FAMILY: dict[str, int] = {"coding": 4096}

# Stima conservativa per i contratti di lunghezza in caratteri (lingue romanze:
# ~3 caratteri/token): vincola il pavimento del tetto `final`.
CONTRACT_CHARS_PER_TOKEN = 3

def resolve_output_cap(
    stage: str,
    task_family: str = "general",
    explicit: int | None = None,
    min_chars: int = 0,
) -> int | None:
    """Tetto di token in uscita per uno stage del workflow System 2.

    Precedenza: override esplicito (env/CLI) > default per famiglia (solo `final`)
    > default per stage (`DEFAULT_OUTPUT_CAPS`). Un override non positivo disattiva
    il tetto e lascia la generazione illimitata (None). Se il contratto del prompt
    impone un minimo in caratteri (`quality` `min_chars`), il solo default di
    `final` è sollevato fino a coprirlo: il guardrail non deve troncare una
    risposta legittima. L'override esplicito resta volontà dell'operatore e
    prevale sul pavimento contrattuale.
    """
    if explicit is not None:
        return explicit if explicit > 0 else None
    if stage == "final":
        base = FINAL_OUTPUT_CAP_BY_FAMILY.get(
            task_family, DEFAULT_OUTPUT_CAPS.get(stage)
        )
        floor = -(-min_chars // CONTRACT_CHARS_PER_TOKEN) if min_chars > 0 else 0
        if base is None:
            return floor or None
        return max(base, floor)
    return DEFAULT_OUTPUT_CAPS.get(stage)

def _env_flag(env: dict[str, str], name: str, default: bool) -> bool:
    """Legge un flag booleano da env: 1/true/yes/on."""
    value = env.get(name)
    if value is None:
        return default
    return value.strip().lower() in ("1", "true", "yes", "on")

@dataclass(frozen=True)
class Settings:
    ollama_base_url: str = "http://ollama.local:11434"
    ollama_api_key: str = ""
    ollama_num_ctx: int = 32768
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
    laya_excerpt_max_chars: int = 1200
    # Tetto di token in uscita per segmento; None usa il default (resolve_output_cap).
    segment_max_output_tokens: int | None = None
    # Traduzione a livelli (Argos -> LibreTranslate -> LLM): attiva di default,
    # ogni backend locale e disattivabile. Senza backend la catena ricade sull-LLM.
    translation_enabled: bool = True
    translation_argos_enabled: bool = True
    translation_libretranslate_enabled: bool = True
    libretranslate_url: str = "http://127.0.0.1:5000"
    libretranslate_api_key: str = ""
    translation_timeout: float = 60.0
    translation_source_language: str = "auto"
    translation_max_chars: int = 5000
    # Tetti espliciti per assemblaggio e risposta finale; None usa il default.
    assembly_max_output_tokens: int | None = None
    final_max_output_tokens: int | None = None

    @classmethod
    def from_env(cls, env_file: Path) -> Settings:
        # config/runtime.env porta la configurazione non-secret (SMTP, lane Qwen,
        # context Ollama...); il file .env dell'utente fa override; l'ambiente
        # reale vince su tutto.
        file_env: dict[str, str] = {}
        for env_path in (ROOT / "config" / "runtime.env", env_file):
            if not Path(env_path).is_file():
                continue
            file_env.update(
                {
                    key: value
                    for key, value in dotenv_values(env_path).items()
                    if value is not None
                }
            )
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
            ollama_num_ctx=int(env.get("OLLAMA_NUM_CTX", "32768")),
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
            laya_excerpt_max_chars=int(
                env.get(
                    "LAYA_EXCERPT_MAX_CHARS",
                    env.get("LAYA_EXTRACT_MAX_CHARS", "1200"),
                )
            ),
            segment_max_output_tokens=(
                int(env["BENCHMARK_SEGMENT_MAX_TOKENS"])
                if env.get("BENCHMARK_SEGMENT_MAX_TOKENS")
                else None
            ),
            assembly_max_output_tokens=(
                int(env["BENCHMARK_ASSEMBLY_MAX_TOKENS"])
                if env.get("BENCHMARK_ASSEMBLY_MAX_TOKENS")
                else None
            ),
            final_max_output_tokens=(
                int(env["BENCHMARK_FINAL_MAX_TOKENS"])
                if env.get("BENCHMARK_FINAL_MAX_TOKENS")
                else None
            ),
            translation_enabled=_env_flag(env, "TRANSLATION_ENABLED", True),
            translation_argos_enabled=_env_flag(env, "TRANSLATION_ARGOS_ENABLED", True),
            translation_libretranslate_enabled=_env_flag(
                env, "TRANSLATION_LIBRETRANSLATE_ENABLED", True
            ),
            libretranslate_url=env.get(
                "LIBRETRANSLATE_URL", "http://127.0.0.1:5000"
            ).rstrip("/"),
            libretranslate_api_key=env.get("LIBRETRANSLATE_API_KEY", ""),
            translation_timeout=float(env.get("TRANSLATION_TIMEOUT", "60")),
            translation_source_language=env.get(
                "TRANSLATION_SOURCE_LANGUAGE", "auto"
            ).strip(),
            translation_max_chars=int(env.get("TRANSLATION_MAX_CHARS", "5000")),
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

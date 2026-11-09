"""Traduzione a livelli: Argos locale, poi LibreTranslate, poi (a monte) l'LLM.

Il livello LLM non e implementato qui: quando nessun backend locale produce una
traduzione, translate_text restituisce None e il chiamante ricade sull'LLM.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache

import httpx

_LANGUAGE_ALIASES: dict[str, str] = {
    "arabo": "ar",
    "arabic": "ar",
    "ceco": "cs",
    "chinese": "zh",
    "cinese": "zh",
    "coreano": "ko",
    "croato": "hr",
    "danese": "da",
    "danish": "da",
    "deutsch": "de",
    "ebraico": "he",
    "english": "en",
    "espanol": "es",
    "estone": "et",
    "finlandese": "fi",
    "finnish": "fi",
    "francese": "fr",
    "french": "fr",
    "german": "de",
    "giapponese": "ja",
    "greco": "el",
    "greek": "el",
    "hindi": "hi",
    "indonesiano": "id",
    "inglese": "en",
    "irlandese": "ga",
    "italian": "it",
    "italiano": "it",
    "japanese": "ja",
    "korean": "ko",
    "lettone": "lv",
    "lituano": "lt",
    "norvegese": "nb",
    "norwegian": "nb",
    "olandese": "nl",
    "polish": "pl",
    "polacco": "pl",
    "portoghese": "pt",
    "portuguese": "pt",
    "romeno": "ro",
    "rumeno": "ro",
    "russian": "ru",
    "russo": "ru",
    "slovacco": "sk",
    "sloveno": "sl",
    "spagnolo": "es",
    "spanish": "es",
    "svedese": "sv",
    "swedish": "sv",
    "tedesco": "de",
    "turco": "tr",
    "turkish": "tr",
    "ucraino": "uk",
    "ungherese": "hu",
    "vietnamita": "vi",
}

_LANGUAGE_CODE_RE = re.compile(r"^[a-z]{2,3}$")


def normalize_language(value: str | None) -> str | None:
    """Codice ISO 639-1 per un nome o codice di lingua, altrimenti None."""
    if not isinstance(value, str):
        return None
    key = value.strip().lower().replace("_", "-")
    if not key:
        return None
    if key in _LANGUAGE_ALIASES:
        return _LANGUAGE_ALIASES[key]
    base = key.split("-")[0]
    if base in _LANGUAGE_ALIASES:
        return _LANGUAGE_ALIASES[base]
    if _LANGUAGE_CODE_RE.fullmatch(base):
        return base
    return None


@dataclass(frozen=True)
class TranslationSettings:
    """Configurazione della catena locale; nessun valore e obbligatorio."""

    argos_enabled: bool = True
    libretranslate_enabled: bool = True
    libretranslate_url: str = "http://127.0.0.1:5000"
    libretranslate_api_key: str = ""
    timeout: float = 60.0
    max_chars_per_request: int = 5000
    libretranslate_format: str = "text"


@dataclass(frozen=True)
class TranslationResult:
    """Esito di una traduzione locale riuscita."""

    text: str
    backend: str
    source_language: str
    target_language: str


def split_for_translation(text: str, max_chars: int) -> list[str]:
    """Spezza il testo su confini di paragrafo entro max_chars caratteri."""
    if max_chars <= 0 or len(text) <= max_chars:
        return [text]
    chunks: list[str] = []
    current = ""
    for paragraph in text.split("\n\n"):
        candidate = f"{current}\n\n{paragraph}" if current else paragraph
        if len(candidate) <= max_chars:
            current = candidate
            continue
        if current:
            chunks.append(current)
        while len(paragraph) > max_chars:
            chunks.append(paragraph[:max_chars])
            paragraph = paragraph[max_chars:]
        current = paragraph
    if current:
        chunks.append(current)
    return chunks


@lru_cache(maxsize=1)
def _argos_module():
    """Importa argostranslate una sola volta; None se non installato."""
    try:
        from argostranslate import translate as argos_translate  # type: ignore
    except Exception:  # noqa: BLE001 - argostranslate e opzionale: import assente o rotto
        return None
    return argos_translate


def _translate_with_argos(text: str, source_language: str, target_language: str) -> str | None:
    """Traduzione offline via Argos; None se sorgente ignota o pacchetto assente."""
    if source_language in {"", "auto"}:
        return None
    module = _argos_module()
    if module is None:
        return None
    try:
        translated = module.translate(text, source_language, target_language)
    except Exception:  # noqa: BLE001 - Argos puo sollevare errori arbitrari: degrada
        return None
    if not isinstance(translated, str) or not translated.strip():
        return None
    return translated


def _libretranslate_translate(
    text: str,
    source_language: str,
    target_language: str,
    settings: TranslationSettings,
    client: httpx.Client,
) -> str | None:
    url = f"{settings.libretranslate_url.rstrip('/')}/translate"
    payload: dict[str, str] = {
        "q": text,
        "source": source_language or "auto",
        "target": target_language,
        "format": settings.libretranslate_format,
    }
    if settings.libretranslate_api_key:
        payload["api_key"] = settings.libretranslate_api_key
    try:
        response = client.post(url, json=payload, timeout=settings.timeout)
        response.raise_for_status()
        data = response.json()
    except (httpx.HTTPError, ValueError):
        return None
    if not isinstance(data, dict):
        return None
    translated = data.get("translatedText")
    if not isinstance(translated, str) or not translated.strip():
        return None
    return translated


def _translate_with_libretranslate(
    text: str,
    source_language: str,
    target_language: str,
    settings: TranslationSettings,
    client: httpx.Client | None,
) -> str | None:
    """Traduzione via LibreTranslate, a segmenti entro il tetto di caratteri."""
    if not settings.libretranslate_url.strip():
        return None
    chunks = split_for_translation(text, settings.max_chars_per_request)
    own_client = client is None
    http = client or httpx.Client(timeout=settings.timeout)
    try:
        parts: list[str] = []
        for chunk in chunks:
            translated = _libretranslate_translate(
                chunk, source_language, target_language, settings, http
            )
            if translated is None:
                return None
            parts.append(translated)
    finally:
        if own_client:
            http.close()
    return "\n\n".join(part.strip() for part in parts)


def translate_text(
    text: str,
    target_language: str,
    *,
    source_language: str = "auto",
    settings: TranslationSettings | None = None,
    client: httpx.Client | None = None,
) -> TranslationResult | None:
    """Traduce text con la catena Argos -> LibreTranslate."""
    if not isinstance(text, str) or not text.strip():
        return None
    target = normalize_language(target_language)
    if target is None:
        return None
    resolved = settings or TranslationSettings()
    source = normalize_language(source_language) or "auto"

    if resolved.argos_enabled:
        translated = _translate_with_argos(text, source, target)
        if translated is not None:
            return TranslationResult(
                text=translated,
                backend="argos",
                source_language=source,
                target_language=target,
            )

    if resolved.libretranslate_enabled:
        translated = _translate_with_libretranslate(text, source, target, resolved, client)
        if translated is not None:
            return TranslationResult(
                text=translated,
                backend="libretranslate",
                source_language=source,
                target_language=target,
            )

    return None

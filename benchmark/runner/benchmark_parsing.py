"""Parsing documenti del benchmark: EPUB, HTML e JSON (T2-09, rv7 N28).

Spostamento meccanico di codice da `app/benchmark_models.py` (nessun
riscrittura).
"""

from __future__ import annotations

import json
import posixpath
import re
import zipfile
from functools import lru_cache
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, ClassVar

from defusedxml import ElementTree as ET

from .benchmark_settings import CHARS_PER_A4_PAGE, MAX_PROMPT_EXCERPT, ROOT


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
        _ = attrs  # firma contrattuale di HTMLParser: non usata qui
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
    else:
        # Apply the default excerpt guardrail only when the prompt has no explicit page limit.
        book = book[:MAX_PROMPT_EXCERPT]
    return f"<libro>\n{book}\n</libro>\n\n{instructions}"

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

def _prompt_min_chars(prompt: dict) -> int:
    """Minimo di caratteri imposto dai controlli quality `min_chars` del prompt."""
    values = [
        check["value"]
        for check in prompt.get("quality") or []
        if check.get("type") == "min_chars" and isinstance(check.get("value"), int)
    ]
    return max(values, default=0)

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

_NO_JSON = object()

def parse_json_document(text: str) -> Any:
    """Return the first JSON array/object in text (optionally fenced), else _NO_JSON."""
    fenced = re.search(r"```(?:json)?(.*?)```", text, re.DOTALL | re.IGNORECASE)
    candidate = fenced.group(1) if fenced else text
    starts = [i for i in (candidate.find("["), candidate.find("{")) if i >= 0]
    if not starts:
        return _NO_JSON
    try:
        return json.JSONDecoder().raw_decode(candidate, min(starts))[0]
    except ValueError:
        return _NO_JSON

def json_document(text: str) -> bool:
    return parse_json_document(text) is not _NO_JSON

def _wants_json_merge(instructions: str, output_format: str) -> bool:
    """True se il contratto richiede un documento JSON (per formato o per istruzioni)."""
    return output_format.strip().lower() == "json" or "json" in instructions.lower()

def _json_merge_items(value):
    """Normalizza un documento JSON di segmento in una lista di elementi da unire."""
    if isinstance(value, list):
        return value
    if isinstance(value, dict) and len(value) == 1:
        (only,) = value.values()
        if isinstance(only, list):
            return only
    return [value]

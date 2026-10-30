#!/usr/bin/env python3
"""Generate / edit images via LLM_MODEL_IMAGE provider from .env (Qwen DashScope)."""

from __future__ import annotations

import argparse
import base64
import http.client
import json
import mimetypes
import re
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, NoReturn, cast
from urllib.parse import urlsplit

# Exit codes (agent-friendly)
EX_OK = 0
EX_USAGE = 1
EX_AUTH = 2
EX_API = 3
EX_IO = 4

EXIT_CODE_LABELS = {
    EX_OK: "SUCCESS",
    EX_USAGE: "USAGE_ERROR",
    EX_AUTH: "AUTH_ERROR",
    EX_API: "API_ERROR",
    EX_IO: "IO_ERROR",
}

# Legacy ImageSynthesis (async) — max ~1328
SYNTHESIS_MODELS = frozenset(
    {"qwen-image-plus", "qwen-image-plus-2026-01-09", "qwen-image"}
)
SNAPSHOT_PLUS = "qwen-image-plus-2026-01-09"

# MultiModalConversation (sync) — native ~2K
MULTIMODAL_T2I_PREFIXES = ("qwen-image-2.0", "qwen-image-max")
EDIT_PREFIXES = ("qwen-image-edit",)
DEFAULT_EDIT_MODEL = "qwen-image-edit-plus"

QWEN_PLUS_SIZE_ALIASES: dict[str, str] = {
    "1:1": "1328*1328",
    "16:9": "1664*928",
    "9:16": "928*1664",
    "4:3": "1472*1104",
    "3:4": "1104*1472",
    "3:2": "1584*1056",
    "2:3": "1056*1584",
}

# Official recommended 2.0 sizes (Alibaba Model Studio)
QWEN2_SIZE_ALIASES: dict[str, str] = {
    "1:1": "2048*2048",
    "16:9": "2688*1536",
    "9:16": "1536*2688",
    "4:3": "2368*1728",
    "3:4": "1728*2368",
    "1K": "1024*1024",
    "2K": "2048*2048",
}

_FMT = "text"


def load_dotenv(path: Path) -> dict[str, str]:
    env: dict[str, str] = {}
    if not path.is_file():
        raise FileNotFoundError(f".env not found: {path}")
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        env[key.strip()] = value.strip().strip('"').strip("'")
    return env


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---"):
        return {}, text
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", text, re.DOTALL)
    if not match:
        return {}, text
    meta: dict[str, Any] = {}
    for line in match.group(1).splitlines():
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        value = value.strip()
        if value.lower() in ("true", "false"):
            meta[key.strip()] = value.lower() == "true"
        elif value.isdigit():
            meta[key.strip()] = int(value)
        elif value == "":
            meta[key.strip()] = None
        else:
            meta[key.strip()] = value.strip('"').strip("'")
    return meta, match.group(2)


def extract_section(body: str, heading: str) -> str:
    pattern = rf"^##\s+{re.escape(heading)}\s*$\n(.*?)(?=^##\s+|\Z)"
    match = re.search(pattern, body, re.MULTILINE | re.DOTALL)
    if not match:
        return ""
    text = match.group(1).strip()
    lines = []
    for line in text.splitlines():
        line = line.strip()
        if line.startswith(">"):
            line = line.lstrip(">").strip()
        if line.startswith("[") and line.endswith("]"):
            continue
        if line:
            lines.append(line)
    return "\n".join(lines).strip()


def load_style_file(path: Path) -> tuple[dict[str, Any], str, str]:
    raw = path.read_text(encoding="utf-8")
    meta, body = parse_frontmatter(raw)
    anchor = extract_section(body, "Style anchor (prompt base)")
    if not anchor:
        anchor = extract_section(body, "Style anchor")
    negative = extract_section(body, "Negative prompt")
    return meta, anchor, negative


def build_prompt(style_anchor: str, subject: str, composition: str = "") -> str:
    parts = [style_anchor.strip(), "", f"Subject: {subject.strip()}."]
    if composition.strip():
        parts.extend(["", f"Composition: {composition.strip()}."])
    return "\n".join(parts).strip()


def model_family(model: str) -> str:
    m = (model or "").strip().lower()
    if m in SYNTHESIS_MODELS or m.startswith("qwen-image-plus"):
        return "synthesis"
    if any(m.startswith(p) for p in EDIT_PREFIXES):
        return "edit"
    if any(m.startswith(p) for p in MULTIMODAL_T2I_PREFIXES):
        return "multimodal_t2i"
    # Unknown qwen-* → treat as multimodal if looks like 2.x else synthesis
    if "2.0" in m or m.startswith("qwen-image-max"):
        return "multimodal_t2i"
    return "synthesis"


def supports_image_input(model: str) -> bool:
    """Edit-* and Qwen-Image-2.0* (unified T2I+I2I) accept --image."""
    return model_family(model) in ("edit", "multimodal_t2i")


def resolve_size(raw: str | None, model: str, *, optional: bool = False) -> str | None:
    """Resolve ratio alias or W*H. Family-aware (plus vs 2.0)."""
    s = (raw or "").strip()
    if not s:
        if optional:
            return None
        fam = model_family(model)
        return "2048*2048" if fam in ("multimodal_t2i", "edit") else "1328*1328"
    if re.fullmatch(r"\d+\*\d+", s):
        return s
    key = s.replace(" ", "")
    fam = model_family(model)
    aliases = (
        QWEN2_SIZE_ALIASES
        if fam in ("multimodal_t2i", "edit")
        else QWEN_PLUS_SIZE_ALIASES
    )
    if key in aliases:
        return aliases[key]
    # Cross-hint: if alias only exists on the other table, say so
    other = (
        QWEN_PLUS_SIZE_ALIASES if aliases is QWEN2_SIZE_ALIASES else QWEN2_SIZE_ALIASES
    )
    hint = f" Known aliases for this model family: {', '.join(aliases)}."
    if key in other:
        hint += f" Alias '{key}' maps differently on the other family."
    raise ValueError(f"Invalid size '{raw}'. Use W*H or alias.{hint}")


def resolve_provider(env: dict[str, str]) -> tuple[str, dict[str, str]]:
    provider = env.get("LLM_MODEL_IMAGE", "").strip().lower()
    if not provider:
        raise ValueError("LLM_MODEL_IMAGE is not set in .env")
    prefix = provider.upper()
    cfg = {
        "api_key": env.get(f"{prefix}_MODEL_API_KEY", ""),
        "model": env.get(f"{prefix}_MODEL_NAME_IMAGE", ""),
        "url_image": env.get(f"{prefix}_MODEL_URL_IMAGE", ""),
        "url_multimodal": env.get(f"{prefix}_MODEL_URL_MULTIMODAL", ""),
        "model_edit": env.get(f"{prefix}_MODEL_NAME_IMAGE_EDIT", ""),
        "model_snapshot": env.get(f"{prefix}_MODEL_SNAPSHOT", SNAPSHOT_PLUS),
    }
    missing = [k for k in ("api_key", "model", "url_image") if not cfg[k]]
    if missing:
        raise ValueError(
            f"Missing {prefix}_MODEL_* for image provider '{provider}': {', '.join(missing)}"
        )
    return provider, cfg


def api_host_base(url: str) -> str:
    return url.rsplit("/services/", 1)[0]


def synthesis_endpoint(cfg: dict[str, str]) -> str:
    url = cfg["url_image"]
    if "multimodal-generation" in url:
        return url.replace(
            "multimodal-generation/generation", "text2image/image-synthesis"
        )
    return url


def multimodal_endpoint(cfg: dict[str, str]) -> str:
    if cfg.get("url_multimodal"):
        return cfg["url_multimodal"]
    url = cfg["url_image"]
    if "multimodal-generation" in url:
        return url
    if "text2image/image-synthesis" in url:
        return url.replace(
            "text2image/image-synthesis", "multimodal-generation/generation"
        )
    return f"{api_host_base(url)}/services/aigc/multimodal-generation/generation"


def tasks_url_from_any(endpoint: str, task_id: str) -> str:
    return f"{api_host_base(endpoint)}/tasks/{task_id}"


# Connessione keep-alive per host, riusata tra le chiamate (N24, doc QwenCloud
# §connection reuse: il loop di poll_synthesis_task non deve riaprire una TCP+TLS
# a ogni poll). Retry con connessione nuova solo su drop del keep-alive.
_CONNECTIONS: dict[tuple[str, int], http.client.HTTPConnection] = {}


def _keepalive_connection(
    scheme: str, host: str, port: int, timeout: int
) -> http.client.HTTPConnection:
    key = (host, port)
    conn = _CONNECTIONS.get(key)
    if conn is None:
        cls = (
            http.client.HTTPSConnection
            if scheme == "https"
            else http.client.HTTPConnection
        )
        netloc = host if port in (80, 443) else f"{host}:{port}"
        conn = cls(netloc, timeout=timeout)
        _CONNECTIONS[key] = conn
    return conn


def http_json(
    method: str,
    url: str,
    headers: dict[str, str],
    payload: dict[str, Any] | None = None,
    timeout: int = 180,
) -> dict[str, Any]:
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    parts = urlsplit(url)
    path = (parts.path or "/") + (f"?{parts.query}" if parts.query else "")
    scheme = parts.scheme or "https"
    host = parts.hostname or ""
    port = parts.port or (443 if scheme == "https" else 80)
    req_headers = dict(headers)
    req_headers.setdefault("Connection", "keep-alive")
    if data is not None:
        req_headers.setdefault("Content-Type", "application/json")
    for attempt in (0, 1):
        conn = _keepalive_connection(scheme, host, port, timeout)
        try:
            conn.request(method, path, body=data, headers=req_headers)
            resp = conn.getresponse()
            body = resp.read().decode("utf-8", errors="replace")
        except (
            http.client.RemoteDisconnected,
            http.client.BadStatusLine,
            ConnectionResetError,
            BrokenPipeError,
        ) as exc:
            # keep-alive drop: la richiesta non è stata processata, riprova nuova
            conn.close()
            _CONNECTIONS.pop((host, port), None)
            if attempt:
                raise urllib.error.URLError(exc) from exc
            continue
        except (http.client.HTTPException, OSError) as exc:
            # errore di rete/timeout: nessuna retry (potrebbe duplicare un POST)
            conn.close()
            _CONNECTIONS.pop((host, port), None)
            raise urllib.error.URLError(exc) from exc
        if resp.status >= 400:
            raise RuntimeError(f"HTTP {resp.status} {url}: {body}")
        return json.loads(body)
    raise urllib.error.URLError(OSError(f"connection failure: {url}"))


def image_ref_for_api(path_or_url: str) -> str:
    """Public URL, data URI, or local file → data:image/...;base64,..."""
    s = path_or_url.strip()
    if s.startswith(("http://", "https://", "data:")):
        return s
    path = Path(s)
    if not path.is_file():
        raise FileNotFoundError(f"Input image not found: {path}")
    mime, _ = mimetypes.guess_type(str(path))
    if not mime or not mime.startswith("image/"):
        mime = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".webp": "image/webp",
            ".gif": "image/gif",
            ".bmp": "image/bmp",
        }.get(path.suffix.lower(), "image/png")
    b64 = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{b64}"


# Profili di polling per modalita' (tabella doc QwenCloud async-task):
# modality -> (intervallo iniziale, moltiplicatore, cap, timeout). Il polling a
# intervallo fisso spreca chiamate contro il limite condiviso di 20 QPS.
POLL_PROFILES: dict[str, tuple[float, float, float, float]] = {
    "image": (3.0, 1.5, 15.0, 120.0),
    "video": (15.0, 1.5, 60.0, 300.0),
    "asr": (5.0, 1.5, 30.0, 300.0),
}
# Stati terminali completi del task model: solo PENDING e' cancellabile e
# RUNNING continua; UNKNOWN (id scaduto/retention 24h) e CANCELED escono subito.
TERMINAL_STATUSES = {"SUCCEEDED", "FAILED", "CANCELED", "UNKNOWN"}
NON_RUNNING_TERMINAL = {"CANCELED", "UNKNOWN"}


@dataclass
class PollResult:
    url: str
    urls: list[str]
    partial: bool = False
    warnings: list[str] = field(default_factory=list)


def _collect_success(result: dict[str, Any]) -> tuple[list[str], list[str]]:
    """Raccoglie gli URL validi da un task SUCCEEDED o da una risposta sync.

    Itera choices verificando ``finish_reason`` (solo "stop"/assente) e results
    (solo entry con url e senza codice di errore): un troncamento 4->2 non puo'
    essere accettato in silenzio. Ritorna (urls, warnings).
    """
    out = result.get("output") or {}
    urls: list[str] = []
    warnings: list[str] = []
    choices = out.get("choices") or []
    for i, choice in enumerate(choices):
        finish = choice.get("finish_reason")
        if finish not in (None, "", "stop"):
            warnings.append(
                f"choice {i} skipped: finish_reason={finish!r} (truncated output)"
            )
            continue
        content = (choice.get("message") or {}).get("content") or []
        for item in content:
            if isinstance(item, dict) and item.get("image"):
                urls.append(item["image"])
    if not urls:
        for i, item in enumerate(out.get("results") or []):
            code = str(item.get("code") or "")
            if item.get("url") and code in ("", "200", "null", "None"):
                urls.append(item["url"])
            else:
                warnings.append(f"result {i} skipped: code={code or 'no-url'}")
    return urls, warnings


def _warn(warnings: list[str]) -> None:
    for message in warnings:
        print(f"Warning: {message}", file=sys.stderr)


def extract_multimodal_image_urls(result: dict[str, Any]) -> list[str]:
    urls, warnings = _collect_success(result)
    _warn(warnings)
    if not urls:
        raise RuntimeError(
            f"Multimodal response missing image URL: {json.dumps(result)[:2000]}"
        )
    return urls


def poll_synthesis_task(
    endpoint: str,
    headers: dict[str, str],
    task_id: str,
    poll_interval: float | None = None,
    poll_timeout: float | None = None,
    modality: str = "image",
) -> PollResult:
    """Polling a backoff esponenziale con intervalli per modalita' e stati
    terminali completi (CANCELED/UNKNOWN escono subito, tabella doc 2026-10-28).
    """
    base, multiplier, cap, profile_timeout = POLL_PROFILES.get(
        modality, POLL_PROFILES["image"]
    )
    interval = poll_interval if poll_interval is not None else base
    timeout = poll_timeout if poll_timeout is not None else profile_timeout
    deadline = time.time() + timeout
    status_url = tasks_url_from_any(endpoint, task_id)
    while time.time() < deadline:
        result = http_json("GET", status_url, headers, timeout=60)
        out = result.get("output") or {}
        status = out.get("task_status", "")
        if status == "SUCCEEDED":
            urls, warnings = _collect_success(result)
            _warn(warnings)
            if not urls:
                raise RuntimeError(f"Qwen succeeded but no URL: {json.dumps(result)}")
            return PollResult(
                url=urls[0], urls=urls, partial=bool(warnings), warnings=warnings
            )
        if status == "FAILED":
            raise RuntimeError(
                f"Qwen task failed: {out.get('code')} — {out.get('message')}"
            )
        if status in NON_RUNNING_TERMINAL:
            raise RuntimeError(
                f"Qwen task {status} (terminal, non retryabile): {task_id}"
            )
        time.sleep(interval)
        interval = min(interval * multiplier, cap)
    raise TimeoutError(f"Qwen task {task_id} timed out after {timeout}s")


def generate_qwen_synthesis(
    cfg: dict[str, str],
    model: str,
    prompt: str,
    negative_prompt: str,
    size: str,
    seed: int | None,
    prompt_extend: bool,
    watermark: bool,
) -> PollResult:
    endpoint = synthesis_endpoint(cfg)
    headers = {
        "Authorization": f"Bearer {cfg['api_key']}",
        "Content-Type": "application/json",
        "X-DashScope-Async": "enable",
    }
    parameters: dict[str, Any] = {
        "negative_prompt": negative_prompt or " ",
        "size": size,
        "n": 1,
        "prompt_extend": prompt_extend,
        "watermark": watermark,
    }
    if seed is not None:
        parameters["seed"] = seed
    payload = {
        "model": model,
        "input": {"prompt": prompt},
        "parameters": parameters,
    }
    created = http_json("POST", endpoint, headers, payload, timeout=60)
    output = created.get("output") or {}
    task_id = output.get("task_id")
    if not task_id:
        raise RuntimeError(
            f"Qwen task creation failed: {json.dumps(created, indent=2)}"
        )
    return poll_synthesis_task(endpoint, headers, task_id)


def generate_qwen_multimodal(
    cfg: dict[str, str],
    model: str,
    prompt: str,
    negative_prompt: str,
    size: str | None,
    seed: int | None,
    prompt_extend: bool,
    watermark: bool,
    images: list[str] | None = None,
    n: int = 1,
) -> PollResult:
    """Sync MultiModalConversation HTTP (2.0 T2I/I2I and edit-*). Returns PollResult."""
    endpoint = multimodal_endpoint(cfg)
    headers = {
        "Authorization": f"Bearer {cfg['api_key']}",
        "Content-Type": "application/json",
    }
    content: list[dict[str, str]] = []
    for img in images or []:
        content.append({"image": img})
    content.append({"text": prompt})
    parameters: dict[str, Any] = {
        "n": max(1, min(6, n)),
        "prompt_extend": prompt_extend,
        "watermark": watermark,
    }
    if negative_prompt and negative_prompt.strip():
        parameters["negative_prompt"] = negative_prompt
    if size:
        parameters["size"] = size
    if seed is not None:
        parameters["seed"] = seed
    payload = {
        "model": model,
        "input": {"messages": [{"role": "user", "content": content}]},
        "parameters": parameters,
    }
    result = http_json("POST", endpoint, headers, payload, timeout=180)
    if (
        result.get("code")
        and str(result.get("code")) not in ("", "null", "None")
        and not (result.get("output") or {}).get("choices")
    ):
        raise RuntimeError(
            f"Qwen multimodal error: {result.get('code')} — {result.get('message')}"
        )
    urls, warnings = _collect_success(result)
    _warn(warnings)
    if not urls:
        raise RuntimeError(
            f"Multimodal response missing image URL: {json.dumps(result)[:2000]}"
        )
    return PollResult(url=urls[0], urls=urls, partial=bool(warnings), warnings=warnings)


def download_file(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if url.startswith("data:"):
        # data:image/png;base64,...
        _, _, b64 = url.partition(",")
        dest.write_bytes(base64.b64decode(b64))
        return
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=120) as resp:
        dest.write_bytes(resp.read())


def emit_success(data: dict[str, Any]) -> None:
    if _FMT == "json":
        print(json.dumps({"ok": True, **data}, ensure_ascii=False))
    else:
        print(data.get("output") or data)


def emit_error(code: int, message: str, retryable: bool = False) -> NoReturn:
    label = EXIT_CODE_LABELS.get(code, "UNKNOWN")
    if _FMT == "json":
        print(
            json.dumps(
                {
                    "ok": False,
                    "error": {
                        "code": label,
                        "message": message,
                        "retryable": retryable,
                    },
                },
                ensure_ascii=False,
            )
        )
    else:
        print(f"Error [{label}]: {message}", file=sys.stderr)
    raise SystemExit(code)


def main() -> int:
    global _FMT
    parser = argparse.ArgumentParser(
        description="Generate/edit image via LLM_MODEL_IMAGE from .env (Qwen)"
    )
    parser.add_argument(
        "--env", type=Path, default=Path(".env"), help="Path to .env file"
    )
    parser.add_argument("--style", type=Path, help="Style brief markdown file")
    parser.add_argument(
        "--subject", type=str, help="Subject to illustrate / edit instruction"
    )
    parser.add_argument(
        "--composition", type=str, default="", help="Optional composition hints"
    )
    parser.add_argument(
        "--prompt", type=str, help="Full prompt (overrides style+subject)"
    )
    parser.add_argument(
        "--negative", type=str, default="", help="Override negative prompt"
    )
    parser.add_argument(
        "--size",
        type=str,
        help="W*H or alias (plus: 1:1/3:2/…; 2.0/edit: 1:1→2048*, also 1K/2K)",
    )
    parser.add_argument("--seed", type=int, help="Random seed for reproducibility")
    parser.add_argument(
        "--prompt-extend",
        action="store_true",
        help="Force prompt rewrite on (T2I default off; edit default on)",
    )
    parser.add_argument(
        "--no-prompt-extend",
        action="store_true",
        help="Force prompt rewrite off (overrides edit default)",
    )
    parser.add_argument(
        "--n",
        type=int,
        default=1,
        help="Number of images for 2.0/edit multimodal (1–6). Synthesis always 1",
    )
    parser.add_argument("--watermark", action="store_true", help="Add Qwen watermark")
    parser.add_argument("--output", type=Path, required=True, help="Output image path")
    parser.add_argument(
        "--dry-run", action="store_true", help="Print payload without calling API"
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="stdout format: text (path) or json ({ok,...})",
    )
    parser.add_argument(
        "--model",
        type=str,
        help="Override model id (e.g. qwen-image-2.0-pro, qwen-image-edit-plus)",
    )
    parser.add_argument(
        "--snapshot",
        action="store_true",
        help=f"Pin legacy plus snapshot ({SNAPSHOT_PLUS}) unless --model set",
    )
    parser.add_argument(
        "--image",
        type=str,
        action="append",
        default=[],
        help="Input image path/URL for I2I (repeatable, max 3). "
        "Keeps 2.0* if already selected; else auto edit-plus",
    )
    parser.add_argument(
        "--idempotency-key",
        type=str,
        help="If set and --output already exists (non-empty), skip API and return cached path",
    )
    args = parser.parse_args()
    _FMT = args.format
    if args.prompt_extend and args.no_prompt_extend:
        emit_error(
            EX_USAGE,
            "Use only one of --prompt-extend / --no-prompt-extend",
            retryable=False,
        )
    if args.n < 1 or args.n > 6:
        emit_error(EX_USAGE, "--n must be between 1 and 6", retryable=False)

    try:
        env = load_dotenv(args.env)
    except FileNotFoundError as exc:
        emit_error(EX_AUTH, str(exc), retryable=False)

    try:
        provider, cfg = resolve_provider(env)
    except ValueError as exc:
        msg = str(exc)
        code = (
            EX_AUTH
            if "API_KEY" in msg or "LLM_MODEL_IMAGE" in msg or "Missing" in msg
            else EX_USAGE
        )
        emit_error(code, msg, retryable=False)

    # Resolve model: CLI --model > --snapshot > .env; --image keeps 2.0* or switches plus→edit
    model = (args.model or "").strip()
    if not model and args.snapshot:
        model = (cfg.get("model_snapshot") or SNAPSHOT_PLUS).strip()
    if not model:
        model = cfg["model"]
    if args.image:
        fam0 = model_family(model)
        if fam0 == "synthesis":
            if args.model:
                emit_error(
                    EX_USAGE,
                    f"--image is incompatible with synthesis model '{args.model}'. "
                    f"Use --model qwen-image-2.0-pro (unified I2I) or "
                    f"--model {DEFAULT_EDIT_MODEL}",
                    retryable=False,
                )
            model = (cfg.get("model_edit") or DEFAULT_EDIT_MODEL).strip()
        # multimodal_t2i (2.0*) and edit-*: keep model (unified / dedicated edit)

    fam = model_family(model)
    doing_i2i = bool(args.image)
    if fam == "edit" and not doing_i2i:
        emit_error(
            EX_USAGE,
            f"Model '{model}' is an edit model and requires --image",
            retryable=False,
        )
    if doing_i2i and not supports_image_input(model):
        emit_error(
            EX_USAGE,
            f"Model '{model}' does not support --image",
            retryable=False,
        )
    if len(args.image) > 3:
        emit_error(EX_USAGE, "At most 3 --image inputs are supported", retryable=False)
    if fam == "synthesis" and args.n != 1:
        emit_error(
            EX_USAGE,
            "Synthesis models (plus/legacy) only support n=1",
            retryable=False,
        )

    # Idempotency: skip if output exists
    if (
        args.idempotency_key
        and args.output.is_file()
        and args.output.stat().st_size > 0
        and not args.dry_run
    ):
        out_path = str(args.output.resolve())
        emit_success(
            {
                "output": out_path,
                "provider": provider,
                "model": model,
                "cached": True,
                "idempotency_key": args.idempotency_key,
            }
        )
        return EX_OK

    style_meta: dict[str, Any] = {}
    style_anchor = ""
    style_negative = ""

    if args.style:
        try:
            style_meta, style_anchor, style_negative = load_style_file(args.style)
        except OSError as exc:
            emit_error(EX_IO, f"Cannot read style file: {exc}", retryable=False)

    if args.prompt:
        prompt = args.prompt
    elif args.subject and style_anchor:
        prompt = build_prompt(style_anchor, args.subject, args.composition)
    elif args.subject:
        prompt = args.subject
    else:
        emit_error(
            EX_USAGE,
            "Provide --prompt or (--style and --subject) or --subject alone",
            retryable=False,
        )

    negative = args.negative or style_negative or " "
    size_optional = fam == "edit" or doing_i2i
    default_raw = None
    if args.size:
        raw_size = args.size
    elif style_meta.get("size"):
        raw_size = str(style_meta.get("size"))
    elif size_optional:
        raw_size = None
        default_raw = None
    else:
        raw_size = "2048*2048" if fam == "multimodal_t2i" else "1328*1328"
        default_raw = raw_size

    try:
        size = resolve_size(raw_size, model, optional=size_optional)
    except ValueError as exc:
        emit_error(EX_USAGE, str(exc), retryable=False)

    seed = args.seed if args.seed is not None else style_meta.get("seed")
    if seed == "" or seed is None:
        seed = None
    elif isinstance(seed, str) and seed.isdigit():
        seed = int(seed)
    # normalizzazione statica: argparse (type=int) e meta dei file di stile
    # producono int|None; il cast non cambia il valore a runtime
    seed = cast("int | None", seed)

    # prompt_extend: T2I style-lock false; edit/I2I default true (stability)
    if args.prompt_extend:
        prompt_extend = True
    elif args.no_prompt_extend:
        prompt_extend = False
    elif "prompt_extend" in style_meta and style_meta.get("prompt_extend") is not None:
        prompt_extend = bool(style_meta.get("prompt_extend"))
    elif doing_i2i:
        prompt_extend = True
    else:
        prompt_extend = False
    watermark = args.watermark or bool(style_meta.get("watermark", False))
    n_images = args.n

    image_refs: list[str] = []
    if args.image and not args.dry_run:
        try:
            image_refs = [image_ref_for_api(p) for p in args.image]
        except FileNotFoundError as exc:
            emit_error(EX_IO, str(exc), retryable=False)

    if fam == "synthesis":
        api_kind = "ImageSynthesis (async)"
    elif doing_i2i and fam == "multimodal_t2i":
        api_kind = "MultiModalConversation (sync I2I, unified 2.0)"
    elif fam == "edit":
        api_kind = "MultiModalConversation (sync edit)"
    else:
        api_kind = "MultiModalConversation (sync T2I)"

    if args.dry_run:
        payload = {
            "provider": provider,
            "model": model,
            "family": fam,
            "i2i": doing_i2i,
            "api": api_kind,
            "endpoint": (
                synthesis_endpoint(cfg)
                if fam == "synthesis"
                else multimodal_endpoint(cfg)
            ),
            "size": size,
            "size_requested": raw_size or default_raw,
            "seed": seed,
            "n": n_images,
            "prompt_extend": prompt_extend,
            "watermark": watermark,
            "prompt": prompt,
            "negative_prompt": negative,
            "images": args.image,
            "output": str(args.output),
            "idempotency_key": args.idempotency_key,
        }
        if _FMT == "json":
            print(
                json.dumps(
                    {"ok": True, "dry_run": True, **payload},
                    indent=2,
                    ensure_ascii=False,
                )
            )
        else:
            print(json.dumps(payload, indent=2, ensure_ascii=False))
        return EX_OK

    if provider != "qwen":
        emit_error(
            EX_USAGE,
            f"Unsupported LLM_MODEL_IMAGE provider: {provider}",
            retryable=False,
        )

    try:
        if fam == "synthesis":
            if size is None:
                emit_error(
                    EX_USAGE, "size required for synthesis models", retryable=False
                )
            poll = generate_qwen_synthesis(
                cfg, model, prompt, negative, size, seed, prompt_extend, watermark
            )
        else:
            poll = generate_qwen_multimodal(
                cfg,
                model,
                prompt,
                negative,
                size,
                seed,
                prompt_extend,
                watermark,
                images=image_refs or None,
                n=n_images,
            )
        image_urls = poll.urls
    except TimeoutError as exc:
        emit_error(EX_API, str(exc), retryable=True)
    except RuntimeError as exc:
        msg = str(exc)
        retryable = (
            "HTTP 429" in msg or "rate" in msg.lower() or "timeout" in msg.lower()
        )
        authish = "InvalidApiKey" in msg or "HTTP 401" in msg or "HTTP 403" in msg
        emit_error(EX_AUTH if authish else EX_API, msg, retryable=retryable)
    except urllib.error.URLError as exc:
        emit_error(EX_API, f"Network error: {exc}", retryable=True)

    output_paths: list[str] = []
    try:
        if len(image_urls) == 1:
            download_file(image_urls[0], args.output)
            output_paths = [str(args.output.resolve())]
        else:
            for i, url in enumerate(image_urls, start=1):
                dest = args.output.with_name(
                    f"{args.output.stem}-{i}{args.output.suffix}"
                )
                download_file(url, dest)
                output_paths.append(str(dest.resolve()))
    except urllib.error.URLError as exc:
        # subclass di OSError: deve precedere il ramo generale, altrimenti
        # i fallimenti di download sarebbero etichettati come "write output"
        emit_error(EX_IO, f"Failed to download image: {exc}", retryable=True)
    except OSError as exc:
        emit_error(EX_IO, f"Failed to write output: {exc}", retryable=False)

    emit_success(
        {
            "output": output_paths[0],
            "outputs": output_paths,
            "provider": provider,
            "model": model,
            "family": fam,
            "i2i": doing_i2i,
            "size": size,
            "seed": seed,
            "n": len(output_paths),
            "partial": poll.partial,
            "cached": False,
        }
    )
    return EX_OK


if __name__ == "__main__":
    raise SystemExit(main())

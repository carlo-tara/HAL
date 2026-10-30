#!/usr/bin/env python3
"""Spike N28 (ToDo 2026-10-28, doc QwenCloud «Context cache»): verifica forwarding
session-cache e marker explicit via OrcaRouter. Esito in
`docs/26_spike_session_cache_orcarouter.md`.

Usage:
    env PYTHONPATH=. python3 scripts/spike_orcarouter_cache.py [model]

Costo: 4 chat completions minime (max_tokens 8) sul modello free.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import requests
from dotenv import dotenv_values

PREFIX = "HAL gateway context block. " * 200  # ~1092 token, sopra soglia 1024
END = "\nRispondi solo con OK"


def call(
    base: str, key: str, model: str, tag: str, *, marker=False, session=False
) -> None:
    content: object = PREFIX + END
    if marker:
        content = [
            {"type": "text", "text": PREFIX, "cache_control": {"type": "ephemeral"}},
            {"type": "text", "text": "Rispondi solo con OK"},
        ]
    body = {
        "model": model,
        "messages": [{"role": "user", "content": content}],
        "max_tokens": 8,
    }
    headers = {"Authorization": f"Bearer {key}"}
    if session:
        headers["x-dashscope-session-cache"] = "enable"
    r = requests.post(
        f"{base}/chat/completions", json=body, headers=headers, timeout=40
    )
    d = r.json()
    u = d.get("usage", {})
    det = u.get("prompt_tokens_details") or {}
    cached = u.get("cached_tokens", det.get("cached_tokens"))
    print(
        f"{tag}: http={r.status_code} prompt_tokens={u.get('prompt_tokens')} cached_tokens={cached}"
    )


def main() -> int:
    env = dotenv_values(Path(__file__).resolve().parent.parent / ".env")
    base = (env.get("ORCAROUTER_API_URI") or "https://api.orcarouter.ai/v1").rstrip("/")
    key = env.get("ORCAROUTER_API_KEY", "")
    if not key:
        print("ORCAROUTER_API_KEY assente in .env: N/A documentato")
        return 1
    model = sys.argv[1] if len(sys.argv) > 1 else "orcarouter/free"
    call(base, key, model, "R1 plain")
    time.sleep(2)
    call(base, key, model, "R2 plain hot")
    call(base, key, model, "R3 session-header", session=True)
    call(base, key, model, "R4 marker ephemeral", marker=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

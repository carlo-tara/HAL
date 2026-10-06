from __future__ import annotations

import hashlib
import json
import re
from typing import Any

# ==========================================
# 05 — RETENTION & REDACTION (P0)
# ==========================================

SECRET_PATTERNS: list[tuple[str, str]] = [
    (r"sk-[a-zA-Z0-9\-_]{20,}", "{{secret:openai}}"),
    (r"AKIA[0-9A-Z]{16}", "{{secret:aws_key}}"),
    (r"ghp_[a-zA-Z0-9]{36}", "{{secret:github_token}}"),
    (r"bearer\s+[a-zA-Z0-9_\-\.]{10,}", "bearer {{secret:bearer_token}}"),
    (r"-----BEGIN (?:RSA|PRIVATE) KEY-----[^-]*-----END (?:RSA|PRIVATE) KEY-----", "{{secret:private_key}}"),
    (r"password\s*[:=]\s*[^\s]+", "password={{secret:password}}"),
]

def redact_text(text: str) -> str:
    """Applica la denylist di regex per oscurare segreti e credenziali prima della scrittura in log."""
    redacted = text
    for pattern, placeholder in SECRET_PATTERNS:
        redacted = re.sub(pattern, placeholder, redacted, flags=re.IGNORECASE)
    return redacted

def process_event_payload(payload: dict[str, Any], laya_pii_check_fn: Any = None) -> dict[str, Any]:
    """Elabora il payload dell'evento applicando redaction e scansione PII opzionale tramite Laya."""
    processed = payload.copy()
    body_str = json.dumps(processed)
    
    redacted_body = redact_text(body_str)
    
    pii_detected = False
    if laya_pii_check_fn:
        try:
            score = laya_pii_check_fn(redacted_body, "contains PII or sensitive personal data")
            if score > 0.7:
                pii_detected = True
        except Exception:
            pass
            
    processed["redacted_body"] = redacted_body
    processed["pii_detected"] = pii_detected
    return processed


# ==========================================
# 07 — CACHE L1 (P0)
# ==========================================

def normalize_prompt(messages: list[dict[str, str]] | str) -> str:
    """Normalizza messaggi o prompt: lowercase, strip whitespace, rimozione timestamp casuali."""
    if isinstance(messages, list):
        serialized = " ".join([m.get("content", "") for m in messages])
    else:
        serialized = str(messages)
    
    # Rimozione preventivo timestamp ISO o simili (es. 2026-10-06T12:00:00Z)
    cleaned = re.sub(r"\d{4}-\d{2}-\d{2}[tT]\d{2}:\d{2}:\d{2}(?:\.\d+)?Z?", "", serialized)
    normalized = " ".join(cleaned.lower().split())
    return normalized

def compute_cache_key(session_id: str, use_case: str, messages: list[dict[str, str]] | str, relevant_files: list[str] | None = None) -> str:
    """Genera la chiave composita per la cache L1 Redis."""
    norm_msg = normalize_prompt(messages)
    msg_hash = hashlib.sha256(norm_msg.encode("utf-8")).hexdigest()
    
    files_str = ",".join(sorted(relevant_files or []))
    files_hash = hashlib.sha256(files_str.encode("utf-8")).hexdigest()
    
    return f"cache:v1:{session_id}:{use_case}:{msg_hash}:{files_hash}"


# ==========================================
# 19 — CIRCUIT BREAKER & SESSION (P1)
# ==========================================

def derive_session_id(api_key: str, workspace_path: str, conversation_id: str) -> str:
    """Deriva un session_id deterministico e isolato da api_key, workspace e conversazione."""
    raw = f"{api_key}:{workspace_path}:{conversation_id}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

class CircuitBreaker:
    """State machine del circuit breaker per provider in Redis / memoria."""
    def __init__(self, provider_name: str, failure_threshold: int = 5, open_s: int = 30) -> None:
        self.provider_name = provider_name
        self.failure_threshold = failure_threshold
        self.open_s = open_s
        self.failures = 0
        self.state = "CLOSED"  # CLOSED, OPEN, HALF-OPEN
        self.last_failure_timestamp = 0.0

    def record_success(self) -> None:
        self.failures = 0
        self.state = "CLOSED"

    def record_failure(self, current_time: float) -> None:
        self.failures += 1
        if self.failures >= self.failure_threshold:
            self.state = "OPEN"
            self.last_failure_timestamp = current_time

    def allow_request(self, current_time: float) -> bool:
        if self.state == "CLOSED":
            return True
        if self.state == "OPEN":
            if current_time - self.last_failure_timestamp > self.open_s:
                self.state = "HALF-OPEN"
                return True
            return False
        if self.state == "HALF-OPEN":
            return True
        return True

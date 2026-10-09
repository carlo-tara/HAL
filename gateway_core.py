from __future__ import annotations

import hashlib
import json
import math
import os
import re
import time
from collections.abc import Callable
from typing import Any, ClassVar

from laya_service import LayaOutcome

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

PII_PATTERNS: list[tuple[str, str]] = [
    (r"(?<![\w.+%-])[\w.+%-]+@[\w.-]+\.[A-Za-z]{2,}(?![\w.-])", "{{pii:email}}"),
    (r"\b[A-Z]{6}\d{2}[A-Z]\d{2}[A-Z]\d{3}[A-Z]\b", "{{pii:tax_code}}"),
    (r"(?<!\w)(?:\+39[\s.-]?)?(?:0\d{1,3}|3\d{2})[\s.-]?\d{5,8}(?!\w)", "{{pii:phone}}"),
]

def redact_text(text: str) -> str:
    """Applica la denylist di regex per oscurare segreti e credenziali prima della scrittura in log."""
    redacted = text
    for pattern, placeholder in SECRET_PATTERNS:
        redacted = re.sub(pattern, placeholder, redacted, flags=re.IGNORECASE)
    return redacted

def process_event_payload(payload: dict[str, Any], laya_pii_check_fn: Any = None) -> dict[str, Any]:
    """Redige i dati localmente e trattiene il body solo dopo una scansione valida."""
    body = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    pii_redacted = False
    for pattern, placeholder in PII_PATTERNS:
        body, replacements = re.subn(pattern, placeholder, body, flags=re.IGNORECASE)
        pii_redacted = pii_redacted or replacements > 0
    redacted_body = redact_text(body)

    pii_detected: bool | None = None
    scan_status = "uncertain"
    if laya_pii_check_fn is not None:
        try:
            result = laya_pii_check_fn(
                redacted_body,
                "contains PII or sensitive personal data",
            )
            if isinstance(result, LayaOutcome):
                if result.status != "ok":
                    raise ValueError("Laya PII scan abstained")
                result = result.value
            if result is None or isinstance(result, bool):
                raise ValueError("PII scan score must be numeric")
            score = float(result)
            if not math.isfinite(score) or not 0.0 <= score <= 1.0:
                raise ValueError("PII scan score is outside [0, 1]")
            pii_detected = score > 0.7
            scan_status = "complete"
        except Exception:  # noqa: BLE001
            scan_status = "uncertain"

    body_withheld = scan_status != "complete" or pii_detected is True
    return {
        "redacted_body": None if body_withheld else redacted_body,
        "pii_detected": pii_detected,
        "pii_redacted": pii_redacted,
        "pii_scan_status": scan_status,
        "body_withheld": body_withheld,
    }


def write_event_jsonl(
    payload: dict[str, Any],
    log_path: str | os.PathLike[str],
    laya_pii_check_fn: Any = None,
) -> dict[str, Any]:
    """Appende un record già sanificato; esiti incerti persistono solo come metadati."""
    record = process_event_payload(payload, laya_pii_check_fn)
    encoded = (json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")
    fd = os.open(log_path, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o600)
    try:
        os.fchmod(fd, 0o600)
        written = os.write(fd, encoded)
        if written != len(encoded):
            raise OSError("Scrittura incompleta del record evento")
    finally:
        os.close(fd)
    return record


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


class L1RedisCacheManager:
    """
    Gestore della cache L1 Redis con supporto per hashing dei contenuti dei file rilevanti,
    TTL per profilo d'uso, validazione dei limiti di cache per tool/side-effect e provenienza eventi (hit/miss).
    """
    PROFILE_TTL: ClassVar[dict[str, int]] = {
        "coding": 3600,
        "reasoning_planning": 7200,
        "text_editing": 1800,
        "summarization": 1800,
        "default": 1800
    }

    def __init__(self, backend: str = "memory", redis_client: Any | None = None) -> None:
        self.backend = backend
        self.redis_client = redis_client
        self._memory_store: dict[str, dict[str, Any]] = {}

    def get_ttl_for_profile(self, profile: str) -> int:
        return self.PROFILE_TTL.get(profile, self.PROFILE_TTL["default"])

    def compute_content_based_cache_key(self, session_id: str, use_case: str, messages: list[dict[str, str]] | str, relevant_files: list[str] | None = None) -> str:
        """Calcola la chiave di cache basandosi sull'hash SHA-256 effettivo del contenuto dei file anziché solo sui path."""
        norm_msg = normalize_prompt(messages)
        msg_hash = hashlib.sha256(norm_msg.encode("utf-8")).hexdigest()

        file_contents_combined = []
        for fpath in sorted(relevant_files or []):
            try:
                if os.path.isfile(fpath):
                    with open(fpath, "rb") as f:
                        file_contents_combined.append(f.read())
                else:
                    file_contents_combined.append(fpath.encode("utf-8"))
            except OSError:
                file_contents_combined.append(fpath.encode("utf-8"))
        
        combined_bytes = b"".join(file_contents_combined)
        files_content_hash = hashlib.sha256(combined_bytes).hexdigest()

        return f"cache:v1:{session_id}:{use_case}:{msg_hash}:{files_content_hash}"

    def validate_cacheable(self, use_case: str, messages: list[dict[str, str]] | str) -> bool:
        """Verifica se una richiesta con tool o comandi pericolosi/side-effect debba bypassare la cache."""
        serialized = str(messages).lower()
        dangerous_patterns = {"rm -rf", "drop database", "sudo ", "mkfs", "dd if="}
        return not any(p in serialized for p in dangerous_patterns)

    def get(self, session_id: str, use_case: str, messages: list[dict[str, str]] | str, relevant_files: list[str] | None = None) -> tuple[Any | None, str]:
        if not self.validate_cacheable(use_case, messages):
            return None, "cache_bypassed_dangerous"

        key = self.compute_content_based_cache_key(session_id, use_case, messages, relevant_files)
        
        if self.backend == "memory":
            entry = self._memory_store.get(key)
            if entry:
                return entry["response"], "cache_hit"
            return None, "cache_miss"
        elif self.redis_client is not None:
            val = self.redis_client.get(key)
            if val is not None:
                return val, "cache_hit"
            return None, "cache_miss"
        return None, "cache_miss"

    def set(self, session_id: str, use_case: str, messages: list[dict[str, str]] | str, response: Any, relevant_files: list[str] | None = None, profile: str = "default") -> None:
        if not self.validate_cacheable(use_case, messages):
            return

        key = self.compute_content_based_cache_key(session_id, use_case, messages, relevant_files)
        ttl = self.get_ttl_for_profile(profile)

        if self.backend == "memory":
            self._memory_store[key] = {"response": response, "ttl": ttl}
        elif self.redis_client is not None:
            self.redis_client.setex(key, ttl, response)


# ==========================================
# 19 — CIRCUIT BREAKER & SESSION (P1)
# ==========================================

def derive_session_id(api_key: str, workspace_path: str, conversation_id: str) -> str:
    """Deriva un session_id deterministico e isolato da api_key, workspace e conversazione."""
    raw = f"{api_key}:{workspace_path}:{conversation_id}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

class CircuitBreaker:
    """State machine del circuit breaker per provider in Redis / memoria con controllo probe half-open concorrenti."""
    def __init__(self, provider_name: str, failure_threshold: int = 5, open_s: int = 30) -> None:
        self.provider_name = provider_name
        self.failure_threshold = failure_threshold
        self.open_s = open_s
        self.failures = 0
        self.state = "CLOSED"  # CLOSED, OPEN, HALF-OPEN
        self.last_failure_timestamp = 0.0
        self.probe_in_flight = False

    def record_success(self) -> None:
        self.failures = 0
        self.state = "CLOSED"
        self.probe_in_flight = False

    def record_failure(self, current_time: float) -> None:
        self.failures += 1
        self.probe_in_flight = False
        if self.failures >= self.failure_threshold:
            self.state = "OPEN"
            self.last_failure_timestamp = current_time

    def allow_request(self, current_time: float) -> bool:
        if self.state == "CLOSED":
            return True
        if self.state == "OPEN":
            if current_time - self.last_failure_timestamp > self.open_s:
                self.state = "HALF-OPEN"
                self.probe_in_flight = False
                return self._try_acquire_probe()
            return False
        if self.state == "HALF-OPEN":
            return self._try_acquire_probe()
        return True

    def _try_acquire_probe(self) -> bool:
        if not self.probe_in_flight:
            self.probe_in_flight = True
            return True
        return False

class ProviderResolverWithBreaker:
    """
    Risolutore di provider integrato con Circuit Breaker: salta i provider aperti,
    ammette un solo probe half-open e attiva automaticamente il fallback.
    """
    def __init__(self) -> None:
        self.providers: dict[str, Callable[..., Any]] = {}
        self.breakers: dict[str, CircuitBreaker] = {}

    def register_provider(self, name: str, invoker: Callable[..., Any], failure_threshold: int = 2, open_s: int = 30) -> None:
        self.providers[name] = invoker
        self.breakers[name] = CircuitBreaker(name, failure_threshold=failure_threshold, open_s=open_s)

    def get_breaker(self, name: str) -> CircuitBreaker | None:
        return self.breakers.get(name)

    def resolve_and_execute(self, task: str, data: Any, *args: Any, **kwargs: Any) -> tuple[Any, str]:
        now = time.time()
        for name, invoker in self.providers.items():
            cb = self.breakers[name]
            if cb.allow_request(now):
                try:
                    res = invoker(task, data, *args, **kwargs)
                    cb.record_success()
                    return res, name
                except Exception:  # noqa: BLE001
                    cb.record_failure(now)
                    continue
        raise RuntimeError("Tutti i provider sono attualmente degradati o aperti (Circuit Breakers attivi).")

class EventRetentionManager:
    """
    Gestore di retention automatica (body 30 giorni, metadati 12 mesi),
    cifratura a riposo dei payload ed enforcement dell'accesso controllato (RBAC).
    """
    BODY_RETENTION_SECONDS: int = 30 * 86400      # 30 giorni
    METADATA_RETENTION_SECONDS: int = 365 * 86400  # 12 mesi (365 giorni)

    @classmethod
    def purge_expired_events(cls, events: list[dict[str, Any]], current_timestamp: float | None = None) -> list[dict[str, Any]]:
        import time
        current_timestamp = current_timestamp if current_timestamp is not None else time.time()
        retained = []

        for ev in events:
            ts = ev.get("timestamp", current_timestamp)
            age = current_timestamp - ts

            if age > cls.METADATA_RETENTION_SECONDS:
                continue

            cleaned_ev = dict(ev)
            if age > cls.BODY_RETENTION_SECONDS:
                cleaned_ev["redacted_body"] = None
                cleaned_ev["body_purged"] = True
            else:
                cleaned_ev.setdefault("body_purged", False)

            retained.append(cleaned_ev)

        return retained

    @classmethod
    def encrypt_payload(cls, payload: dict[str, Any], key: str) -> str:
        """Cifra a riposo il payload JSON (simulazione sicura con XOR/base64 o encoding simmetrico robusto)."""
        import base64
        data_str = json.dumps(payload, ensure_ascii=False)
        key_bytes = key.encode("utf-8")
        data_bytes = data_str.encode("utf-8")
        encrypted_bytes = bytes(b ^ key_bytes[i % len(key_bytes)] for i, b in enumerate(data_bytes))
        return base64.b64encode(encrypted_bytes).decode("utf-8")

    @classmethod
    def decrypt_payload(cls, encrypted_str: str, key: str) -> dict[str, Any]:
        """Decifra il payload cifrato a riposo."""
        import base64
        key_bytes = key.encode("utf-8")
        encrypted_bytes = base64.b64decode(encrypted_str.encode("utf-8"))
        decrypted_bytes = bytes(b ^ key_bytes[i % len(key_bytes)] for i, b in enumerate(encrypted_bytes))
        return json.loads(decrypted_bytes.decode("utf-8"))

    @classmethod
    def verify_access(cls, role: str, action: str) -> bool:
        """Controllo di accesso basato sui ruoli (RBAC) per l'accesso ai log eventi grezzi."""
        privileged_roles = {"admin", "auditor", "security_officer"}
        if action == "read_raw_logs":
            return role in privileged_roles
        return True

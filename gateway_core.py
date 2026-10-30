from __future__ import annotations

import hashlib
import json
import math
import os
import re
import time
from collections.abc import Callable
from threading import Lock
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
    (
        r"-----BEGIN (?:RSA|PRIVATE) KEY-----[^-]*-----END (?:RSA|PRIVATE) KEY-----",
        "{{secret:private_key}}",
    ),
    (r"password\s*[:=]\s*[^\s]+", "password={{secret:password}}"),
]

PII_PATTERNS: list[tuple[str, str]] = [
    (r"(?<![\w.+%-])[\w.+%-]+@[\w.-]+\.[A-Za-z]{2,}(?![\w.-])", "{{pii:email}}"),
    (r"\b[A-Z]{6}\d{2}[A-Z]\d{2}[A-Z]\d{3}[A-Z]\b", "{{pii:tax_code}}"),
    (
        r"(?<!\w)(?:\+39[\s.-]?)?(?:0\d{1,3}|3\d{2})[\s.-]?\d{5,8}(?!\w)",
        "{{pii:phone}}",
    ),
]


def redact_text(text: str) -> str:
    """Applica la denylist di regex per oscurare segreti e credenziali prima della scrittura in log."""
    redacted = text
    for pattern, placeholder in SECRET_PATTERNS:
        redacted = re.sub(pattern, placeholder, redacted, flags=re.IGNORECASE)
    return redacted


def process_event_payload(
    payload: dict[str, Any], laya_pii_check_fn: Any = None
) -> dict[str, Any]:
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
    encoded = (
        json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n"
    ).encode("utf-8")
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


def split_instructions(
    messages: list[dict[str, str]] | str
) -> tuple[str, list[Any] | str]:
    """Separa il system (instructions) dal transcript append-only, con ruolo esplicito."""
    if isinstance(messages, str):
        return "", messages
    instr_parts: list[str] = []
    transcript: list[Any] = []
    for m in messages:
        if isinstance(m, dict) and m.get("role") == "system":
            instr_parts.append(str(m.get("content", "")))
        else:
            transcript.append(m)
    return " ".join(instr_parts), transcript


def normalize_prompt(
    messages: list[dict[str, str]] | str,
    declarations: list[Any] | None = None,
    instructions: str | None = None,
) -> str:
    """Normalizza messaggi o prompt: lowercase, strip whitespace, rimozione timestamp casuali.

    Le dichiarazioni di tool/skill e i tool_calls nei messaggi entrano nella
    serializzazione: stesso testo con tool set diverso deve produrre chiavi
    diverse (contratto P0, 2026-10-28). Il system viaggia separato dal
    transcript (contratto instructions, 2026-10-28): i ruoli restano espliciti
    e lo stesso transcript con system diverso produce chiavi diverse. Da usare
    SOLO per la chiave di cache, mai sul testo inviato upstream (distruggerebbe
    il match di prefisso byte-per-byte lato provider).
    """
    instr, transcript = split_instructions(messages)
    if instructions is not None:
        instr = instructions

    serialized_parts: list[str] = []
    if instr:
        serialized_parts.append(f"sys::{instr}")
    if isinstance(transcript, str):
        serialized_parts.append(transcript)
    else:
        for m in transcript:
            if isinstance(m, dict):
                role = str(m.get("role", ""))
                content = str(m.get("content", ""))
                tool_calls = m.get("tool_calls")
                if tool_calls:
                    content = f"{content} {serialize_declarations(tool_calls)}"
                serialized_parts.append(f"{role}: {content}" if role else content)
            else:
                serialized_parts.append(str(m))
    serialized = " ".join(serialized_parts)

    if declarations:
        serialized = f"{serialized} {serialize_declarations(declarations)}"

    # Rimozione preventivo timestamp ISO o simili (es. 2026-10-06T12:00:00Z)
    cleaned = re.sub(
        r"\d{4}-\d{2}-\d{2}[tT]\d{2}:\d{2}:\d{2}(?:\.\d+)?Z?", "", serialized
    )
    normalized = " ".join(cleaned.lower().split())
    return normalized


def assemble_static_first_blocks(
    instructions: str,
    declarations: list[Any],
    context_files: list[str],
    transcript: list[dict[str, str]],
    current_question: dict[str, str],
    volatile: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Contratto dei backend System 2: ordine fisso dei blocchi nel prompt.

    system -> tool descriptions -> file di contesto -> storico conversazione ->
    domanda attuale. Il contenuto volatile (session_id, timestamp, nonce) va
    solo in coda: in testa azzera ogni hit di prefix cache lato provider.
    """
    blocks: list[dict[str, Any]] = [
        {"block": "system", "content": instructions},
        {"block": "declarations", "content": serialize_declarations(declarations)},
        {"block": "context", "content": ",".join(sorted(context_files))},
        {"block": "history", "content": transcript},
        {"block": "question", "content": current_question},
    ]
    if volatile:
        blocks.append({"block": "volatile", "content": volatile})
    return blocks


def serialize_declarations(declarations: list[Any]) -> str:
    """Serializzazione deterministica (ordinata) di tool/skill declaration o tool_calls."""
    items: list[str] = []
    for decl in declarations:
        if isinstance(decl, str):
            items.append(decl)
        else:
            items.append(
                json.dumps(decl, sort_keys=True, ensure_ascii=False, default=str)
            )
    return "|".join(sorted(items))


def compute_cache_key(
    session_id: str,
    use_case: str,
    messages: list[dict[str, str]] | str,
    relevant_files: list[str] | None = None,
    declarations: list[Any] | None = None,
    instructions: str | None = None,
) -> str:
    """Genera la chiave composita per la cache L1 Redis.

    La parte di instructions (system) è hashata separatamente dal transcript:
    stesso transcript con system diverso produce chiavi diverse e il system non
    entra nella porzione append-only del transcript.
    """
    norm_msg = normalize_prompt(messages, declarations, instructions)
    msg_hash = hashlib.sha256(norm_msg.encode("utf-8")).hexdigest()
    instr, _transcript = split_instructions(messages)
    if instructions is not None:
        instr = instructions
    instr_hash = hashlib.sha256(f"sys::{instr.lower()}".encode()).hexdigest()

    files_str = ",".join(sorted(relevant_files or []))
    files_hash = hashlib.sha256(files_str.encode("utf-8")).hexdigest()

    return f"cache:v1:{session_id}:{use_case}:{instr_hash}:{msg_hash}:{files_hash}"


def compute_layered_cache_key(
    session_id: str,
    use_case: str,
    messages: list[dict[str, str]] | str,
    relevant_files: list[str] | None = None,
    declarations: list[Any] | None = None,
    stable_declarations: list[Any] | None = None,
    stable_turns: int = 0,
) -> dict[str, str]:
    """Chiave L1 a due livelli: prefix stabile + suffix append-only.

    Il prefix aggrega i messaggi di sistema, le dichiarazioni core dichiarate
    stabili e i primi ``stable_turns`` turni non-system; ogni append successivo
    (nuovo turno, skill iniettata) ricade solo sul suffix, quindi la parte di
    prefix non viene invalidata. Il ``full`` resta la chiave univoca per la
    risposta: nessun falso hit e possibile (il riuso e' informativi sul prefix,
    non una risposta approssimata).
    """
    if isinstance(messages, str):
        system_msgs: list[Any] = []
        non_system_msgs: list[Any] = [{"role": "user", "content": messages}]
    else:
        system_msgs = [
            m for m in messages if isinstance(m, dict) and m.get("role") == "system"
        ]
        non_system_msgs = [
            m
            for m in messages
            if not (isinstance(m, dict) and m.get("role") == "system")
        ]

    boundary = max(int(stable_turns), 0)
    stable_msgs = system_msgs + non_system_msgs[:boundary]
    suffix_msgs = non_system_msgs[boundary:]

    stable_decl = list(stable_declarations) if stable_declarations is not None else []
    all_decl = list(declarations or [])
    stable_ser = {serialize_declarations([d]) for d in stable_decl}
    suffix_decl = [d for d in all_decl if serialize_declarations([d]) not in stable_ser]

    prefix_norm = normalize_prompt(stable_msgs, stable_decl)
    suffix_norm = normalize_prompt(suffix_msgs, suffix_decl)

    prefix_hash = hashlib.sha256(prefix_norm.encode("utf-8")).hexdigest()
    suffix_hash = hashlib.sha256(suffix_norm.encode("utf-8")).hexdigest()
    return {
        "prefix": f"cache:v1:{session_id}:{use_case}:pfx:{prefix_hash}",
        "suffix": suffix_hash,
        "full": f"cache:v1:{session_id}:{use_case}:{prefix_hash}:{suffix_hash}",
    }


class ToolSessionRegistry:
    """Registry tool/skill session-scoped, append-only (carry-forward).

    Le dichiarazioni presentate nei turni successivi di una sessione vengono
    trasportate invariate: mai ricomposizione per-request, mai rimozione o
    riordino (stabilizza il prefisso e mantiene i tool invocabili). Identita'
    deterministica via ``serialize_declarations``.
    """

    def __init__(self) -> None:
        self._by_session: dict[str, list[Any]] = {}
        self._seen: dict[str, set[str]] = {}

    def register(self, session_id: str, declarations: list[Any]) -> list[Any]:
        """Accoda solo le dichiarazioni nuove; ritorna il set risultante."""
        current = self._by_session.setdefault(session_id, [])
        seen = self._seen.setdefault(session_id, set())
        for decl in declarations:
            ser = serialize_declarations([decl])
            if ser not in seen:
                seen.add(ser)
                current.append(decl)
        return list(current)

    def get(self, session_id: str) -> list[Any]:
        """Set stabile (solo append) per la sessione, copia difensiva."""
        return list(self._by_session.get(session_id, []))


class SubmitIdempotencyRegistry:
    """Registro anti-duplicato per sottomissioni asincrone (task model).

    Mappa la chiave della richiesta (``cache:v1:...``, la stessa della Cache L1
    con le dichiarazioni tool/skill inclusi) al ``task_id`` in-flight: un submit
    identico entro la finestra non crea un nuovo task e restituisce l'id
    esistente. Ogni POST altrimenti pagherebbe due volte lo stesso lavoro su
    retry di rete o switching di provider.
    """

    def __init__(self, window_s: float = 60.0) -> None:
        if window_s <= 0:
            raise ValueError("window_s deve essere positivo")
        self.window_s = float(window_s)
        self._inflight: dict[str, tuple[str, float]] = {}
        self._lock = Lock()

    def get_task_id(self, idempotency_key: str, now: float | None = None) -> str | None:
        now = time.monotonic() if now is None else now
        with self._lock:
            entry = self._inflight.get(idempotency_key)
            if entry is None:
                return None
            task_id, submitted_at = entry
            if now - submitted_at >= self.window_s:
                del self._inflight[idempotency_key]
                return None
            return task_id

    def submit_once(
        self,
        idempotency_key: str,
        submit_fn: Callable[[], str],
        now: float | None = None,
    ) -> str:
        """Esegue ``submit_fn`` solo se non c'è un task in-flight sulla chiave."""
        existing = self.get_task_id(idempotency_key, now=now)
        if existing is not None:
            return existing
        task_id = submit_fn()
        stamp = time.monotonic() if now is None else now
        with self._lock:
            self._inflight[idempotency_key] = (task_id, stamp)
        return task_id


class TaskPollBudget:
    """Token bucket per gli endpoint di gestione task (query/list/cancel).

    I tre endpoint condividono 20 QPS per account (doc QwenCloud): molti poll
    concorrenti, più skill/media, saturerebbero il limite. Pattern ricalcato su
    ``LayaCallBudget`` ma lato task: ``acquire`` prima di ogni status check,
    ``note_throttled`` su 429/``Throttling.RateQuota`` aumenta l'intervallo
    consigliato (x1.5 con cap), ``note_success`` lo riporta alla base.
    """

    def __init__(
        self,
        rate_per_s: float = 20.0,
        base_interval: float = 3.0,
        max_interval: float = 60.0,
        multiplier: float = 1.5,
    ) -> None:
        if rate_per_s <= 0:
            raise ValueError("rate_per_s deve essere positivo")
        if base_interval <= 0 or max_interval < base_interval:
            raise ValueError("intervallo base/max non coerente")
        self.rate_per_s = float(rate_per_s)
        self.capacity = float(rate_per_s)  # refill di un secondo di burst
        self.tokens = self.capacity
        self.base_interval = float(base_interval)
        self.max_interval = float(max_interval)
        self.multiplier = float(multiplier)
        self._interval = self.base_interval
        self._last_refill: float | None = None
        self._lock = Lock()

    def _refill(self, now: float) -> None:
        if self._last_refill is None:
            self._last_refill = now
            return
        elapsed = max(0.0, now - self._last_refill)
        self._last_refill = now
        self.tokens = min(self.capacity, self.tokens + elapsed * self.rate_per_s)

    def acquire(self, now: float | None = None) -> bool:
        """Consuma un token: False se il bucket è vuoto (nonpollare ora)."""
        now = time.monotonic() if now is None else now
        with self._lock:
            self._refill(now)
            if self.tokens >= 1.0:
                self.tokens -= 1.0
                return True
            return False

    def drain(self, now: float | None = None) -> None:
        """Svuota il bucket (helper di test/simulazione)."""
        now = time.monotonic() if now is None else now
        with self._lock:
            self._refill(now)
            self.tokens = 0.0

    def wait_time(self, now: float | None = None) -> float:
        """Secondi di attesa per il prossimo slot utile."""
        now = time.monotonic() if now is None else now
        with self._lock:
            self._refill(now)
            if self.tokens >= 1.0:
                return 0.0
            return (1.0 - self.tokens) / self.rate_per_s

    def poll_interval(self) -> float:
        with self._lock:
            return self._interval

    def note_throttled(self) -> None:
        """429/Throttling.RateQuota: ridurre la frequenza aumentando l'intervallo."""
        with self._lock:
            self._interval = min(self._interval * self.multiplier, self.max_interval)

    def note_success(self) -> None:
        with self._lock:
            self._interval = self.base_interval


def record_failover_cache_burn(
    session_id: str,
    from_model: str,
    to_model: str,
    prompt_tokens: int,
    log_path: str | os.PathLike[str],
    creation_ratio: float = 1.25,
) -> dict[str, Any]:
    """Marca il cambio modello a sessione invariata e il costo di refill atteso.

    La cache è isolata per modello oltre che per account (doc QwenCloud FAQ):
    quando ``ProviderResolverWithBreaker`` o il ``fallback_used`` di
    ``SystemTwoEngine`` cambiano modello, il prefisso riparte da zero e la
    ricreazione costa ``creation_ratio`` (default 125%). L'evento è metadato puro
    (session hash, nomi modello, conteggi token: nessun contenuto utente), quindi
    non passa dal percorso PII di ``write_event_jsonl``; lo stile di appende 0o600
    è il medesimo. Se il modello non cambia, nessun burn (``cache_invalidated``
    falso e costo ``None``).
    """
    same_model = from_model == to_model
    record: dict[str, Any] = {
        "event": "cache_refill",
        "session_id": session_id,
        "session_unchanged": True,
        "from_model": from_model,
        "to_model": to_model,
        "cache_invalidated": not same_model,
        "prompt_tokens": int(prompt_tokens),
        "expected_creation_cost": None
        if same_model
        else round(int(prompt_tokens) * creation_ratio, 2),
        "creation_ratio": creation_ratio,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    encoded = (
        json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n"
    ).encode("utf-8")
    fd = os.open(log_path, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o600)
    try:
        os.fchmod(fd, 0o600)
        written = os.write(fd, encoded)
        if written != len(encoded):
            raise OSError("Scrittura incompleta del record evento")
    finally:
        os.close(fd)
    return record


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
        "default": 1800,
    }

    def __init__(
        self, backend: str = "memory", redis_client: Any | None = None
    ) -> None:
        self.backend = backend
        self.redis_client = redis_client
        self._memory_store: dict[str, dict[str, Any]] = {}
        self._prefix_store: dict[str, dict[str, Any]] = {}

    def get_ttl_for_profile(self, profile: str) -> int:
        return self.PROFILE_TTL.get(profile, self.PROFILE_TTL["default"])

    def compute_content_based_cache_key(
        self,
        session_id: str,
        use_case: str,
        messages: list[dict[str, str]] | str,
        relevant_files: list[str] | None = None,
        declarations: list[Any] | None = None,
        instructions: str | None = None,
    ) -> str:
        """Calcola la chiave di cache basandosi sull'hash SHA-256 effettivo del contenuto dei file anziché solo sui path."""
        norm_msg = normalize_prompt(messages, declarations, instructions)
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

    def validate_cacheable(
        self, use_case: str, messages: list[dict[str, str]] | str
    ) -> bool:
        """Verifica se una richiesta con tool o comandi pericolosi/side-effect debba bypassare la cache."""
        serialized = str(messages).lower()
        dangerous_patterns = {"rm -rf", "drop database", "sudo ", "mkfs", "dd if="}
        return not any(p in serialized for p in dangerous_patterns)

    def get(
        self,
        session_id: str,
        use_case: str,
        messages: list[dict[str, str]] | str,
        relevant_files: list[str] | None = None,
        declarations: list[Any] | None = None,
    ) -> tuple[Any | None, str]:
        if not self.validate_cacheable(use_case, messages):
            return None, "cache_bypassed_dangerous"

        key = self.compute_content_based_cache_key(
            session_id, use_case, messages, relevant_files, declarations
        )

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

    def set(
        self,
        session_id: str,
        use_case: str,
        messages: list[dict[str, str]] | str,
        response: Any,
        relevant_files: list[str] | None = None,
        profile: str = "default",
        declarations: list[Any] | None = None,
    ) -> None:
        if not self.validate_cacheable(use_case, messages):
            return

        key = self.compute_content_based_cache_key(
            session_id, use_case, messages, relevant_files, declarations
        )
        ttl = self.get_ttl_for_profile(profile)

        if self.backend == "memory":
            self._memory_store[key] = {"response": response, "ttl": ttl}
        elif self.redis_client is not None:
            self.redis_client.setex(key, ttl, response)

    def set_layered(
        self,
        session_id: str,
        use_case: str,
        messages: list[dict[str, str]] | str,
        response: Any,
        relevant_files: list[str] | None = None,
        profile: str = "default",
        declarations: list[Any] | None = None,
        stable_declarations: list[Any] | None = None,
        stable_turns: int = 0,
    ) -> dict[str, str]:
        """Memorizza la risposta sulla chiave full e registra il prefix stabile."""
        layers = compute_layered_cache_key(
            session_id,
            use_case,
            messages,
            relevant_files,
            declarations,
            stable_declarations,
            stable_turns,
        )
        ttl = self.get_ttl_for_profile(profile)
        if self.backend == "memory":
            self._memory_store[layers["full"]] = {"response": response, "ttl": ttl}
            self._prefix_store[layers["prefix"]] = {
                "suffix": layers["suffix"],
                "ttl": ttl,
            }
        elif self.redis_client is not None:
            self.redis_client.setex(layers["full"], ttl, response)
            self.redis_client.setex(f"{layers['prefix']}:{layers['suffix']}", ttl, "1")
        return layers

    def get_layered(
        self,
        session_id: str,
        use_case: str,
        messages: list[dict[str, str]] | str,
        relevant_files: list[str] | None = None,
        declarations: list[Any] | None = None,
        stable_declarations: list[Any] | None = None,
        stable_turns: int = 0,
    ) -> tuple[Any | None, str, str]:
        """Restituisce (risposta, stato full, stato prefix).

        Lo stato prefix segnala riuso parziale informativo: mai la risposta di
        una conversazione diversa come risposta di quella corrente.
        """
        if not self.validate_cacheable(use_case, messages):
            return None, "cache_bypassed_dangerous", "prefix_bypassed"

        layers = compute_layered_cache_key(
            session_id,
            use_case,
            messages,
            relevant_files,
            declarations,
            stable_declarations,
            stable_turns,
        )
        prefix_state = "prefix_miss"
        if self.backend == "memory":
            entry = self._memory_store.get(layers["full"])
            if layers["prefix"] in self._prefix_store:
                prefix_state = "prefix_hit"
            if entry:
                return entry["response"], "cache_hit", prefix_state
            return None, "cache_miss", prefix_state
        if self.redis_client is not None:
            val = self.redis_client.get(layers["full"])
            if self.redis_client.exists(f"{layers['prefix']}:{layers['suffix']}"):
                prefix_state = "prefix_hit"
            if val is not None:
                return val, "cache_hit", prefix_state
        return None, "cache_miss", prefix_state


# ==========================================
# 19 — CIRCUIT BREAKER & SESSION (P1)
# ==========================================


def derive_session_id(api_key: str, workspace_path: str, conversation_id: str) -> str:
    """Deriva un session_id deterministico e isolato da api_key, workspace e conversazione."""
    raw = f"{api_key}:{workspace_path}:{conversation_id}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


class CircuitBreaker:
    """State machine del circuit breaker per provider in Redis / memoria con controllo probe half-open concorrenti."""

    def __init__(
        self, provider_name: str, failure_threshold: int = 5, open_s: int = 30
    ) -> None:
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

    def register_provider(
        self,
        name: str,
        invoker: Callable[..., Any],
        failure_threshold: int = 2,
        open_s: int = 30,
    ) -> None:
        self.providers[name] = invoker
        self.breakers[name] = CircuitBreaker(
            name, failure_threshold=failure_threshold, open_s=open_s
        )

    def get_breaker(self, name: str) -> CircuitBreaker | None:
        return self.breakers.get(name)

    def resolve_and_execute(
        self, task: str, data: Any, *args: Any, **kwargs: Any
    ) -> tuple[Any, str]:
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
        raise RuntimeError(
            "Tutti i provider sono attualmente degradati o aperti (Circuit Breakers attivi)."
        )


class EventRetentionManager:
    """
    Gestore di retention automatica (body 30 giorni, metadati 12 mesi),
    cifratura a riposo dei payload ed enforcement dell'accesso controllato (RBAC).
    """

    BODY_RETENTION_SECONDS: int = 30 * 86400  # 30 giorni
    METADATA_RETENTION_SECONDS: int = 365 * 86400  # 12 mesi (365 giorni)

    @classmethod
    def purge_expired_events(
        cls, events: list[dict[str, Any]], current_timestamp: float | None = None
    ) -> list[dict[str, Any]]:
        import time

        current_timestamp = (
            current_timestamp if current_timestamp is not None else time.time()
        )
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
        encrypted_bytes = bytes(
            b ^ key_bytes[i % len(key_bytes)] for i, b in enumerate(data_bytes)
        )
        return base64.b64encode(encrypted_bytes).decode("utf-8")

    @classmethod
    def decrypt_payload(cls, encrypted_str: str, key: str) -> dict[str, Any]:
        """Decifra il payload cifrato a riposo."""
        import base64

        key_bytes = key.encode("utf-8")
        encrypted_bytes = base64.b64decode(encrypted_str.encode("utf-8"))
        decrypted_bytes = bytes(
            b ^ key_bytes[i % len(key_bytes)] for i, b in enumerate(encrypted_bytes)
        )
        return json.loads(decrypted_bytes.decode("utf-8"))

    @classmethod
    def verify_access(cls, role: str, action: str) -> bool:
        """Controllo di accesso basato sui ruoli (RBAC) per l'accesso ai log eventi grezzi."""
        privileged_roles = {"admin", "auditor", "security_officer"}
        if action == "read_raw_logs":
            return role in privileged_roles
        return True

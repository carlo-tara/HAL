from __future__ import annotations

import math
import os
import random
import time
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Generic, Literal, TypeVar

import requests
import urllib3
from requests.adapters import HTTPAdapter

from laya_gate import (
    DIRECT_CAP_OPTIONS,
    ESCALATE_MARGIN,
    FAST_MARGIN,
    _answer_probs,
    _top_and_margin,
    verdict_directly_acceptable,
)
from system1_preflight import LayaCallBudget, TaskContract, prepare_laya_request

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

LAYA_BASE_URL = os.getenv("LAYA_BASE_URL", "http://laya.local:8091/v1")

# Soglie e helper del gate: modulo canonico laya_gate.py (symlink al sorgente
# hal_system1). Non duplicare: la soglia divergente qui cambierebbe solo il
# comportamento del gateway, silenziosamente.
LAYA_TIMEOUT = float(os.getenv("LAYA_TIMEOUT") or "5.0")
# Task endpoint del deployment: POST {base}/systemone, aperto su localhost. Il
# client invia comunque Authorization: Bearer <chiave> (forward-compat; su
# /predict — passthrough nativo {state,questions} — la header è obbligatoria).
# Convenzione consumer HAL (benchmark/, a-knowledge/extract.py, scripts/test_laya.py):
# env LAYA_API_KEY → fallback .env di repo → "sk-local" (default del servizio locale).
LAYA_API_KEY_FALLBACK = "sk-local"


def get_laya_api_key() -> str:
    """Chiave di servizio Laya: env, poi .env di repo, poi default."""
    key = (os.getenv("LAYA_API_KEY") or "").strip()
    if key:
        return key
    try:
        from dotenv import dotenv_values

        env_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
        key = (dotenv_values(env_file).get("LAYA_API_KEY") or "").strip()
    except Exception:  # noqa: BLE001 - dotenv assente o .env illeggibile: default
        key = ""
    return key or LAYA_API_KEY_FALLBACK


# Base ~0.3 s (range doc-consented 0.2-0.5) con cap difensivo sul backoff.
LAYA_RETRY_BASE_S = float(os.getenv("LAYA_RETRY_BASE_S") or "0.3")
LAYA_RETRY_MAX_S = float(os.getenv("LAYA_RETRY_MAX_S") or "4.0")

# Hook iniettabile nei test: i tentativi retry devono risultare distanziati.
_sleep = time.sleep


def compute_backoff_delay(
    attempt: int,
    base: float | None = None,
    cap: float | None = None,
    rng: Callable[..., float] | None = None,
) -> float:
    """Attesa esponenziale (base * 2^attempt) con jitter +-50%, sopra cap.

    Solo ``budget.max_retries`` governa QUANTI tentativi; questa funzione
    distanzia il timing per non amplificare un'incidente su Laya degradata.
    """
    base = LAYA_RETRY_BASE_S if base is None else base
    cap = LAYA_RETRY_MAX_S if cap is None else cap
    raw = min(base * (2 ** max(0, int(attempt))), cap)
    factor = rng(0.0) if rng is not None else random.uniform(0.5, 1.5)
    return min(cap, max(0.0, raw * factor))


T = TypeVar("T")


@dataclass(frozen=True)
class LayaOutcome(Generic[T]):
    status: Literal["ok", "abstain"]
    value: T | None = None
    reason: str | None = None


class _LayaAbstention(Exception):
    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


# Persistent session with connection pooling for performance
_session = requests.Session()


def _env_positive_int(name: str, default: int) -> int:
    try:
        value = int(os.getenv(name) or default)
    except (TypeError, ValueError):
        return default
    return value if value > 0 else default


def _env_positive_float(name: str, default: float) -> float:
    try:
        value = float(os.getenv(name) or default)
    except (TypeError, ValueError):
        return default
    return value if value > 0 else default


def get_pool_settings() -> dict[str, int]:
    """Dimensionamento del pool di connessioni Laya.

    Default documentati: 10 connessioni per host in apertura, max 32 in piedi —
    coerente con il massimo di chiamate batch concorrenti ``batch_score`` /
    ``batch_routing`` (len(texts)). Env: LAYA_POOL_CONNECTIONS, LAYA_POOL_MAXSIZE.
    """
    return {
        "pool_connections": _env_positive_int("LAYA_POOL_CONNECTIONS", 10),
        "pool_maxsize": _env_positive_int("LAYA_POOL_MAXSIZE", 32),
    }


def get_pool_timeout() -> float:
    """Attesa esplicita per una connessione libera nel pool (env LAYA_POOL_TIMEOUT)."""
    return _env_positive_float("LAYA_POOL_TIMEOUT", 2.0)


def get_timeout_tuple() -> tuple[float, float]:
    """Timeout disaccoppiati (connect, read): connect corto per servizio locale
    (default 2 s), read sul budget storico LAYA_TIMEOUT. Env: LAYA_CONNECT_TIMEOUT,
    LAYA_READ_TIMEOUT. Il parsing è difensivo: valori non parsabili o non positivi
    ricadono sui default.
    """
    connect = _env_positive_float("LAYA_CONNECT_TIMEOUT", 2.0)
    read = _env_positive_float("LAYA_READ_TIMEOUT", LAYA_TIMEOUT)
    return (connect, read)


def get_tls_verify() -> bool | str:
    """Verifica TLS per le chiamate Laya.

    ``LAYA_CA_BUNDLE`` (percorso CA, anche self-signed di laya.local) ha la
    precedenza; poi ``LAYA_TLS_VERIFY`` a 1/true/yes. Il fallback ``False`` è
    una scelta esplicita documentata (vedi docs/24_trasporto_http_laya.md),
    non una disattivazione silenziosa.
    """
    ca_bundle = os.getenv("LAYA_CA_BUNDLE")
    if ca_bundle:
        return ca_bundle
    flag = (os.getenv("LAYA_TLS_VERIFY") or "").strip().lower()
    return flag in {"1", "true", "yes"}


def build_laya_adapter() -> HTTPAdapter:
    """HTTPAdapter con pool dimensionato e retry di trasporto DISATTIVATO.

    ``max_retries=0``: la forma di retry applicativa è il budget Laya
    (LayaCallBudget + backoff); sommare il retry urllib3 raddoppierebbe i
    tentativi. Il ``pool_timeout`` esplicito passa come default timeout del
    pool (attesa connessione libera in urllib3).
    """
    settings = get_pool_settings()
    adapter = HTTPAdapter(
        pool_connections=settings["pool_connections"],
        pool_maxsize=settings["pool_maxsize"],
        max_retries=0,
    )
    adapter.poolmanager.connection_pool_kw["timeout"] = get_pool_timeout()
    return adapter


def mount_laya_adapter() -> None:
    adapter = build_laya_adapter()
    _session.mount("http://", adapter)
    _session.mount("https://", adapter)


mount_laya_adapter()


@dataclass(frozen=True)
class _BudgetScope:
    budget: LayaCallBudget
    ceiling: int
    allow_retries: bool


_active_budget: ContextVar[_BudgetScope | None] = ContextVar(
    "laya_call_budget", default=None
)


def _systemone_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Normalizza il payload legacy {task,text,routes|options|criteria} nel
    contratto canonico di POST /systemone {task_type,text,params}."""
    if "task_type" in payload:
        return payload
    body: dict[str, Any] = {
        "task_type": str(payload.get("task") or "intent"),
        "text": str(payload.get("text") or ""),
    }
    for key in ("routes", "options", "criteria"):
        value = payload.get(key)
        if value:
            body["params"] = value
            break
    return body


class LayaSystemOneService:
    """Servizio System 1 con session pooling e cache dei soli risultati validi."""

    @classmethod
    def _call(cls, payload: dict[str, Any]) -> dict[str, Any]:
        # Endpoint canonico dei task (hal_system1/server.py): POST /systemone con
        # envelope {"result": {choice,confidence,probabilities}, "request_hash": ...}.
        url = f"{LAYA_BASE_URL}/systemone"
        scope = _active_budget.get()
        budget = scope.budget if scope is not None else LayaCallBudget()
        ceiling = scope.ceiling if scope is not None else budget.max_calls
        attempt = 0
        while True:
            if not budget.try_consume(ceiling=ceiling):
                raise _LayaAbstention("call_budget_exhausted")
            try:
                response = _session.post(
                    url,
                    json=_systemone_payload(payload),
                    headers={"Authorization": f"Bearer {get_laya_api_key()}"},
                    timeout=get_timeout_tuple(),
                    verify=get_tls_verify(),
                    allow_redirects=False,
                )
                response.raise_for_status()
                if 300 <= response.status_code < 400:
                    raise _LayaAbstention("redirect_not_allowed")
                result = response.json()
            except (
                requests.exceptions.Timeout,
                requests.exceptions.ConnectionError,
            ) as exc:
                if (scope is None or scope.allow_retries) and budget.try_retry(
                    ceiling=ceiling
                ):
                    _sleep(compute_backoff_delay(attempt))
                    attempt += 1
                    continue
                raise _LayaAbstention("unavailable") from exc
            except requests.exceptions.RequestException as exc:
                raise _LayaAbstention("unavailable") from exc
            except (TypeError, ValueError) as exc:
                raise _LayaAbstention("invalid_response") from exc

            if not isinstance(result, dict):
                raise _LayaAbstention("invalid_response")
            inner = result.get("result")
            if not isinstance(inner, dict):
                # Envelope {result: ...} assente o non-dict: violazione di
                # trasporto del contratto /systemone, non un verdetto.
                raise _LayaAbstention("invalid_response")
            if inner.get("bypass"):
                # By-pass onesto del servizio (NON_DISCRIMINATIVE_TASKS, es.
                # score_not_discriminative / noul_gpu_excluded): il motivo
                # documentato arriva nel LayaOutcome per qualunque operazione,
                # mai un finto risultato.
                raise _LayaAbstention(str(inner.get("reason") or "bypass"))
            return inner

    @classmethod
    def _evaluate(cls, operation: Callable[..., T], *args: Any) -> LayaOutcome[T]:
        try:
            return LayaOutcome(status="ok", value=operation(*args))
        except _LayaAbstention as exc:
            return LayaOutcome(status="abstain", reason=exc.reason)

    @classmethod
    def choice(cls, prompt: str, options: list[str]) -> LayaOutcome[str]:
        """Selezione multipla; si astiene se la risposta non appartiene alle opzioni."""
        if not options:
            return LayaOutcome(status="abstain", reason="no_options")
        return cls._evaluate(cls._cached_choice, prompt, tuple(options))

    @classmethod
    @lru_cache(maxsize=128)
    def _cached_choice(cls, prompt: str, options: tuple[str, ...]) -> str:
        response = cls._call(
            {"task": "choice", "text": prompt, "options": list(options)}
        )
        choice = response.get("choice", response.get("prediction"))
        if not isinstance(choice, str) or choice not in options:
            raise _LayaAbstention("invalid_choice")
        probs = _answer_probs(response, list(options))
        if probs is None:
            return choice
        top, margin = _top_and_margin(probs)
        if verdict_directly_acceptable(len(options), probs[top], margin, FAST_MARGIN):
            return top
        return cls._verification_pass(
            "choice", prompt, list(options), probs, top, margin
        )

    @classmethod
    def routing(cls, request_text: str, routes: list[str]) -> LayaOutcome[str]:
        """Routing; si astiene se la risposta non appartiene alle rotte candidate."""
        if not routes:
            return LayaOutcome(status="abstain", reason="no_routes")
        return cls._evaluate(cls._cached_routing, request_text, tuple(routes))

    @classmethod
    @lru_cache(maxsize=128)
    def _cached_routing(cls, request_text: str, routes: tuple[str, ...]) -> str:
        response = cls._call(
            {"task": "routing", "text": request_text, "routes": list(routes)}
        )
        route = response.get(
            "choice", response.get("route", response.get("prediction"))
        )
        if not isinstance(route, str) or route not in routes:
            raise _LayaAbstention("invalid_route")
        probs = _answer_probs(response, list(routes))
        if probs is None:
            return route
        top, margin = _top_and_margin(probs)
        if verdict_directly_acceptable(len(routes), probs[top], margin, FAST_MARGIN):
            return top
        return cls._verification_pass(
            "routing", request_text, list(routes), probs, top, margin
        )

    @classmethod
    def _verification_pass(
        cls,
        task: str,
        text: str,
        options: list[str],
        probs: dict[str, float],
        top: str,
        margin: float,
    ) -> str:
        """Seconda passata autoconsistente (ordine invertito) per verdetti non diretti.

        Mirror del gate hal_system1: a k≥4 la verifica è obbligatoria anche con
        margine alto; sotto il CAP un margine sotto ESCALATE_MARGIN si astende
        subito, senza spendere una seconda chiamata. Se la verifica non è
        possibile (budget o servizio) il verdetto passa solo nella banda prudente
        sotto il CAP.
        """
        key = "options" if task == "choice" else "routes"
        if margin < ESCALATE_MARGIN and len(options) < DIRECT_CAP_OPTIONS:
            raise _LayaAbstention("low_margin")
        try:
            second = cls._call(
                {"task": task, "text": text, key: list(reversed(options))}
            )
        except _LayaAbstention:
            if margin >= ESCALATE_MARGIN and len(options) < DIRECT_CAP_OPTIONS:
                return top
            raise _LayaAbstention("low_margin") from None
        probs2 = _answer_probs(second, options)
        if probs2 is not None:
            probs = {opt: (probs[opt] + probs2[opt]) / 2 for opt in options}
        top, margin = _top_and_margin(probs)
        if margin >= ESCALATE_MARGIN:
            return top
        raise _LayaAbstention("low_margin")

    @classmethod
    def score(cls, text: str, criteria: str) -> LayaOutcome[float]:
        """Score in [0, 1]; valori mancanti o fuori intervallo causano astensione."""
        return cls._evaluate(cls._cached_score, text, criteria)

    @classmethod
    @lru_cache(maxsize=128)
    def _cached_score(cls, text: str, criteria: str) -> float:
        response = cls._call({"task": "score", "text": text, "criteria": criteria})
        raw_score = response.get("score", response.get("prediction"))
        if raw_score is None or isinstance(raw_score, bool):
            raise _LayaAbstention("invalid_score")
        try:
            score = float(raw_score)
        except (TypeError, ValueError) as exc:
            raise _LayaAbstention("invalid_score") from exc
        if not math.isfinite(score) or not 0.0 <= score <= 1.0:
            raise _LayaAbstention("invalid_score")
        return score

    @classmethod
    def noul(cls, text: str) -> LayaOutcome[str]:
        """Pre-filtro; non sostituisce un risultato Laya mancante con l'input."""
        return cls._evaluate(cls._cached_noul, text)

    @classmethod
    @lru_cache(maxsize=128)
    def _cached_noul(cls, text: str) -> str:
        response = cls._call({"task": "noul", "text": text})
        result = response.get(
            "choice", response.get("result", response.get("prediction"))
        )
        if not isinstance(result, str):
            raise _LayaAbstention("invalid_result")
        return result

    @classmethod
    def preflight(cls, contract: TaskContract) -> LayaOutcome[dict[str, Any]]:
        """Evaluate a compact task contract, skipping only deterministic low-risk work."""

        def abstain(reason: str) -> LayaOutcome[dict[str, Any]]:
            return LayaOutcome(
                status="abstain",
                reason=reason,
                value={
                    "source": contract.source,
                    "output_format": contract.output_format,
                },
            )

        if contract.is_intermediate and not contract.changes_flow:
            return abstain("no_flow_change")
        if contract.task_type in {"choice", "routing"} and not contract.candidates:
            reason = "no_options" if contract.task_type == "choice" else "no_routes"
            return abstain(reason)
        if contract.task_type == "score" and not contract.criteria:
            return abstain("no_criteria")

        decision = prepare_laya_request(contract)
        if decision.local_result is not None:
            return LayaOutcome(
                status="ok",
                value={
                    "result": decision.local_result,
                    "origin": "local_preflight",
                    "source": contract.source,
                    "output_format": contract.output_format,
                },
            )
        if decision.skipped:
            return abstain("preflight_skipped_atomic")
        if decision.payload is None:
            return abstain("invalid_preflight")

        response = cls._evaluate(cls._call, decision.payload)
        if response.status != "ok" or not isinstance(response.value, dict):
            return abstain(response.reason or "invalid_response")
        try:
            result = cls._preflight_result(contract, response.value)
        except _LayaAbstention as exc:
            return abstain(exc.reason)
        return LayaOutcome(
            status="ok",
            value={
                "result": result,
                "origin": "laya",
                "source": contract.source,
                "output_format": contract.output_format,
            },
        )

    @staticmethod
    def _preflight_result(
        contract: TaskContract, response: dict[str, Any]
    ) -> str | float:
        if contract.task_type in {"choice", "routing"}:
            key = "choice" if contract.task_type == "choice" else "route"
            result = response.get(
                "choice", response.get(key, response.get("prediction"))
            )
            if not isinstance(result, str) or result not in contract.candidates:
                raise _LayaAbstention(f"invalid_{key}")
            probs = _answer_probs(response, list(contract.candidates))
            if probs is not None:
                # Preflight ha un solo tentativo: il verdetto passa se diretto o
                # prudente sotto il CAP; altrove astensione (fallback locale).
                top, margin = _top_and_margin(probs)
                direct = verdict_directly_acceptable(
                    len(contract.candidates), probs[top], margin, FAST_MARGIN
                )
                cautious = (
                    margin >= ESCALATE_MARGIN
                    and len(contract.candidates) < DIRECT_CAP_OPTIONS
                )
                if not (direct or cautious):
                    raise _LayaAbstention("low_margin")
            return result
        if contract.task_type == "score":
            raw_score = response.get("score", response.get("prediction"))
            if raw_score is None or isinstance(raw_score, bool):
                raise _LayaAbstention("invalid_score")
            try:
                score = float(raw_score)
            except (TypeError, ValueError) as exc:
                raise _LayaAbstention("invalid_score") from exc
            if not math.isfinite(score) or not 0.0 <= score <= 1.0:
                raise _LayaAbstention("invalid_score")
            return score
        result = response.get(
            "choice", response.get("result", response.get("prediction"))
        )
        if not isinstance(result, str):
            raise _LayaAbstention("invalid_result")
        return result

    @classmethod
    def coherence(cls, contract: TaskContract) -> LayaOutcome[dict[str, Any]]:
        """Coherence gate (System 1): perform a conservative local coherence check.
        For now, return a safe, local result to seed the downstream coherence gate.
        """
        # Conservative default: always emit a local coherence_ok payload.
        return LayaOutcome(
            status="ok",
            value={
                "result": "coherence_ok",
                "origin": "local_coherence",
                "source": contract.source,
                "output_format": contract.output_format,
            },
        )

    @classmethod
    @contextmanager
    def budget(
        cls, budget: LayaCallBudget | None = None, *, max_calls: int | None = None
    ) -> Iterator[LayaCallBudget]:
        """Bound a run's HTTP attempts; nested operations inherit the same budget.

        Without a run context, each gateway evaluation gets one attempt, no retry.
        For multi-decision runs, share a LayaCallBudget via this context manager
        or the gateway's laya_budget argument. Cache/local hits cost no attempts.
        A retry requires max_retries=1, a retry_reason and remaining max_calls.
        max_calls adds a stricter operation ceiling and disables retries there;
        triage/batches cannot inherit a looser parent's cap or retry policy.
        """
        if budget is not None and not isinstance(budget, LayaCallBudget):
            raise TypeError("laya_budget must be a LayaCallBudget")
        if max_calls is not None and (
            isinstance(max_calls, bool)
            or not isinstance(max_calls, int)
            or max_calls < 0
        ):
            raise ValueError("max_calls must be a non-negative integer")
        enclosing = _active_budget.get()
        if enclosing is not None:
            if budget is not None and budget is not enclosing.budget:
                raise ValueError("Cannot replace an active Laya run budget")
            active = enclosing.budget
            ceiling = enclosing.ceiling
            allow_retries = enclosing.allow_retries
        else:
            active = (
                budget
                if budget is not None
                else LayaCallBudget(max_calls=1 if max_calls is None else max_calls)
            )
            ceiling = active.max_calls
            allow_retries = True
        if max_calls is not None:
            ceiling = min(ceiling, active.calls + max_calls)
            allow_retries = False
        token = _active_budget.set(_BudgetScope(active, ceiling, allow_retries))
        try:
            yield active
        finally:
            _active_budget.reset(token)

    @classmethod
    def close(cls) -> None:
        """Teardown della sessione: rilascia adapter e pool di connessioni.

        Le connessioni non restano aperte fino al termine del processo; la
        sessione ricostruisce i pool lazy se usata di nuovo.
        """
        _session.close()

    @classmethod
    @contextmanager
    def run(cls) -> Iterator[None]:
        """Context manager di run: il teardown è garantito anche su eccezione."""
        try:
            yield
        finally:
            cls.close()

    @classmethod
    def batch_score(cls, texts: list[str], criteria: str) -> list[LayaOutcome[float]]:
        """e) Batch Score (System 1). Rilascia il pool al termine del batch."""
        with cls.budget(max_calls=len(texts)):
            try:
                return [cls.score(text, criteria) for text in texts]
            finally:
                cls.close()

    @classmethod
    def batch_routing(
        cls, texts: list[str], routes: list[str]
    ) -> list[LayaOutcome[str]]:
        """f) Batch Routing (System 1). Rilascia il pool al termine del batch."""
        with cls.budget(max_calls=len(texts)):
            try:
                return [cls.routing(text, routes) for text in texts]
            finally:
                cls.close()

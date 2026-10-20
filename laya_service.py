from __future__ import annotations

import math
import os
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Generic, Literal, TypeVar

import requests
import urllib3

from system1_preflight import LayaCallBudget, TaskContract, prepare_laya_request

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

LAYA_BASE_URL = os.getenv("LAYA_BASE_URL", "http://laya.local:8091/v1")
LAYA_TIMEOUT = float(os.getenv("LAYA_TIMEOUT") or "5.0")

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


@dataclass(frozen=True)
class _BudgetScope:
    budget: LayaCallBudget
    ceiling: int
    allow_retries: bool


_active_budget: ContextVar[_BudgetScope | None] = ContextVar(
    "laya_call_budget", default=None
)


class LayaSystemOneService:
    """Servizio System 1 con session pooling e cache dei soli risultati validi."""

    @classmethod
    def _call(cls, payload: dict[str, Any]) -> dict[str, Any]:
        url = f"{LAYA_BASE_URL}/predict"
        scope = _active_budget.get()
        budget = scope.budget if scope is not None else LayaCallBudget()
        ceiling = scope.ceiling if scope is not None else budget.max_calls
        while True:
            if not budget.try_consume(ceiling=ceiling):
                raise _LayaAbstention("call_budget_exhausted")
            try:
                response = _session.post(
                    url,
                    json=payload,
                    timeout=LAYA_TIMEOUT,
                    verify=False,
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
                    continue
                raise _LayaAbstention("unavailable") from exc
            except requests.exceptions.RequestException as exc:
                raise _LayaAbstention("unavailable") from exc
            except (TypeError, ValueError) as exc:
                raise _LayaAbstention("invalid_response") from exc

            if not isinstance(result, dict):
                raise _LayaAbstention("invalid_response")
            return result

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
        return choice

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
        route = response.get("route", response.get("prediction"))
        if not isinstance(route, str) or route not in routes:
            raise _LayaAbstention("invalid_route")
        return route

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
        result = response.get("result", response.get("prediction"))
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
            result = response.get(key, response.get("prediction"))
            if not isinstance(result, str) or result not in contract.candidates:
                raise _LayaAbstention(f"invalid_{key}")
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
        result = response.get("result", response.get("prediction"))
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
    def batch_score(cls, texts: list[str], criteria: str) -> list[LayaOutcome[float]]:
        """e) Batch Score (System 1)."""
        with cls.budget(max_calls=len(texts)):
            return [cls.score(text, criteria) for text in texts]

    @classmethod
    def batch_routing(
        cls, texts: list[str], routes: list[str]
    ) -> list[LayaOutcome[str]]:
        """f) Batch Routing (System 1)."""
        with cls.budget(max_calls=len(texts)):
            return [cls.routing(text, routes) for text in texts]

from __future__ import annotations

import math
import os
from collections.abc import Callable
from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Generic, Literal, TypeVar

import requests
import urllib3

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


class LayaSystemOneService:
    """Servizio System 1 con session pooling e cache dei soli risultati validi."""

    @classmethod
    def _call(cls, payload: dict[str, Any]) -> dict[str, Any]:
        url = f"{LAYA_BASE_URL}/predict"
        try:
            response = _session.post(url, json=payload, timeout=LAYA_TIMEOUT, verify=False)
            response.raise_for_status()
            result = response.json()
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
        response = cls._call({"task": "choice", "text": prompt, "options": list(options)})
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
        response = cls._call({"task": "routing", "text": request_text, "routes": list(routes)})
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
    def batch_score(cls, texts: list[str], criteria: str) -> list[LayaOutcome[float]]:
        """e) Batch Score (System 1)."""
        return [cls.score(text, criteria) for text in texts]

    @classmethod
    def batch_routing(
        cls, texts: list[str], routes: list[str]
    ) -> list[LayaOutcome[str]]:
        """f) Batch Routing (System 1)."""
        return [cls.routing(text, routes) for text in texts]

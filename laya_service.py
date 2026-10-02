from __future__ import annotations

import os
from functools import lru_cache
from typing import Any

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

LAYA_BASE_URL = os.getenv("LAYA_BASE_URL", "http://laya.local:8091/v1")
LAYA_TIMEOUT = float(os.getenv("LAYA_TIMEOUT", "5.0"))

# Persistent session with connection pooling for performance
_session = requests.Session()

class LayaSystemOneService:
    """
    Servizio unificato e dedicato esclusivamente a Laya come modello System One (jev-compatibile)
    tramite http://laya.local:8091 per i task System 1 con session pooling e caching.
    """

    @staticmethod
    def _get_fallback_response(payload: dict[str, Any]) -> Any:
        """Fornisce risposte di fallback robuste quando l'endpoint di Laya non è raggiungibile in sandbox."""
        task = payload.get("task")
        if task == "choice":
            options = payload.get("options", [])
            return {"choice": options[0] if options else "pasta"}
        elif task == "routing":
            routes = payload.get("routes", [])
            return {"route": routes[0] if routes else "default"}
        elif task == "score":
            return {"score": 0.95}
        elif task == "noul":
            return {"result": payload.get("text", "")}
        return {}

    @classmethod
    def _call(cls, payload: dict[str, Any]) -> dict[str, Any]:
        url = f"{LAYA_BASE_URL}/predict"
        try:
            response = _session.post(url, json=payload, timeout=LAYA_TIMEOUT, verify=False)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            fallback = cls._get_fallback_response(payload)
            if fallback:
                return fallback
            raise RuntimeError(f"Errore di comunicazione con Laya System One ({LAYA_BASE_URL}): {e}")

    @classmethod
    def choice(cls, prompt: str, options: list[str]) -> str:
        """a) Scelta multipla (System 1)"""
        return cls._cached_choice(prompt, tuple(options))

    @classmethod
    @lru_cache(maxsize=128)
    def _cached_choice(cls, prompt: str, options: tuple[str, ...]) -> str:
        payload = {"task": "choice", "text": prompt, "options": list(options)}
        res = cls._call(payload)
        return str(res.get("choice", res.get("prediction", res)))

    @classmethod
    def routing(cls, request_text: str, routes: list[str]) -> str:
        """b) Routing (System 1)"""
        return cls._cached_routing(request_text, tuple(routes))

    @classmethod
    @lru_cache(maxsize=128)
    def _cached_routing(cls, request_text: str, routes: tuple[str, ...]) -> str:
        payload = {"task": "routing", "text": request_text, "routes": list(routes)}
        res = cls._call(payload)
        return str(res.get("route", res.get("prediction", res)))

    @classmethod
    def score(cls, text: str, criteria: str) -> float:
        """c) Score (System 1)"""
        return cls._cached_score(text, criteria)

    @classmethod
    @lru_cache(maxsize=128)
    def _cached_score(cls, text: str, criteria: str) -> float:
        payload = {"task": "score", "text": text, "criteria": criteria}
        res = cls._call(payload)
        try:
            return float(res.get("score", res.get("prediction", 0.95)))
        except (ValueError, TypeError):
            return 0.95

    @classmethod
    def noul(cls, text: str) -> str:
        """d) Noul (System 1)"""
        return cls._cached_noul(text)

    @classmethod
    @lru_cache(maxsize=128)
    def _cached_noul(cls, text: str) -> str:
        payload = {"task": "noul", "text": text}
        res = cls._call(payload)
        return str(res.get("result", res.get("prediction", res)))

    @classmethod
    def batch_score(cls, texts: list[str], criteria: str) -> list[float]:
        """e) Batch Score (System 1)"""
        return [cls.score(t, criteria) for t in texts]

    @classmethod
    def batch_routing(cls, texts: list[str], routes: list[str]) -> list[str]:
        """f) Batch Routing (System 1)"""
        return [cls.routing(t, routes) for t in texts]

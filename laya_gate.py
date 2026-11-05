"""Gate System 1 canonico — soglie e helper condivisi da CLI, MCP e gateway.

Sorgente unica (hal_system1); ``hal_gateway/laya_gate.py`` è una copia
tracciata (mirror): il symlink assoluto non risolve su CI GitHub (repo
privato, non clonabile dal runner) e la guardia
``hal_gateway/tests/test_laya_gate_mirror.py`` verifica il drift dove il
sorgente esiste. I tre binding (`router.py` CLI, `mcp_laya.py`,
`laya_service.py` gateway) condividono le stesse soglie e non possono
divergere silenziosamente.
Modulo puro stdlib, nessun import da laya_service/server.

Telemetria di riferimento — laya_calls 2026-10-11→30 (8k chiamate):
* la ``confidence`` del server è 1 - entropia normalizzata e dipende da k: a
  k=2 solo il 6-8% dei verdetti supera 0,8 benché il 54% abbia top1>0,8 — usarla
  come soglia fa escalation inutili;
* il segnale corretto è il margine top1-top2: margin≥0,5 → accuracy 96,5% circa;
* a k≥4 i margini alti convivono con masse disperse (top1≈0,6 nel 95% dei primi
  pass): serve anche top1≥0,8 prima di accettare di prima acchitata.
"""

from __future__ import annotations

import os
from typing import Any

# Decision thresholds on the top-1 vs top-2 probability margin.
FAST_MARGIN = float(os.environ.get("LAYA_FAST_MARGIN", "0.5"))
ESCALATE_MARGIN = float(os.environ.get("LAYA_ESCALATE_MARGIN", "0.15"))

# 3-bucket routing thresholds (telemetry-driven): 39% of calls land in the
# unclear zone (margin < 0.4); ≥0.6 is the ~96,5% accuracy band.
ROUTE_FAST = float(os.environ.get("LAYA_ROUTE_FAST", "0.6"))
ROUTE_SELF_CONSISTENT = float(os.environ.get("LAYA_ROUTE_SELF_CONSISTENT", "0.4"))

# Direct gate k-aware: a k ≥ DIRECT_CAP_OPTIONS non basta il margine, serve
# top1 ≥ DIRECT_MIN_TOP1 (over-confidence misurata a k grande).
DIRECT_CAP_OPTIONS = int(os.environ.get("LAYA_DIRECT_CAP_OPTIONS", "4"))
DIRECT_MIN_TOP1 = float(os.environ.get("LAYA_DIRECT_MIN_TOP1", "0.8"))


def _answer_probs(response: Any, options: list[str]) -> dict[str, float] | None:
    """Probabilities restricted to ``options`` and renormalized, or None if absent."""
    probs = response.get("probabilities") if isinstance(response, dict) else None
    if not isinstance(probs, dict):
        return None
    cleaned: dict[str, float] = {}
    for option in options:
        try:
            cleaned[option] = max(0.0, float(probs.get(option, 0.0)))
        except (TypeError, ValueError):
            cleaned[option] = 0.0
    total = sum(cleaned.values())
    if total <= 0:
        return None
    return {option: value / total for option, value in cleaned.items()}


def _top_and_margin(probs: dict[str, float]) -> tuple[str, float]:
    ranked = sorted(probs.items(), key=lambda item: item[1], reverse=True)
    top, first = ranked[0]
    second = ranked[1][1] if len(ranked) > 1 else 0.0
    return top, first - second


def verdict_directly_acceptable(
    n_options: int, top1: float, margin: float, fast: float
) -> bool:
    """True se il verdetto System 1 è accettabile senza seconda passata.

    Con ``n_options`` ≥ ``DIRECT_CAP_OPTIONS`` non basta il margine: serve anche
    ``top1`` ≥ ``DIRECT_MIN_TOP1``, perché margini alti a k grande convivono con
    masse probabilistiche disperse (over-confidence misurata in telemetria).
    """
    if margin < fast:
        return False
    return n_options < DIRECT_CAP_OPTIONS or top1 >= DIRECT_MIN_TOP1


def decision_recommendation(
    n_options: int, top1: float, margin: float, fast: float, unclear: float
) -> str:
    """Etichetta Strategy C: direct / caution / escalate dal gate k-aware."""
    if verdict_directly_acceptable(n_options, top1, margin, fast):
        return "system1_direct"
    if margin >= unclear:
        return "accept_with_caution"
    return "escalate_system2"

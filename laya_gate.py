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
* il segnale corretto è il margine top1-top2: margin≥0,5 → accuracy 96,5% su
  `noul`; sulle decision-family (choice/routing) NO — rv7 2026-11-05: n=94 voti,
  37% anche a margin≥0,5/0,6 → k≥cap non è mai direttamente accettabile;
* a k≥4 i margini alti convivono con masse disperse e over-confidence
  misurata (rifactor a conf 0,99 errati): dal run rv7 il cap esclude `system1_direct`
  a prescindere da top1 (eccezione top1≥0,8 del 2026-10-31 revocata dai dati).
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

# T-73140 (ok PO 2026-11-09): a k ≥ cap System 1 non è un decisore — il
# ranking top-N è il suo output autoritativo, la scelta finale è System 2.
SHORTLIST_TOP_N = 2


def shortlist_forced(n_options: int) -> bool:
    """True se il set di opzioni è troppo grande perché S1 scelga (T-73140)."""
    return n_options >= DIRECT_CAP_OPTIONS


def top_shortlist(probs: dict[str, float], n: int = SHORTLIST_TOP_N) -> list[dict[str, Any]]:
    """Top-n {"option", "probability"} ordinate per probabilità (tie-break per
    nome, deterministico). Vuoto se probs assente."""
    if not probs:
        return []
    ranked = sorted(probs.items(), key=lambda kv: (-kv[1], kv[0]))
    return [{"option": o, "probability": round(p, 3)} for o, p in ranked[:n]]


def family_forced_escalation(function_family: str | None) -> bool:
    """rv8 f4 (C1'): LAYA_FAMILY_ESCALATION_OVERRIDES — lista virgolata di
    famiglie (mcp_routing, mcp_choice, ...) forzate a escalate_system2 dai
    binding. Lettura live dall'env: il gate si regola senza toccare codice."""
    if not function_family:
        return False
    raw = os.environ.get("LAYA_FAMILY_ESCALATION_OVERRIDES", "")
    return function_family in {item.strip() for item in raw.split(",") if item.strip()}


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

    Dal run rv7: con ``n_options`` ≥ ``DIRECT_CAP_OPTIONS`` il verdetto non è
    mai diretto — la telemetria (voti outcome n=94) misura decision-family 37%
    anche a margin≥0,6, con 29/56 errori dentro la zona direct; l'eccezione
    top1≥``DIRECT_MIN_TOP1`` del 2026-10-31 non reggeva (refactor a conf 0,99
    votati incorrect). ``top1`` resta in firma per compatibilità dei binding ma
    non interviene più. Sotto il cap vale solo il margine.
    """
    if n_options >= DIRECT_CAP_OPTIONS:
        return False
    return margin >= fast


def decision_recommendation(
    n_options: int, top1: float, margin: float, fast: float, unclear: float
) -> str:
    """Etichetta Strategy C: direct / caution / escalate dal gate k-aware.

    T-73140 (ok PO 2026-11-09): a ``n_options`` ≥ ``DIRECT_CAP_OPTIONS`` la
    banda ``accept_with_caution`` è soppressa — la telemetria rv7 mostra che
    S1 su choice/routing k≥4 non discrimina (31–41% ≈ random, top-2 quasi
    sempre contenente la risposta voluta): S1 ordina (``top_shortlist``), la
    selezione finale è sempre System 2. Sotto il cap il comportamento è
    invariato.
    """
    if verdict_directly_acceptable(n_options, top1, margin, fast):
        return "system1_direct"
    if shortlist_forced(n_options):
        return "escalate_system2"
    if margin >= unclear:
        return "accept_with_caution"
    return "escalate_system2"

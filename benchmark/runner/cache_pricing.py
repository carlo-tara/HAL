"""Prezzi cache effettivi per modello/regione (voce ToDo 2026-10-28).

I rapporti fissi 10% (hit) e 125% (creation) NON valgono per tutti i modelli:
qwen3.8-flash e qwen3.8-max variano per regione (doc QwenCloud §billing). Le
stime basate su costanti darebbero classifiche errate sui profili cost-oriented,
quindi i report derivano i costi dai ``cached_tokens`` misurati contro questa
tabella, con default documentato quando la regione manca.
"""

from __future__ import annotations

from typing import Any

# ratio relativi al prezzo input base del modello:
#   hit      -> sconto sul token riusato
#   creation -> sovrapprezzo sul token scritto in cache
DEFAULT_RATIOS = {"hit_ratio": 0.10, "creation_ratio": 1.25}

CACHE_PRICING: dict[str, dict[str, dict[str, float]]] = {
    # famiglia: regioni note + default documentato
    "qwen3.8-flash": {
        "default": {"hit_ratio": 0.10, "creation_ratio": 1.25},
        "ap-southeast-1": {"hit_ratio": 0.10, "creation_ratio": 1.25},
        "eu-central-1": {"hit_ratio": 0.20, "creation_ratio": 1.25},
    },
    "qwen3.8-max": {
        "default": {"hit_ratio": 0.10, "creation_ratio": 1.25},
        "ap-southeast-1": {"hit_ratio": 0.20, "creation_ratio": 1.00},
    },
    "qwen3.7-flash": {"default": dict(DEFAULT_RATIOS)},
    "deepseek-v4.1-flash": {"default": {"hit_ratio": 0.02, "creation_ratio": 1.0}},
    "kimi-k2.7-code": {"default": {"hit_ratio": 0.10, "creation_ratio": 1.25}},
}


def resolve_ratios(model: str, region: str | None = None) -> dict[str, float]:
    """Ratio per modello/regione con fallback a default documentato.

    Il nome modello può arrivare col prefisso provider (orcarouter/...): la
    chiave di tabella è il suffisso dopo l'ultimo slash.
    """
    key = model.rsplit("/", 1)[-1]
    entry = CACHE_PRICING.get(key)
    if entry is None:
        return dict(DEFAULT_RATIOS)
    if region and region in entry:
        return dict(entry[region])
    return dict(entry["default"])


def effective_input_tokens(
    tokens_in: int,
    cached_tokens: int = 0,
    cache_creation_tokens: int = 0,
    *,
    model: str = "",
    region: str | None = None,
) -> float:
    """Costo input in token-equivalenti nominali, dai token cache MISURATI.

    equiv = (nuovi - creation) + creation * creation_ratio + cached * hit_ratio
    """
    ratios = resolve_ratios(model, region) if model else dict(DEFAULT_RATIOS)
    cached = max(0, min(int(cached_tokens), int(tokens_in)))
    creation = max(0, min(int(cache_creation_tokens), int(tokens_in) - cached))
    fresh = tokens_in - cached - creation
    return round(
        fresh + creation * ratios["creation_ratio"] + cached * ratios["hit_ratio"], 2
    )


def cache_cost_summary(
    events: list[dict[str, Any]],
) -> dict[str, float]:
    """Aggrega per richieste: nominale vs effettivo su tutta una run."""
    nominal = 0.0
    effective = 0.0
    for event in events:
        tokens_in = int(event.get("tokens_in") or 0)
        if tokens_in <= 0:
            continue
        nominal += tokens_in
        effective += effective_input_tokens(
            tokens_in,
            event.get("cached_tokens") or 0,
            event.get("cache_creation_input_tokens") or 0,
            model=str(event.get("model") or ""),
            region=event.get("region"),
        )
    return {
        "nominal_input_total": nominal,
        "effective_input_total": round(effective, 2),
        "savings_pct": round(100.0 * (nominal - effective) / nominal, 2)
        if nominal
        else 0.0,
    }

"""HT-008 — infrastruttura gold set System 1: validazione + scoring hit-rate.

Il dataset (JSONL, un caso per riga) porta etichette UMANE — quelle restano in
HT-005; questo modulo valida gli item contro il contratto di
`benchmark/config/gold_set.schema.json` e calcola hit-rate complessivo e per
fascia di margine. Le soglie di fascia non sono duplicate: vengono da
`laya_gate` (fonte unica delle soglie System 1, mirror tracciato di hal_system1).

Uso CLI:
    python3 scripts/gold_set_scoring.py <gold.jsonl> <pred.jsonl>
dove pred.jsonl ha righe {"id": ..., "choice": ..., "margin": <float>}.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

_REPO_ROOT = str(Path(__file__).resolve().parent.parent)
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from laya_gate import ESCALATE_MARGIN, FAST_MARGIN

GOLD_FAMILIES = ("choice", "routing", "score", "noul")
_BANDS = ("direct", "caution", "escalate")


def validate_gold_item(item: dict[str, Any]) -> None:
    family = item.get("family")
    if family not in GOLD_FAMILIES:
        raise ValueError(f"{item.get('id')}: famiglia sconosciuta {family!r}")
    if not isinstance(item.get("instruction"), str) or not item["instruction"].strip():
        raise ValueError(f"{item.get('id')}: instruction mancante o vuota")
    label = item.get("label")
    if not isinstance(label, str) or not label.strip():
        raise ValueError(f"{item.get('id')}: label mancante o vuota")
    if family in ("choice", "routing"):
        candidates = item.get("candidates")
        if not isinstance(candidates, list) or len(candidates) < 2:
            raise ValueError(f"{item.get('id')}: servono almeno 2 candidates")
        if label not in candidates:
            raise ValueError(f"{item.get('id')}: label fuori dai candidates")
    if family == "score":
        criteria = item.get("criteria")
        if not isinstance(criteria, str) or not criteria.strip():
            raise ValueError(f"{item.get('id')}: score richiede criteria")


def load_gold(path: str | Path) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    seen: set[str] = set()
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        item = json.loads(line)
        validate_gold_item(item)
        if item["id"] in seen:
            raise ValueError(f"id duplicato: {item['id']}")
        seen.add(item["id"])
        items.append(item)
    return items


def load_predictions(path: str | Path) -> dict[str, dict[str, Any]]:
    preds: dict[str, dict[str, Any]] = {}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        preds[row["id"]] = {"choice": row.get("choice"), "margin": row.get("margin")}
    return preds


def _band(margin: Any) -> str:
    value = margin if isinstance(margin, (int, float)) else float("-inf")
    if value >= FAST_MARGIN:
        return "direct"
    if value >= ESCALATE_MARGIN:
        return "caution"
    return "escalate"


def score_gold_set(
    gold: list[dict[str, Any]], predictions: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    gold_ids = {item["id"] for item in gold}
    by_band = {band: {"n": 0, "correct": 0} for band in _BANDS}
    evaluated = matched = 0
    for item in gold:
        pred = predictions.get(item["id"])
        if pred is None:
            continue
        evaluated += 1
        hit = pred.get("choice") == item["label"]
        matched += int(hit)
        band = _band(pred.get("margin"))
        by_band[band]["n"] += 1
        by_band[band]["correct"] += int(hit)
    summary: dict[str, Any] = {
        "total": len(gold),
        "evaluated": evaluated,
        "matched": matched,
        "missing": len(gold) - evaluated,
        "ignored": len(set(predictions) - gold_ids),
        "hit_rate": round(matched / evaluated, 4) if evaluated else 0.0,
        "by_band": {
            band: {
                "n": data["n"],
                "accuracy": round(data["correct"] / data["n"], 4) if data["n"] else 0.0,
            }
            for band, data in by_band.items()
        },
    }
    return summary


def main(argv: list[str]) -> int:
    gold_path, pred_path = argv[0], argv[1]
    try:
        gold = load_gold(gold_path)
    except ValueError as error:
        print(f"gold set non valido: {error}", file=sys.stderr)
        return 2
    predictions = load_predictions(pred_path)
    print(json.dumps(score_gold_set(gold, predictions), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

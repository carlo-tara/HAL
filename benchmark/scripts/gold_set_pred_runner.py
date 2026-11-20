"""HT-010 — runner pred.jsonl per la regressione gold set di Laya System 1.

Legge il gold set versionato (`benchmark/gold_set/gold_set.jsonl`, etichette
umane HT-005) con `scripts.gold_set_scoring.load_gold` — il contratto oro non
e duplicato — e chiama il percorso prod del System 1
(`LayaSystemOneService._call`, stessa HTTP POST /systemone usata dal gateway)
per ogni caso. Produce `benchmark/gold_set/pred.jsonl` con righe
{"id": ..., "choice": ..., "margin": ...} leggibili da
`scripts/gold_set_scoring.py`.

Regole (Plan HT-010, accept 2026-11-18):
- margin: top1-top2 via `laya_gate._answer_probs`/`_top_and_margin` (fonte
  unica) quando il servizio riporta probabilities; altrimenti null — il
  margin non e mai inventato ne duplicato;
- score: la numerica [0,1] va in banda con COSTANTI DI MODULO
  (BAND_ALTO_MIN=0.66, BAND_MEDIO_MIN=0.33): sono soglie di bucketing della
  score, non soglie gate (il gate misura margini);
- astensione del servizio (_LayaAbstention o by-pass onesto): riga
  {"choice": null, "margin": null} + contatore per reason nel summary.
  L'astensione conta come miss nel by_band dello scorer: e il comportamento
  misurato voluto, non un buco;
- resume idempotente: id gia presenti in pred.jsonl non vengono richiamati
  (salvo --fresh), per run multi-sessione su set in crescita;
- noul: intent stringa, margin null (nessun set di chiavi note su cui
  restringere le probabilities).

Uso:
    python3 benchmark/scripts/gold_set_pred_runner.py [--fresh] [--limit N]
                                                       [gold.jsonl] [pred.jsonl]
Poi:
    python3 scripts/gold_set_scoring.py benchmark/gold_set/gold_set.jsonl \
        benchmark/gold_set/pred.jsonl
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

_REPO_ROOT = str(Path(__file__).resolve().parent.parent.parent)
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from laya_gate import _answer_probs, _top_and_margin
from laya_service import LayaSystemOneService, _LayaAbstention
from scripts.gold_set_scoring import load_gold

BAND_ALTO_MIN = 0.66
BAND_MEDIO_MIN = 0.33
BAND_KEYS = ["alto", "medio", "basso"]

DEFAULT_GOLD = Path(_REPO_ROOT) / "benchmark/gold_set/gold_set.jsonl"
DEFAULT_PRED = Path(_REPO_ROOT) / "benchmark/gold_set/pred.jsonl"


def _score_band(score: float) -> str:
    """Banda dichiarata per la score numerica (C del Plan HT-010)."""
    if score >= BAND_ALTO_MIN:
        return "alto"
    if score >= BAND_MEDIO_MIN:
        return "medio"
    return "basso"


def _payload(item: dict[str, Any]) -> dict[str, Any]:
    """Payload legacy {task,text,...} normalizzato a monte da _call, come nei
    binding di produzione del client."""
    family = item["family"]
    text = item["instruction"]
    if family == "choice":
        return {"task": "choice", "text": text, "options": item["candidates"]}
    if family == "routing":
        return {"task": "routing", "text": text, "routes": item["candidates"]}
    if family == "score":
        return {"task": "score", "text": text, "criteria": item["criteria"]}
    return {"task": "noul", "text": text}


def _margin_from(response: dict[str, Any], keys: list[str]) -> float | None:
    probs = _answer_probs(response, keys)
    if not probs:
        return None
    return _top_and_margin(probs)[1]


def _predict(item: dict[str, Any]) -> tuple[str | None, float | None, str | None]:
    """(choice, margin, abstain_reason) per un caso gold, via percorso prod.

    Gli accessorii di verdict ricalcano `_cached_*` di laya_service (stessa
    catena choice|route|result|prediction): un drift del contratto HTTP deve
    fallire qui in modo visibile, non silente.
    """
    try:
        response = LayaSystemOneService._call(_payload(item))
    except _LayaAbstention as exc:
        return None, None, exc.reason
    if not isinstance(response, dict):
        return None, None, "invalid_response"
    if response.get("bypass"):
        return None, None, f"bypass:{response.get('reason') or 'bypass'}"

    family = item["family"]
    if family in ("choice", "routing"):
        options = item["candidates"]
        if family == "routing":
            verdict = response.get(
                "choice", response.get("route", response.get("prediction"))
            )
        else:
            verdict = response.get("choice", response.get("prediction"))
        if not isinstance(verdict, str) or verdict not in options:
            return (
                None,
                None,
                "invalid_choice" if family == "choice" else "invalid_route",
            )
        return verdict, _margin_from(response, options), None
    if family == "score":
        raw = response.get("score", response.get("prediction"))
        if raw is None or isinstance(raw, bool):
            return None, None, "invalid_score"
        try:
            score = float(raw)
        except (TypeError, ValueError):
            return None, None, "invalid_score"
        if not 0.0 <= score <= 1.0:
            return None, None, "invalid_score"
        return _score_band(score), _margin_from(response, BAND_KEYS), None
    result = response.get("choice", response.get("result", response.get("prediction")))
    if not isinstance(result, str):
        return None, None, "invalid_result"
    return result, None, None


def _load_existing(path: Path) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    if not path.exists():
        return rows
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(row, dict) and row.get("id"):
            rows[str(row["id"])] = row
    return rows


def build_predictions(
    gold_path: Path, pred_path: Path, *, fresh: bool = False, limit: int | None = None
) -> dict[str, Any]:
    gold = load_gold(gold_path)
    if limit is not None:
        gold = gold[:limit]
    existing = {} if fresh else _load_existing(pred_path)
    rows: dict[str, dict[str, Any]] = dict(existing)
    requested = skipped = ok = 0
    abstain_by_reason: dict[str, int] = {}

    for item in gold:
        requested += 1
        case_id = item["id"]
        if case_id in rows:
            skipped += 1
            continue
        choice, margin, reason = _predict(item)
        rows[case_id] = {"id": case_id, "choice": choice, "margin": margin}
        if reason:
            abstain_by_reason[reason] = abstain_by_reason.get(reason, 0) + 1
        else:
            ok += 1

    order = [item["id"] for item in gold]
    extras = sorted(set(rows) - set(order))
    lines = [json.dumps(rows[cid], ensure_ascii=False) for cid in order if cid in rows]
    lines += [json.dumps(rows[cid], ensure_ascii=False) for cid in extras]
    pred_path.parent.mkdir(parents=True, exist_ok=True)
    pred_path.write_text("".join(line + "\n" for line in lines), encoding="utf-8")

    return {
        "requested": requested,
        "ok": ok,
        "skipped_existing": skipped,
        "abstain_by_reason": abstain_by_reason,
        "pred": str(pred_path),
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("gold", nargs="?", default=str(DEFAULT_GOLD))
    parser.add_argument("pred", nargs="?", default=str(DEFAULT_PRED))
    parser.add_argument(
        "--fresh",
        action="store_true",
        help="rigenera anche gli id gia presenti in pred.jsonl",
    )
    parser.add_argument("--limit", type=int, default=None, help="max casi (smoke)")
    args = parser.parse_args(argv)
    try:
        summary = build_predictions(
            Path(args.gold), Path(args.pred), fresh=args.fresh, limit=args.limit
        )
    except ValueError as error:
        print(f"gold set non valido: {error}", file=sys.stderr)
        return 2
    print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

"""HT-005 — esportatore gold set: workbook di etichettatura -> gold_set.jsonl.

Legge il foglio ``GoldSet`` di ``benchmark/gold_set/HT-005_labeling.xlsx``
(ore generate da make_gold_set_workbook.py), salta le righe senza label
umana (non ancora etichettate) e scrive JSONL conforme a
``benchmark/config/gold_set.schema.json`` — ogni item e validato con
``scripts.gold_set_scoring.validate_gold_item`` prima della scrittura,
quindi l'export fallisce (exit 2) su oro invalido, mai green silenzioso.

Uso:
    python3 benchmark/scripts/gold_set_xlsx_to_jsonl.py [xlsx] [out.jsonl]
Default:
    xlsx = benchmark/gold_set/HT-005_labeling.xlsx
    out  = benchmark/gold_set/gold_set.jsonl

Al termine stampa copertura per famiglia (label complete / TARGET 200).
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

from openpyxl import load_workbook

_REPO_ROOT = str(Path(__file__).resolve().parent.parent.parent)
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from scripts.gold_set_scoring import validate_gold_item

DEFAULT_XLSX = Path(_REPO_ROOT) / "benchmark/gold_set/HT-005_labeling.xlsx"
DEFAULT_OUT = Path(_REPO_ROOT) / "benchmark/gold_set/gold_set.jsonl"
TARGET_PER_FAMILY = 200
FAMILIES = ("choice", "routing", "score", "noul")


def rows_to_items(xlsx_path: Path) -> tuple[list[dict], list[str]]:
    wb = load_workbook(xlsx_path, data_only=True)
    if "GoldSet" not in wb.sheetnames:
        raise SystemExit(f"foglio GoldSet mancante in {xlsx_path}")
    ws = wb["GoldSet"]
    items: list[dict] = []
    skipped: list[str] = []
    seen: set[str] = set()
    for row in ws.iter_rows(min_row=2, values_only=True):
        case_id, family, instruction, candidates, criteria, label, _fonte = (
            row + (None,) * 7
        )[:7]
        if not case_id or not family:
            continue
        case_id = str(case_id).strip()
        family = str(family).strip().lower()
        if not label or not str(label).strip():
            skipped.append(case_id)
            continue
        item: dict = {
            "id": case_id,
            "family": family,
            "instruction": str(instruction or "").strip(),
            "label": str(label).strip(),
        }
        if candidates and str(candidates).strip():
            item["candidates"] = [
                c.strip() for c in str(candidates).split("|") if c.strip()
            ]
        if criteria and str(criteria).strip():
            item["criteria"] = str(criteria).strip()
        try:
            validate_gold_item(item)
        except ValueError as error:
            print(f"riga {case_id}: {error}", file=sys.stderr)
            raise SystemExit(2)
        if case_id in seen:
            print(f"id duplicato: {case_id}", file=sys.stderr)
            raise SystemExit(2)
        seen.add(case_id)
        items.append(item)
    return items, skipped


def main(argv: list[str]) -> int:
    xlsx = Path(argv[0]) if len(argv) > 0 else DEFAULT_XLSX
    out = Path(argv[1]) if len(argv) > 1 else DEFAULT_OUT
    if not xlsx.exists():
        print(f"workbook mancante: {xlsx}", file=sys.stderr)
        return 2
    items, skipped = rows_to_items(xlsx)
    if not items:
        print(
            "nessuna label umana nel foglio: gold_set.jsonl NON scritto "
            f"(righe etichettabili saltate: {len(skipped)})",
            file=sys.stderr,
        )
        return 1
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as fh:
        for item in items:
            fh.write(json.dumps(item, ensure_ascii=False) + "\n")
    per_family = Counter(item["family"] for item in items)
    print(f"scritto: {out} ({len(items)} casi validati)")
    for family in FAMILIES:
        done = per_family.get(family, 0)
        gap = TARGET_PER_FAMILY - done
        flag = "OK" if gap <= 0 else f"gap {gap}"
        print(f"  {family:8s} {done:3d}/{TARGET_PER_FAMILY}  {flag}")
    print(f"righe senza label (saltate): {len(skipped)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

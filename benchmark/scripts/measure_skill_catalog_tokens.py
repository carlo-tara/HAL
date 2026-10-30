#!/usr/bin/env python3
"""Misura il risparmio token del catalogo skill compatto (voce ToDo 2026-10-28).

Evidenza per le voci su tool-search e Cache L1: baseline di prompt token in
funzione del numero di skill dichiarate (descrizioni integrali vs righe
nome+keyword). Output JSON in benchmark/events/skill_catalog_tokens.json.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from router import catalog_token_report, load_skill_catalog


def main() -> int:
    catalog = load_skill_catalog()
    if not catalog:
        print("Nessuna skill nel catalogo", file=sys.stderr)
        return 1
    report = catalog_token_report(catalog)
    payload: dict[str, object] = {
        **report,
        "catalog_root": str(Path(".agents/skills").resolve()),
    }
    out = Path(__file__).resolve().parents[1] / "events" / "skill_catalog_tokens.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(payload, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

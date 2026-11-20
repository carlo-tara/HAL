#!/usr/bin/env python3
"""consumers_list.py — lettura della lista canonica dei consumer HAL.

Single source of truth: agents/consumers.list (un path assoluto per riga, '#' =
commento, righe vuote ignorate). Ogni tool HAL che deve iterare i consumer usa
load_consumers() invece di hardcodare path: le tre liste preesistenti erano
divergenti (hal-contract.py 11 repo, prune-local-commands.py 11,
sync-consumer-stale.sh 10 → 19 unici) e lasciavano fuori i consumer con più
mount residui — pickwaise (41), liberating.it (18), gDrive_ops (2), misurati
da `hal-contract.py` in dry-run — che restavano invisibili al fence.

CLI (report + validazione):
    python3 agents/scripts/consumers_list.py [--strict] [--paths]

--strict esce 1 se un path listato non esiste; il Makefile lo espone come
`make consumers-list` (report; `STRICT=1` per il gate). --paths stampa solo i
path (consumo da shell).
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

LIST_RELPATH = Path("agents") / "consumers.list"


def hal_root() -> Path:
    """Radice canonica HAL: $HAL_ROOT se impostato, altrimenti dedotta da __file__."""
    env = os.environ.get("HAL_ROOT")
    if env:
        return Path(env).resolve()
    return Path(__file__).resolve().parents[2]


def list_path(root: Path | None = None) -> Path:
    """Path assoluto di agents/consumers.list dentro la radice canonica."""
    return (root or hal_root()) / LIST_RELPATH


def load_consumers(root: Path | None = None) -> list[str]:
    """Path dei consumer in ordine di lista, deduplicati (list[str]).

    Nessuna verifica di esistenza: ogni tool HAL gestisce i path mancanti con il
    proprio messaggio. La validazione sta nella CLI (--strict).
    """
    path = list_path(root)
    try:
        raw = path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(
            f"ERRORE: lista canonica dei consumer assente: {path}"
        ) from exc
    out: list[str] = []
    for line in raw.splitlines():
        entry = line.split("#", 1)[0].strip()
        if entry and entry not in out:
            out.append(entry)
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Report/validazione di agents/consumers.list"
    )
    ap.add_argument(
        "--strict", action="store_true", help="esce 1 se un path listato non esiste"
    )
    ap.add_argument(
        "--paths", action="store_true", help="stampa solo i path (per pipe bash)"
    )
    args = ap.parse_args(argv)

    consumers = load_consumers()
    if args.paths:
        for c in consumers:
            print(c)
        return 0

    hal = hal_root()
    print(f"consumers.list — {list_path()}")
    print(f"canonico: {hal} — consumer: {len(consumers)}")
    missing: list[str] = []
    for c in consumers:
        p = Path(c)
        ok = p.is_dir()
        if not ok:
            missing.append(c)
        note = "  <-- canonico: rimuoverlo dalla lista" if p.resolve() == hal else ""
        print(f"  [{'OK     ' if ok else 'MISSING'}] {c}{note}")
    if missing:
        print(f"ATTENZIONE: {len(missing)} path inesistenti: {', '.join(missing)}")
        if args.strict:
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

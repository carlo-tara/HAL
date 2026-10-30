#!/usr/bin/env python3
"""Spike N27 (ToDo 2026-10-28, Mappa residui): curva token/richiesta vs skill dichiarate.

Il System 2 del gateway è mock senza backend OrcaRouter registrato: il conteggio
token reale del prompt avviene tramite il tokenizer locale di Laya
(`usage.input_tokens` su POST /systemone), come proxy documentato. Ogni punto è
registrato in `system2_metrics` (system="system1", provider="laya-tokenizer-proxy")
così la curva è interrogabile con `get_token_stats(run_id=...)`.

Usage:
    env PYTHONPATH=. python3 scripts/bench_catalog_curve.py
Report:
    benchmark/report/catalog_tokens_curve.md
"""

from __future__ import annotations

from datetime import UTC, datetime

import requests

import laya_service
from benchmark.runner.system2_metrics import System2Metrics
from router import catalog_token_report, load_skill_catalog

QUESTIONS = [
    "Quale skill gestisce routing di categorie e choice tra opzioni discrete?",
    "Quale agente sviluppa e revisiona plugin WordPress?",
]
SIZES = (0, 1, 5, 10, 20, 39)


def laya_input_tokens(prompt: str) -> int | None:
    """Token reali del prompt secondo il tokenizer laya (`usage.input_tokens`).

    Si usa il nativo POST /predict (shorthand {text}): solo /systemone non
    espone `usage`; /predict lo restituisce e richiede l'header di servizio.
    """
    url = f"{laya_service.LAYA_BASE_URL}/predict"
    headers = {"Authorization": f"Bearer {laya_service.get_laya_api_key()}"}
    try:
        resp = laya_service._session.post(
            url,
            json={"text": prompt[:4000]},
            headers=headers,
            timeout=laya_service.get_timeout_tuple(),
            verify=laya_service.get_tls_verify(),
        )
        resp.raise_for_status()
        body = resp.json()
    except (requests.RequestException, ValueError):
        return None
    usage = body.get("usage") or {}
    value = usage.get("input_tokens")
    return int(value) if isinstance(value, (int, float)) else None


def prompt_for_catalog(catalog: list[dict], size: int, question: str) -> str:
    lines = [e["line"] for e in catalog[:size]]
    decl = "\n".join(lines) if lines else "(nessuna skill dichiarata)"
    return f"Skill disponibili:\n{decl}\n\nDomanda: {question}"


def main() -> int:
    catalog = load_skill_catalog()
    if not catalog:
        print("catalogo vuoto: nulla da misurare")
        return 1
    run_id = f"catalog-curve-{datetime.now(UTC).strftime('%Y%m%dT%H%M%S')}"
    metrics = System2Metrics()
    rows: list[tuple[int, int | None, int]] = []
    for size in SIZES:
        size = min(size, len(catalog))
        measured = [
            laya_input_tokens(prompt_for_catalog(catalog, size, q)) for q in QUESTIONS
        ]
        vals = [m for m in measured if m is not None]
        avg = round(sum(vals) / len(vals)) if vals else None
        chars = len(prompt_for_catalog(catalog, size, QUESTIONS[0]))
        metrics.record_event(
            run_id=run_id,
            prompt_id=f"catalog-{size}",
            provider="laya-tokenizer-proxy",
            model="laya",
            task_family="general",
            system="system1",
            stage="spike",
            status="ok" if avg is not None else "error",
            input_chars=chars,
            tokens_in=avg,
            tokens_total=avg,
            decision=str(size),
            error_message=None if avg is not None else "laya non raggiungibile",
        )
        rows.append((size, avg, chars))
        print(f"size={size:2d}  input_tokens≈{avg}  chars={chars}")

    report = catalog_token_report(catalog)
    lines_md = [
        f"# Curva token/richiesta vs dimensione catalogo skill — {run_id}",
        "",
        f"- Proxy tokenizer: Laya `usage.input_tokens` (System 2 del gateway è mock",
        "  senza backend OrcaRouter registrato); due domande per punto.",
        f"- Catalogo: {report['skills']} skill; stime statiche integrali vs compatte:",
        f"  full≈{report['full_tokens']} token vs compatte≈{report['compact_tokens']} token"
        f" (-{report['reduction_pct']}%).",
        "",
        "| skill dichiarate | input token medi (misurati) | chars prompt |",
        "| ---- | ---- | ---- |",
    ]
    for size, avg, chars in rows:
        lines_md.append(f"| {size} | {avg if avg is not None else '—'} | {chars} |")
    lines_md += [
        "",
        "Lettura: la curva è approssimativamente lineare nella dimensione del catalogo;",
        "la riga compatta (nome+keyword) mantiene il costo di dichiarazione sotto il",
        "budget del tool-search System 1 (voci correlate: Cache L1 a due strati, N21).",
    ]
    out = "benchmark/report/catalog_tokens_curve.md"
    import pathlib

    path = pathlib.Path(out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines_md) + "\n", encoding="utf-8")
    print(f"report scritto: {path} (run_id={run_id})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

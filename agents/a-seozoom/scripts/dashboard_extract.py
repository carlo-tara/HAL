#!/usr/bin/env python3
"""Export SeoZoom project dashboard widgets to seozoom/dashboard/."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

from csv_mappers import (
    andamento_annuale_csv,
    andamento_dominio_flat,
    backlink_csv,
    distribuzione_keyword_flat,
    generic_csv,
    idee_articoli_csv,
    keywordsmetrics_flat,
    keywordstrend_flat,
    metriche_json,
    pagine_competitor_csv,
    previsione_traffico_flat,
)
from seozoom_api import SeoZoomClient
from seozoom_lib import domain_underscore


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _run_step(results: dict[str, str], key: str, fn: Callable[[], None]) -> None:
    try:
        fn()
        results[key] = "ok"
    except Exception as exc:  # noqa: BLE001
        results[key] = f"error:{exc.__class__.__name__}:{exc}"


def dashboard_filenames(manifest: dict[str, Any]) -> dict[str, str]:
    domain = manifest.get("domain_slug", "example.it")
    return {
        "backlink": f"{domain}_backlink.csv",
        "backlink_summary": f"{domain}_backlink_summary.json",
        "andamento_dominio": f"{domain}_andamento_dominio.json",
        "andamento_dominio_flat": f"{domain}_andamento_dominio_flat.csv",
        "distribuzione": f"{domain}_distribuzione_keyword_storica.json",
        "distribuzione_flat": f"{domain}_distribuzione_keyword_storica_flat.csv",
        "metriche": f"{domain}_metriche.json",
        "andamento_annuale": f"{domain}_andamento_annuale.csv",
        "pagine_competitor": f"{domain}_pagine_competitor.csv",
        "competitor_trends": f"{domain}_competitor_trends.csv",
        "previsione": f"{domain}_previsione_traffico.json",
        "previsione_flat": f"{domain}_previsione_traffico_flat.csv",
        "posizionamento": f"{domain}_posizionamento_monitorate.json",
        "posizionamento_flat": f"{domain}_posizionamento_monitorate_flat.csv",
        "keyword_progetto": f"{domain}_andamento_keyword_progetto.json",
        "keyword_progetto_flat": f"{domain}_andamento_keyword_progetto_flat.csv",
        "idee_articoli": f"{domain}_idee_articoli.csv",
        "keyup": f"{domain}_dashboard_keywords_up.csv",
        "keydown": f"{domain}_dashboard_keywords_down.csv",
    }


def export_dashboard(
    client: SeoZoomClient,
    out_dir: Path,
    manifest: dict[str, Any],
) -> dict[str, str]:
    """Export dashboard widgets into out_dir (typically seozoom/dashboard/)."""
    results: dict[str, str] = {}
    names = dashboard_filenames(manifest)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Warm once: loads AJAX widgets + previsione JS globals
    _run_step(results, "warm_dashboard", client.warm_dashboard)
    if results.get("warm_dashboard", "").startswith("error:"):
        return results

    trend_cache: list[dict[str, Any]] = []

    def load_trend() -> list[dict[str, Any]]:
        nonlocal trend_cache
        if not trend_cache:
            trend_cache = client.dashboard_site_trend()
        return trend_cache

    def write_metriche() -> None:
        stats = client.dashboard_domainstats()
        extras = {
            "keywordsstats": client.dashboard_keywords_stats(),
            "trafficstats": client.dashboard_traffic_stats(),
            "pianotrimestrale": client.dashboard_piano_trimestrale(),
        }
        content = metriche_json(stats, extras=extras)
        if not stats:
            raise RuntimeError("empty domainstats")
        _write(out_dir / names["metriche"], content)

    def write_trend_bundle() -> None:
        rows = load_trend()
        if not rows:
            raise RuntimeError("empty site trend")
        _write(out_dir / names["andamento_dominio"], json.dumps(rows, indent=2, ensure_ascii=False) + "\n")
        _write(out_dir / names["andamento_dominio_flat"], andamento_dominio_flat(rows))
        dist = [
            {
                "datarilievo": r.get("datarilievo"),
                "1a3": r.get("1a3"),
                "4a6": r.get("4a6"),
                "7a10": r.get("7a10"),
                "p1": r.get("p1"),
                "p2": r.get("p2"),
                "p3": r.get("p3"),
                "p4": r.get("p4"),
                "p5": r.get("p5"),
                "totk": r.get("totk"),
                "oltre5": r.get("oltre5"),
            }
            for r in rows
        ]
        _write(out_dir / names["distribuzione"], json.dumps(dist, indent=2, ensure_ascii=False) + "\n")
        _write(out_dir / names["distribuzione_flat"], distribuzione_keyword_flat(rows))
        annuale = andamento_annuale_csv(rows)
        if not annuale.strip():
            raise RuntimeError("empty annual aggregate")
        _write(out_dir / names["andamento_annuale"], annuale)

    def write_backlink() -> None:
        payload = client.dashboard_backlink_counters()
        if not payload:
            raise RuntimeError("empty backlink counters")
        _write(out_dir / names["backlink_summary"], json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
        csv_text = backlink_csv(payload)
        if not csv_text.strip():
            raise RuntimeError("empty backlink csv")
        _write(out_dir / names["backlink"], csv_text)

    def write_idee() -> None:
        rows = client.dashboard_suggest_articles()
        text = idee_articoli_csv(rows)
        if not text.strip():
            raise RuntimeError("empty article ideas")
        _write(out_dir / names["idee_articoli"], text)

    def write_pagine_competitor() -> None:
        suggestions = client.dashboard_copilot_suggestions()
        text = pagine_competitor_csv(suggestions)
        if not text.strip():
            # still write empty-ish when no COMPETITOR-PAGES; mark empty
            raise RuntimeError("no COMPETITOR-PAGES suggestions")
        _write(out_dir / names["pagine_competitor"], text)
        trends = client.dashboard_competitor_stats()
        if trends:
            _write(out_dir / names["competitor_trends"], generic_csv(trends))

    def write_previsione() -> None:
        payload = client.dashboard_traffic_forecast()
        if not payload.get("seriesPrevisionData") and payload.get("totalTraffic") is None:
            raise RuntimeError("previsione traffico globals empty")
        _write(out_dir / names["previsione"], json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
        _write(out_dir / names["previsione_flat"], previsione_traffico_flat(payload))

    def write_posizionamento() -> None:
        series = client.dashboard_keywords_metrics()
        if not series:
            raise RuntimeError("empty keywordsmetrics")
        _write(out_dir / names["posizionamento"], json.dumps(series, indent=2, ensure_ascii=False) + "\n")
        _write(out_dir / names["posizionamento_flat"], keywordsmetrics_flat(series))

    def write_keyword_progetto() -> None:
        rows = client.dashboard_keywords_trend()
        if not rows:
            raise RuntimeError("empty keywordstrend")
        _write(out_dir / names["keyword_progetto"], json.dumps(rows, indent=2, ensure_ascii=False) + "\n")
        _write(out_dir / names["keyword_progetto_flat"], keywordstrend_flat(rows))

    def write_keyup_down() -> None:
        up = client.dashboard_keyup()
        down = client.dashboard_keydown()
        if up:
            _write(out_dir / names["keyup"], generic_csv(up))
        if down:
            _write(out_dir / names["keydown"], generic_csv(down))
        if not up and not down:
            raise RuntimeError("empty keyup/keydown")

    _run_step(results, names["metriche"], write_metriche)
    _run_step(results, "site_trend_bundle", write_trend_bundle)
    if results.get("site_trend_bundle") == "ok":
        results[names["andamento_dominio"]] = "ok"
        results[names["andamento_dominio_flat"]] = "ok"
        results[names["distribuzione"]] = "ok"
        results[names["distribuzione_flat"]] = "ok"
        results[names["andamento_annuale"]] = "ok"
    _run_step(results, names["backlink"], write_backlink)
    _run_step(results, names["idee_articoli"], write_idee)
    _run_step(results, names["pagine_competitor"], write_pagine_competitor)
    _run_step(results, names["previsione"], write_previsione)
    _run_step(results, names["posizionamento"], write_posizionamento)
    _run_step(results, names["keyword_progetto"], write_keyword_progetto)
    _run_step(results, "dashboard_keyup_down", write_keyup_down)

    # Note: OnPage SEO stays in parent seozoom/ via existing export_globals
    results["onpage_note"] = f"see parent {domain_underscore(manifest.get('domain_slug', 'example.it'))}_OnPageSEO.csv"

    return results

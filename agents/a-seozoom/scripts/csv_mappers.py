#!/usr/bin/env python3
"""Convert SeoZoom API payloads to CSV text."""
from __future__ import annotations

import csv
import io
import json
from typing import Any, Iterable


def rows_to_csv(rows: Iterable[dict[str, Any]], fieldnames: list[str] | None = None) -> str:
    rows = list(rows)
    if not rows:
        return ""
    if fieldnames is None:
        fieldnames = sorted({k for r in rows for k in r.keys()})
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    for row in rows:
        writer.writerow({k: row.get(k, "") for k in fieldnames})
    return buf.getvalue()


def monitored_csv(rows: list[dict[str, Any]]) -> str:
    out = []
    for r in rows:
        out.append(
            {
                "Keyword": r.get("keyword", ""),
                "POS": r.get("posizione", ""),
                "P.M.": r.get("posizionemedia", r.get("posizione", "")),
                "Var": r.get("variazione", ""),
                "Lingua": (r.get("lingua", "") or "").replace("it", "it"),
                "Ext": r.get("estensione", ""),
                "Localcode": r.get("localcode", ""),
                "Vol.": r.get("volumericerca", ""),
                "Traffico": r.get("traffico", r.get("svol", "")),
                "Cambio URL": r.get("cambiourl", 0),
                "URL": r.get("url", ""),
                "Andamento": r.get("andamento", ""),
                "SERP Features": r.get("features", r.get("serpfeatures", "")),
                "SEO": r.get("seoscore", ""),
                "CPC": r.get("cpcapprox", ""),
                "Concorrenza": r.get("concorrenzappc", ""),
                "Keyword Difficulty": r.get("keydiff", ""),
                "Keyword Opportunity": r.get("opportunity", ""),
                "Tags": r.get("tag", ""),
            }
        )
    fields = [
        "Keyword", "POS", "P.M.", "Var", "Lingua", "Ext", "Localcode", "Vol.", "Traffico",
        "Cambio URL", "URL", "Andamento", "SERP Features", "SEO", "CPC", "Concorrenza",
        "Keyword Difficulty", "Keyword Opportunity", "Tags",
    ]
    return rows_to_csv(out, fields)


def keyword_all_csv(rows: list[dict[str, Any]]) -> str:
    out = []
    for r in rows:
        out.append(
            {
                "Keyword": r.get("keyword", ""),
                "Pos": r.get("posizione", ""),
                "Var": r.get("variazione", ""),
                "Volume": r.get("volumericerca", ""),
                "Traffico Stimato": r.get("volumestimato", ""),
                "Keyword Difficulty": r.get("keydiff", ""),
                "Keyword Opportunity": r.get("opportunity", ""),
                "Intent": r.get("intent", ""),
                "URL": r.get("url", ""),
                "SERP Features": r.get("serpfeatures", ""),
            }
        )
    return rows_to_csv(out)


def per_url_keywords_csv(rows: list[dict[str, Any]]) -> str:
    out = []
    for r in rows:
        out.append(
            {
                "Keyword": r.get("keyword", ""),
                "Pos": r.get("posizione", ""),
                "Var": r.get("variazione", ""),
                "Volume": r.get("volumericerca", ""),
                "Traffico Stimato": r.get("svol", ""),
                "Keyword Difficulty": r.get("keydiff", ""),
                "Keyword Opportunity": r.get("opportunity", ""),
            }
        )
    return rows_to_csv(out)


def pages_csv(rows: list[dict[str, Any]], extra_map: dict[str, str] | None = None) -> str:
    extra_map = extra_map or {}
    out = []
    for r in rows:
        row = dict(r)
        for src, dst in extra_map.items():
            if src in row:
                row[dst] = row.pop(src)
        out.append(row)
    return rows_to_csv(out)


def onpage_csv(rows: list[dict[str, Any]]) -> str:
    out = []
    for r in rows:
        out.append(
            {
                "Keyword": r.get("keyword", r.get("Keyword", "")),
                "Volume ricerca": r.get("volume", r.get("Volume ricerca", "")),
                "Pos": r.get("pos", r.get("Pos", "")),
                "Var": r.get("var", r.get("Var", "")),
                "URL": r.get("url", r.get("URL", "")),
                "SEO": r.get("seo", r.get("SEO", "")),
                "Tag": r.get("tag", r.get("Tag", "")),
            }
        )
    fields = ["Keyword", "Volume ricerca", "Pos", "Var", "URL", "SEO", "Tag"]
    return rows_to_csv(out, fields)


def content_gap_ai_csv(rows: list[dict[str, Any]]) -> str:
    out = []
    for r in rows:
        out.append(
            {
                "Keyword": r.get("keyword", ""),
                "Intent": "Informational",
                "Keyword Difficulty": r.get("keydiff", ""),
                "Keyword Opportunity": r.get("opportunity", ""),
                "CPC": r.get("cpcapprox", ""),
                "Volume ricerca": r.get("volumericerca", ""),
                "Stagionalità": "",
            }
        )
    fields = [
        "Keyword", "Intent", "Keyword Difficulty", "Keyword Opportunity",
        "CPC", "Volume ricerca", "Stagionalità",
    ]
    return rows_to_csv(out, fields)


def questions_txt(questions: list[str]) -> str:
    return "\n".join(q.strip() for q in questions if q and q.strip()) + ("\n" if questions else "")


def generic_csv(rows: list[Any]) -> str:
    if not rows:
        return ""
    if isinstance(rows[0], dict):
        return rows_to_csv(rows)
    return rows_to_csv([{"value": json.dumps(r, ensure_ascii=False)} for r in rows])


def timeseries_to_flat_csv(
    points: list[dict[str, Any]],
    fieldnames: list[str] | None = None,
) -> str:
    """Normalize chart/table points into a long CSV (date, metric, value or wide rows)."""
    if not points:
        return ""
    if fieldnames is None:
        preferred = [
            "date", "metric", "value", "datarilievo", "name", "series",
            "x", "y", "totk", "svol", "za", "zo", "zs", "zt",
            "1a3", "4a6", "7a10", "p1", "p2", "p3", "p4", "p5",
        ]
        present = sorted({k for r in points for k in r.keys()})
        ordered = [c for c in preferred if c in present]
        ordered.extend(c for c in present if c not in ordered)
        fieldnames = ordered
    return rows_to_csv(points, fieldnames)


def metriche_json(payload: dict[str, Any], extras: dict[str, Any] | None = None) -> str:
    """Stable site metrics schema (ZA/ZT/ZS/ZO) from domainstats (+ optional extras)."""
    data = {
        "ZA": _num(payload.get("zoomauthority")),
        "ZT": _num(payload.get("za_trust")),
        "ZS": _num(payload.get("za_stability")),
        "ZO": _num(payload.get("za_opportunity")),
        "traffico": _num(payload.get("trafficodominio")),
        "var_traffico": _num(payload.get("variazionetrafficodominio")),
        "keyword": _num(payload.get("totk")),
        "p1": _num(payload.get("p1")),
        "p2": _num(payload.get("p2")),
        "p3": _num(payload.get("p3")),
        "p4": _num(payload.get("p4")),
        "p5": _num(payload.get("p5")),
        "pos_1_3": _num(payload.get("1a3")),
        "pos_4_6": _num(payload.get("4a6")),
        "pos_7_10": _num(payload.get("7a10")),
        "oltre5": _num(payload.get("oltre5")),
        "raw": payload,
    }
    if extras:
        data["extras"] = extras
    return json.dumps(data, indent=2, ensure_ascii=False) + "\n"


def _num(value: Any) -> Any:
    if value is None or value == "":
        return None
    try:
        if isinstance(value, str) and "." in value:
            return float(value)
        return int(value)
    except (TypeError, ValueError):
        return value


def _strip_html(text: str) -> str:
    import re

    t = re.sub(r"<[^>]+>", " ", text or "")
    return re.sub(r"\s+", " ", t).strip()


def backlink_csv(payload: dict[str, Any]) -> str:
    """Flatten links/counters summary + top pages/anchors into CSV rows."""
    summary = payload.get("summary") or []
    if isinstance(summary, dict):
        summary = [summary]
    rows: list[dict[str, Any]] = []
    for s in summary:
        if not isinstance(s, dict):
            continue
        base = {
            "tipo": "summary",
            "target": s.get("target", ""),
            "backlinks": s.get("backlinks", ""),
            "refdomains": s.get("refdomains", ""),
            "dofollow_backlinks": s.get("dofollow_backlinks", ""),
            "nofollow_backlinks": s.get("nofollow_backlinks", ""),
            "inlink_rank": s.get("inlink_rank", ""),
            "domain_inlink_rank": s.get("domain_inlink_rank", ""),
            "pages_with_backlinks": s.get("pages_with_backlinks", ""),
            "anchors": s.get("anchors", ""),
            "url": "",
            "anchor": "",
        }
        rows.append(base)
        for page in s.get("top_pages_by_backlinks") or []:
            rows.append(
                {
                    "tipo": "top_page",
                    "target": s.get("target", ""),
                    "backlinks": page.get("backlinks", ""),
                    "refdomains": "",
                    "dofollow_backlinks": "",
                    "nofollow_backlinks": "",
                    "inlink_rank": "",
                    "domain_inlink_rank": "",
                    "pages_with_backlinks": "",
                    "anchors": "",
                    "url": page.get("url", ""),
                    "anchor": "",
                }
            )
        for anc in s.get("top_anchors_by_backlinks") or []:
            rows.append(
                {
                    "tipo": "top_anchor",
                    "target": s.get("target", ""),
                    "backlinks": anc.get("backlinks", ""),
                    "refdomains": "",
                    "dofollow_backlinks": "",
                    "nofollow_backlinks": "",
                    "inlink_rank": "",
                    "domain_inlink_rank": "",
                    "pages_with_backlinks": "",
                    "anchors": "",
                    "url": "",
                    "anchor": anc.get("anchor", ""),
                }
            )
    fields = [
        "tipo", "target", "backlinks", "refdomains", "dofollow_backlinks",
        "nofollow_backlinks", "inlink_rank", "domain_inlink_rank",
        "pages_with_backlinks", "anchors", "url", "anchor",
    ]
    return rows_to_csv(rows, fields)


def andamento_annuale_csv(trend_rows: list[dict[str, Any]]) -> str:
    """Aggregate weekly site-trend rows into yearly summary."""
    by_year: dict[str, list[dict[str, Any]]] = {}
    for row in trend_rows:
        date = str(row.get("datarilievo") or "")
        year = date[:4] if len(date) >= 4 else ""
        if not year:
            continue
        by_year.setdefault(year, []).append(row)
    out = []
    for year in sorted(by_year):
        rows = by_year[year]
        last = rows[-1]
        out.append(
            {
                "anno": year,
                "rilievi": len(rows),
                "traffico_ultimo": last.get("svol", ""),
                "keyword_ultimo": last.get("totk", ""),
                "ZA_ultimo": last.get("za", ""),
                "ZT_ultimo": last.get("zt", ""),
                "ZS_ultimo": last.get("zs", ""),
                "ZO_ultimo": last.get("zo", ""),
                "pos_1_3_ultimo": last.get("1a3", ""),
                "pos_4_6_ultimo": last.get("4a6", ""),
                "pos_7_10_ultimo": last.get("7a10", ""),
                "data_ultimo": last.get("datarilievo", ""),
            }
        )
    fields = [
        "anno", "rilievi", "traffico_ultimo", "keyword_ultimo",
        "ZA_ultimo", "ZT_ultimo", "ZS_ultimo", "ZO_ultimo",
        "pos_1_3_ultimo", "pos_4_6_ultimo", "pos_7_10_ultimo", "data_ultimo",
    ]
    return rows_to_csv(out, fields)


def idee_articoli_csv(rows: list[dict[str, Any]]) -> str:
    out = []
    for r in rows:
        out.append(
            {
                "Keyword": r.get("keyword", ""),
                "Volume": r.get("volumericerca", ""),
                "Keyword Difficulty": r.get("keydiff", ""),
                "Keyword Opportunity": r.get("opportunity", ""),
                "Pos competitor": r.get("pos_competitor", ""),
                "Pos sito": r.get("pos_sito", ""),
                "URL competitor": r.get("urlc", ""),
                "URL sito": r.get("urls", "") or "",
                "Lingua": r.get("lingua", ""),
            }
        )
    fields = [
        "Keyword", "Volume", "Keyword Difficulty", "Keyword Opportunity",
        "Pos competitor", "Pos sito", "URL competitor", "URL sito", "Lingua",
    ]
    return rows_to_csv(out, fields)


def pagine_competitor_csv(suggestions: list[dict[str, Any]]) -> str:
    import re

    out = []
    for s in suggestions:
        if s.get("category") and s.get("category") != "COMPETITOR-PAGES":
            continue
        msg = s.get("message") or ""
        plain = _strip_html(msg)
        comp = ""
        kw = ""
        m_comp = re.search(r"competitor\s+([^\s]+)", plain, re.I)
        if m_comp:
            comp = m_comp.group(1).strip(".,;")
        m_kw = re.search(r"keyword\s+(.+?)\s+che ha", plain, re.I)
        if m_kw:
            kw = m_kw.group(1).strip()
        out.append(
            {
                "data": s.get("data", ""),
                "priority": s.get("priority", ""),
                "competitor": comp,
                "keyword": kw,
                "message": plain,
                "id": s.get("id", ""),
            }
        )
    fields = ["data", "priority", "competitor", "keyword", "message", "id"]
    return rows_to_csv(out, fields)


def distribuzione_keyword_flat(trend_rows: list[dict[str, Any]]) -> str:
    points = []
    for row in trend_rows:
        date = row.get("datarilievo", "")
        for metric in ("1a3", "4a6", "7a10", "p1", "p2", "p3", "p4", "p5", "totk", "oltre5"):
            if metric in row:
                points.append({"date": date, "metric": metric, "value": row.get(metric)})
    return timeseries_to_flat_csv(points, ["date", "metric", "value"])


def andamento_dominio_flat(trend_rows: list[dict[str, Any]]) -> str:
    points = []
    for row in trend_rows:
        date = row.get("datarilievo", "")
        for metric in ("svol", "totk", "za", "zo", "zs", "zt", "volm", "cpcval"):
            if metric in row:
                points.append({"date": date, "metric": metric, "value": row.get(metric)})
    return timeseries_to_flat_csv(points, ["date", "metric", "value"])


def keywordsmetrics_flat(series_list: list[dict[str, Any]]) -> str:
    """Flatten keywordsmetrics area series to CSV."""
    from datetime import datetime, timezone

    points = []
    for series in series_list:
        name = series.get("name", "")
        for pt in series.get("data") or []:
            if not isinstance(pt, dict):
                continue
            ts = pt.get("x")
            date = ""
            if isinstance(ts, (int, float)):
                date = datetime.fromtimestamp(ts / 1000, tz=timezone.utc).strftime("%Y-%m-%d")
            base = {
                "date": date,
                "series": name,
                "y": pt.get("y", ""),
                "totk": pt.get("totk", ""),
                "1a3": pt.get("1a3", ""),
                "4a6": pt.get("4a6", ""),
                "7a10": pt.get("7a10", ""),
                "static": pt.get("static", ""),
            }
            points.append(base)
    return timeseries_to_flat_csv(
        points,
        ["date", "series", "y", "totk", "1a3", "4a6", "7a10", "static"],
    )


def keywordstrend_flat(rows: list[dict[str, Any]]) -> str:
    return timeseries_to_flat_csv(
        [
            {
                "date": r.get("datarilievo", ""),
                "p1": r.get("p1", ""),
                "altre": r.get("altre", ""),
            }
            for r in rows
        ],
        ["date", "p1", "altre"],
    )


def previsione_traffico_flat(payload: dict[str, Any]) -> str:
    """Month index rows for actual vs forecast traffic."""
    actual = payload.get("seriesActualTrafficData") or []
    previs = payload.get("seriesPrevisionData") or []
    months = [
        "M-11", "M-10", "M-9", "M-8", "M-7", "M-6",
        "M-5", "M-4", "M-3", "M-2", "M-1", "M0",
    ]
    points = []
    for i in range(max(len(actual), len(previs), 12)):
        label = months[i] if i < len(months) else f"M{i}"
        act = actual[i] if i < len(actual) else ""
        prev = previs[i] if i < len(previs) else {}
        if isinstance(prev, dict):
            prev_y = prev.get("y", "")
            prev_perc = prev.get("perc", "")
        else:
            prev_y = prev
            prev_perc = ""
        points.append(
            {
                "month_index": label,
                "traffico_attuale": act,
                "traffico_previsione": prev_y,
                "var_perc_previsione": prev_perc,
            }
        )
    return timeseries_to_flat_csv(
        points,
        ["month_index", "traffico_attuale", "traffico_previsione", "var_perc_previsione"],
    )

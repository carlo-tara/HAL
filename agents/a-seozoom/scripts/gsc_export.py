#!/usr/bin/env python3
"""Export Google Search Console data to seo/YYMMDD/gsc_*.csv."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from analytics_lib import (  # noqa: E402
    apply_google_credentials_env,
    date_range,
    google_credentials,
    load_analytics_env,
    period_suffix,
    resolve_project_paths,
    write_csv,
)
from seozoom_lib import default_project_root  # noqa: E402


def fetch_search_analytics(service, site_url: str, start: str, end: str, dimensions: list[str], row_limit: int = 25000):
    body = {
        "startDate": start,
        "endDate": end,
        "dimensions": dimensions,
        "rowLimit": row_limit,
        "dataState": "final",
    }
    response = service.searchanalytics().query(siteUrl=site_url, body=body).execute()
    return response.get("rows", [])


def rows_query_page(raw_rows: list) -> list[dict]:
    out = []
    for row in raw_rows:
        keys = row.get("keys", [])
        out.append(
            {
                "query": keys[0] if len(keys) > 0 else "",
                "page": keys[1] if len(keys) > 1 else "",
                "clicks": row.get("clicks", 0),
                "impressions": row.get("impressions", 0),
                "ctr": row.get("ctr", 0),
                "position": row.get("position", 0),
            }
        )
    return out


def rows_page_only(raw_rows: list) -> list[dict]:
    out = []
    for row in raw_rows:
        keys = row.get("keys", [])
        out.append(
            {
                "page": keys[0] if keys else "",
                "clicks": row.get("clicks", 0),
                "impressions": row.get("impressions", 0),
                "ctr": row.get("ctr", 0),
                "position": row.get("position", 0),
            }
        )
    return out


def export_gsc(project_root: Path, export_date: str | None, days: int) -> dict:
    from googleapiclient.discovery import build

    root, out_dir = resolve_project_paths(project_root, export_date)
    env = load_analytics_env(root)
    apply_google_credentials_env(root, env)

    site_url = env.get("GSC_SITE_URL")
    if not site_url:
        raise ValueError("GSC_SITE_URL mancante in .env del progetto")
    creds = google_credentials(env, root)
    service = build("searchconsole", "v1", credentials=creds, cache_discovery=False)

    start_d, end_d = date_range(days)
    start_s, end_s = start_d.isoformat(), end_d.isoformat()
    suffix = period_suffix(start_d, end_d)

    query_rows = rows_query_page(
        fetch_search_analytics(service, site_url, start_s, end_s, ["query", "page"])
    )
    page_rows = rows_page_only(fetch_search_analytics(service, site_url, start_s, end_s, ["page"]))

    queries_path = out_dir / f"gsc_queries_{suffix}.csv"
    pages_path = out_dir / f"gsc_pages_{suffix}.csv"

    n_queries = write_csv(
        queries_path,
        ["query", "page", "clicks", "impressions", "ctr", "position"],
        query_rows,
    )
    n_pages = write_csv(
        pages_path,
        ["page", "clicks", "impressions", "ctr", "position"],
        page_rows,
    )

    return {
        "ok": n_queries > 0 or n_pages > 0,
        "out_dir": str(out_dir),
        "site_url": site_url,
        "period": suffix,
        "gsc_queries": str(queries_path),
        "gsc_queries_rows": n_queries,
        "gsc_pages": str(pages_path),
        "gsc_pages_rows": n_pages,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Export GSC data to seo/YYMMDD/")
    parser.add_argument("--project-root", type=Path, default=default_project_root())
    parser.add_argument("--date", help="Export folder YYMMDD (default: today)")
    parser.add_argument("--days", type=int, default=28, help="Lookback days (default: 28)")
    args = parser.parse_args()

    try:
        result = export_gsc(args.project_root, args.date, args.days)
    except Exception as exc:  # noqa: BLE001
        print(f"GSC export failed: {exc}", file=sys.stderr)
        return 1

    print(
        f"GSC export OK: {result['gsc_queries_rows']} query rows, "
        f"{result['gsc_pages_rows']} page rows -> {result['out_dir']}"
    )
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

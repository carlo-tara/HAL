#!/usr/bin/env python3
"""Export Cloudflare zone analytics to seo/YYMMDD/cf_*.csv."""
from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from analytics_lib import date_range, load_analytics_env, period_suffix, resolve_project_paths, write_csv  # noqa: E402
from seozoom_lib import default_project_root  # noqa: E402

CF_GRAPHQL = "https://api.cloudflare.com/client/v4/graphql"


def cf_datetime_range(start_d, end_d) -> tuple[str, str]:
    start = datetime.combine(start_d, datetime.min.time(), tzinfo=timezone.utc)
    end = datetime.combine(end_d + timedelta(days=1), datetime.min.time(), tzinfo=timezone.utc)
    return start.isoformat().replace("+00:00", "Z"), end.isoformat().replace("+00:00", "Z")


def fetch_http_requests(zone_id: str, token: str, start_iso: str, end_iso: str) -> list[dict]:
    query = """
    query HttpRequests($zoneTag: String!, $start: Time!, $end: Time!) {
      viewer {
        zones(filter: { zoneTag: $zoneTag }) {
          httpRequestsAdaptiveGroups(
            limit: 10000
            filter: { datetime_geq: $start, datetime_lt: $end }
            orderBy: [count_DESC]
          ) {
            count
            dimensions {
              clientRequestPath
              edgeResponseStatus
            }
          }
        }
      }
    }
    """
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {
        "query": query,
        "variables": {"zoneTag": zone_id, "start": start_iso, "end": end_iso},
    }
    resp = requests.post(CF_GRAPHQL, headers=headers, json=payload, timeout=120)
    resp.raise_for_status()
    data = resp.json()
    if data.get("errors"):
        raise RuntimeError(data["errors"])
    zones = data.get("data", {}).get("viewer", {}).get("zones", [])
    if not zones:
        return []
    return zones[0].get("httpRequestsAdaptiveGroups", [])


def export_cf(project_root: Path, export_date: str | None, days: int, min_404: int = 5) -> dict:
    root, out_dir = resolve_project_paths(project_root, export_date, source="cloudflare")
    env = load_analytics_env(root)

    token = env.get("CLOUDFLARE_API_TOKEN", "").strip()
    zone_id = env.get("CLOUDFLARE_ZONE_ID", "").strip()
    if not token or not zone_id:
        raise ValueError("CLOUDFLARE_API_TOKEN and CLOUDFLARE_ZONE_ID required in .env")

    # Cloudflare GraphQL httpRequestsAdaptiveGroups: max 1 day per query on many plans.
    effective_days = min(max(days, 1), 1)

    start_d, end_d = date_range(effective_days)
    start_iso, end_iso = cf_datetime_range(start_d, end_d)
    suffix = period_suffix(start_d, end_d)

    groups = fetch_http_requests(zone_id, token, start_iso, end_iso)
    aggregated: dict[tuple[str, int], int] = defaultdict(int)
    for group in groups:
        dims = group.get("dimensions", {})
        path = dims.get("clientRequestPath", "")
        status = int(dims.get("edgeResponseStatus", 0) or 0)
        aggregated[(path, status)] += int(group.get("count", 0))

    request_rows = [
        {"path": path, "status": status, "count": count}
        for (path, status), count in sorted(aggregated.items(), key=lambda x: -x[1])
    ]
    rows_404 = [r for r in request_rows if r["status"] == 404 and r["count"] >= min_404]

    requests_path = out_dir / f"cf_requests_{suffix}.csv"
    not_found_path = out_dir / f"cf_404_{suffix}.csv"

    n_requests = write_csv(requests_path, ["path", "status", "count"], request_rows)
    n_404 = write_csv(not_found_path, ["path", "status", "count"], rows_404)

    return {
        "ok": n_requests > 0,
        "out_dir": str(out_dir),
        "period": suffix,
        "cf_requests": str(requests_path),
        "cf_requests_rows": n_requests,
        "cf_404": str(not_found_path),
        "cf_404_rows": n_404,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Export Cloudflare analytics to seo/YYMMDD/")
    parser.add_argument("--project-root", type=Path, default=default_project_root())
    parser.add_argument("--date", help="Export folder YYMMDD (default: today)")
    parser.add_argument("--days", type=int, default=28)
    parser.add_argument("--min-404", type=int, default=5, help="Min 404 count to include in cf_404 CSV")
    args = parser.parse_args()

    try:
        result = export_cf(args.project_root, args.date, args.days, args.min_404)
    except Exception as exc:  # noqa: BLE001
        print(f"Cloudflare export failed: {exc}", file=sys.stderr)
        return 1

    print(
        f"CF export OK: {result['cf_requests_rows']} request rows, "
        f"{result['cf_404_rows']} 404 rows -> {result['out_dir']}"
    )
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

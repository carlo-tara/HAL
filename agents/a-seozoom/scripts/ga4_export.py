#!/usr/bin/env python3
"""Export GA4 Data API reports to seo/YYMMDD/ga4_*.csv."""
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


def run_ga4_report(client, property_id: str, dimensions: list[str], metrics: list[str], start: str, end: str, dimension_filter=None):
    from google.analytics.data_v1beta.types import DateRange, Dimension, Filter, FilterExpression, Metric, RunReportRequest

    request = RunReportRequest(
        property=f"properties/{property_id}",
        date_ranges=[DateRange(start_date=start, end_date=end)],
        dimensions=[Dimension(name=d) for d in dimensions],
        metrics=[Metric(name=m) for m in metrics],
        limit=10000,
    )
    if dimension_filter is not None:
        request.dimension_filter = dimension_filter

    response = client.run_report(request)
    rows = []
    for row in response.rows:
        item = {}
        for i, dim in enumerate(dimensions):
            item[dim] = row.dimension_values[i].value
        for i, met in enumerate(metrics):
            raw = row.metric_values[i].value
            if met in ("bounceRate", "engagementRate"):
                try:
                    item[met] = float(raw)
                except ValueError:
                    item[met] = 0.0
            elif met == "averageSessionDuration":
                try:
                    item[met] = float(raw)
                except ValueError:
                    item[met] = 0.0
            else:
                try:
                    item[met] = int(float(raw))
                except ValueError:
                    item[met] = 0
        rows.append(item)
    return rows


def export_ga4(project_root: Path, export_date: str | None, days: int) -> dict:
    from google.analytics.data_v1beta import BetaAnalyticsDataClient
    from google.analytics.data_v1beta.types import Filter, FilterExpression, FilterExpressionList

    root, out_dir = resolve_project_paths(project_root, export_date)
    env = load_analytics_env(root)
    apply_google_credentials_env(root, env)

    property_id = env.get("GA4_PROPERTY_ID", "").strip()
    if not property_id:
        raise ValueError("GA4_PROPERTY_ID missing in .env")

    creds = google_credentials(env, root)
    client = BetaAnalyticsDataClient(credentials=creds)

    start_d, end_d = date_range(days)
    start_s, end_s = start_d.isoformat(), end_d.isoformat()
    suffix = period_suffix(start_d, end_d)

    landing_dims = ["landingPage"]
    landing_metrics = ["sessions", "totalUsers", "engagedSessions", "bounceRate", "averageSessionDuration"]

    landing_rows_raw = run_ga4_report(client, property_id, landing_dims, landing_metrics, start_s, end_s)
    landing_rows = [
        {
            "landing_page": r.get("landingPage", ""),
            "sessions": r.get("sessions", 0),
            "users": r.get("totalUsers", 0),
            "engaged_sessions": r.get("engagedSessions", 0),
            "bounce_rate": r.get("bounceRate", 0),
            "avg_session_duration": r.get("averageSessionDuration", 0),
        }
        for r in landing_rows_raw
    ]

    organic_filter = FilterExpression(
        and_group=FilterExpressionList(
            expressions=[
                FilterExpression(filter=Filter(field_name="sessionSource", string_filter=Filter.StringFilter(match_type=Filter.StringFilter.MatchType.EXACT, value="google"))),
                FilterExpression(filter=Filter(field_name="sessionMedium", string_filter=Filter.StringFilter(match_type=Filter.StringFilter.MatchType.EXACT, value="organic"))),
            ]
        )
    )
    organic_rows_raw = run_ga4_report(
        client, property_id, landing_dims, landing_metrics, start_s, end_s, dimension_filter=organic_filter
    )
    organic_rows = [
        {
            "landing_page": r.get("landingPage", ""),
            "sessions": r.get("sessions", 0),
            "users": r.get("totalUsers", 0),
            "engaged_sessions": r.get("engagedSessions", 0),
            "bounce_rate": r.get("bounceRate", 0),
            "avg_session_duration": r.get("averageSessionDuration", 0),
        }
        for r in organic_rows_raw
    ]

    exit_rows_raw = run_ga4_report(
        client,
        property_id,
        ["pagePath"],
        ["sessions", "engagedSessions", "averageSessionDuration"],
        start_s,
        end_s,
    )
    exit_rows = [
        {
            "page_path": r.get("pagePath", ""),
            "sessions": r.get("sessions", 0),
            "engaged_sessions": r.get("engagedSessions", 0),
            "avg_session_duration": r.get("averageSessionDuration", 0),
        }
        for r in exit_rows_raw
    ]

    event_rows_raw = run_ga4_report(
        client,
        property_id,
        ["eventName"],
        ["eventCount", "totalUsers"],
        start_s,
        end_s,
    )
    tracked = {
        "view_structure",
        "view_hub",
        "scroll_75",
        "internal_link_click",
        "start_path_iniziare_subito",
        "generate_lead",
        "membership_form_view",
        "membership_form_start",
        "membership_quota_select",
        "membership_form_error",
    }
    event_rows = [
        {
            "event_name": r.get("eventName", ""),
            "event_count": r.get("eventCount", 0),
            "users": r.get("totalUsers", 0),
        }
        for r in event_rows_raw
        if r.get("eventName", "") in tracked
    ]

    landing_path = out_dir / f"ga4_landing_pages_{suffix}.csv"
    organic_path = out_dir / f"ga4_organic_landing_{suffix}.csv"
    exit_path = out_dir / f"ga4_exit_pages_{suffix}.csv"
    events_path = out_dir / f"ga4_events_{suffix}.csv"

    n_landing = write_csv(
        landing_path,
        ["landing_page", "sessions", "users", "engaged_sessions", "bounce_rate", "avg_session_duration"],
        landing_rows,
    )
    n_organic = write_csv(
        organic_path,
        ["landing_page", "sessions", "users", "engaged_sessions", "bounce_rate", "avg_session_duration"],
        organic_rows,
    )
    n_exit = write_csv(
        exit_path,
        ["page_path", "sessions", "engaged_sessions", "avg_session_duration"],
        exit_rows,
    )
    n_events = write_csv(events_path, ["event_name", "event_count", "users"], event_rows)

    return {
        "ok": n_landing > 0,
        "out_dir": str(out_dir),
        "period": suffix,
        "ga4_landing_pages": str(landing_path),
        "ga4_landing_rows": n_landing,
        "ga4_organic_landing": str(organic_path),
        "ga4_organic_rows": n_organic,
        "ga4_exit_pages": str(exit_path),
        "ga4_exit_rows": n_exit,
        "ga4_events": str(events_path),
        "ga4_events_rows": n_events,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Export GA4 data to seo/YYMMDD/")
    parser.add_argument("--project-root", type=Path, default=default_project_root())
    parser.add_argument("--date", help="Export folder YYMMDD (default: today)")
    parser.add_argument("--days", type=int, default=28, help="Lookback days (default: 28)")
    args = parser.parse_args()

    try:
        result = export_ga4(args.project_root, args.date, args.days)
    except Exception as exc:  # noqa: BLE001
        print(f"GA4 export failed: {exc}", file=sys.stderr)
        return 1

    print(
        f"GA4 export OK: {result['ga4_landing_rows']} landing rows, "
        f"{result['ga4_organic_rows']} organic, {result['ga4_events_rows']} events -> {result['out_dir']}"
    )
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Export Google Ads performance to seo/YYMMDD/google/google_ads_*.csv."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from analytics_lib import date_range, load_analytics_env, period_suffix, resolve_project_paths, write_csv  # noqa: E402
from seozoom_lib import default_project_root  # noqa: E402

REQUIRED_ENV = (
    "GOOGLE_ADS_DEVELOPER_TOKEN",
    "GOOGLE_ADS_CLIENT_ID",
    "GOOGLE_ADS_CLIENT_SECRET",
    "GOOGLE_ADS_REFRESH_TOKEN",
    "GOOGLE_ADS_CUSTOMER_ID",
)


def _ads_config(env: dict[str, str]) -> dict:
    missing = [key for key in REQUIRED_ENV if not env.get(key, "").strip()]
    if missing:
        raise ValueError(f"Missing Google Ads credentials in .env: {', '.join(missing)}")

    config = {
        "developer_token": env["GOOGLE_ADS_DEVELOPER_TOKEN"].strip(),
        "client_id": env["GOOGLE_ADS_CLIENT_ID"].strip(),
        "client_secret": env["GOOGLE_ADS_CLIENT_SECRET"].strip(),
        "refresh_token": env["GOOGLE_ADS_REFRESH_TOKEN"].strip(),
        "use_proto_plus": True,
    }
    login_customer_id = env.get("GOOGLE_ADS_LOGIN_CUSTOMER_ID", "").strip().replace("-", "")
    if login_customer_id:
        config["login_customer_id"] = login_customer_id
    return config


def _micros_to_eur(value: int | float | None) -> float:
    if not value:
        return 0.0
    return round(float(value) / 1_000_000, 2)


def _search_rows(client, customer_id: str, query: str) -> list[dict]:
    service = client.get_service("GoogleAdsService")
    rows: list[dict] = []
    stream = service.search_stream(customer_id=customer_id, query=query)
    for batch in stream:
        for row in batch.results:
            rows.append(row)
    return rows


def export_google_ads(project_root: Path, export_date: str | None, days: int) -> dict:
    from google.ads.googleads.client import GoogleAdsClient

    root, out_dir = resolve_project_paths(project_root, export_date)
    env = load_analytics_env(root)
    config = _ads_config(env)
    customer_id = env["GOOGLE_ADS_CUSTOMER_ID"].strip().replace("-", "")

    client = GoogleAdsClient.load_from_dict(config)
    start_d, end_d = date_range(days)
    start_s, end_s = start_d.isoformat(), end_d.isoformat()
    suffix = period_suffix(start_d, end_d)
    date_filter = f"segments.date BETWEEN '{start_s}' AND '{end_s}'"

    campaign_query = f"""
        SELECT
          campaign.id,
          campaign.name,
          campaign.status,
          campaign.advertising_channel_type,
          metrics.impressions,
          metrics.clicks,
          metrics.cost_micros,
          metrics.conversions,
          metrics.conversions_value
        FROM campaign
        WHERE {date_filter}
    """
    ad_group_query = f"""
        SELECT
          campaign.name,
          ad_group.id,
          ad_group.name,
          ad_group.status,
          metrics.impressions,
          metrics.clicks,
          metrics.cost_micros,
          metrics.conversions,
          metrics.conversions_value
        FROM ad_group
        WHERE {date_filter}
    """
    search_terms_query = f"""
        SELECT
          campaign.name,
          ad_group.name,
          search_term_view.search_term,
          metrics.impressions,
          metrics.clicks,
          metrics.cost_micros,
          metrics.conversions
        FROM search_term_view
        WHERE {date_filter}
          AND metrics.impressions > 0
        ORDER BY metrics.clicks DESC
        LIMIT 10000
    """

    campaign_rows = []
    for row in _search_rows(client, customer_id, campaign_query):
        campaign_rows.append(
            {
                "campaign_id": row.campaign.id,
                "campaign_name": row.campaign.name,
                "status": row.campaign.status.name,
                "channel_type": row.campaign.advertising_channel_type.name,
                "impressions": row.metrics.impressions,
                "clicks": row.metrics.clicks,
                "cost_eur": _micros_to_eur(row.metrics.cost_micros),
                "conversions": round(row.metrics.conversions, 2),
                "conversion_value_eur": round(row.metrics.conversions_value, 2),
            }
        )

    ad_group_rows = []
    for row in _search_rows(client, customer_id, ad_group_query):
        ad_group_rows.append(
            {
                "campaign_name": row.campaign.name,
                "ad_group_id": row.ad_group.id,
                "ad_group_name": row.ad_group.name,
                "status": row.ad_group.status.name,
                "impressions": row.metrics.impressions,
                "clicks": row.metrics.clicks,
                "cost_eur": _micros_to_eur(row.metrics.cost_micros),
                "conversions": round(row.metrics.conversions, 2),
                "conversion_value_eur": round(row.metrics.conversions_value, 2),
            }
        )

    search_term_rows = []
    for row in _search_rows(client, customer_id, search_terms_query):
        search_term_rows.append(
            {
                "campaign_name": row.campaign.name,
                "ad_group_name": row.ad_group.name,
                "search_term": row.search_term_view.search_term,
                "impressions": row.metrics.impressions,
                "clicks": row.metrics.clicks,
                "cost_eur": _micros_to_eur(row.metrics.cost_micros),
                "conversions": round(row.metrics.conversions, 2),
            }
        )

    campaigns_path = out_dir / f"google_ads_campaigns_{suffix}.csv"
    ad_groups_path = out_dir / f"google_ads_ad_groups_{suffix}.csv"
    search_terms_path = out_dir / f"google_ads_search_terms_{suffix}.csv"

    n_campaigns = write_csv(
        campaigns_path,
        [
            "campaign_id",
            "campaign_name",
            "status",
            "channel_type",
            "impressions",
            "clicks",
            "cost_eur",
            "conversions",
            "conversion_value_eur",
        ],
        campaign_rows,
    )
    n_ad_groups = write_csv(
        ad_groups_path,
        [
            "campaign_name",
            "ad_group_id",
            "ad_group_name",
            "status",
            "impressions",
            "clicks",
            "cost_eur",
            "conversions",
            "conversion_value_eur",
        ],
        ad_group_rows,
    )
    n_search_terms = write_csv(
        search_terms_path,
        ["campaign_name", "ad_group_name", "search_term", "impressions", "clicks", "cost_eur", "conversions"],
        search_term_rows,
    )

    return {
        "ok": n_campaigns > 0 or n_ad_groups > 0 or n_search_terms > 0,
        "out_dir": str(out_dir),
        "period": suffix,
        "customer_id": customer_id,
        "google_ads_campaigns": str(campaigns_path),
        "google_ads_campaigns_rows": n_campaigns,
        "google_ads_ad_groups": str(ad_groups_path),
        "google_ads_ad_groups_rows": n_ad_groups,
        "google_ads_search_terms": str(search_terms_path),
        "google_ads_search_terms_rows": n_search_terms,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Export Google Ads data to seo/YYMMDD/google/")
    parser.add_argument("--project-root", type=Path, default=default_project_root())
    parser.add_argument("--date", help="Export folder YYMMDD (default: today)")
    parser.add_argument("--days", type=int, default=28, help="Lookback days (default: 28)")
    args = parser.parse_args()

    try:
        result = export_google_ads(args.project_root, args.date, args.days)
    except Exception as exc:  # noqa: BLE001
        print(f"Google Ads export failed: {exc}", file=sys.stderr)
        return 1

    print(
        f"Google Ads export OK: {result['google_ads_campaigns_rows']} campaigns, "
        f"{result['google_ads_ad_groups_rows']} ad groups, "
        f"{result['google_ads_search_terms_rows']} search terms -> {result['out_dir']}"
    )
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

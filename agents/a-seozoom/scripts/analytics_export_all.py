#!/usr/bin/env python3
"""Run optional GSC, GA4 and Cloudflare exports into seo/YYMMDD/."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from cf_analytics_export import export_cf  # noqa: E402
from ga4_export import export_ga4  # noqa: E402
from gmc_export import export_gmc  # noqa: E402
from google_ads_export import export_google_ads  # noqa: E402
from gsc_export import export_gsc  # noqa: E402
from gtm_export import export_gtm  # noqa: E402
from seozoom_lib import default_project_root  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Export GSC + GA4 + Cloudflare analytics")
    parser.add_argument("--project-root", type=Path, default=default_project_root())
    parser.add_argument("--date", help="Export folder YYMMDD")
    parser.add_argument("--days", type=int, default=28)
    parser.add_argument("--skip-gsc", action="store_true")
    parser.add_argument("--skip-ga4", action="store_true")
    parser.add_argument("--skip-cf", action="store_true")
    parser.add_argument("--skip-gtm", action="store_true")
    parser.add_argument("--skip-gmc", action="store_true")
    parser.add_argument("--skip-google-ads", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    results: dict[str, dict] = {}
    exit_code = 0

    if not args.skip_gsc:
        try:
            results["gsc"] = export_gsc(args.project_root, args.date, args.days)
        except Exception as exc:  # noqa: BLE001
            results["gsc"] = {"ok": False, "error": str(exc)}
            exit_code = 1

    if not args.skip_ga4:
        try:
            results["ga4"] = export_ga4(args.project_root, args.date, args.days)
        except Exception as exc:  # noqa: BLE001
            results["ga4"] = {"ok": False, "error": str(exc)}
            exit_code = 1

    if not args.skip_cf:
        try:
            results["cf"] = export_cf(args.project_root, args.date, args.days)
        except Exception as exc:  # noqa: BLE001
            results["cf"] = {"ok": False, "error": str(exc)}
            exit_code = 1

    if not args.skip_gtm:
        try:
            results["gtm"] = export_gtm(args.project_root, args.date)
        except Exception as exc:  # noqa: BLE001
            results["gtm"] = {"ok": False, "error": str(exc)}
            exit_code = 1

    if not args.skip_gmc:
        try:
            results["gmc"] = export_gmc(args.project_root, args.date, args.days)
        except Exception as exc:  # noqa: BLE001
            results["gmc"] = {"ok": False, "error": str(exc)}
            exit_code = 1

    if not args.skip_google_ads:
        try:
            results["google_ads"] = export_google_ads(args.project_root, args.date, args.days)
        except Exception as exc:  # noqa: BLE001
            results["google_ads"] = {"ok": False, "error": str(exc)}
            exit_code = 1

    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        for name, data in results.items():
            if data.get("ok"):
                print(f"{name}: OK -> {data.get('out_dir', '')}")
            else:
                print(f"{name}: FAILED — {data.get('error', 'no data')}", file=sys.stderr)

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())

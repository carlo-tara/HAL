#!/usr/bin/env python3
"""Export SeoZoom project data to seo/YYMMDD/."""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

from playwright.sync_api import Page, sync_playwright

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from csv_mappers import (  # noqa: E402
    content_gap_ai_csv,
    generic_csv,
    keyword_all_csv,
    monitored_csv,
    onpage_csv,
    per_url_keywords_csv,
    questions_txt,
    rows_to_csv,
)
from dashboard_extract import export_dashboard  # noqa: E402
from seozoom_api import SeoZoomClient  # noqa: E402
from seozoom_lib import (  # noqa: E402
    competitor_project_from_env,
    dedupe_download_name,
    default_project_root,
    detect_project_domain,
    export_filenames,
    get_project_vars,
    load_dotenv,
    load_project_manifest,
    login,
    manifest_with_domain,
    select_project,
    today_yymmdd,
)
from batch_paths import resolve_batch_dir, resolve_source_dir  # noqa: E402
from url_list import load_urls  # noqa: E402


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _run_global_step(results: dict[str, str], key: str, result_key: str, fn) -> None:
    try:
        dest, content = fn()
        if not content.strip():
            results[result_key] = "empty"
            if dest.is_file() and dest.stat().st_size > 0:
                return
        write_text(dest, content)
        results[result_key] = "ok" if content.strip() else "empty"
    except Exception as exc:  # noqa: BLE001
        results[result_key] = f"error:{exc.__class__.__name__}"


def export_globals(client: SeoZoomClient, out_dir: Path, skip: set[str], manifest: dict) -> dict[str, str]:
    results: dict[str, str] = {}
    names = export_filenames(manifest)

    if "monitored" not in skip:
        _run_global_step(
            results, "monitored", names["monitored"],
            lambda: (out_dir / names["monitored"], monitored_csv(client.monitored_keywords())),
        )
    if "keyword_all" not in skip:
        _run_global_step(
            results, "keyword_all", names["keyword_all"],
            lambda: (out_dir / names["keyword_all"], keyword_all_csv(client.keyword_all())),
        )
    if "onpage" not in skip:
        _run_global_step(
            results, "onpage", names["onpage"],
            lambda: (out_dir / names["onpage"], onpage_csv(client.onpage_seo())),
        )
    if "long_tail" not in skip:
        _run_global_step(
            results, "long_tail", names["long_tail"],
            lambda: (out_dir / names["long_tail"], generic_csv(client.long_tail())),
        )
    if "content_gap" not in skip:
        _run_global_step(
            results, "content_gap", names["content_gap"],
            lambda: (out_dir / names["content_gap"], generic_csv(client.content_gap(ai=False))),
        )
    if "content_gap_ai" not in skip:
        _run_global_step(
            results, "content_gap_ai", names["content_gap_ai"],
            lambda: (out_dir / names["content_gap_ai"], content_gap_ai_csv(client.content_gap(ai=True))),
        )

    if "pages_potential" not in skip:
        _run_global_step(
            results, "pages_potential", names["pages_potential"],
            lambda: (
                out_dir / names["pages_potential"],
                rows_to_csv([
                    {"URL": r.get("url", ""), "Traffico Potenziale": r.get("totpot", ""),
                     "Keyword": r.get("keywordposizionate", ""), "Menzioni AI": r.get("menzioni", 0)}
                    for r in client.pages_list("/api/ajax/pages/getpotentialpages")
                ]),
            ),
        )
    if "pages_main" not in skip:
        _run_global_step(
            results, "pages_main", names["pages_main"],
            lambda: (
                out_dir / names["pages_main"],
                rows_to_csv([
                    {"URL": r.get("url", ""), "Traffico": r.get("svol", ""),
                     "Keyword": r.get("totk", ""), "Menzioni AI": r.get("menzioni", 0)}
                    for r in client.pages_list("/api/ajax/pages/getmainpages")
                ]),
            ),
        )
    if "pages_more_keywords" not in skip:
        _run_global_step(
            results, "pages_more_keywords", names["pages_more_keywords"],
            lambda: (
                out_dir / names["pages_more_keywords"],
                rows_to_csv([
                    {"URL": r.get("url", ""), "Traffico": r.get("svol", ""),
                     "Keyword": r.get("totk", ""), "Menzioni AI": r.get("menzioni", 0)}
                    for r in client.pages_with_more_keywords()
                ]),
            ),
        )
    if "pages_traffic_up" not in skip:
        _run_global_step(
            results, "pages_traffic_up", names["pages_traffic_up"],
            lambda: (out_dir / names["pages_traffic_up"], generic_csv(client.pages_traffic_up())),
        )
    if "pages_traffic_down" not in skip:
        _run_global_step(
            results, "pages_traffic_down", names["pages_traffic_down"],
            lambda: (out_dir / names["pages_traffic_down"], generic_csv(client.pages_traffic_down())),
        )
    if "pages_new_entry" not in skip:
        _run_global_step(
            results, "pages_new_entry", names["pages_new_entry"],
            lambda: (out_dir / names["pages_new_entry"], generic_csv(client.pages_new_entry())),
        )

    if "competitor" not in skip:
        _run_global_step(
            results, "competitor", names["competitor"],
            lambda: (out_dir / names["competitor"], rows_to_csv(client.competitor_grid())),
        )

    if "clusters" not in skip:
        _run_global_step(
            results, "clusters", "clusters_keyword.csv",
            lambda: (out_dir / "clusters_keyword.csv", generic_csv(client.clusters())),
        )
    if "keywords_cluster" not in skip:
        _run_global_step(
            results, "keywords_cluster", "keywords_cluster.csv",
            lambda: (out_dir / "keywords_cluster.csv", generic_csv(client.keywords_clusters())),
        )
    if "questions" not in skip:
        _run_global_step(
            results, "questions", names["questions"],
            lambda: (out_dir / names["questions"], questions_txt(client.faq_questions())),
        )
    if "group_pages" not in skip:
        try:
            for fname, rows in client.pages_traffic_groups().items():
                write_text(out_dir / fname, rows_to_csv(rows))
                results[fname] = "ok" if rows else "empty"
        except Exception as exc:  # noqa: BLE001
            for fname in ("group_page_0.csv", "group_page_1_10.csv", "group_page_11_100.csv", "group_page_101_500.csv"):
                results[fname] = f"error:{exc.__class__.__name__}"
    if "cannibalization" not in skip:
        _run_global_step(
            results, "cannibalization", names["cannibalization"],
            lambda: (out_dir / names["cannibalization"], generic_csv(client.cannibalization())),
        )

    return results


def export_per_url(
    client: SeoZoomClient,
    out_dir: Path,
    urls: list[dict[str, str]],
    throttle: float,
) -> dict[str, str]:
    results: dict[str, str] = {}
    idurl_map = client.build_idurl_map()
    for item in urls:
        url = item["url"]
        fname = dedupe_download_name(item["filename"])
        dest = out_dir / fname
        idurl = idurl_map.get(url)
        if not idurl:
            results[fname] = "missing-idurl"
            continue
        try:
            rows = client.url_keywords(idurl)
            if not rows:
                results[fname] = "empty"
                continue
            write_text(dest, per_url_keywords_csv(rows))
            results[fname] = "ok"
        except Exception as exc:  # noqa: BLE001
            results[fname] = f"error:{exc.__class__.__name__}"
        time.sleep(throttle)
    return results


def export_project(
    page: Page,
    *,
    project_name: str,
    out_dir: Path,
    manifest: dict[str, Any],
    skip_dashboard: bool = False,
    skip_globals: bool = False,
    skip_per_url: bool = True,
    urls: list[dict[str, str]] | None = None,
    throttle: float = 1.0,
    detect_domain: bool = False,
) -> dict[str, Any]:
    """
    Export one SeoZoom project into out_dir (same Playwright session).

    When detect_domain is True, override manifest domain_slug from the project page
    (required for competitor projects so filenames match their hostname).
    """
    pid = select_project(page, project_name)
    domain_id = page.evaluate("() => (typeof DomainID !== 'undefined' ? String(DomainID) : '')") or ""
    vars_map: dict[str, str] | None = None
    if not domain_id:
        vars_map = get_project_vars(page, pid)
        domain_id = vars_map.get("DomainID", "")

    export_manifest = dict(manifest)
    if detect_domain:
        detected = detect_project_domain(page, pid, vars_map=vars_map)
        if detected:
            export_manifest = manifest_with_domain(manifest, detected)

    client = SeoZoomClient(page, pid, domain_id)
    results: dict[str, str] = {}

    if not skip_dashboard:
        dash_dir = out_dir / "dashboard"
        dash_results = export_dashboard(client, dash_dir, export_manifest)
        results.update({f"dashboard/{k}": v for k, v in dash_results.items()})

    if not skip_globals:
        results.update(export_globals(client, out_dir, skip=set(), manifest=export_manifest))

    if not skip_per_url and urls:
        results.update(export_per_url(client, out_dir, urls, throttle))

    report: dict[str, Any] = {
        "exported_at": datetime.now().isoformat(),
        "project_name": project_name,
        "project_id": pid,
        "domain_slug": export_manifest.get("domain_slug"),
        "out_dir": str(out_dir),
        "skip_per_url": skip_per_url,
        "results": results,
    }
    write_text(out_dir / "export-report.json", json.dumps(report, indent=2, ensure_ascii=False))
    return report


def _dir_nonempty(path: Path) -> bool:
    return path.exists() and any(path.iterdir())


def main() -> int:
    parser = argparse.ArgumentParser(description="Export SeoZoom data to seo/YYMMDD/")
    parser.add_argument("--project-root", type=Path, default=default_project_root())
    parser.add_argument("--date", default="", help="YYMMDD folder (default: today)")
    parser.add_argument("--env", type=Path, default=None, help=".env path")
    parser.add_argument("--headed", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--skip-per-url", action="store_true")
    parser.add_argument("--skip-globals", action="store_true")
    parser.add_argument("--skip-dashboard", action="store_true", help="Skip project overview dashboard widgets")
    parser.add_argument(
        "--skip-competitor-project",
        action="store_true",
        help="Skip SEOZOOM_PROJECT_COMPETITOR export even if env is set",
    )
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--throttle", type=float, default=1.0)
    args = parser.parse_args()

    env_path = args.env or (args.project_root / ".env")
    env = load_dotenv(env_path)
    manifest = load_project_manifest(args.project_root)
    date = args.date or today_yymmdd()
    batch_dir = resolve_batch_dir(args.project_root, date)
    out_dir = resolve_source_dir(args.project_root, date, "seozoom")
    competitor_name = None if args.skip_competitor_project else competitor_project_from_env(env)
    competitor_dir = (
        resolve_source_dir(args.project_root, date, "seozoom-competitor")
        if competitor_name
        else None
    )

    if _dir_nonempty(out_dir) and not args.force:
        print(f"Output dir exists (use --force): {out_dir}", file=sys.stderr)
        return 1
    if competitor_dir is not None and _dir_nonempty(competitor_dir) and not args.force:
        print(f"Competitor output dir exists (use --force): {competitor_dir}", file=sys.stderr)
        return 1

    sitemap_path = args.project_root / "sitemap-enriched.json"
    exclude_prefixes = manifest.get("exclude_url_prefixes")
    urls = load_urls(sitemap_path, exclude_prefixes=exclude_prefixes)
    if args.dry_run:
        print(json.dumps({
            "batch_dir": str(batch_dir),
            "out_dir": str(out_dir),
            "url_count": len(urls),
            "domain_slug": manifest.get("domain_slug"),
            "seozoom_project": env.get("SEOZOOM_PROJECT"),
            "seozoom_project_competitor": competitor_name,
            "competitor_out_dir": str(competitor_dir) if competitor_dir else None,
            "competitor_skip_per_url": True if competitor_name else None,
        }, indent=2))
        return 0

    out_dir.mkdir(parents=True, exist_ok=True)
    session_dir = args.project_root / ".seozoom"
    session_dir.mkdir(exist_ok=True)
    session_file = session_dir / "session.json"

    primary_report: dict[str, Any] = {}
    competitor_report: dict[str, Any] | None = None

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=not args.headed)
        context = browser.new_context()
        page = context.new_page()
        login(page, env, force_fresh=True)

        project_name = env.get("SEOZOOM_PROJECT", "Liberating.it")
        primary_report = export_project(
            page,
            project_name=project_name,
            out_dir=out_dir,
            manifest=manifest,
            skip_dashboard=args.skip_dashboard,
            skip_globals=args.skip_globals,
            skip_per_url=args.skip_per_url,
            urls=urls,
            throttle=args.throttle,
            detect_domain=False,
        )

        if competitor_name and competitor_dir is not None:
            competitor_dir.mkdir(parents=True, exist_ok=True)
            competitor_report = export_project(
                page,
                project_name=competitor_name,
                out_dir=competitor_dir,
                manifest=manifest,
                skip_dashboard=args.skip_dashboard,
                skip_globals=args.skip_globals,
                skip_per_url=True,
                urls=None,
                throttle=args.throttle,
                detect_domain=True,
            )

        context.storage_state(path=str(session_file))
        browser.close()

    combined = {
        "exported_at": datetime.now().isoformat(),
        "batch_dir": str(batch_dir),
        "out_dir": str(out_dir),
        "primary": {
            "project_name": primary_report.get("project_name"),
            "project_id": primary_report.get("project_id"),
            "domain_slug": primary_report.get("domain_slug"),
            "out_dir": primary_report.get("out_dir"),
        },
        "competitor": None,
        "results": primary_report.get("results", {}),
    }
    if competitor_report:
        combined["competitor"] = {
            "project_name": competitor_report.get("project_name"),
            "project_id": competitor_report.get("project_id"),
            "domain_slug": competitor_report.get("domain_slug"),
            "out_dir": competitor_report.get("out_dir"),
            "skip_per_url": True,
            "results": competitor_report.get("results", {}),
        }
        combined["competitor_out_dir"] = competitor_report.get("out_dir")

    write_text(out_dir / "export-report.json", json.dumps(combined, indent=2, ensure_ascii=False))
    write_text(batch_dir / "export-report.json", json.dumps(combined, indent=2, ensure_ascii=False))

    # validate (unless we intentionally skipped the critical globals)
    validate_script = SCRIPT_DIR / "validate_export.py"
    if validate_script.is_file() and not (args.skip_globals and args.skip_per_url):
        import subprocess

        proc = subprocess.run(
            [
                sys.executable,
                str(validate_script),
                str(batch_dir),
                "--write-md",
                "--project-root",
                str(args.project_root),
            ],
            capture_output=True,
            text=True,
        )
        print(proc.stdout)
        if proc.returncode != 0:
            print(proc.stderr, file=sys.stderr)
            return proc.returncode
    elif validate_script.is_file():
        import subprocess

        subprocess.run(
            [
                sys.executable,
                str(validate_script),
                str(batch_dir),
                "--write-md",
                "--project-root",
                str(args.project_root),
            ],
            capture_output=True,
            text=True,
        )

    primary_results = primary_report.get("results", {})
    ok = sum(1 for v in primary_results.values() if v == "ok")
    msg = f"Export complete: {ok}/{len(primary_results)} OK -> {out_dir}"
    if competitor_report:
        c_results = competitor_report.get("results", {})
        c_ok = sum(1 for v in c_results.values() if v == "ok")
        msg += (
            f" | competitor {competitor_report.get('project_name')}: "
            f"{c_ok}/{len(c_results)} OK -> {competitor_report.get('out_dir')}"
        )
    print(msg)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

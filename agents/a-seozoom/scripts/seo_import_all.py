#!/usr/bin/env python3
"""Mass import SEO/analytics data into seo/YYMMDD/ from all configured sources."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from cf_analytics_export import export_cf  # noqa: E402
from ga4_export import export_ga4  # noqa: E402
from gmc_export import export_gmc  # noqa: E402
from google_ads_export import export_google_ads  # noqa: E402
from gsc_export import export_gsc  # noqa: E402
from gtm_export import export_gtm  # noqa: E402
from seozoom_lib import today_yymmdd, default_project_root  # noqa: E402


def compute_seozoom_usable(validate: dict) -> bool:
    """True when Batch SEO is analyzable despite validate ok=false (FAILED ma usabile).

    Requires empty missing_critical and at least one dashboard metric file.
    Does not flip ok to true.
    """
    if not isinstance(validate, dict):
        return False
    missing = validate.get("missing_critical")
    if not isinstance(missing, list) or missing:
        return False
    try:
        dashboard_ok = int(validate.get("dashboard_ok") or 0)
    except (TypeError, ValueError):
        dashboard_ok = 0
    return dashboard_ok > 0


def parse_validate_payload(stdout: str) -> dict | None:
    """Parse validate JSON from seozoom_export stdout (may be multi-line)."""
    text = (stdout or "").strip()
    if not text:
        return None
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return None
    if isinstance(data, dict) and any(
        key in data for key in ("per_url_ok", "missing_critical", "dashboard_ok", "ok")
    ):
        return data
    return None


def enrich_seozoom_source(sz: dict) -> dict:
    """Attach usable flag and summary; keep ok tied to export/validate exit."""
    out = dict(sz)
    validate = parse_validate_payload(out.get("stdout") or "")
    usable = compute_seozoom_usable(validate or {})
    out["usable"] = usable
    if validate is not None:
        out["validate"] = {
            "ok": validate.get("ok"),
            "per_url_ok": validate.get("per_url_ok"),
            "missing_critical": validate.get("missing_critical"),
            "dashboard_ok": validate.get("dashboard_ok"),
            "analytics_ok": validate.get("analytics_ok"),
        }
    summary = _seozoom_summary(out)
    if summary:
        summary = f"{summary}, usable={usable}"
    else:
        summary = f"usable={usable}"
    out["summary"] = summary
    return out


def env_soft_gtm_enabled(env: dict | None = None) -> bool:
    """True if SEO_IMPORT_SOFT_GTM is set to a truthy non-false string."""
    raw = (env if env is not None else os.environ).get("SEO_IMPORT_SOFT_GTM", "")
    text = str(raw).strip().lower()
    if not text or text in {"0", "false", "off", "no"}:
        return False
    return True


def is_gtm_soft_fail_error(message: object) -> bool:
    """Detect Tag Manager API disabled / accessNotConfigured (403)."""
    text = str(message or "")
    lower = text.lower()
    return "accessnotconfigured" in lower or (
        "tag manager api" in lower and "disabled" in lower
    )


def soft_gtm_result(message: object, *, reason: str = "soft_fail") -> dict:
    """Mark GTM as skipped/soft so analytics batch does not hard-fail."""
    detail = str(message or reason)[:300]
    return {
        "ok": True,
        "soft_fail": True,
        "skipped": True,
        "reason": reason,
        "error": detail,
        "summary": f"skipped soft_fail reason={reason} — {detail}",
    }


def _run_seozoom(
    project_root: Path,
    export_date: str,
    force: bool,
    skip_per_url: bool,
    headed: bool,
    skip_dashboard: bool = False,
    skip_competitor_project: bool = False,
) -> dict:
    cmd = [
        sys.executable,
        str(SCRIPT_DIR / "seozoom_export.py"),
        "--project-root",
        str(project_root),
        "--date",
        export_date,
    ]
    if force:
        cmd.append("--force")
    if skip_per_url:
        cmd.append("--skip-per-url")
    if skip_dashboard:
        cmd.append("--skip-dashboard")
    if skip_competitor_project:
        cmd.append("--skip-competitor-project")
    if headed:
        cmd.append("--headed")
    proc = subprocess.run(cmd, capture_output=True, text=True)
    return {
        "ok": proc.returncode == 0,
        "returncode": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
    }


def _seozoom_summary(sz: dict) -> str:
    """Build a one-line SeoZoom summary from validate JSON or export stdout.

    ``seozoom_export`` may print multi-line validate JSON then exit non-zero;
    taking ``splitlines()[-1]`` alone yields a useless ``}``.
    """
    stdout = (sz.get("stdout") or "").strip()
    stderr = (sz.get("stderr") or "").strip()
    if stdout:
        try:
            data = json.loads(stdout)
        except json.JSONDecodeError:
            data = None
        if isinstance(data, dict) and any(
            key in data for key in ("per_url_ok", "missing_critical", "dashboard_ok", "ok")
        ):
            parts: list[str] = []
            if "ok" in data:
                parts.append(f"validate_ok={data.get('ok')}")
            if "per_url_ok" in data:
                parts.append(f"per_url_ok={data.get('per_url_ok')}")
            if "missing_critical" in data:
                parts.append(f"missing_critical={data.get('missing_critical')}")
            if "dashboard_ok" in data:
                parts.append(f"dashboard_ok={data.get('dashboard_ok')}")
            if "analytics_ok" in data:
                parts.append(f"analytics_ok={data.get('analytics_ok')}")
            return ", ".join(parts)
        for line in reversed(stdout.splitlines()):
            line = line.strip()
            if line and line not in {"{", "}", "[", "]"}:
                return line[:300]
    if stderr:
        for line in stderr.splitlines():
            line = line.strip()
            if line:
                return line[:300]
    return ""


def _md_table_cell(value: object, limit: int = 200) -> str:
    """Flatten and escape a value for a Markdown table cell."""
    text = " ".join(str(value or "").split())
    return text.replace("|", "\\|")[:limit]


def _write_import_report(out_dir: Path, payload: dict) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "import-report.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    lines = [
        f"# Import report — {out_dir.name}",
        "",
        f"- Started: **{payload.get('started_at', '')}**",
        f"- Finished: **{payload.get('finished_at', '')}**",
        "",
        "| Source | Status | Detail |",
        "|--------|--------|--------|",
    ]
    for name, result in payload.get("sources", {}).items():
        if result.get("ok"):
            status = "OK"
        elif result.get("usable"):
            status = "FAILED (usable)"
        elif result.get("skipped") or result.get("soft_fail"):
            status = "SKIPPED"
        else:
            status = "FAILED"
        detail = result.get("summary") or result.get("error") or result.get("stderr", "")
        lines.append(f"| {name} | {status} | {_md_table_cell(detail)} |")
    (out_dir / "import-report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_import(
    project_root: Path,
    export_date: str | None = None,
    *,
    days: int = 28,
    force: bool = False,
    skip_seozoom: bool = False,
    skip_gsc: bool = False,
    skip_ga4: bool = False,
    skip_gtm: bool = False,
    skip_gmc: bool = False,
    skip_google_ads: bool = False,
    skip_cf: bool = False,
    skip_per_url: bool = False,
    skip_dashboard: bool = False,
    skip_competitor_project: bool = False,
    headed: bool = False,
) -> dict:
    root = project_root.resolve()
    yymmdd = export_date or today_yymmdd()
    out_dir = root / "seo" / yymmdd
    started = datetime.now().isoformat()
    sources: dict[str, dict] = {}

    if not skip_seozoom:
        sz = _run_seozoom(
            root,
            yymmdd,
            force=force,
            skip_per_url=skip_per_url,
            headed=headed,
            skip_dashboard=skip_dashboard,
            skip_competitor_project=skip_competitor_project,
        )
        sources["seozoom"] = enrich_seozoom_source(sz)

    if not skip_gsc:
        try:
            r = export_gsc(root, yymmdd, days)
            r["summary"] = f"{r.get('gsc_queries_rows', 0)} queries, {r.get('gsc_pages_rows', 0)} pages"
            sources["gsc"] = r
        except Exception as exc:  # noqa: BLE001
            sources["gsc"] = {"ok": False, "error": str(exc)}

    if not skip_ga4:
        try:
            r = export_ga4(root, yymmdd, days)
            r["summary"] = (
                f"{r.get('ga4_landing_rows', 0)} landing, "
                f"{r.get('ga4_events_rows', 0)} events"
            )
            sources["ga4"] = r
        except Exception as exc:  # noqa: BLE001
            sources["ga4"] = {"ok": False, "error": str(exc)}

    if not skip_gtm:
        try:
            r = export_gtm(root, yymmdd)
            r["summary"] = f"v{r.get('version_id', '?')} — {r.get('gtm_tags_rows', 0)} tags"
            sources["gtm"] = r
        except Exception as exc:  # noqa: BLE001
            err_text = str(exc)
            if is_gtm_soft_fail_error(err_text) or env_soft_gtm_enabled():
                reason = (
                    "accessNotConfigured"
                    if is_gtm_soft_fail_error(err_text)
                    else "SEO_IMPORT_SOFT_GTM"
                )
                sources["gtm"] = soft_gtm_result(err_text, reason=reason)
            else:
                sources["gtm"] = {"ok": False, "error": err_text}

    if not skip_gmc:
        try:
            r = export_gmc(root, yymmdd, days)
            r["summary"] = f"{r.get('gmc_products_rows', 0)} products, {r.get('gmc_product_issues_rows', 0)} issues"
            # Optional project-local feed audit (title/mm/policy/labels).
            validate_script = root / "scripts" / "validate_gmc_feed.py"
            if validate_script.is_file():
                vproc = subprocess.run(
                    [
                        sys.executable,
                        str(validate_script),
                        str(out_dir),
                        "--project-root",
                        str(root),
                        "--write",
                        "--json",
                    ],
                    capture_output=True,
                    text=True,
                )
                try:
                    r["validation"] = json.loads(vproc.stdout) if vproc.stdout.strip() else {
                        "ok": False,
                        "error": vproc.stderr[:300],
                    }
                except json.JSONDecodeError:
                    r["validation"] = {"ok": False, "raw": vproc.stdout[:500]}
            sources["gmc"] = r
        except Exception as exc:  # noqa: BLE001
            sources["gmc"] = {"ok": False, "error": str(exc)}

    if not skip_google_ads:
        try:
            r = export_google_ads(root, yymmdd, days)
            r["summary"] = (
                f"{r.get('google_ads_campaigns_rows', 0)} campaigns, "
                f"{r.get('google_ads_search_terms_rows', 0)} search terms"
            )
            sources["google_ads"] = r
        except Exception as exc:  # noqa: BLE001
            sources["google_ads"] = {"ok": False, "error": str(exc)}

    if not skip_cf:
        try:
            r = export_cf(root, yymmdd, days)
            r["summary"] = f"{r.get('cf_requests_rows', 0)} requests"
            sources["cf"] = r
        except Exception as exc:  # noqa: BLE001
            sources["cf"] = {"ok": False, "error": str(exc)}

    validate_proc = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_DIR / "validate_export.py"),
            str(out_dir),
            "--write-md",
            "--json",
            "--project-root",
            str(root),
        ],
        capture_output=True,
        text=True,
    )
    validation = {}
    if validate_proc.stdout.strip():
        try:
            validation = json.loads(validate_proc.stdout)
        except json.JSONDecodeError:
            validation = {"raw": validate_proc.stdout}
    validation["returncode"] = validate_proc.returncode

    finished = datetime.now().isoformat()
    payload = {
        "started_at": started,
        "finished_at": finished,
        "out_dir": str(out_dir),
        "days": days,
        "sources": sources,
        "validation": validation,
        "ok": all(s.get("ok") for s in sources.values()) if sources else False,
    }
    _write_import_report(out_dir, payload)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Import massivo SeoZoom + GSC + GA4 + GTM + Cloudflare → seo/YYMMDD/"
    )
    parser.add_argument("--project-root", type=Path, default=default_project_root())
    parser.add_argument("--date", help="Cartella export YYMMDD (default: oggi)")
    parser.add_argument("--days", type=int, default=28, help="Finestra GSC/GA4 in giorni (CF: max 1)")
    parser.add_argument("--force", action="store_true", help="Sovrascrive cartella SeoZoom esistente")
    parser.add_argument("--headed", action="store_true", help="Browser visibile per SeoZoom")
    parser.add_argument("--skip-seozoom", action="store_true")
    parser.add_argument("--skip-gsc", action="store_true")
    parser.add_argument("--skip-ga4", action="store_true")
    parser.add_argument("--skip-gtm", action="store_true")
    parser.add_argument("--skip-gmc", action="store_true")
    parser.add_argument("--skip-google-ads", action="store_true")
    parser.add_argument("--skip-cf", action="store_true")
    parser.add_argument("--skip-per-url", action="store_true", help="SeoZoom: solo report globali")
    parser.add_argument("--skip-dashboard", action="store_true", help="SeoZoom: salta panoramica progetto")
    parser.add_argument(
        "--skip-competitor-project",
        action="store_true",
        help="SeoZoom: salta progetto SEOZOOM_PROJECT_COMPETITOR",
    )
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    payload = run_import(
        args.project_root,
        args.date,
        days=args.days,
        force=args.force,
        skip_seozoom=args.skip_seozoom,
        skip_gsc=args.skip_gsc,
        skip_ga4=args.skip_ga4,
        skip_gtm=args.skip_gtm,
        skip_gmc=args.skip_gmc,
        skip_google_ads=args.skip_google_ads,
        skip_cf=args.skip_cf,
        skip_per_url=args.skip_per_url,
        skip_dashboard=args.skip_dashboard,
        skip_competitor_project=args.skip_competitor_project,
        headed=args.headed,
    )

    skip_seozoom = args.skip_seozoom
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        for name, result in payload["sources"].items():
            if result.get("ok"):
                print(f"{name}: OK — {result.get('summary', '')}")
            else:
                fail_detail = (
                    result.get("summary")
                    or result.get("error")
                    or result.get("stderr", "")
                    or result.get("stdout", "")[:200]
                )
                print(f"{name}: FAILED — {fail_detail}", file=sys.stderr)
        v = payload.get("validation", {})
        print(
            f"validate: seozoom_ok={v.get('ok')} per_url={v.get('per_url_ok')} "
            f"analytics_ok={v.get('analytics_ok', 0)}"
        )
        print(f"report: {payload['out_dir']}/import-report.md")

    core_ok = (
        payload["sources"]["seozoom"]["ok"]
        if "seozoom" in payload["sources"]
        else skip_seozoom
    )
    analytics_sources = [k for k in ("gsc", "ga4", "gtm", "gmc", "google_ads", "cf") if k in payload["sources"]]
    analytics_ok = all(payload["sources"][k].get("ok") for k in analytics_sources) if analytics_sources else True
    return 0 if core_ok and analytics_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

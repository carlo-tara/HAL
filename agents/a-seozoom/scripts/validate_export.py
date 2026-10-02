#!/usr/bin/env python3
"""Validate SeoZoom export folder against manifest."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))

from batch_paths import DEFAULT_SUBDIRS, analytics_subdir_for_pattern, normalize_batch_dir  # noqa: E402
from dashboard_extract import dashboard_filenames  # noqa: E402
from seozoom_lib import load_json  # noqa: E402


def _match_optional_files(search_dir: Path, pattern: str) -> list[Path]:
    if not search_dir.is_dir():
        return []
    return sorted(search_dir.glob(pattern))


def _dashboard_expected_files(manifest: dict) -> list[dict]:
    """Resolve dashboard file list; substitute domain_slug into template names."""
    domain = manifest.get("domain_slug", "example.it")
    specs = manifest.get("dashboard_files")
    if not specs:
        # derive from canonical naming when section absent
        names = dashboard_filenames(manifest)
        return [{"filename": n, "critical": False} for n in names.values()]
    out = []
    for spec in specs:
        fname = spec["filename"].replace("example.it", domain).replace("example_it", domain.replace(".", "_"))
        row = dict(spec)
        row["filename"] = fname
        out.append(row)
    return out


def resolve_manifest(export_dir: Path, project_root: Path | None = None) -> dict:
    if project_root is not None:
        from seozoom_lib import load_project_manifest  # noqa: WPS433

        return load_project_manifest(project_root)
    batch_dir = normalize_batch_dir(export_dir)
    candidate = batch_dir.parent.parent
    if (candidate / "seo" / "export-manifest.json").is_file():
        from seozoom_lib import load_project_manifest  # noqa: WPS433

        return load_project_manifest(candidate)
    return load_json(SKILL_ROOT / "references" / "export-manifest.json")


def _resolve_global_file(batch_dir: Path, seozoom_dir: Path, fname: str) -> tuple[Path, str]:
    alt = fname.replace(".xlsx", ".csv")
    for base in (seozoom_dir, batch_dir):
        for name in (fname, alt):
            path = base / name
            if path.is_file():
                return path, "OK" if path.stat().st_size > 0 else "EMPTY"
    return seozoom_dir / fname, "MISSING"


def validate_dir(export_dir: Path, project_root: Path | None = None) -> dict:
    batch_dir = normalize_batch_dir(export_dir)
    manifest = resolve_manifest(batch_dir, project_root)
    subdirs = manifest.get("subdirs", DEFAULT_SUBDIRS)
    seozoom_dir = batch_dir / subdirs.get("seozoom", "seozoom")
    critical = set(manifest.get("critical_files", []))
    optional_per_url = manifest.get("per_url_optional", True)

    rows = []
    missing_critical = []
    for spec in manifest.get("global_files", []):
        fname = spec["filename"]
        target, status = _resolve_global_file(batch_dir, seozoom_dir, fname)
        size = target.stat().st_size if target.is_file() else 0
        rows.append({"file": fname, "status": status, "size": size, "critical": fname in critical})
        if fname in critical and status != "OK":
            missing_critical.append(fname)

    per_url_ok = 0
    per_url_missing = 0
    per_url_paths: list[Path] = []
    for base in (seozoom_dir, batch_dir):
        if base.is_dir():
            per_url_paths.extend(sorted(base.glob("*__all_keywords.csv")))
    seen: set[str] = set()
    for path in per_url_paths:
        if path.name in seen:
            continue
        seen.add(path.name)
        size = path.stat().st_size
        if size > 0:
            per_url_ok += 1
        else:
            per_url_missing += 1
            rows.append({"file": path.name, "status": "EMPTY", "size": 0, "critical": False})

    dashboard_subdir = manifest.get("dashboard_subdir", "dashboard")
    dashboard_dir = seozoom_dir / dashboard_subdir
    dashboard_rows = []
    dashboard_ok = 0
    for spec in _dashboard_expected_files(manifest):
        fname = spec["filename"]
        critical = bool(spec.get("critical"))
        target = dashboard_dir / fname
        if target.is_file():
            size = target.stat().st_size
            status = "OK" if size > 0 else "EMPTY"
            if status == "OK":
                dashboard_ok += 1
        else:
            size = 0
            status = "MISSING"
        dashboard_rows.append(
            {
                "file": f"{dashboard_subdir}/{fname}",
                "status": status,
                "size": size,
                "critical": critical,
                "widget": spec.get("widget", ""),
            }
        )

    analytics_rows = []
    analytics_ok = 0
    for spec in manifest.get("optional_analytics_files", []):
        pattern = spec["pattern"]
        subdir_name = spec.get("subdir") or analytics_subdir_for_pattern(pattern, subdirs)
        search_dir = batch_dir / subdir_name
        matches = _match_optional_files(search_dir, pattern)
        if not matches:
            matches = _match_optional_files(batch_dir, pattern)
        if matches:
            for match in matches:
                size = match.stat().st_size
                status = "EMPTY" if size == 0 else "OK"
                if status == "OK":
                    analytics_ok += 1
                analytics_rows.append(
                    {
                        "file": match.name,
                        "pattern": pattern,
                        "source": spec.get("source", ""),
                        "subdir": subdir_name,
                        "status": status,
                        "size": size,
                    }
                )
        else:
            analytics_rows.append(
                {
                    "file": pattern,
                    "pattern": pattern,
                    "source": spec.get("source", ""),
                    "subdir": subdir_name,
                    "status": "MISSING",
                    "size": 0,
                }
            )

    summary = {
        "export_dir": str(batch_dir),
        "global_rows": rows,
        "per_url_ok": per_url_ok,
        "per_url_missing_or_empty": per_url_missing,
        "missing_critical": missing_critical,
        "dashboard_rows": dashboard_rows,
        "dashboard_ok": dashboard_ok,
        "analytics_rows": analytics_rows,
        "analytics_ok": analytics_ok,
        "ok": not missing_critical and (per_url_ok >= manifest.get("min_per_url_ok", 5) or optional_per_url),
    }
    return summary


def write_report_md(export_dir: Path, summary: dict) -> None:
    batch_dir = normalize_batch_dir(export_dir)
    lines = [
        f"# Export report — {batch_dir.name}",
        "",
        f"- Per-URL OK: **{summary['per_url_ok']}**",
        f"- Missing critical: **{len(summary['missing_critical'])}**",
        f"- Dashboard OK: **{summary.get('dashboard_ok', 0)}**",
        f"- Analytics files OK: **{summary.get('analytics_ok', 0)}**",
        "",
        "## SeoZoom globali (`seozoom/`)",
        "",
        "| File | Status | Size | Critical |",
        "|------|--------|------|----------|",
    ]
    for row in summary["global_rows"]:
        lines.append(
            f"| {row['file']} | {row['status']} | {row['size']} | {'yes' if row['critical'] else 'no'} |"
        )
    if summary.get("dashboard_rows"):
        lines += [
            "",
            "## Dashboard panoramica (`seozoom/dashboard/`)",
            "",
            "| File | Status | Size | Widget |",
            "|------|--------|------|--------|",
        ]
        for row in summary["dashboard_rows"]:
            lines.append(
                f"| {row['file']} | {row['status']} | {row['size']} | {row.get('widget', '')} |"
            )
    if summary.get("analytics_rows"):
        lines += [
            "",
            "## Analytics opzionali (google/ / cloudflare/ / substack/)",
            "",
            "| File | Status | Size | Source | Subdir |",
            "|------|--------|------|--------|--------|",
        ]
        for row in summary["analytics_rows"]:
            fname = row["file"] if row["status"] != "MISSING" else row["pattern"]
            lines.append(
                f"| {fname} | {row['status']} | {row['size']} | {row.get('source', '')} | {row.get('subdir', '')} |"
            )
    if summary["missing_critical"]:
        lines += ["", "## Missing critical", ""] + [f"- {f}" for f in summary["missing_critical"]]
    (batch_dir / "export-report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("export_dir", type=Path, help="Batch root seo/YYMMDD/ (or legacy flat folder)")
    parser.add_argument("--project-root", type=Path, default=None, help="Project root for export-manifest.json")
    parser.add_argument("--write-md", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    summary = validate_dir(args.export_dir, args.project_root)
    if args.write_md:
        write_report_md(args.export_dir, summary)
    if args.json:
        print(json.dumps(summary, indent=2, ensure_ascii=False))
    else:
        print(
            json.dumps(
                {
                    "ok": summary["ok"],
                    "per_url_ok": summary["per_url_ok"],
                    "missing_critical": summary["missing_critical"],
                    "dashboard_ok": summary.get("dashboard_ok", 0),
                    "analytics_ok": summary.get("analytics_ok", 0),
                },
                indent=2,
            )
        )
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

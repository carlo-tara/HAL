#!/usr/bin/env python3
"""Batch directory layout for seo/YYMMDD/ exports."""
from __future__ import annotations

from pathlib import Path

from seozoom_lib import today_yymmdd

SUBDIRS = {
    "seozoom": "seozoom",
    "seozoom-competitor": "seozoom-competitor",
    "google": "google",
    "cloudflare": "cloudflare",
    "substack": "substack",
}

DEFAULT_SUBDIRS = SUBDIRS


def resolve_batch_dir(project_root: Path, export_date: str | None = None) -> Path:
    root = project_root.resolve()
    yymmdd = export_date or today_yymmdd()
    batch_dir = root / "seo" / yymmdd
    batch_dir.mkdir(parents=True, exist_ok=True)
    return batch_dir


def resolve_source_dir(project_root: Path, export_date: str | None, source: str) -> Path:
    if source not in SUBDIRS:
        raise ValueError(f"Unknown source {source!r}; expected one of {sorted(SUBDIRS)}")
    out_dir = resolve_batch_dir(project_root, export_date) / SUBDIRS[source]
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir


def normalize_batch_dir(export_dir: Path) -> Path:
    """Return batch root when export_dir is a source subfolder."""
    path = export_dir.resolve()
    if path.name in SUBDIRS.values():
        parent = path.parent
        name = parent.name
        if len(name) == 6 and name.isdigit():
            return parent
    return path


def analytics_subdir_for_pattern(pattern: str, subdirs: dict[str, str] | None = None) -> str:
    dirs = subdirs or SUBDIRS
    if pattern.startswith(("gsc_", "ga4_", "gtm_", "gmc_", "google_ads_")):
        return dirs["google"]
    if pattern.startswith("cf_"):
        return dirs["cloudflare"]
    if pattern.startswith("substack"):
        return dirs["substack"]
    return dirs["google"]

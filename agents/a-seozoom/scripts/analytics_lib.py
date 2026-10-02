#!/usr/bin/env python3
"""Shared helpers for GSC, GA4 and Cloudflare analytics exports."""
from __future__ import annotations

import csv
import os
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Iterable

from batch_paths import resolve_batch_dir, resolve_source_dir  # noqa: E402
from seozoom_lib import load_dotenv, today_yymmdd


def resolve_project_paths(
    project_root: Path,
    export_date: str | None,
    source: str = "google",
) -> tuple[Path, Path]:
    root = project_root.resolve()
    out_dir = resolve_source_dir(root, export_date, source)
    return root, out_dir


def load_analytics_env(project_root: Path) -> dict[str, str]:
    env_path = project_root / ".env"
    if not env_path.is_file():
        raise FileNotFoundError(f".env not found: {env_path}")
    return load_dotenv(env_path)


def date_range(days: int, end: date | None = None) -> tuple[date, date]:
    end_date = end or date.today() - timedelta(days=1)
    start_date = end_date - timedelta(days=max(days - 1, 0))
    return start_date, end_date


def period_suffix(start: date, end: date) -> str:
    return f"{start.isoformat()}_{end.isoformat()}"


def write_csv(path: Path, fieldnames: list[str], rows: Iterable[dict[str, Any]]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
            count += 1
    return count


def resolve_creds_path(project_root: Path, env: dict[str, str]) -> Path:
    creds_path = env.get("GOOGLE_APPLICATION_CREDENTIALS", "")
    if not creds_path:
        raise ValueError("GOOGLE_APPLICATION_CREDENTIALS missing in .env")
    path = Path(creds_path).expanduser()
    if not path.is_absolute():
        path = project_root / path
    if not path.is_file():
        raise FileNotFoundError(f"Service account JSON not found: {path}")
    return path


def google_credentials(env: dict[str, str], project_root: Path | None = None, *, include_gtm: bool = False):
    from google.oauth2 import service_account

    root = project_root or Path.cwd()
    path = resolve_creds_path(root, env)
    scopes = [
        "https://www.googleapis.com/auth/webmasters.readonly",
        "https://www.googleapis.com/auth/analytics.readonly",
    ]
    if include_gtm:
        scopes.append("https://www.googleapis.com/auth/tagmanager.readonly")
    return service_account.Credentials.from_service_account_file(str(path), scopes=scopes)


def apply_google_credentials_env(project_root: Path, env: dict[str, str]) -> None:
    path = resolve_creds_path(project_root, env)
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(path)

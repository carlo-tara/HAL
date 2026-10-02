#!/usr/bin/env python3
"""Generate URL list for per-URL SeoZoom exports from sitemap-enriched.json."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from seozoom_lib import default_project_root, url_to_filename

DEFAULT_LEGAL_PARTS = ("privacy-policy", "cookie-policy")


def load_urls(
    sitemap_path: Path,
    exclude_legal: bool = True,
    exclude_prefixes: tuple[str, ...] | list[str] | None = None,
) -> list[dict[str, str]]:
    data = json.loads(sitemap_path.read_text(encoding="utf-8"))
    urls: list[str] = []
    for sm in data.get("sitemaps", []):
        for entry in sm.get("urls", []):
            loc = entry.get("loc") or entry.get("url")
            if loc:
                urls.append(loc if loc.endswith("/") else loc + "/")
    urls = sorted(set(urls))
    if exclude_legal:
        parts = tuple(exclude_prefixes or DEFAULT_LEGAL_PARTS)
        urls = [u for u in urls if not any(part in u for part in parts)]
    return [{"url": u, "filename": url_to_filename(u)} for u in urls]


def main() -> None:
    parser = argparse.ArgumentParser(description="List SeoZoom per-URL export targets")
    parser.add_argument("--project-root", type=Path, default=default_project_root())
    parser.add_argument("--sitemap", type=Path, help="Override sitemap path (default: {project-root}/sitemap-enriched.json)")
    parser.add_argument("--json", action="store_true", help="Print JSON array")
    args = parser.parse_args()
    sitemap = args.sitemap or (args.project_root / "sitemap-enriched.json")
    items = load_urls(sitemap)
    if args.json:
        print(json.dumps(items, ensure_ascii=False, indent=2))
    else:
        for item in items:
            print(f"{item['filename']}\t{item['url']}")
    print(f"# total: {len(items)}", file=sys.stderr)


if __name__ == "__main__":
    main()

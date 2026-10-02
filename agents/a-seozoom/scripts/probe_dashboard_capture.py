#!/usr/bin/env python3
"""Capture AJAX endpoints and chart data from SeoZoom project dashboard."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

from playwright.sync_api import sync_playwright

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from seozoom_lib import (  # noqa: E402
    BASE_URL,
    default_project_root,
    get_project_vars,
    load_dotenv,
    login,
    select_project,
)


def _truncate(obj, max_chars: int = 8000):
    text = json.dumps(obj, ensure_ascii=False, default=str)
    if len(text) <= max_chars:
        return obj
    return {"_truncated": True, "preview": text[:max_chars]}


def main() -> int:
    parser = argparse.ArgumentParser(description="Probe SeoZoom project dashboard APIs")
    parser.add_argument("--project-root", type=Path, default=None)
    parser.add_argument("--env", type=Path, default=None)
    parser.add_argument("--headed", action="store_true")
    parser.add_argument("--wait-ms", type=int, default=12000)
    args = parser.parse_args()

    project_root = (args.project_root or default_project_root()).resolve()
    env_path = args.env or (project_root / ".env")
    env = load_dotenv(env_path)

    captures: list[dict] = []
    page_meta: dict = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=not args.headed)
        context = browser.new_context()
        page = context.new_page()

        def on_response(resp):
            url = resp.url
            if "/api/ajax/" not in url:
                return
            req = resp.request
            if req.method != "POST":
                return
            try:
                body = resp.json()
            except Exception:
                try:
                    body = {"raw": (resp.text() or "")[:1500]}
                except Exception:
                    body = {"raw": None}
            captures.append(
                {
                    "url": url.split("seozoom.it")[-1] if "seozoom.it" in url else url,
                    "status": resp.status,
                    "post_data": (req.post_data or "")[:2000],
                    "response": _truncate(body),
                }
            )

        page.on("response", on_response)
        login(page, env, force_fresh=True)
        project_name = env.get("SEOZOOM_PROJECT", "")
        pid = select_project(page, project_name)
        page.goto(f"{BASE_URL}/project/view/{pid}", wait_until="domcontentloaded", timeout=90000)
        page.wait_for_timeout(3000)

        # Scroll to trigger lazy-loaded widgets
        for y in (800, 1600, 2400, 3200, 4000, 0):
            page.evaluate(f"window.scrollTo(0, {y})")
            page.wait_for_timeout(1500)

        page.wait_for_timeout(max(0, args.wait_ms - 3000))

        page_meta = page.evaluate(
            """() => {
              const out = {
                title: document.title,
                pid: typeof pid !== 'undefined' ? String(pid) : null,
                DomainID: typeof DomainID !== 'undefined' ? String(DomainID) : null,
                mainDomain: typeof mainDomain !== 'undefined' ? mainDomain : null,
                headings: [...document.querySelectorAll('h1,h2,h3,.card-title,.widget-title')]
                  .map(el => (el.innerText||'').replace(/\\s+/g,' ').trim())
                  .filter(Boolean)
                  .slice(0, 80),
                charts: {
                  highcharts: typeof Highcharts !== 'undefined'
                    ? (Highcharts.charts||[]).filter(Boolean).map(c => ({
                        id: c.renderTo && (c.renderTo.id || c.renderTo.className),
                        series: (c.series||[]).map(s => ({
                          name: s.name,
                          dataLen: (s.data||[]).length,
                          dataSample: (s.data||[]).slice(0, 5).map(p =>
                            p && typeof p === 'object'
                              ? {x: p.x, y: p.y, name: p.name, category: p.category}
                              : p
                          ),
                        })),
                      }))
                    : [],
                  apex: typeof ApexCharts !== 'undefined',
                },
                ajaxRefs: [...new Set(
                  (document.documentElement.innerHTML.match(/\\/api\\/ajax\\/[a-zA-Z0-9/_-]+/g) || [])
                )].slice(0, 100),
              };
              return out;
            }"""
        )
        try:
            page_meta["project_vars"] = get_project_vars(page, pid)
        except Exception as exc:  # noqa: BLE001
            page_meta["project_vars_error"] = str(exc)

        browser.close()

    # Deduplicate by url+post_data prefix
    seen = set()
    unique = []
    for c in captures:
        key = (c["url"], c["post_data"][:120])
        if key in seen:
            continue
        seen.add(key)
        unique.append(c)

    result = {
        "captured_at": datetime.now().isoformat(),
        "project_root": str(project_root),
        "page": page_meta,
        "api_calls": unique,
        "api_paths": sorted({c["url"].split("?")[0] for c in unique}),
    }

    debug_dir = project_root / ".seozoom" / "debug"
    debug_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%y%m%d")
    out_path = debug_dir / f"dashboard-apis-{stamp}.json"
    out_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"out": str(out_path), "api_count": len(unique), "paths": result["api_paths"]}, indent=2))
    print("--- headings ---")
    for h in (page_meta.get("headings") or [])[:40]:
        print(h)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

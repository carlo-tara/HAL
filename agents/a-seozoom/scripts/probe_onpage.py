#!/usr/bin/env python3
"""Capture XHR on SeoZoom OnPage / Content Gap AI pages."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from playwright.sync_api import sync_playwright

from seozoom_lib import load_dotenv, login, select_project, project_env_path

PATHS = [
    "/project/view/keyword-studio/167592?tab=zero",
    "/project/view/rankings/on-page-seo/167592",
    "/project/view/rankings/onpage/167592",
    "/project/view/seo/on-page/167592",
    "/project/view/rankings/content-gap/167592",
]

def main() -> None:
    env = load_dotenv(project_env_path())
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_context().new_page()
        login(page, env)
        select_project(page, env.get("SEOZOOM_PROJECT", ""))
        seen = []
        def on_resp(r):
            u = r.url
            if "/api/" in u or "ajax" in u:
                seen.append({"url": u, "method": r.request.method, "post": r.request.post_data})
        page.on("response", on_resp)
        for path in PATHS:
            seen.clear()
            try:
                page.goto(f"https://sznew.seozoom.it{path}", wait_until="domcontentloaded", timeout=60000)
                page.wait_for_timeout(8000)
                title = page.title()
                print("PATH", path, "title", title[:60], "api", len(seen))
                for s in seen[:5]:
                    print(" ", s["url"].split("seozoom.it")[-1][:80])
                    if s.get("post"):
                        print("   post", s["post"][:120])
            except Exception as e:
                print("PATH", path, "ERR", e)
        browser.close()

if __name__ == "__main__":
    main()

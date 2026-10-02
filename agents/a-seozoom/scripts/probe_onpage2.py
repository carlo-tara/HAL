#!/usr/bin/env python3
"""Find OnPage API by scanning keyword studio tabs."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from playwright.sync_api import sync_playwright

from seozoom_api import SeoZoomClient
from seozoom_lib import load_dotenv, login, select_project, project_env_path

ENDPOINTS = [
    "/api/ajax/keyword/get-onpage-keywords",
    "/api/ajax/keyword/getOnPageKeywords",
    "/api/ajax/keyword/get-on-page-keywords",
    "/api/ajax/domain/getonpageseo",
    "/api/ajax/domain/onpageseo",
    "/api/ajax/seo/get-onpage",
]

def main() -> None:
    env = load_dotenv(project_env_path())
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_context().new_page()
        login(page, env)
        pid = select_project(page, env.get("SEOZOOM_PROJECT", ""))
        domain_id = page.evaluate("() => String(DomainID || '')")
        client = SeoZoomClient(page, pid, domain_id)
        client.warm(f"/project/view/keyword-studio/{pid}?tab=zero")
        base = {"domainID": domain_id, "args[skip]": 0, "args[take]": 500}
        for ep in ENDPOINTS:
            try:
                r = client.post(ep, base)
                data = r.get("data", r)
                n = len(data.get("data", data)) if isinstance(data, dict) else (len(data) if isinstance(data, list) else "?")
                print("OK", ep, n)
            except Exception as e:
                print("FAIL", ep, str(e)[:80])
        browser.close()

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from playwright.sync_api import sync_playwright
from seozoom_api import SeoZoomClient
from seozoom_lib import load_dotenv, login, select_project, project_env_path

env = load_dotenv(project_env_path())
with sync_playwright() as p:
    page = p.chromium.launch(headless=True).new_context().new_page()
    login(page, env)
    pid = select_project(page, env.get("SEOZOOM_PROJECT", ""))
    did = page.evaluate("() => String(DomainID || '')")
    c = SeoZoomClient(page, pid, did)
    c.warm(f"/project/view/keyword-studio/{pid}?tab=zero")
    filters = ["all", "zero", "notranked", "onpage", "seo", "opportunity"]
    tabs = ["zero", "all"]
    for tab in tabs:
        for flt in filters:
            try:
                r = c.post("/api/ajax/keyword/get-page-keywords", {
                    "domainID": did, "args[skip]": 0, "args[take]": 500,
                    "activeTab": tab, "activeFilter": flt,
                })
                data = r.get("data", {})
                rows = data.get("data", []) if isinstance(data, dict) else []
                if rows:
                    print(f"tab={tab} filter={flt} rows={len(rows)} sample={rows[0].get('keyword','')}")
            except Exception as e:
                pass

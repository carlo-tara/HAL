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
    for tab in ["zero", "all", "monitorate", "monitored", "onpage", "on-page", "seo", "notranked", "101"]:
        c.warm(f"/project/view/keyword-studio/{pid}?tab={tab}")
        try:
            r = c.post("/api/ajax/keyword/get-page-keywords", {
                "domainID": did, "args[skip]": 0, "args[take]": 500,
                "activeTab": tab, "activeFilter": "all",
            })
            data = r.get("data", {})
            rows = data.get("data", []) if isinstance(data, dict) else (data if isinstance(data, list) else [])
            print(tab, len(rows), rows[0].get("keyword") if rows else "")
        except Exception as e:
            print(tab, "ERR", str(e)[:60])

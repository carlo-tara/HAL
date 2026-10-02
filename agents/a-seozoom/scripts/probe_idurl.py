#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from playwright.sync_api import sync_playwright
from seozoom_api import SeoZoomClient
from seozoom_lib import load_dotenv, login, select_project, project_env_path

env = load_dotenv(project_env_path())
probe_url = env.get("SEOZOOM_PROBE_URL", "")
with sync_playwright() as p:
    page = p.chromium.launch(headless=True).new_context().new_page()
    login(page, env)
    pid = select_project(page, env.get("SEOZOOM_PROJECT", ""))
    did = page.evaluate("() => String(DomainID || '')")
    c = SeoZoomClient(page, pid, did)
    if not probe_url:
        probe_url = f"https://{c.main_domain()}/"
    for ep, fields in [
        ("/api/ajax/pages/geturlbyurl", {"iddominio": did, "url": probe_url}),
        ("/api/ajax/pages/getUrlByUrl", {"iddominio": did, "url": probe_url}),
        ("/api/ajax/pages/findurl", {"iddominio": did, "url": probe_url}),
        ("/api/ajax/pages/getURLKeywords", {"iddominio": did, "url": probe_url}),
    ]:
        try:
            r = c.post(ep, fields)
            print("OK", ep, str(r)[:200])
        except Exception as e:
            print("FAIL", ep, str(e)[:80])

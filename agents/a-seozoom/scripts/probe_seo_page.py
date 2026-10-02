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
    seen = []
    def on_resp(r):
        if "/api/ajax/" in r.url and r.request.method == "POST":
            seen.append({"url": r.url.split("seozoom.it")[-1], "post": (r.request.post_data or "")[:200]})
    page.on("response", on_resp)
    login(page, env)
    pid = select_project(page, env.get("SEOZOOM_PROJECT", ""))
    did = page.evaluate("() => String(DomainID || '')")
    page.goto(f"https://sznew.seozoom.it/project/view/seo/{pid}", wait_until="domcontentloaded", timeout=90000)
    page.wait_for_timeout(8000)
    print("title", page.title(), "apis", len(seen))
    for s in seen:
        print(s)
    c = SeoZoomClient(page, pid, did)
    for ep in ["/api/ajax/seo/getkeywords", "/api/ajax/seo/getKeywords", "/api/ajax/project/getseokeywords", "/api/ajax/domain/getseokeywords"]:
        try:
            r = c.post(ep, {"domainID": did, "projectId": pid, "iddominio": did})
            print("TRY", ep, str(r)[:200])
        except Exception as e:
            print("FAIL", ep, str(e)[:80])

#!/usr/bin/env python3
import sys, json
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
            seen.append(r.url.split("seozoom.it")[-1])
    page.on("response", on_resp)
    login(page, env)
    pid = select_project(page, env.get("SEOZOOM_PROJECT", ""))
    did = page.evaluate("() => String(DomainID || '')")
    seen.clear()
    page.goto(f"https://sznew.seozoom.it/project/view/seo/{pid}", wait_until="domcontentloaded", timeout=90000)
    for wait in (3, 8, 15):
        page.wait_for_timeout(wait * 1000)
        print(f"after {wait}s apis:", [u for u in seen if u not in ['/api/ajax/projects/counterEvents']])
    c = SeoZoomClient(page, pid, did)
    # try endpoints seen in SeoZoom docs / guesses
    for ep, fields in [
        ("/api/ajax/seo/get-keywords-on-page", {"domainID": did, "projectId": pid}),
        ("/api/ajax/seo/getKeywordsOnPage", {"domainID": did}),
        ("/api/ajax/project/getOnPageSeo", {"projectId": pid, "domainId": did}),
        ("/api/ajax/project/getonpageseo", {"projectId": pid, "domainId": did}),
        ("/api/ajax/domain/get-on-page-seo", {"domainID": did}),
        ("/api/ajax/keyword/get-on-page-seo-keywords", {"domainID": did, "projectId": pid}),
    ]:
        try:
            r = c.post(ep, fields)
            data = r.get("data", r)
            n = len(data) if isinstance(data, list) else (len(data.get("data", [])) if isinstance(data, dict) else "?")
            print("OK", ep, "n=", n)
        except Exception as e:
            print("FAIL", ep, str(e)[:70])

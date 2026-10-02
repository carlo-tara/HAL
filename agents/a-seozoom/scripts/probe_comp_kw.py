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
    c.warm(f"/project/view/competitor/{pid}")
    main = c.main_domain()
    comp = page.evaluate("() => (typeof competitor !== 'undefined' ? competitor : '')") or env.get("SEOZOOM_COMPETITOR", "")
    endpoints = [
        "/api/ajax/domain-vs-domain/get-keywords",
        "/api/ajax/domain-vs-domain/getKeywords",
        "/api/ajax/domain-vs-domain/keyword-competition",
        "/api/ajax/domain-vs-domain/competitionkeywords",
        "/api/ajax/competition/getkeywords",
    ]
    base = {"main": main, "competitor": comp, "domainID": did, "competitionMode": "keyword"}
    for ep in endpoints:
        try:
            r = c.post(ep, base)
            data = r.get("data", r)
            n = len(data) if isinstance(data, list) else (len(data.get("keywords",[])) if isinstance(data,dict) else type(data))
            print("OK", ep, n)
        except Exception as e:
            print("FAIL", ep, str(e)[:60])

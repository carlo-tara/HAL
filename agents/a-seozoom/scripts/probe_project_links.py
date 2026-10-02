#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from playwright.sync_api import sync_playwright
from seozoom_lib import load_dotenv, login, select_project, project_env_path

env = load_dotenv(project_env_path())
with sync_playwright() as p:
    page = p.chromium.launch(headless=True).new_context().new_page()
    login(page, env)
    pid = select_project(page, env.get("SEOZOOM_PROJECT", ""))
    for path in [
        f"/project/view/rankings/{pid}",
        f"/project/view/{pid}",
        f"/project/view/pages/overview-contents/{pid}",
    ]:
        page.goto(f"https://sznew.seozoom.it{path}", wait_until="domcontentloaded", timeout=90000)
        page.wait_for_timeout(2000)
        links = page.evaluate("""() => [...document.querySelectorAll('a[href*=\"/project/\"]')].map(a => ({text:(a.innerText||'').replace(/\\s+/g,' ').trim().slice(0,60), href:a.getAttribute('href')}))""")
        print("===", path, "===")
        for l in links:
            t = (l["text"] + " " + l["href"]).lower()
            if any(x in t for x in ["onpage", "on-page", "on page", "zero", "studio", "gap", "long"]):
                print(l)

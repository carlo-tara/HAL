#!/usr/bin/env python3
import re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from playwright.sync_api import sync_playwright
from seozoom_lib import load_dotenv, login, select_project, project_env_path

env = load_dotenv(project_env_path())
with sync_playwright() as p:
    page = p.chromium.launch(headless=True).new_context().new_page()
    login(page, env)
    pid = select_project(page, env.get("SEOZOOM_PROJECT", ""))
    page.goto(f"https://sznew.seozoom.it/project/view/keyword-studio/{pid}?tab=zero", wait_until="domcontentloaded", timeout=90000)
    page.wait_for_timeout(5000)
    html = page.content()
    apis = sorted(set(re.findall(r"/api/ajax/[a-zA-Z0-9/_-]+", html)))
    for a in apis:
        if any(x in a.lower() for x in ("keyword", "onpage", "page", "seo", "zero")):
            print(a)
    # also check inline scripts
    scripts = page.evaluate("""() => {
      const t = document.documentElement.innerHTML;
      const m = t.match(/\\/api\\/ajax\\/[^\"']+/g) || [];
      return [...new Set(m)].filter(u => /keyword|onpage|zero|seo/i.test(u)).slice(0,30);
    }""")
    print("JS refs:", scripts)

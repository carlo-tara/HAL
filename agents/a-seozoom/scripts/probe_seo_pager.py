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
    page.goto(f"https://sznew.seozoom.it/project/view/seo/{pid}", wait_until="domcontentloaded", timeout=90000)
    page.wait_for_timeout(5000)
    info = page.evaluate("""() => {
      const pager = document.querySelector('.dx-datagrid-pager');
      const pages = pager ? pager.innerText : '';
      const total = document.querySelector('.dx-datagrid-total-count, .dx-info')?.innerText || '';
      return {pager: pages.slice(0,120), total};
    }""")
    print(info)

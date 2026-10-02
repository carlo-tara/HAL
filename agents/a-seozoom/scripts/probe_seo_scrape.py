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
    page.wait_for_timeout(8000)
    rows = page.evaluate("""() => {
      const out = [];
      document.querySelectorAll('.dx-datagrid-rowsview tr.dx-data-row').forEach(tr => {
        const cells = [...tr.querySelectorAll('td')].map(td => td.innerText.trim());
        if (cells.length) out.push(cells);
      });
      return {count: out.length, headers: [...document.querySelectorAll('.dx-datagrid-headers td, .dx-header-row td')].map(x=>x.innerText.trim()).slice(0,8), sample: out.slice(0,5)};
    }""")
    print(rows)

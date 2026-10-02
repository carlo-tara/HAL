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
    page.goto(f"https://sznew.seozoom.it/project/view/seo/{pid}", wait_until="domcontentloaded", timeout=90000)
    page.wait_for_timeout(10000)
    info = page.evaluate("""() => {
      const html = document.documentElement.innerHTML;
      const apis = [...new Set((html.match(/\\/api\\/ajax\\/[a-zA-Z0-9_\\/-]+/g) || []))];
      const grids = typeof $ !== 'undefined' ? $('.dx-datagrid').length : 0;
      const rows = document.querySelectorAll('table tr, .dx-datagrid-rowsview tr').length;
      return { apis: apis.filter(u => /keyword|seo|page|on/i.test(u)).slice(0,20), grids, rows, h1: document.querySelector('h1,h2,.page-title')?.innerText?.slice(0,80) };
    }""")
    print(info)
    # capture any xhr from clicking export if present
    exp = page.locator("#exportStandardTable, .export-standard-table, .fa-file-export").first
    print("export btn count", exp.count())

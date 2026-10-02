#!/usr/bin/env python3
import json, sys
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
    data = page.evaluate("""() => {
      const grid = $('.dx-datagrid').first().dxDataGrid('instance');
      if (!grid) return {error: 'no grid'};
      const ds = grid.getDataSource();
      const items = ds.items ? ds.items() : (ds._items || []);
      return {count: items.length, sample: items.slice(0,3), cols: grid.option('columns')?.map(c=>c.caption||c.dataField).slice(0,8)};
    }""")
    print(json.dumps(data, indent=2, ensure_ascii=False)[:2000])

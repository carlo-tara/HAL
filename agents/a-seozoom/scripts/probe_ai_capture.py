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
    def on_req(r):
        if "content-gap-ai-overview" in r.url and r.method == "POST":
            print("REQ URL", r.url)
            print("POST", r.post_data)
    page.on("request", on_req)
    page.goto(f"https://sznew.seozoom.it/project/view/rankings/content-gap/{pid}?tab=aioverview", wait_until="domcontentloaded", timeout=90000)
    page.wait_for_timeout(10000)

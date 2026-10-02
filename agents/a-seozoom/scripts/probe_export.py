#!/usr/bin/env python3
"""Probe SeoZoom export endpoints (dev helper)."""
from __future__ import annotations

import json
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent))

from seozoom_lib import load_dotenv, login, open_export_modal, project_env_path, select_project  # noqa: E402


def main() -> None:
    env = load_dotenv(project_env_path())
    from playwright.sync_api import sync_playwright

    captures: list[dict] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()

        def on_response(resp):
            url = resp.url
            if any(x in url.lower() for x in ("export", "download", "csv", "xlsx", "excel")):
                captures.append({"url": url, "status": resp.status, "type": resp.headers.get("content-type", "")})

        page.on("response", on_response)
        login(page, env)
        select_project(page, env.get("SEOZOOM_PROJECT", ""))
        page.goto("https://sznew.seozoom.it/project/view/rankings/167592", wait_until="domcontentloaded", timeout=90000)
        page.wait_for_timeout(3000)
        if page.locator("#exportCsv").count():
            open_export_modal(page)
            with page.expect_download(timeout=60000) as dl_info:
                page.locator("#exportCsv").click(force=True)
            dl = dl_info.value
            captures.append({"download": dl.suggested_filename, "url": dl.url})
        browser.close()

    print(json.dumps(captures, indent=2))


if __name__ == "__main__":
    main()

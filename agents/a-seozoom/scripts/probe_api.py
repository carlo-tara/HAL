#!/usr/bin/env python3
"""Quick API probe for SeoZoom competitor/onpage params."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from playwright.sync_api import sync_playwright

from seozoom_api import SeoZoomClient
from seozoom_lib import load_dotenv, login, select_project, project_env_path


def main() -> None:
    env = load_dotenv(project_env_path())
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_context().new_page()
        login(page, env)
        pid = select_project(page, env.get("SEOZOOM_PROJECT", ""))
        domain_id = page.evaluate("() => String(DomainID || '')")
        vars_ = page.evaluate(
            """() => ({
              main: typeof mainDomain !== 'undefined' ? mainDomain : '',
              projectUrl: typeof projectUrl !== 'undefined' ? projectUrl : '',
              competitor: typeof competitor !== 'undefined' ? competitor : ''
            })"""
        )
        client = SeoZoomClient(page, pid, domain_id)
        client.warm(f"/project/view/rankings/content-gap/{pid}")
        vars_["competitor"] = page.evaluate("() => (typeof competitor !== 'undefined' ? competitor : '')")
        print("vars:", json.dumps(vars_, indent=2)[:800])

        for payload in [
            {"domainID": domain_id, "competitor": vars_["competitor"], "main": vars_["main"], "competitionMode": "keyword"},
            {"domainID": domain_id, "competitor": vars_["competitor"], "main": vars_["main"], "competitionMode": "domain"},
            {"domainID": domain_id, "competitor": vars_["competitor"], "main": vars_["main"], "competitionMode": "0"},
        ]:
            try:
                r = client.post("/api/ajax/domain-vs-domain/competition", payload)
                data = r.get("data", r)
                n = len(data) if isinstance(data, list) else "?"
                print("OK main=", payload["main"], "rows=", n)
                break
            except Exception as e:
                print("FAIL main=", payload.get("main"), e)

        client.warm(f"/project/view/keyword-studio/{pid}?tab=zero")
        for tab in ("zero", "all"):
            try:
                r = client.post(
                    "/api/ajax/keyword/get-page-keywords",
                    {
                        "domainID": domain_id,
                        "args[skip]": 0,
                        "args[take]": 100,
                        "activeTab": tab,
                        "activeFilter": "all",
                    },
                )
                data = r.get("data", {})
                rows = data.get("data", []) if isinstance(data, dict) else data
                print(f"tab={tab} rows={len(rows)}")
            except Exception as e:
                print(f"tab={tab} err={e}")

        browser.close()


if __name__ == "__main__":
    main()

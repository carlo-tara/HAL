#!/usr/bin/env python3
"""SeoZoom authenticated API client (browser session required)."""
from __future__ import annotations

import json
from typing import Any

from playwright.sync_api import Page

from seozoom_lib import BASE_URL


class SeoZoomClient:
    def __init__(self, page: Page, project_id: str, domain_id: str) -> None:
        self.page = page
        self.project_id = project_id
        self.domain_id = domain_id
        self._competitor_json: str | None = None

    def warm(self, path: str = "/project/view/167592") -> None:
        self.page.goto(f"{BASE_URL}{path}", wait_until="domcontentloaded", timeout=90000)
        self.page.wait_for_timeout(2500)

    def main_domain(self) -> str:
        return self.page.evaluate(
            """() => (typeof mainDomain !== 'undefined' ? mainDomain : '')"""
        ) or ""

    def post(self, endpoint: str, fields: dict[str, Any] | None = None, arrays: dict[str, list[Any]] | None = None) -> Any:
        fields = fields or {}
        arrays = arrays or {}
        result = self.page.evaluate(
            """async ({endpoint, fields, arrays}) => {
              const token = window.csrf || ($?.ajaxSettings?.data?.nonce);
              const fd = new FormData();
              fd.append('nonce', token);
              for (const [k, v] of Object.entries(fields)) {
                if (v === null || v === undefined) continue;
                fd.append(k, String(v));
              }
              for (const [k, vals] of Object.entries(arrays)) {
                for (const v of vals) fd.append(k, String(v));
              }
              const r = await fetch(endpoint, { method: 'POST', body: fd, credentials: 'include' });
              const text = await r.text();
              try { return JSON.parse(text); } catch (e) { return { status: r.status, raw: text.slice(0, 500) }; }
            }""",
            {"endpoint": endpoint, "fields": fields, "arrays": arrays},
        )
        if isinstance(result, dict) and result.get("status", 200) >= 400:
            raise RuntimeError(f"API {endpoint} failed: {result}")
        return result

    def competitor_json(self) -> str:
        if self._competitor_json:
            return self._competitor_json
        self.warm("/project/view/rankings/content-gap/" + self.project_id)
        comp = self.page.evaluate(
            """() => (typeof competitor !== 'undefined' ? competitor : '')"""
        )
        if not comp:
            raise RuntimeError("competitor JSON not found on content-gap page")
        self._competitor_json = comp
        return comp

    def monitored_keywords(self) -> list[dict[str, Any]]:
        self.warm(f"/project/view/rankings/{self.project_id}")
        payload = self.post(
            "/api/ajax/project/getmonitoredkeyfull",
            {"projectId": self.project_id, "domainId": self.domain_id},
        )
        ds = payload["data"]["dataSourceKeyword"]
        return json.loads(ds["keywordmonitorate"])

    def keyword_all(self) -> list[dict[str, Any]]:
        self.warm(f"/project/view/keyword-studio/{self.project_id}?tab=all")
        payload = self.post(
            "/api/ajax/keyword/get-page-keywords",
            {
                "domainID": self.domain_id,
                "args[skip]": 0,
                "args[take]": 15000,
                "activeTab": "all",
                "activeFilter": "all",
            },
        )
        return payload["data"]["data"]

    def long_tail(self) -> list[dict[str, Any]]:
        self.warm(f"/project/view/rankings/long-tail/{self.project_id}")
        payload = self.post(
            "/api/ajax/keyword/get-longtail-keywords",
            {"domainID": self.domain_id, "userLimit": 15000},
            arrays={"volumelimit[]": [110, 140]},
        )
        data = payload.get("data", payload)
        if isinstance(data, dict) and "data" in data:
            return data["data"]
        return data if isinstance(data, list) else []

    def content_gap(self, ai: bool = False) -> list[dict[str, Any]]:
        if ai:
            self.warm(f"/project/view/rankings/content-gap/{self.project_id}?tab=aioverview")
            comp_arr = list(json.loads(self.competitor_json()).keys())
            payload = self.post(
                "/api/ajax/domain/content-gap-ai-overview",
                {
                    "domainID": self.domain_id,
                    "competitor": json.dumps(comp_arr),
                    "limit": "false",
                },
            )
            data = payload.get("data", payload)
            return data if isinstance(data, list) else []
        self.warm(f"/project/view/rankings/content-gap/{self.project_id}")
        payload = self.post(
            "/api/ajax/domain/content-gap",
            {"domainID": self.domain_id, "competitor": self.competitor_json()},
        )
        data = payload.get("data", payload)
        rows = data if isinstance(data, list) else data.get("data", [])
        return rows

    def pages_list(self, endpoint: str) -> list[dict[str, Any]]:
        payload = self.post(endpoint, {"iddominio": self.domain_id})
        data = payload.get("data", payload)
        return data if isinstance(data, list) else []

    def competitor_grid(self) -> list[dict[str, Any]]:
        """Scrape competitor overview grid (domain-level summary)."""
        self.warm(f"/project/view/competitor/{self.project_id}")
        try:
            self.page.wait_for_selector(".dx-datagrid-rowsview tr.dx-data-row", timeout=30000)
        except Exception:
            self.page.wait_for_timeout(3000)
        return self.page.evaluate(
            """() => {
              const out = [];
              document.querySelectorAll('.dx-datagrid-rowsview tr.dx-data-row').forEach(tr => {
                const c = [...tr.querySelectorAll('td')].map(td => td.innerText.trim());
                if (c.length >= 4) {
                  out.push({rank: c[0], competitor: c[1], za: c[2], traffic: c[4] || '', keywords: c[5] || ''});
                }
              });
              return out;
            }"""
        )

    def competitor(self) -> Any:
        self.warm(f"/project/view/competitor/{self.project_id}")
        comp_json = self.competitor_json()
        competitors = json.loads(comp_json)
        first = next(iter(competitors.values()), "")
        payload = self.post(
            "/api/ajax/domain-vs-domain/competition",
            {
                "main": self.main_domain(),
                "competitor": first,
                "competitionMode": "content-gap",
            },
        )
        return payload

    def faq_questions(self) -> list[str]:
        self.warm(f"/project/view/rankings/questions/{self.project_id}")
        payload = self.post(
            "/api/ajax/domain/getFaq",
            {"domainID": self.domain_id, "projectID": self.project_id},
        )
        data = payload.get("data", payload)
        if isinstance(data, list):
            return [str(x.get("question", x)) if isinstance(x, dict) else str(x) for x in data]
        return []

    def clusters(self) -> list[dict[str, Any]]:
        self.warm(f"/project/view/rankings/clusters/{self.project_id}")
        payload = self.post("/api/ajax/domain/getClustersResearch", {"domainID": self.domain_id})
        data = payload.get("data", payload)
        if isinstance(data, list) and data and isinstance(data[0], list):
            return data[0]
        return data if isinstance(data, list) else []

    def keywords_clusters(self) -> list[dict[str, Any]]:
        self.warm(f"/project/view/rankings/clusters/{self.project_id}")
        clusters = self.clusters()
        url_id = ""
        for row in clusters:
            url_id = str(row.get("idurl") or row.get("urlID") or "")
            if url_id:
                break
        if not url_id:
            return []
        payload = self.post(
            "/api/ajax/domain/getKeywordsClustersResearch",
            {"domainID": self.domain_id, "urlID": url_id},
        )
        data = payload.get("data", payload)
        if isinstance(data, list) and data and isinstance(data[0], list):
            return data[0]
        return data if isinstance(data, list) else []

    def cannibalization(self) -> list[dict[str, Any]]:
        self.warm(f"/project/view/pages/overview-contents/{self.project_id}?tab=page-7-tab")
        payload = self.post(
            "/api/ajax/pages/cannibalization",
            {"iddominio": self.domain_id, "projectId": self.project_id},
        )
        data = payload.get("data", payload)
        return data if isinstance(data, list) else []

    def url_keywords(self, idurl: str) -> list[dict[str, Any]]:
        payload = self.post(
            "/api/ajax/pages/getURLKeywords",
            {"iddominio": self.domain_id, "idurl": idurl},
        )
        data = payload.get("data", payload)
        if isinstance(data, list) and data and isinstance(data[0], list):
            return data[0]
        if isinstance(data, list):
            return data
        return []

    def _store_url(self, mapping: dict[str, str], url: str, idurl: str) -> None:
        if not url or not idurl:
            return
        u = url.strip()
        variants = {u, u.rstrip("/") + "/", u.rstrip("/")}
        for v in variants:
            mapping[v] = str(idurl)

    def build_idurl_map(self) -> dict[str, str]:
        self.warm(f"/project/view/pages/overview-contents/{self.project_id}?tab=page-2-tab")
        mapping: dict[str, str] = {}
        for endpoint in (
            "/api/ajax/pages/getmainpages",
            "/api/ajax/pages/getpotentialpages",
        ):
            for row in self.pages_list(endpoint):
                self._store_url(mapping, row.get("url", ""), str(row.get("idurl", "")))
        self.warm(f"/project/view/keyword-studio/{self.project_id}?tab=all")
        for row in self.keyword_all():
            self._store_url(mapping, row.get("url", ""), str(row.get("idurl", "")))
        return mapping

    def onpage_seo(self) -> list[dict[str, Any]]:
        """Scrape SEO OnPage grid from /project/view/seo/{pid}."""
        path = f"/project/view/seo/{self.project_id}"
        scrape_js = """() => {
              const out = [];
              document.querySelectorAll('.dx-datagrid-rowsview tr.dx-data-row').forEach(tr => {
                const cells = [...tr.querySelectorAll('td')].map(td => td.innerText.trim());
                if (cells.length >= 6) {
                  out.push({
                    keyword: cells[1] || '',
                    volume: (cells[2] || '').replace(/\\./g, ''),
                    pos: cells[3] === '> 50' ? '101' : cells[3],
                    var: cells[4] || '',
                    url: cells[5] || '',
                    seo: cells[6] || '',
                    tag: cells[7] || '',
                  });
                }
              });
              return out;
            }"""
        rows: list[dict[str, Any]] = []
        for attempt in range(4):
            self.page.goto(f"{BASE_URL}/project/view/{self.project_id}", wait_until="domcontentloaded", timeout=90000)
            self.page.wait_for_timeout(2000)
            self.page.goto(f"{BASE_URL}{path}", wait_until="domcontentloaded", timeout=90000)
            for _ in range(8):
                title = self.page.title()
                if title and title != "seozoom":
                    break
                self.page.wait_for_timeout(2000)
            rows = self.page.evaluate(scrape_js)
            if rows:
                break
        return rows

    def onpage_zero(self) -> list[dict[str, Any]]:
        return self.onpage_seo()

    def pages_traffic_up(self) -> list[dict[str, Any]]:
        self.warm(f"/project/view/pages/overview-contents/{self.project_id}?tab=page-4-tab")
        payload = self.post("/api/ajax/pages/growingpagesdash", {"iddominio": self.domain_id})
        data = payload.get("data", payload)
        return data if isinstance(data, list) else []

    def pages_traffic_down(self) -> list[dict[str, Any]]:
        self.warm(f"/project/view/pages/overview-contents/{self.project_id}?tab=page-5-tab")
        payload = self.post("/api/ajax/pages/decreasingpagedash", {"iddominio": self.domain_id})
        data = payload.get("data", payload)
        return data if isinstance(data, list) else []

    def pages_with_more_keywords(self) -> list[dict[str, Any]]:
        self.warm(f"/project/view/pages/overview-contents/{self.project_id}?tab=page-3-tab")
        rows = self.pages_list("/api/ajax/pages/getmainpages")
        return sorted(rows, key=lambda r: int(r.get("totk") or 0), reverse=True)

    def pages_new_entry(self) -> list[dict[str, Any]]:
        self.warm(f"/project/view/pages/overview-contents/{self.project_id}?tab=page-6-tab")
        rows = self.pages_list("/api/ajax/pages/getmainpages")
        return [r for r in rows if int(r.get("newentry") or r.get("isnew") or 0) > 0]

    def pages_traffic_groups(self) -> dict[str, list[dict[str, Any]]]:
        """Build group_page_* buckets from main pages list."""
        rows = self.pages_list("/api/ajax/pages/getmainpages")
        groups = {
            "group_page_0.csv": [],
            "group_page_1_10.csv": [],
            "group_page_11_100.csv": [],
            "group_page_101_500.csv": [],
        }
        for row in rows:
            traffic = float(row.get("svol") or 0)
            out = {
                "URL": row.get("url", ""),
                "Traffico": int(traffic) if traffic == int(traffic) else traffic,
                "Keyword": row.get("totk", ""),
                "Menzioni AI": row.get("menzioni", 0),
            }
            if traffic <= 0:
                groups["group_page_0.csv"].append(out)
            elif traffic <= 10:
                groups["group_page_1_10.csv"].append(out)
            elif traffic <= 100:
                groups["group_page_11_100.csv"].append(out)
            else:
                groups["group_page_101_500.csv"].append(out)
        return groups

    # --- Project dashboard (/project/view/{pid}) ---

    def warm_dashboard(self) -> None:
        """Load project overview and scroll to trigger lazy widgets / JS globals."""
        self.warm(f"/project/view/{self.project_id}")
        self.page.wait_for_timeout(2500)
        for y in (800, 1600, 2800, 4000, 5500, 0):
            self.page.evaluate(f"window.scrollTo(0, {y})")
            self.page.wait_for_timeout(900)

    def dashboard_site_trend(self) -> list[dict[str, Any]]:
        payload = self.post(
            "/api/ajax/domain/get-chart-site-trend-data",
            {"domainID": self.domain_id},
        )
        data = payload.get("data", payload)
        return data if isinstance(data, list) else []

    def dashboard_domainstats(self) -> dict[str, Any]:
        payload = self.post(
            "/api/ajax/project/domainstats",
            {"ProjectID": self.project_id, "DomainID": self.domain_id},
        )
        data = payload.get("data", payload)
        return data if isinstance(data, dict) else {}

    def dashboard_backlink_counters(self) -> dict[str, Any]:
        domain = self.main_domain() or ""
        payload = self.post("/api/ajax/links/counters", {"domainUrl": domain})
        data = payload.get("data", payload)
        return data if isinstance(data, dict) else {}

    def dashboard_suggest_articles(self) -> list[dict[str, Any]]:
        payload = self.post(
            "/api/ajax/domain/suggest-articles",
            {"domainID": self.domain_id},
        )
        data = payload.get("data", payload)
        return data if isinstance(data, list) else []

    def dashboard_copilot_suggestions(self) -> list[dict[str, Any]]:
        payload = self.post(
            "/api/ajax/copilot/suggestions",
            {"ProjectID": self.project_id},
        )
        data = payload.get("data", payload)
        if isinstance(data, dict):
            return data.get("suggestions") or []
        return data if isinstance(data, list) else []

    def dashboard_competitor_stats(self) -> list[dict[str, Any]]:
        payload = self.post(
            "/api/ajax/project/competitorstats",
            {"ProjectID": self.project_id},
        )
        data = payload.get("data", payload)
        raw = data.get("competitortrends") if isinstance(data, dict) else data
        if isinstance(raw, str):
            try:
                return json.loads(raw)
            except json.JSONDecodeError:
                return []
        return raw if isinstance(raw, list) else []

    def dashboard_keywords_metrics(self, project_url: str = "") -> list[dict[str, Any]]:
        url = project_url or self.page.evaluate(
            """() => (typeof projectUrl !== 'undefined' ? projectUrl : '')"""
        ) or ""
        payload = self.post(
            "/api/ajax/project/keywordsmetrics",
            {"ProjectID": self.project_id, "url": url},
        )
        data = payload.get("data", payload)
        return data if isinstance(data, list) else []

    def dashboard_keywords_trend(self) -> list[dict[str, Any]]:
        payload = self.post(
            "/api/ajax/project/keywordstrend",
            {"ProjectID": self.project_id},
        )
        data = payload.get("data", payload)
        if isinstance(data, str):
            try:
                return json.loads(data)
            except json.JSONDecodeError:
                return []
        return data if isinstance(data, list) else []

    def dashboard_keywords_stats(self) -> dict[str, Any]:
        payload = self.post(
            "/api/ajax/project/keywordsstats",
            {"ProjectID": self.project_id},
        )
        data = payload.get("data", payload)
        return data if isinstance(data, dict) else {}

    def dashboard_traffic_stats(self) -> dict[str, Any]:
        payload = self.post(
            "/api/ajax/project/trafficstats",
            {"ProjectID": self.project_id},
        )
        data = payload.get("data", payload)
        return data if isinstance(data, dict) else {}

    def dashboard_piano_trimestrale(self) -> dict[str, Any]:
        payload = self.post(
            "/api/ajax/project/pianotrimestrale",
            {"ProjectID": self.project_id, "DomainID": self.domain_id},
        )
        data = payload.get("data", payload)
        return data if isinstance(data, dict) else {}

    def dashboard_traffic_forecast(self) -> dict[str, Any]:
        """Read previsione traffico from JS globals after warm_dashboard()."""
        return self.page.evaluate(
            """() => {
              const pick = (v) => {
                try { return JSON.parse(JSON.stringify(v)); } catch (e) { return null; }
              };
              return {
                seriesPrevisionData: pick(window.seriesPrevisionData) || [],
                seriesActualTrafficData: pick(window.seriesActualTrafficData) || [],
                totalTraffic: window.totalTraffic ?? null,
                totalTrafficPrevision: window.totalTrafficPrevision ?? null,
                trafficDifference: window.trafficDifference ?? null,
                statisticsText: (document.getElementById('trafficPrevisionStatistics') || {}).innerText || '',
              };
            }"""
        )

    def dashboard_keyup(self) -> list[dict[str, Any]]:
        payload = self.post(
            "/api/ajax/project/dashboardkeyup",
            {"projectId": self.project_id},
        )
        data = payload.get("data", payload)
        return data if isinstance(data, list) else []

    def dashboard_keydown(self) -> list[dict[str, Any]]:
        payload = self.post(
            "/api/ajax/project/dashboardkeydown",
            {"projectId": self.project_id},
        )
        data = payload.get("data", payload)
        return data if isinstance(data, list) else []


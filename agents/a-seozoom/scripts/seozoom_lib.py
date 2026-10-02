#!/usr/bin/env python3
"""Shared helpers for a-seozoom scripts."""
from __future__ import annotations

import json
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Any

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeout

BASE_URL = "https://sznew.seozoom.it"
SKILL_ROOT = Path(__file__).resolve().parents[1]


def default_project_root() -> Path:
    """Root progetto consumer: directory corrente (deve contenere .env e seo/)."""
    return Path.cwd()


def project_env_path(project_root: Path | None = None) -> Path:
    return (project_root or default_project_root()) / ".env"


def load_dotenv(path: Path) -> dict[str, str]:
    env: dict[str, str] = {}
    if not path.is_file():
        raise FileNotFoundError(f".env not found: {path}")
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        env[key.strip()] = value.strip().strip('"').strip("'")
    return env


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def today_yymmdd() -> str:
    return datetime.now().strftime("%y%m%d")


def domain_underscore(domain_slug: str) -> str:
    """Convert domain slug for underscore-prefixed export filenames."""
    return domain_slug.replace(".", "_")


def normalize_domain_slug(raw: str) -> str:
    """Normalize mainDomain / URL to hostname slug (no scheme, path, www)."""
    s = (raw or "").strip().lower()
    if not s:
        return ""
    s = re.sub(r"^https?://", "", s)
    s = s.split("/")[0].split("?")[0].strip()
    if s.startswith("www."):
        s = s[4:]
    return s


def competitor_project_from_env(env: dict[str, str]) -> str | None:
    """Return SEOZOOM_PROJECT_COMPETITOR if set (non-empty after strip), else None."""
    value = (env.get("SEOZOOM_PROJECT_COMPETITOR") or "").strip()
    return value or None


def load_project_manifest(project_root: Path) -> dict[str, Any]:
    """Load per-project export manifest; fallback to AgentFactory default."""
    project_manifest = project_root / "seo" / "export-manifest.json"
    if project_manifest.is_file():
        return load_json(project_manifest)
    return load_json(SKILL_ROOT / "references" / "export-manifest.json")


def export_filenames_for_domain(
    domain: str,
    questions_file: str | None = None,
) -> dict[str, str]:
    """Build global export filenames for a domain slug."""
    domain_u = domain_underscore(domain)
    questions = questions_file or f"questions_{domain_u}.txt"
    return {
        "monitored": f"https___{domain}_monitored.csv",
        "keyword_all": f"{domain}_keyword_all.csv",
        "onpage": f"{domain_u}_OnPageSEO.csv",
        "long_tail": f"{domain}_LongTailKeywords.csv",
        "content_gap": f"{domain_u}_ContentGap.csv",
        "content_gap_ai": f"{domain_u}_ContentGap_AI.csv",
        "pages_potential": f"{domain_u}_PagesWithPotential.csv",
        "pages_main": f"{domain_u}_MainPages.csv",
        "pages_more_keywords": f"{domain_u}_PagesWithMoreKeywords.csv",
        "pages_traffic_up": f"{domain_u}_PagesWithTrafficUp.csv",
        "pages_traffic_down": f"{domain_u}_PagesWithTrafficDown.csv",
        "pages_new_entry": f"{domain_u}_NewEntry.csv",
        "competitor": f"https___{domain}_competitor.csv",
        "questions": questions,
        "cannibalization": f"{domain_u}_Cannibalization.csv",
    }


def export_filenames(manifest: dict[str, Any]) -> dict[str, str]:
    """Build global export filenames from manifest domain_slug."""
    domain = manifest.get("domain_slug", "example.it")
    return export_filenames_for_domain(domain, manifest.get("questions_file"))


def manifest_with_domain(manifest: dict[str, Any], domain: str) -> dict[str, Any]:
    """Copy manifest with domain_slug (and questions_file) overridden for filenames."""
    out = dict(manifest)
    out["domain_slug"] = domain
    out["questions_file"] = f"questions_{domain_underscore(domain)}.txt"
    return out


def detect_project_domain(
    page: Page,
    pid: str,
    vars_map: dict[str, str] | None = None,
) -> str:
    """Detect project hostname from SeoZoom page JS globals (mainDomain / projectUrl)."""
    main = page.evaluate(
        "() => (typeof mainDomain !== 'undefined' ? String(mainDomain) : '')"
    ) or ""
    domain = normalize_domain_slug(main)
    if domain:
        return domain
    data = vars_map if vars_map is not None else get_project_vars(page, pid)
    domain = normalize_domain_slug(data.get("mainDomain", "") or "")
    if domain:
        return domain
    return normalize_domain_slug(data.get("projectUrl", "") or "")


def url_to_filename(url: str) -> str:
    u = url.strip()
    if not u.endswith("/"):
        u += "/"
    name = u.replace("https://", "https___").replace("/", "_")
    if name.endswith("_"):
        name = name[:-1]
    return f"{name}__all_keywords.csv"


def dedupe_download_name(name: str) -> str:
    return re.sub(r"\s*\(\d+\)(?=\.[^.]+$)", "", name)


def accept_cookies(page: Page) -> None:
    for sel in (
        "#CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll",
        "button:has-text('Accetta tutti')",
        "#CybotCookiebotDialogBodyButtonAccept",
    ):
        try:
            btn = page.locator(sel).first
            if btn.count() and btn.is_visible():
                btn.click(timeout=5000)
                page.wait_for_timeout(800)
                return
        except PlaywrightTimeout:
            continue


def login(page: Page, env: dict[str, str], force_fresh: bool = False) -> None:
    if not force_fresh and "login" not in page.url:
        page.goto(f"{BASE_URL}/", wait_until="domcontentloaded", timeout=90000)
        if "login" not in page.url and page.locator('a[href*="/project/view/"]').count():
            accept_cookies(page)
            return
    user = env["SEOZOOM_USER"]
    password = env["SEOZOOM_PASSWORD"]
    page.goto(f"{BASE_URL}/login/", wait_until="domcontentloaded", timeout=90000)
    accept_cookies(page)
    email = page.locator('input[placeholder="Email o Username"], input[type="email"], input[name="email"]')
    if not email.count():
        if page.locator('a[href*="/project/view/"]').count():
            return
        raise RuntimeError("Login form not found on SeoZoom login page")
    email.first.wait_for(state="visible", timeout=60000)
    email.first.fill(user)
    pwd = page.locator('input[placeholder="Password"], input[type="password"]')
    pwd.first.fill(password)
    page.locator('button:has-text("ACCEDI"), button:has-text("LOGIN")').first.click()
    page.wait_for_url(re.compile(r"sznew\.seozoom\.it/(?!login)"), timeout=90000)
    accept_cookies(page)


def resolve_project_id(page: Page, project_name: str) -> str:
    page.goto(f"{BASE_URL}/", wait_until="domcontentloaded", timeout=90000)
    accept_cookies(page)
    combo = page.locator('select, [role="combobox"]').filter(has_text=re.compile("Seleziona", re.I))
    if combo.count():
        combo.first.click()
        page.locator(f'[role="option"]:has-text("{project_name}")').first.click()
        page.wait_for_timeout(800)
    links = page.locator(f'a[href*="/project/view/"]:has-text("{project_name}")')
    if links.count():
        href = links.first.get_attribute("href") or ""
        m = re.search(r"/project/view/(\d+)", href)
        if m:
            return m.group(1)
    # fallback: scan all project links
    for el in page.locator('a[href*="/project/view/"]').all():
        text = (el.inner_text() or "").strip()
        href = el.get_attribute("href") or ""
        if project_name.lower() in text.lower():
            m = re.search(r"/project/view/(\d+)", href)
            if m:
                return m.group(1)
    raise RuntimeError(f"Project not found: {project_name}")


def select_project(page: Page, project_name: str) -> str:
    pid = resolve_project_id(page, project_name)
    page.goto(f"{BASE_URL}/project/view/{pid}", wait_until="domcontentloaded", timeout=90000)
    return pid


def open_export_modal(page: Page) -> None:
    if page.locator("#exportCsv").count() and page.locator("#exportCsv").first.is_visible():
        return
    for sel in (
        "#exportStandardTable",
        ".export-standard-table",
        "#exportAndamentoKeyword",
        ".export-andamento-keyword",
        ".fas.fa-file-export",
        ".fa-file-export",
        'button:has-text("Esporta tutti i dati in Excel")',
    ):
        loc = page.locator(sel).first
        if loc.count():
            try:
                loc.click(timeout=8000)
                page.wait_for_timeout(800)
                if page.locator("#exportCsv").count() and page.locator("#exportCsv").first.is_visible():
                    return
            except PlaywrightTimeout:
                continue


def click_export(page: Page, fmt: str = "csv") -> None:
    """Click export button; fmt is csv or xlsx."""
    btn_id = "exportCsv" if fmt == "csv" else "exportXlsx"
    target = page.locator(f"#{btn_id}").first
    if not (target.count() and target.is_visible()):
        open_export_modal(page)
    if target.count() and target.is_visible():
        target.click()
        return
    alt = page.locator(f"button:has-text('.{fmt}')").first
    if alt.count() and alt.is_visible():
        alt.click()
        return
    raise RuntimeError("Export button not found on page")


def download_from_page(
    page: Page,
    url: str,
    dest: Path,
    fmt: str = "csv",
    wait_ms: int = 1500,
    retries: int = 2,
) -> bool:
    dest.parent.mkdir(parents=True, exist_ok=True)
    for attempt in range(retries):
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=90000)
            page.wait_for_timeout(wait_ms)
            accept_cookies(page)
            if not (
                page.locator("#exportCsv").count()
                or page.locator("button:has-text('.csv')").count()
                or page.locator('button:has-text("Esporta tutti i dati in Excel")').count()
                or page.locator(".fa-file-export").count()
            ):
                return False
            with page.expect_download(timeout=60000) as dl_info:
                click_export(page, fmt=fmt)
            download = dl_info.value
            download.save_as(dest)
            return dest.is_file() and dest.stat().st_size > 0
        except PlaywrightTimeout:
            if attempt + 1 == retries:
                return False
            time.sleep(2)
    return False


def get_project_vars(page: Page, pid: str) -> dict[str, str]:
    page.goto(f"{BASE_URL}/project/view/pages/page-keyword-match/{pid}", wait_until="domcontentloaded", timeout=90000)
    raw = page.evaluate(
        """() => JSON.stringify({
            pid: typeof pid !== 'undefined' ? String(pid) : '',
            projectUrl: typeof projectUrl !== 'undefined' ? projectUrl : '',
            DomainID: typeof DomainID !== 'undefined' ? String(DomainID) : '',
            mainDomain: typeof mainDomain !== 'undefined' ? mainDomain : ''
        })"""
    )
    return json.loads(raw)

#!/usr/bin/env python3
"""Export Google Merchant Center catalog to seo/YYMMDD/google/gmc_*.csv."""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from analytics_lib import (  # noqa: E402
    apply_google_credentials_env,
    date_range,
    load_analytics_env,
    period_suffix,
    resolve_creds_path,
    resolve_project_paths,
    write_csv,
)
from seozoom_lib import default_project_root  # noqa: E402

GMC_CONTENT_SCOPE = "https://www.googleapis.com/auth/content"

PRODUCT_FIELDS = [
    "offer_id",
    "title",
    "description",
    "link",
    "image_link",
    "brand",
    "availability",
    "condition",
    "price",
    "gtin",
    "mpn",
    "google_product_category",
    "custom_label_0",
    "custom_label_1",
    "custom_label_2",
    "custom_label_3",
    "custom_label_4",
    "size",
    "feed_label",
    "content_language",
    "channel",
    "product_id",
]

ISSUE_FIELDS = [
    "offer_id",
    "product_id",
    "severity",
    "code",
    "detail",
    "resolution",
    "attribute",
]

# Align Merchant API Severity enum with legacy Content API productstatuses labels.
_SEVERITY_MAP = {
    "DISAPPROVED": "disapproved",
    "DEMOTED": "demoted",
    "NOT_IMPACTED": "unaffected",
    "SEVERITY_UNSPECIFIED": "",
}


def _merchant_credentials(env: dict[str, str], project_root: Path):
    from google.oauth2 import service_account

    path = resolve_creds_path(project_root, env)
    return service_account.Credentials.from_service_account_file(
        str(path), scopes=[GMC_CONTENT_SCOPE]
    )


def _format_price_micros(amount_micros: Any, currency: str) -> str:
    try:
        amount = float(amount_micros or 0) / 1_000_000
    except (TypeError, ValueError):
        amount = 0.0
    return f"{amount:.2f} {currency or 'EUR'}"


def _desc_plain(text: Any, limit: int = 500) -> str:
    if not text:
        return ""
    raw = re.sub(r"<[^>]+>", " ", str(text))
    raw = re.sub(r"\s+", " ", raw).strip()
    return raw[:limit]


def _enum_name(value: Any) -> str:
    if value is None:
        return ""
    name = getattr(value, "name", None)
    if name:
        return str(name)
    text = str(value).strip()
    if "." in text:
        text = text.rsplit(".", 1)[-1]
    return text


def _normalize_severity(value: Any) -> str:
    raw = _enum_name(value).upper()
    if not raw:
        return ""
    if raw in _SEVERITY_MAP:
        return _SEVERITY_MAP[raw]
    return raw.lower()


def _product_attrs(product: Any) -> Any:
    return getattr(product, "product_attributes", None) or getattr(
        product, "attributes", None
    )


def _product_row_merchant(
    product: Any, target_country: str, content_language: str
) -> dict[str, str]:
    attrs = _product_attrs(product)
    price = ""
    if attrs is not None and getattr(attrs, "price", None) is not None:
        price = _format_price_micros(
            getattr(attrs.price, "amount_micros", 0),
            getattr(attrs.price, "currency_code", "EUR") or "EUR",
        )
    size_val = ""
    if attrs is not None:
        size_val = str(getattr(attrs, "size", "") or "")
        if not size_val:
            sizes = getattr(attrs, "sizes", None)
            if sizes:
                try:
                    size_list = list(sizes)
                    size_val = str(size_list[0]) if size_list else ""
                except TypeError:
                    size_val = str(sizes)

    offer_id = getattr(product, "offer_id", "") or ""
    if not offer_id and attrs is not None:
        offer_id = getattr(attrs, "offer_id", "") or ""

    return {
        "offer_id": offer_id,
        "title": getattr(attrs, "title", "") if attrs else "",
        "description": _desc_plain(getattr(attrs, "description", "") if attrs else ""),
        "link": getattr(attrs, "link", "") if attrs else "",
        "image_link": getattr(attrs, "image_link", "") if attrs else "",
        "brand": getattr(attrs, "brand", "") if attrs else "",
        "availability": _enum_name(getattr(attrs, "availability", "") if attrs else ""),
        "condition": _enum_name(getattr(attrs, "condition", "") if attrs else ""),
        "price": price,
        "gtin": getattr(attrs, "gtin", "") if attrs else "",
        "mpn": getattr(attrs, "mpn", "") if attrs else "",
        "google_product_category": str(
            getattr(attrs, "google_product_category", "") or ""
        )
        if attrs
        else "",
        "custom_label_0": getattr(attrs, "custom_label_0", "") if attrs else "",
        "custom_label_1": getattr(attrs, "custom_label_1", "") if attrs else "",
        "custom_label_2": getattr(attrs, "custom_label_2", "") if attrs else "",
        "custom_label_3": getattr(attrs, "custom_label_3", "") if attrs else "",
        "custom_label_4": getattr(attrs, "custom_label_4", "") if attrs else "",
        "size": size_val,
        "feed_label": getattr(product, "feed_label", "") or target_country,
        "content_language": getattr(product, "content_language", "") or content_language,
        "channel": "local" if getattr(product, "legacy_local", False) else "online",
        "product_id": getattr(product, "name", ""),
    }


def _issue_rows_merchant(product: Any) -> list[dict[str, str]]:
    """Item-level issues from Merchant API Product.product_status (replaces productstatuses)."""
    offer_id = getattr(product, "offer_id", "") or ""
    attrs = _product_attrs(product)
    if not offer_id and attrs is not None:
        offer_id = getattr(attrs, "offer_id", "") or ""

    status = getattr(product, "product_status", None)
    raw_issues = getattr(status, "item_level_issues", None) if status else None
    if not raw_issues:
        raw_issues = getattr(product, "product_issues", None) or []

    issues: list[dict[str, str]] = []
    for issue in raw_issues:
        detail = (
            getattr(issue, "description", "")
            or getattr(issue, "detail", "")
            or ""
        )
        issues.append(
            {
                "offer_id": offer_id,
                "product_id": getattr(product, "name", ""),
                "severity": _normalize_severity(getattr(issue, "severity", "")),
                "code": getattr(issue, "code", "") or "",
                "detail": detail,
                "resolution": getattr(issue, "resolution", "") or "",
                "attribute": getattr(issue, "attribute", "") or "",
            }
        )
    return issues


def _product_row_content(item: dict[str, Any]) -> dict[str, str]:
    price = item.get("price", {}) or {}
    amount = price.get("value", "")
    currency = price.get("currency", "EUR")
    sizes = item.get("sizes") or []
    size_val = sizes[0] if isinstance(sizes, list) and sizes else item.get("size", "")
    return {
        "offer_id": item.get("offerId", ""),
        "title": item.get("title", ""),
        "description": _desc_plain(item.get("description", "")),
        "link": item.get("link", ""),
        "image_link": item.get("imageLink", ""),
        "brand": item.get("brand", ""),
        "availability": item.get("availability", ""),
        "condition": item.get("condition", ""),
        "price": f"{amount} {currency}".strip(),
        "gtin": item.get("gtin", "") or "",
        "mpn": item.get("mpn", "") or "",
        "google_product_category": str(item.get("googleProductCategory", "") or ""),
        "custom_label_0": item.get("customLabel0", "") or "",
        "custom_label_1": item.get("customLabel1", "") or "",
        "custom_label_2": item.get("customLabel2", "") or "",
        "custom_label_3": item.get("customLabel3", "") or "",
        "custom_label_4": item.get("customLabel4", "") or "",
        "size": str(size_val or ""),
        "feed_label": item.get("targetCountry", "") or item.get("feedLabel", ""),
        "content_language": item.get("contentLanguage", ""),
        "channel": item.get("channel", ""),
        "product_id": item.get("id", ""),
    }


def _issue_rows_content(item: dict[str, Any]) -> list[dict[str, str]]:
    offer_id = item.get("offerId", "")
    product_id = item.get("id", "")
    issues = []
    for issue in item.get("issues", []) or []:
        issues.append(
            {
                "offer_id": offer_id,
                "product_id": product_id,
                "severity": issue.get("servability", "") or issue.get("severity", ""),
                "code": issue.get("code", ""),
                "detail": issue.get("detail", "") or issue.get("description", ""),
                "resolution": issue.get("resolution", "") or "",
                "attribute": issue.get("attributeName", "") or issue.get("attribute", "") or "",
            }
        )
    return issues


def _export_merchant_api(
    creds,
    merchant_id: str,
    target_country: str,
    content_language: str,
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    from google.shopping import merchant_products_v1

    client = merchant_products_v1.ProductsServiceClient(credentials=creds)
    request = merchant_products_v1.ListProductsRequest(
        parent=f"accounts/{merchant_id}",
        page_size=250,
    )
    products: list[dict[str, str]] = []
    issues: list[dict[str, str]] = []
    for product in client.list_products(request=request):
        products.append(_product_row_merchant(product, target_country, content_language))
        issues.extend(_issue_rows_merchant(product))
    return products, issues


def _export_content_api(creds, merchant_id: str) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    """Legacy Content API path (GMC_API=content only). Sunset 2026-08-18."""
    from googleapiclient.discovery import build

    service = build("content", "v2.1", credentials=creds, cache_discovery=False)
    products: list[dict[str, str]] = []
    issues: list[dict[str, str]] = []
    page_token = None
    while True:
        request = service.products().list(
            merchantId=merchant_id, maxResults=250, pageToken=page_token
        )
        response = request.execute()
        for item in response.get("resources", []):
            products.append(_product_row_content(item))
            issues.extend(_issue_rows_content(item))
        page_token = response.get("nextPageToken")
        if not page_token:
            break
    return products, issues


def export_gmc(project_root: Path, export_date: str | None, days: int) -> dict:
    root, out_dir = resolve_project_paths(project_root, export_date)
    env = load_analytics_env(root)
    apply_google_credentials_env(root, env)

    merchant_id = env.get("GMC_MERCHANT_ID", "").strip()
    if not merchant_id:
        raise ValueError("GMC_MERCHANT_ID missing in .env")

    target_country = env.get("GMC_TARGET_COUNTRY", "IT").strip() or "IT"
    content_language = env.get("GMC_CONTENT_LANGUAGE", "it").strip() or "it"
    api_mode = env.get("GMC_API", "merchant").strip().lower() or "merchant"

    creds = _merchant_credentials(env, root)
    start_d, end_d = date_range(days)
    suffix = period_suffix(start_d, end_d)

    errors: list[str] = []
    products: list[dict[str, str]] = []
    issues: list[dict[str, str]] = []

    if api_mode == "content":
        products, issues = _export_content_api(creds, merchant_id)
    else:
        products, issues = _export_merchant_api(
            creds, merchant_id, target_country, content_language
        )

    products_path = out_dir / f"gmc_products_{suffix}.csv"
    issues_path = out_dir / f"gmc_product_issues_{suffix}.csv"
    summary_path = out_dir / f"gmc_summary_{suffix}.json"

    n_products = write_csv(products_path, PRODUCT_FIELDS, products)
    n_issues = write_csv(issues_path, ISSUE_FIELDS, issues)
    summary = {
        "merchant_id": merchant_id,
        "api_mode": api_mode,
        "issues_source": (
            "merchant_product_status"
            if api_mode != "content"
            else "content_products_issues"
        ),
        "target_country": target_country,
        "content_language": content_language,
        "period": suffix,
        "products_rows": n_products,
        "issues_rows": n_issues,
        "errors": errors,
        "exported_at": date.today().isoformat(),
        "fields": PRODUCT_FIELDS,
    }
    summary_path.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    return {
        "ok": n_products > 0,
        "out_dir": str(out_dir),
        "period": suffix,
        "merchant_id": merchant_id,
        "gmc_products": str(products_path),
        "gmc_products_rows": n_products,
        "gmc_product_issues": str(issues_path),
        "gmc_product_issues_rows": n_issues,
        "gmc_summary": str(summary_path),
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Export GMC catalog to seo/YYMMDD/google/")
    parser.add_argument("--project-root", type=Path, default=default_project_root())
    parser.add_argument("--date", help="Export folder YYMMDD (default: today)")
    parser.add_argument("--days", type=int, default=28, help="Period suffix lookback days")
    args = parser.parse_args()

    try:
        result = export_gmc(args.project_root, args.date, args.days)
    except Exception as exc:  # noqa: BLE001
        print(f"GMC export failed: {exc}", file=sys.stderr)
        return 1

    print(
        f"GMC export OK: {result['gmc_products_rows']} products, "
        f"{result['gmc_product_issues_rows']} issues -> {result['out_dir']}"
    )
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

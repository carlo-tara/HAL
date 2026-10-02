#!/usr/bin/env python3
"""Export Google Tag Manager container snapshot to seo/YYMMDD/gtm_*."""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from analytics_lib import (  # noqa: E402
    apply_google_credentials_env,
    google_credentials,
    load_analytics_env,
    resolve_project_paths,
    write_csv,
)
from seozoom_lib import default_project_root  # noqa: E402

DEFAULT_CONTAINER = "GTM-KN9M84W"


def _tag_params(tag: dict) -> dict[str, str]:
    return {p.get("key", ""): p.get("value", "") for p in (tag.get("parameter") or [])}


def _event_settings_table(tag: dict) -> list[dict[str, str]]:
    rows = []
    for p in tag.get("parameter") or []:
        if p.get("key") != "eventSettingsTable" or not p.get("list"):
            continue
        for item in p["list"]:
            m = {x.get("key"): x.get("value") for x in item.get("map", [])}
            if m.get("parameter"):
                rows.append({"parameter": m["parameter"], "value": m.get("parameterValue", "")})
    return rows


def export_gtm(project_root: Path, export_date: str | None, container_public_id: str | None = None) -> dict:
    from googleapiclient.discovery import build

    root, out_dir = resolve_project_paths(project_root, export_date)
    env = load_analytics_env(root)
    apply_google_credentials_env(root, env)

    target_id = (container_public_id or env.get("GTM_CONTAINER_ID") or DEFAULT_CONTAINER).strip()
    creds = google_credentials(env, root, include_gtm=True)
    svc = build("tagmanager", "v2", credentials=creds, cache_discovery=False)

    live = None
    account_name = ""
    container_name = ""
    for account in svc.accounts().list().execute().get("account", []):
        for container in svc.accounts().containers().list(parent=account["path"]).execute().get("container", []):
            if container.get("publicId") != target_id:
                continue
            live = svc.accounts().containers().versions().live(parent=container["path"]).execute()
            account_name = account.get("name", "")
            container_name = container.get("name", "")
            break
        if live:
            break

    if not live:
        raise ValueError(f"GTM container not found or not accessible: {target_id}")

    version_id = live.get("containerVersionId", "")
    json_path = out_dir / f"gtm_container_live_{target_id}_v{version_id}.json"
    json_path.write_text(json.dumps(live, indent=2, ensure_ascii=False), encoding="utf-8")

    triggers = {t["triggerId"]: t for t in (live.get("trigger") or [])}

    tag_rows = []
    for tag in live.get("tag") or []:
        params = _tag_params(tag)
        firing = [triggers.get(fid, {}).get("name", fid) for fid in (tag.get("firingTriggerId") or [])]
        settings = _event_settings_table(tag)
        tag_rows.append(
            {
                "name": tag.get("name", ""),
                "type": tag.get("type", ""),
                "event_name": params.get("eventName", ""),
                "measurement_id": params.get("tagId") or params.get("measurementIdOverride", ""),
                "triggers": "; ".join(firing),
                "event_params": "; ".join(f"{s['parameter']}={s['value']}" for s in settings),
            }
        )

    trigger_rows = []
    for tr in live.get("trigger") or []:
        event_name = ""
        for filt in tr.get("customEventFilter") or tr.get("filter") or []:
            if isinstance(filt, dict):
                for param in filt.get("parameter") or []:
                    if param.get("key") == "arg1":
                        event_name = param.get("value", "")
        trigger_rows.append(
            {
                "name": tr.get("name", ""),
                "type": tr.get("type", ""),
                "event_name": event_name,
                "trigger_id": tr.get("triggerId", ""),
            }
        )

    variable_rows = []
    for var in live.get("variable") or []:
        params = _tag_params(var)
        variable_rows.append(
            {
                "name": var.get("name", ""),
                "type": var.get("type", ""),
                "data_layer_name": params.get("name", params.get("dataLayerVersion", "")),
            }
        )

    tags_path = out_dir / f"gtm_tags_{target_id}_v{version_id}.csv"
    triggers_path = out_dir / f"gtm_triggers_{target_id}_v{version_id}.csv"
    variables_path = out_dir / f"gtm_variables_{target_id}_v{version_id}.csv"

    n_tags = write_csv(
        tags_path,
        ["name", "type", "event_name", "measurement_id", "triggers", "event_params"],
        tag_rows,
    )
    n_triggers = write_csv(
        triggers_path,
        ["name", "type", "event_name", "trigger_id"],
        trigger_rows,
    )
    n_variables = write_csv(
        variables_path,
        ["name", "type", "data_layer_name"],
        variable_rows,
    )

    return {
        "ok": True,
        "out_dir": str(out_dir),
        "container_public_id": target_id,
        "container_name": container_name,
        "account_name": account_name,
        "version_id": version_id,
        "gtm_json": str(json_path),
        "gtm_tags": str(tags_path),
        "gtm_tags_rows": n_tags,
        "gtm_triggers": str(triggers_path),
        "gtm_triggers_rows": n_triggers,
        "gtm_variables": str(variables_path),
        "gtm_variables_rows": n_variables,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Export GTM live container to seo/YYMMDD/")
    parser.add_argument("--project-root", type=Path, default=default_project_root())
    parser.add_argument("--date", help="Export folder YYMMDD (default: today)")
    parser.add_argument("--container-id", help=f"GTM public ID (default: {DEFAULT_CONTAINER})")
    args = parser.parse_args()

    try:
        result = export_gtm(args.project_root, args.date, args.container_id)
    except Exception as exc:  # noqa: BLE001
        print(f"GTM export failed: {exc}", file=sys.stderr)
        return 1

    print(
        f"GTM export OK: {result['container_name']} {result['container_public_id']} "
        f"v{result['version_id']} -> {result['out_dir']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

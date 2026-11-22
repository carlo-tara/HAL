"""HT-022 — forwarder outcome: import inbox/laya-outcomes/*.ndjson → replay POST /outcome.

Contratto (docs/slices/M1.5-gateway-import-spec.md, hal_mcp_docs 2026-11-22):
- Scansione solo `.ndjson` a estensione finale (mai `.tmp`, mai `.imported/`);
- una riga = un evento; il voto è `outcome` (esplicito, source `chapter_outcome`)
  o `proxy_outcome` (proxy, source `access_after_route`); `route` non è un voto;
- dedup per `request_hash` a carico del consumer: esplicito ha precedenza sul
  proxy — una inferenza = un voto (le cache-hit restano saltate server-side);
- trasporto: `POST {LAYA_BASE_URL}/outcome` {request_hash, outcome, source
  [, correction]} con Bearer, stessi header/timeout/TLS di `laya_service`;
- file importato riuscito → archiviato in `.imported/` (stesso nome, audit,
  mai cancellare); fallimento di trasporto ⇒ file lasciato in inbox (retry-safe
  grazie a content-addressing + dedup Laya);
- righe senza `request_hash` o con `event` sconosciuto: saltate con contatore,
  mai raise. Precondizioni insoddisfatte: codici macchina senza scrivere nulla
  (`gateway_root_unset` / `gateway_root_missing` / `inbox_absent` /
  `inbox_not_writable`).

Uso: `python3 scripts/outcome_forwarder.py [--gateway-root PATH]` (on-demand o
schedulato). Root di default: env `HAL_GATEWAY_ROOT`, poi il canonico (repo).
"""

from __future__ import annotations

import argparse
import json
import os
from collections.abc import Callable
from pathlib import Path
from typing import Any

# eventi-voto: priorità più alta vince a parità di request_hash
_VOTE_PRIORITY: dict[str, int] = {"outcome": 2, "proxy_outcome": 1}
_VALID_VERDICTS = frozenset({"correct", "incorrect"})
_INBOX_RELPATH = Path("inbox") / "laya-outcomes"
_ARCHIVE_DIRNAME = ".imported"
_REPO_ROOT = Path(__file__).resolve().parents[1]

PostFn = Callable[[dict[str, Any]], dict[str, Any]]


def _default_post(body: dict[str, Any]) -> dict[str, Any]:
    """Trasporto canonico del voto verso Laya (stessi header/timeout/TLS)."""
    import requests

    import laya_service

    session = requests.Session()
    adapter = laya_service.build_laya_adapter()
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    try:
        response = session.post(
            f"{laya_service.LAYA_BASE_URL}/outcome",
            json=body,
            headers={"Authorization": f"Bearer {laya_service.get_laya_api_key()}"},
            timeout=laya_service.get_timeout_tuple(),
            verify=laya_service.get_tls_verify(),
            allow_redirects=False,
        )
        response.raise_for_status()
        try:
            payload = response.json()
        except ValueError:
            return {}
        return payload if isinstance(payload, dict) else {}
    finally:
        session.close()


def _resolve_root(gateway_root: str | None) -> tuple[Path | None, str | None]:
    """Radice gateway: parametro, poi env HAL_GATEWAY_ROOT, poi canonico (repo)."""
    raw: str | None
    if gateway_root is not None:
        raw = gateway_root
    else:
        raw = os.environ.get("HAL_GATEWAY_ROOT")
        if raw is None:
            raw = str(_REPO_ROOT)
    if not str(raw).strip():
        return None, "gateway_root_unset"
    base = Path(str(raw)).expanduser()
    if not base.is_dir():
        return None, "gateway_root_missing"
    return base, None


def forward_outcomes(
    gateway_root: str | None = None, post_fn: PostFn | None = None
) -> dict[str, Any]:
    """Importa gli ndjson dell'inbox e replay dei voti verso Laya. Mai raise."""
    result: dict[str, Any] = {
        "ok": False,
        "error": None,
        "files_scanned": 0,
        "votes_forwarded": 0,
        "votes_failed": 0,
        "dedup_dropped": 0,
        "skipped_no_hash": 0,
        "skipped_no_verdict": 0,
        "skipped_unknown_event": 0,
        "skipped_not_vote": 0,
        "skipped_malformed": 0,
        "files_archived": 0,
    }
    base, err = _resolve_root(gateway_root)
    if base is None or err is not None:
        result["error"] = err
        return result

    inbox = base / _INBOX_RELPATH
    if not inbox.is_dir():
        result["error"] = "inbox_absent"
        return result
    if not os.access(inbox, os.W_OK):
        result["error"] = "inbox_not_writable"
        return result

    post = post_fn or _default_post
    forwarded: set[str] = set()
    archive_dir = inbox / _ARCHIVE_DIRNAME

    for path in sorted(p for p in inbox.glob("*.ndjson") if p.is_file()):
        result["files_scanned"] += 1
        votes: dict[str, dict[str, Any]] = {}
        for raw_line in path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
            except ValueError:
                result["skipped_malformed"] += 1
                continue
            if not isinstance(event, dict):
                result["skipped_malformed"] += 1
                continue

            request_hash = event.get("request_hash")
            if not isinstance(request_hash, str) or not request_hash.strip():
                result["skipped_no_hash"] += 1
                continue

            priority = _VOTE_PRIORITY.get(str(event.get("event")), 0)
            if priority == 0:
                if event.get("event") == "route":
                    result["skipped_not_vote"] += 1
                else:
                    result["skipped_unknown_event"] += 1
                continue

            verdict = event.get("verdict")
            if not isinstance(verdict, str) or verdict not in _VALID_VERDICTS:
                result["skipped_no_verdict"] += 1
                continue

            candidate: dict[str, Any] = {
                "request_hash": request_hash,
                "outcome": verdict,
                "source": str(event.get("source") or ""),
                "priority": priority,
            }
            correction = event.get("correction")
            if isinstance(correction, str) and correction:
                candidate["correction"] = correction

            current = votes.get(request_hash)
            if current is None or candidate["priority"] > current["priority"]:
                if current is not None:
                    result["dedup_dropped"] += 1
                votes[request_hash] = candidate
            else:
                result["dedup_dropped"] += 1

        failed_here = 0
        for request_hash, vote in votes.items():
            if request_hash in forwarded:
                result["dedup_dropped"] += 1
                continue
            body = {key: value for key, value in vote.items() if key != "priority"}
            try:
                post(body)
            except Exception:  # noqa: BLE001 - retry-safe: il file resta in inbox
                result["votes_failed"] += 1
                failed_here += 1
                continue
            forwarded.add(request_hash)
            result["votes_forwarded"] += 1

        if failed_here == 0:
            archive_dir.mkdir(parents=True, exist_ok=True)
            os.replace(path, archive_dir / path.name)
            result["files_archived"] += 1

    result["ok"] = True
    return result


def main(argv: list[str] | None = None, post_fn: PostFn | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="outcome_forwarder",
        description="HT-022: importa inbox/laya-outcomes/*.ndjson e replay "
        "dei voti verso Laya (POST /outcome).",
    )
    parser.add_argument(
        "--gateway-root",
        default=None,
        help="radice gateway (default: env HAL_GATEWAY_ROOT, poi il canonico)",
    )
    args = parser.parse_args(argv)
    result = forward_outcomes(args.gateway_root, post_fn=post_fn)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

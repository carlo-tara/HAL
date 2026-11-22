"""HT-022 — forwarder outcome: import inbox/laya-outcomes/*.ndjson → replay POST /outcome.

Contratto: docs/slices/M1.5-gateway-import-spec.md (hal_mcp_docs, 2026-11-22):
- solo estensione finale `.ndjson`, mai `.tmp`;
- dedup per `request_hash` a carico del consumer: esplicito (`outcome`) ha
  precedenza sul proxy (`proxy_outcome`/access_after_route), una inferenza = un voto;
- file importato riuscito → archiviato in `.imported/` con lo stesso nome
  (audit, mai cancellare); re-run → 0 nuovi voti;
- righe senza `request_hash` o con `event` sconosciuto → saltate con
  contatore, mai raise (exit 0);
- inbox assente → il forwarder non parte, esito `inbox_absent` senza scrivere.

Voto wire verso Laya (contratto laya_outcome, SKILL laya §Calibrazione):
`POST {LAYA_BASE_URL}/outcome` {request_hash, outcome, source[, correction]} con
Bearer; il server salta le cache-hit (una inferenza = un voto).

Nessuna rete nei test: il trasporto è iniettato (`post_fn`).
"""

from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path
from typing import Any

from scripts import outcome_forwarder


def _vote(
    event: str,
    request_hash: str,
    verdict: str = "correct",
    source: str = "chapter_outcome",
    **extra: Any,
) -> dict[str, Any]:
    line: dict[str, Any] = {
        "ts": "2026-11-22T00:00:00+00:00",
        "event": event,
        "request_hash": request_hash,
        "verdict": verdict,
        "source": source,
        "doc_id": "doc-x",
        "project": "hal_mcp_docs",
    }
    line.update(extra)
    return line


class _Recorder:
    """post_fn fake: registra i body, opzionalmente fallisce (RuntimeError)."""

    def __init__(self, fail_times: int = 0) -> None:
        self.calls: list[dict[str, Any]] = []
        self._fail_times = fail_times

    def __call__(self, body: dict[str, Any]) -> dict[str, Any]:
        if self._fail_times > 0:
            self._fail_times -= 1
            raise RuntimeError("laya down (test)")
        self.calls.append(body)
        return {"rows_updated": 1}


class OutcomeForwarderTest(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path(tempfile.mkdtemp(prefix="ht022-"))
        self.inbox = self.root / "inbox" / "laya-outcomes"
        self.inbox.mkdir(parents=True)

    def tearDown(self) -> None:
        shutil.rmtree(self.root, ignore_errors=True)

    def _write(self, name: str, lines: list[Any]) -> Path:
        payload = "\n".join(
            line if isinstance(line, str) else json.dumps(line, sort_keys=True)
            for line in lines
        )
        path = self.inbox / name
        path.write_text(payload + "\n", encoding="utf-8")
        return path

    # ---- acceptance 1: fixture 2 route + 1 proxy (hash condiviso) ----

    def test_votes_forwarded_dedup_and_archive(self) -> None:
        self._write(
            "hal_mcp_docs-doc-x-aaaa.ndjson",
            [
                _vote("route", "h1"),
                _vote("route", "h2"),
                _vote("proxy_outcome", "h2", source="access_after_route"),
            ],
        )
        rec = _Recorder()
        res = outcome_forwarder.forward_outcomes(str(self.root), post_fn=rec)

        self.assertTrue(res["ok"])
        self.assertEqual(
            rec.calls,
            [
                {
                    "request_hash": "h2",
                    "outcome": "correct",
                    "source": "access_after_route",
                }
            ],
        )
        self.assertEqual(res["votes_forwarded"], 1)
        self.assertEqual(res["dedup_dropped"], 0)
        self.assertEqual(res["skipped_not_vote"], 2)
        self.assertEqual(res["files_archived"], 1)
        # archivio: stesso nome in .imported/, inbox svuotato
        self.assertFalse((self.inbox / "hal_mcp_docs-doc-x-aaaa.ndjson").exists())
        self.assertTrue(
            (self.inbox / ".imported" / "hal_mcp_docs-doc-x-aaaa.ndjson").is_file()
        )

    def test_explicit_vote_wins_over_proxy_same_hash(self) -> None:
        self._write(
            "hal_mcp_docs-doc-x-bbbb.ndjson",
            [
                _vote(
                    "proxy_outcome",
                    "h1",
                    verdict="correct",
                    source="access_after_route",
                ),
                _vote("outcome", "h1", verdict="incorrect", correction="chunk-7"),
            ],
        )
        rec = _Recorder()
        res = outcome_forwarder.forward_outcomes(str(self.root), post_fn=rec)

        self.assertEqual(len(rec.calls), 1)
        self.assertEqual(rec.calls[0]["request_hash"], "h1")
        self.assertEqual(rec.calls[0]["outcome"], "incorrect")
        self.assertEqual(rec.calls[0]["correction"], "chunk-7")
        self.assertEqual(res["dedup_dropped"], 1)

    def test_same_hash_deduped_across_files_in_one_run(self) -> None:
        self._write("a.ndjson", [_vote("outcome", "h1")])
        self._write("b.ndjson", [_vote("outcome", "h1")])
        rec = _Recorder()
        res = outcome_forwarder.forward_outcomes(str(self.root), post_fn=rec)

        self.assertEqual(len(rec.calls), 1)
        self.assertEqual(res["dedup_dropped"], 1)

    # ---- acceptance 2: re-run a 0 nuovi voti ----

    def test_rerun_after_archive_forwards_nothing(self) -> None:
        self._write("hal_mcp_docs-doc-x-cccc.ndjson", [_vote("proxy_outcome", "h1")])
        rec = _Recorder()
        outcome_forwarder.forward_outcomes(str(self.root), post_fn=rec)
        first = len(rec.calls)
        res2 = outcome_forwarder.forward_outcomes(str(self.root), post_fn=rec)

        self.assertEqual(len(rec.calls), first)  # nessun nuovo POST
        self.assertEqual(res2["files_scanned"], 0)
        self.assertEqual(res2["votes_forwarded"], 0)

    # ---- acceptance 3: righe saltate, mai raise, esito 0 ----

    def test_lines_without_hash_or_unknown_event_skipped_not_raised(self) -> None:
        self._write(
            "mixed.ndjson",
            [
                {"event": "outcome", "verdict": "correct", "source": "chapter_outcome"},
                _vote("fantasma", "h9"),
                "{json rotto",
                _vote("proxy_outcome", "h1", source="access_after_route"),
            ],
        )
        rec = _Recorder()
        res = outcome_forwarder.forward_outcomes(str(self.root), post_fn=rec)

        self.assertTrue(res["ok"])  # exit 0: nessun raise
        self.assertEqual(len(rec.calls), 1)
        self.assertGreaterEqual(res["skipped_no_hash"], 1)
        self.assertGreaterEqual(res["skipped_unknown_event"], 1)
        self.assertGreaterEqual(res["skipped_malformed"], 1)

    def test_tmp_extension_never_consumed(self) -> None:
        self._write("pippo.ndjson.tmp", [_vote("proxy_outcome", "h1")])
        rec = _Recorder()
        res = outcome_forwarder.forward_outcomes(str(self.root), post_fn=rec)

        self.assertEqual(rec.calls, [])
        self.assertEqual(res["files_scanned"], 0)
        self.assertTrue((self.inbox / "pippo.ndjson.tmp").is_file())

    # ---- acceptance 4: inbox assente → non parte ----

    def test_inbox_absent_does_not_start(self) -> None:
        shutil.rmtree(self.inbox)
        rec = _Recorder()
        res = outcome_forwarder.forward_outcomes(str(self.root), post_fn=rec)

        self.assertFalse(res["ok"])
        self.assertEqual(res["error"], "inbox_absent")
        self.assertEqual(rec.calls, [])

    def test_gateway_root_missing_and_unset(self) -> None:
        rec = _Recorder()
        missing = outcome_forwarder.forward_outcomes(
            str(self.root / "nope"), post_fn=rec
        )
        self.assertFalse(missing["ok"])
        self.assertEqual(missing["error"], "gateway_root_missing")

        unset = outcome_forwarder.forward_outcomes("   ", post_fn=rec)
        self.assertFalse(unset["ok"])
        self.assertEqual(unset["error"], "gateway_root_unset")
        self.assertEqual(rec.calls, [])

    # ---- fallimento trasporto: file NON archiviato (retry-safe) ----

    def test_failed_post_keeps_file_for_retry(self) -> None:
        path = self._write("retry.ndjson", [_vote("proxy_outcome", "h1")])
        rec = _Recorder(fail_times=1)
        res = outcome_forwarder.forward_outcomes(str(self.root), post_fn=rec)

        self.assertEqual(res["votes_failed"], 1)
        self.assertEqual(res["files_archived"], 0)
        self.assertTrue(path.is_file())  # resta in inbox per il prossimo giro
        # re-run con Laya ripristinata: il voto passa e il file si archivia
        ok_rec = _Recorder()
        res2 = outcome_forwarder.forward_outcomes(str(self.root), post_fn=ok_rec)
        self.assertEqual(len(ok_rec.calls), 1)
        self.assertTrue((self.inbox / ".imported" / "retry.ndjson").is_file())
        self.assertEqual(res2["files_archived"], 1)

    # ---- CLI: esiti macchina-leggibili ----

    def test_cli_exit_codes(self) -> None:
        self._write(
            "cli.ndjson", [_vote("proxy_outcome", "h1", source="access_after_route")]
        )
        rec = _Recorder()
        code = outcome_forwarder.main(["--gateway-root", str(self.root)], post_fn=rec)
        self.assertEqual(code, 0)

        shutil.rmtree(self.inbox)
        code2 = outcome_forwarder.main(
            ["--gateway-root", str(self.root)], post_fn=_Recorder()
        )
        self.assertEqual(code2, 1)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import json
import tempfile
import time
import unittest
from pathlib import Path

from gateway_core import (
    CircuitBreaker,
    compute_cache_key,
    derive_session_id,
    normalize_prompt,
    process_event_payload,
    redact_text,
    write_event_jsonl,
)
from laya_service import LayaOutcome


class TestGatewayCore(unittest.TestCase):

    def test_redaction_secrets(self) -> None:
        raw_text = "Connessione con sk-proj-1234567890abcdefghijklmnopqrstuvwxyz e token bearer abcdef1234567890."
        redacted = redact_text(raw_text)
        self.assertNotIn("sk-proj-1234567890abcdefghijklmnopqrstuvwxyz", redacted)
        self.assertIn("{{secret:openai}}", redacted)
        self.assertIn("{{secret:bearer_token}}", redacted)

    def test_event_payload_redaction(self) -> None:
        payload = {"user": "carlo", "secret": "AKIA1234567890ABCDEF"}
        processed = process_event_payload(payload, lambda _body, _criteria: 0.1)
        self.assertIn("{{secret:aws_key}}", processed["redacted_body"])
        self.assertNotIn("AKIA1234567890ABCDEF", str(processed))

    def test_pii_is_redacted_before_scan_and_output(self) -> None:
        payload = {
            "email": "alice@example.com",
            "phone": "+39 333 1234567",
            "secret": "AKIA1234567890ABCDEF",
        }
        scanned: list[str] = []

        def scan(body: str, _criteria: str) -> LayaOutcome[float]:
            scanned.append(body)
            return LayaOutcome(status="ok", value=0.1)

        processed = process_event_payload(payload, scan)
        body = processed["redacted_body"]

        self.assertIn("{{pii:email}}", body)
        self.assertIn("{{pii:phone}}", body)
        self.assertIn("{{secret:aws_key}}", body)
        for raw_value in ("alice@example.com", "+39 333 1234567", "AKIA1234567890ABCDEF"):
            self.assertNotIn(raw_value, body)
            self.assertNotIn(raw_value, scanned[0])
            self.assertNotIn(raw_value, str(processed))
        self.assertEqual(processed["pii_scan_status"], "complete")
        self.assertTrue(processed["pii_redacted"])
        self.assertFalse(processed["body_withheld"])

    def test_pii_scan_abstention_fails_closed(self) -> None:
        payload = {"email": "alice@example.com", "message": "contact me"}
        processed = process_event_payload(
            payload,
            lambda _body, _criteria: LayaOutcome(status="abstain", reason="unavailable"),
        )

        self.assertEqual(processed["pii_scan_status"], "uncertain")
        self.assertIsNone(processed["pii_detected"])
        self.assertTrue(processed["body_withheld"])
        self.assertIsNone(processed["redacted_body"])
        self.assertNotIn("alice@example.com", str(processed))

    def test_pii_scan_exception_fails_closed(self) -> None:
        def scan_error(_body: str, _criteria: str) -> float:
            raise RuntimeError("scanner unavailable")

        processed = process_event_payload({"message": "unverified content"}, scan_error)

        self.assertEqual(processed["pii_scan_status"], "uncertain")
        self.assertIsNone(processed["pii_detected"])
        self.assertTrue(processed["body_withheld"])
        self.assertIsNone(processed["redacted_body"])

    def test_positive_pii_scan_withholds_body(self) -> None:
        processed = process_event_payload(
            {"message": "unrecognized sensitive content"},
            lambda _body, _criteria: LayaOutcome(status="ok", value=0.9),
        )

        self.assertEqual(processed["pii_scan_status"], "complete")
        self.assertTrue(processed["pii_detected"])
        self.assertTrue(processed["body_withheld"])
        self.assertIsNone(processed["redacted_body"])

    def test_event_writer_persists_only_redacted_body(self) -> None:
        payload = {
            "email": "alice@example.com",
            "phone": "+39 333 1234567",
            "secret": "AKIA1234567890ABCDEF",
        }
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "events.jsonl"
            write_event_jsonl(payload, path, lambda _body, _criteria: 0.1)
            stored = path.read_text(encoding="utf-8")

        self.assertEqual(len(stored.splitlines()), 1)
        self.assertIn("{{pii:email}}", stored)
        self.assertIn("{{pii:phone}}", stored)
        self.assertIn("{{secret:aws_key}}", stored)
        for raw_value in ("alice@example.com", "+39 333 1234567", "AKIA1234567890ABCDEF"):
            self.assertNotIn(raw_value, stored)

    def test_event_writer_withholds_body_when_scan_is_uncertain(self) -> None:
        payload = {"email": "alice@example.com", "message": "private"}
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "events.jsonl"
            write_event_jsonl(
                payload,
                path,
                lambda _body, _criteria: LayaOutcome(status="abstain", reason="unavailable"),
            )
            stored = path.read_text(encoding="utf-8")

        record = json.loads(stored)
        self.assertEqual(record["pii_scan_status"], "uncertain")
        self.assertTrue(record["body_withheld"])
        self.assertIsNone(record["redacted_body"])
        self.assertNotIn("alice@example.com", stored)
        self.assertNotIn("private", stored)

    def test_cache_normalization_and_key(self) -> None:
        msg1 = [{"content": "  Fix BUG in main.py   2026-10-06T12:00:00Z "}]
        msg2 = [{"content": "fix bug in main.py"}]
        
        norm1 = normalize_prompt(msg1)
        norm2 = normalize_prompt(msg2)
        self.assertEqual(norm1, norm2)

        key1 = compute_cache_key("sess_123", "code-tdd", msg1, ["main.py"])
        key2 = compute_cache_key("sess_123", "code-tdd", msg2, ["main.py"])
        self.assertEqual(key1, key2)

    def test_session_id_derivation(self) -> None:
        s1 = derive_session_id("key_abc", "/var/www/proj1", "chat_1")
        s2 = derive_session_id("key_abc", "/var/www/proj1", "chat_1")
        s3 = derive_session_id("key_abc", "/var/www/proj1", "chat_2")
        self.assertEqual(s1, s2)
        self.assertNotEqual(s1, s3)

    def test_circuit_breaker(self) -> None:
        cb = CircuitBreaker("openai", failure_threshold=2, open_s=1)
        now = time.time()
        
        self.assertTrue(cb.allow_request(now))
        cb.record_failure(now)
        self.assertTrue(cb.allow_request(now)) # ancora sotto soglia
        
        cb.record_failure(now) # raggiunta soglia -> OPEN
        self.assertFalse(cb.allow_request(now))
        
        # Simula scadenza tempo open_s
        self.assertTrue(cb.allow_request(now + 2.0))
        self.assertEqual(cb.state, "HALF-OPEN")
        
        cb.record_success()
        self.assertEqual(cb.state, "CLOSED")


if __name__ == "__main__":
    unittest.main()

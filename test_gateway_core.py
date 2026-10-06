from __future__ import annotations

import time
import unittest

from gateway_core import (
    CircuitBreaker,
    compute_cache_key,
    derive_session_id,
    normalize_prompt,
    process_event_payload,
    redact_text,
)


class TestGatewayCore(unittest.TestCase):

    def test_redaction_secrets(self) -> None:
        raw_text = "Connessione con sk-proj-1234567890abcdefghijklmnopqrstuvwxyz e token bearer abcdef1234567890."
        redacted = redact_text(raw_text)
        self.assertNotIn("sk-proj-1234567890abcdefghijklmnopqrstuvwxyz", redacted)
        self.assertIn("{{secret:openai}}", redacted)
        self.assertIn("{{secret:bearer_token}}", redacted)

    def test_event_payload_redaction(self) -> None:
        payload = {"user": "carlo", "secret": "AKIA1234567890ABCDEF"}
        processed = process_event_payload(payload)
        self.assertIn("{{secret:aws_key}}", processed["redacted_body"])

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

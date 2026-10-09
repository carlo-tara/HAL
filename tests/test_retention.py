import unittest  # noqa: I001
import time
from gateway_core import EventRetentionManager

class TestEventRetentionAndEncryption(unittest.TestCase):
    def test_retention_purge_rules(self) -> None:
        now = time.time()
        day_in_s = 86400

        # Event within 30 days -> body and metadata retained
        recent_event = {
            "timestamp": now - (10 * day_in_s),
            "redacted_body": "recent message",
            "metadata": {"event_id": "1"}
        }

        # Event body older than 30 days, metadata newer than 365 days -> body purged (set to None), metadata retained
        medium_event = {
            "timestamp": now - (40 * day_in_s),
            "redacted_body": "old body",
            "metadata": {"event_id": "2"}
        }

        # Event older than 365 days -> fully purged
        expired_event = {
            "timestamp": now - (400 * day_in_s),
            "redacted_body": "very old body",
            "metadata": {"event_id": "3"}
        }

        events = [recent_event, medium_event, expired_event]
        purged = EventRetentionManager.purge_expired_events(events, current_timestamp=now)

        self.assertEqual(len(purged), 2)
        self.assertEqual(purged[0]["redacted_body"], "recent message")
        self.assertIsNone(purged[1]["redacted_body"]) # body purged after 30 days
        self.assertEqual(purged[1]["metadata"]["event_id"], "2")

    def test_encryption_at_rest(self) -> None:
        key = "secret-encryption-key-32-bytes!!"
        payload = {"sensitive": "event data"}
        encrypted = EventRetentionManager.encrypt_payload(payload, key)
        self.assertIsInstance(encrypted, str)
        self.assertNotEqual(encrypted, str(payload))

        decrypted = EventRetentionManager.decrypt_payload(encrypted, key)
        self.assertEqual(decrypted, payload)

    def test_access_control(self) -> None:
        self.assertTrue(EventRetentionManager.verify_access(role="admin", action="read_raw_logs"))
        self.assertTrue(EventRetentionManager.verify_access(role="auditor", action="read_raw_logs"))
        self.assertFalse(EventRetentionManager.verify_access(role="developer", action="read_raw_logs"))

if __name__ == "__main__":
    unittest.main()

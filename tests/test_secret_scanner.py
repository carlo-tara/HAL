import os  # noqa: I001
import tempfile
import unittest

class TestSecretScanner(unittest.TestCase):
    def test_scanner_detects_secret(self) -> None:
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".py") as tmp:
            tmp.write("API_KEY = 'sk-proj-1234567890abcdefghijklmnopqrstuvwxyz'\n")
            tmp_path = tmp.name

        try:
            from scripts.check_secrets import scan_file
            findings = scan_file(tmp_path)
            self.assertTrue(len(findings) > 0)
            self.assertEqual(findings[0][1], "OpenAI API Key")
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def test_scanner_ignores_synthetic_fixture(self) -> None:
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".py") as tmp:
            tmp.write("# synthetic fixture\nAPI_KEY = 'sk-proj-1234567890abcdefghijklmnopqrstuvwxyz'\n")
            tmp_path = tmp.name

        try:
            from scripts.check_secrets import scan_file
            findings = scan_file(tmp_path)
            self.assertEqual(len(findings), 0)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

if __name__ == "__main__":
    unittest.main()

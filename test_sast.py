import unittest  # noqa: I001
import os
import tempfile
from check_sast import scan_file

class TestSASTScanner(unittest.TestCase):
    def test_sast_detects_eval(self) -> None:
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".py") as tmp:
            tmp.write("res = eval('1 + 1')\n")
            tmp_path = tmp.name

        try:
            findings = scan_file(tmp_path)
            self.assertTrue(len(findings) > 0)
            self.assertEqual(findings[0][1], "Use of dynamic eval()")
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def test_sast_ignores_comments(self) -> None:
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".py") as tmp:
            tmp.write("# res = eval('1 + 1')\n")
            tmp_path = tmp.name

        try:
            findings = scan_file(tmp_path)
            self.assertEqual(len(findings), 0)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

if __name__ == "__main__":
    unittest.main()

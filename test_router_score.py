import subprocess  # noqa: I001
import sys
import unittest

class TestRouterScoreCLI(unittest.TestCase):
    def test_router_score_execution(self) -> None:
        cmd = [sys.executable, "router.py", "score", "test", "--criteria", "relevance"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=5, check=False)
        self.assertEqual(result.returncode, 0)

if __name__ == "__main__":
    unittest.main()

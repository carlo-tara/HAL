import os  # noqa: I001
import unittest

from check_deps import audit_dependencies

class TestDependencyAudit(unittest.TestCase):
    def test_audit_passes_clean_requirements(self) -> None:
        old_env = os.environ.get("TEST_ADVISORY_TRIGGER")
        if "TEST_ADVISORY_TRIGGER" in os.environ:
            del os.environ["TEST_ADVISORY_TRIGGER"]
        try:
            exit_code = audit_dependencies()
            self.assertEqual(exit_code, 0)
        finally:
            if old_env is not None:
                os.environ["TEST_ADVISORY_TRIGGER"] = old_env

    def test_audit_fails_on_advisory(self) -> None:
        os.environ["TEST_ADVISORY_TRIGGER"] = "requests"
        try:
            exit_code = audit_dependencies()
            self.assertEqual(exit_code, 1)
        finally:
            if "TEST_ADVISORY_TRIGGER" in os.environ:
                del os.environ["TEST_ADVISORY_TRIGGER"]

if __name__ == "__main__":
    unittest.main()

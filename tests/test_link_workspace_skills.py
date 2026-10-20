from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = (
    Path(__file__).resolve().parent.parent / "agents/scripts/link-workspace-skills.sh"
)


class TestWrapperVersion(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        self.source = self.root / "cmd.md"

    def write_source(self, frontmatter: str = "model: m") -> None:
        self.source.write_text(f"---\n{frontmatter}\n---\n\n# Corpo\n")

    def link(self, name: str = "demo") -> subprocess.CompletedProcess[str]:
        script = (
            f"source '{SCRIPT}' && WORKSPACE_ROOT='{self.root}' "
            f"&& link_zed_skill '{self.source}' '{name}'"
        )
        return subprocess.run(
            ["bash", "-c", script], capture_output=True, text=True, check=False
        )

    def wrapper(self, name: str = "demo") -> str:
        return (self.root / f".agents/skills/{name}/SKILL.md").read_text()

    def test_sourcing_the_script_does_not_link_anything(self) -> None:
        result = subprocess.run(
            ["bash", "-c", f"source '{SCRIPT}'"],
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")

    def test_default_version_when_source_has_none(self) -> None:
        self.write_source()

        self.assertEqual(self.link().returncode, 0)

        self.assertIn("\nversion: 1.0.0\n", self.wrapper())

    def test_wrapper_takes_version_from_canonical_frontmatter(self) -> None:
        self.write_source("model: m\nversion: 1.2.1")

        self.assertEqual(self.link().returncode, 0)

        content = self.wrapper()
        self.assertIn("\nversion: 1.2.1\n", content)
        self.assertNotIn("model: m", content)
        self.assertTrue(content.rstrip().endswith("# Corpo"))

    def test_two_consecutive_syncs_are_idempotent(self) -> None:
        self.write_source("model: m\nversion: 1.4.0")

        self.link()
        first = self.wrapper()
        self.link()

        self.assertEqual(self.wrapper(), first)

    def test_bump_on_canonical_survives_the_next_sync(self) -> None:
        self.write_source("model: m\nversion: 1.4.0")
        self.link()

        self.write_source("model: m\nversion: 1.4.1")
        self.link()

        self.assertIn("\nversion: 1.4.1\n", self.wrapper())

    def test_invalid_version_fails_without_writing_wrapper(self) -> None:
        self.write_source("model: m\nversion: latest")

        result = self.link()

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Invalid version", result.stderr)
        self.assertFalse((self.root / ".agents/skills/demo/SKILL.md").exists())


if __name__ == "__main__":
    unittest.main()

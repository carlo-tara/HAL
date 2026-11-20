"""Contratto del mirror locale dei comandi L0 — versione 2026-11-20.

I wrapper-skill locali `.agents/skills/<cmd>/` NON sono più generati da
`link-workspace-skills.sh` (funzione `link_zed_skill` dismessa): la sede unica
delle skill-comando è globale (`~/.agents/skills/`, pubblicata da
`publish-global-commands.sh` dal canone, che estrae la `version:` dal
frontmatter). Lo script ora espone `prune_command_skill_wrapper`, che pota i
mirror residui marcati «Command <cmd> for HAL workspace» e lascia intatti gli
override genuini e i symlink (mai potare through-link, mai toccare ciò che
risolve fuori dal workspace fisico).
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = (
    Path(__file__).resolve().parent.parent / "agents/scripts/link-workspace-skills.sh"
)

MARKER = (
    "---\nname: {name}\nversion: 1.0.0\n"
    "description: Command {name} for HAL workspace.\n---\n\n# Corpo\n"
)
OVERRIDE = (
    "---\nname: {name}\nversion: 9.9.9\ndescription: Override di progetto.\n"
    "---\n\n# Corpo\n"
)


def run_fn(workspace: Path, fn: str, *args: str) -> subprocess.CompletedProcess[str]:
    script = (
        f"source '{SCRIPT}' && WORKSPACE_ROOT='{workspace}' && {fn} {' '.join(args)}"
    )
    return subprocess.run(
        ["bash", "-c", script], capture_output=True, text=True, check=False
    )


class TestSourceDoesNotLink(unittest.TestCase):
    def test_sourcing_the_script_does_not_link_anything(self) -> None:
        result = subprocess.run(
            ["bash", "-c", f"source '{SCRIPT}'"],
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")


class TestPruneCommandSkillWrapper(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        (self.root / ".agents/skills").mkdir(parents=True)
        self.outside = Path(self._tmp.name + "-outside")
        self.addCleanup(lambda: shutil.rmtree(self.outside, ignore_errors=True))

    def make(self, name: str, template: str = MARKER) -> Path:
        d = self.root / ".agents/skills" / name
        d.mkdir(parents=True)
        (d / "SKILL.md").write_text(template.format(name=name), encoding="utf-8")
        return d

    def prune(self, name: str) -> subprocess.CompletedProcess[str]:
        return run_fn(self.root, "prune_command_skill_wrapper", f"'{name}'")

    def test_prune_removes_stale_marker_wrapper(self) -> None:
        stale = self.make("commit")
        result = self.prune("commit")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(stale.exists())

    def test_prune_is_idempotent_and_noop_when_absent(self) -> None:
        self.make("commit")
        self.prune("commit")
        again = self.prune("commit")
        self.assertEqual(again.returncode, 0, again.stderr)
        absent = self.prune("graph")
        self.assertEqual(absent.returncode, 0, absent.stderr)

    def test_genuine_override_without_marker_is_kept(self) -> None:
        kept = self.make("commit", OVERRIDE)
        result = self.prune("commit")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((kept / "SKILL.md").is_file())

    def test_symlinked_wrapper_dir_is_never_pruned_through(self) -> None:
        target = self.outside / "commit"
        target.mkdir(parents=True)
        (target / "SKILL.md").write_text(MARKER.format(name="commit"), encoding="utf-8")
        (self.root / ".agents/skills/commit").symlink_to(target)

        result = self.prune("commit")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.root / ".agents/skills/commit").is_symlink())
        self.assertTrue((target / "SKILL.md").is_file())

    def test_wrapper_under_mounted_skills_root_fails_closed(self) -> None:
        """.agents reale ma `skills` symlink fuori workspace: la guardia
        require_inside_workspace rifiuta; il bersaglio esterno resta intatto."""
        skills = self.outside / "skills"
        (skills / "commit").mkdir(parents=True)
        (skills / "commit/SKILL.md").write_text(
            MARKER.format(name="commit"), encoding="utf-8"
        )
        (self.root / ".agents/skills").rmdir()
        (self.root / ".agents/skills").symlink_to(skills)

        result = self.prune("commit")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Guardia HAL", result.stderr)
        self.assertTrue((skills / "commit/SKILL.md").is_file())

    def test_marker_prefix_matches_published_wrapper_format(self) -> None:
        # Il pattern di prune deve riconoscere esattamente il description
        # scritto dal publisher globale: «Command <cmd> for HAL workspace»
        # (locale) e la sua variante «… (global, published by hal_gateway)».
        d = self.make("learn")
        head = (d / "SKILL.md").read_text(encoding="utf-8").splitlines()
        self.assertIn("description: Command learn for HAL workspace.", head)
        result = self.prune("learn")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(d.exists())


if __name__ == "__main__":
    unittest.main()

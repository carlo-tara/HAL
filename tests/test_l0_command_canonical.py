"""Contratto RED->GREEN per la regola canonico-vs-mirror dei comandi L0.

Appreso dal chain /version+/commit 2026-10-30 (hal_system2): il bump di
`.agents/skills/graph/SKILL.md` (mirror generato) era stato sovrascritto da
`/sync !` perche` il canonico `agents/a-agentzero/commands/graph.md` non era
stato toccato. Le regole consolidate:

1. command L0 `version` 1.3.1: regola di coerenza «bump sul canonico, mai
   solo sul mirror».
2. skill `sync` 1.2.1: note «le modifiche al mirror sono annullate da
   `/sync !`».
3. learn 1.5.12: sezione tool-pitfalls «Path dei comandi L0: canonico vs
   mirror generato» (include edit_file su path via symlink `agents/` e
   write_file fuori progetto -> heredoc terminale).
"""

from __future__ import annotations

import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
VERSION_CMD = REPO / "agents" / "a-agentzero" / "commands" / "version.md"
VERSION_MIRROR = REPO / ".agents" / "skills" / "version" / "SKILL.md"
SYNC_SKILL = REPO / "agents" / "a-agentzero" / "sync" / "SKILL.md"
SYNC_CL = REPO / "agents" / "a-agentzero" / "sync" / "CHANGELOG.md"
LEARN_SKILL = REPO / "agents" / "a-agentzero" / "learn" / "SKILL.md"
LEARN_CL = REPO / "agents" / "a-agentzero" / "learn" / "CHANGELOG.md"
PITFALLS = REPO / "agents" / "a-agentzero" / "learn" / "references" / "tool-pitfalls.md"


class TestVersionRegolaCanonico(unittest.TestCase):
    def test_canonico_contiene_regola(self) -> None:
        text = VERSION_CMD.read_text(encoding="utf-8")
        self.assertIn("mai solo sul mirror", text)
        self.assertIn("version: 1.3.1", text)

    def test_mirror_rigenerato_allineato(self) -> None:
        text = VERSION_MIRROR.read_text(encoding="utf-8")
        self.assertIn("version: 1.3.1", text)


class TestSyncNoteMirror(unittest.TestCase):
    def test_sync_contiene_note_mirror(self) -> None:
        text = SYNC_SKILL.read_text(encoding="utf-8")
        self.assertIn("le modifiche al mirror sono annullate da", text)
        self.assertIn("version: 1.2.1", text)

    def test_sync_changelog_ha_voce(self) -> None:
        self.assertIn("[1.2.1]", SYNC_CL.read_text(encoding="utf-8"))


class TestLearnPitfallPath(unittest.TestCase):
    def test_pitfalls_sezione_canonico_mirror(self) -> None:
        text = PITFALLS.read_text(encoding="utf-8")
        self.assertIn("## Path dei comandi L0: canonico vs mirror generato", text)

    def test_learn_bump_e_changelog(self) -> None:
        self.assertIn("version: 1.5.12", LEARN_SKILL.read_text(encoding="utf-8"))
        self.assertIn("[1.5.12]", LEARN_CL.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

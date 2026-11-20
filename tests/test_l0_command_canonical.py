"""Contratto RED->GREEN per la regola canonico-vs-mirror dei comandi L0.

Appreso dal chain /version+/commit 2026-10-30 (hal_system2): il bump di
`.agents/skills/graph/SKILL.md` (mirror generato) era stato sovrascritto da
`/sync !` perche` il canonico `agents/a-agentzero/commands/graph.md` non era
stato toccato. Le regole consolidate:

1. command L0 `version`: regola di coerenza «bump sul canonico, mai sugli
   specchi». Dal 2026-11-20 il mirror locale non esiste più (sede unica
   skill-comando: globale); il contratto verifica l'assenza.
2. skill `sync`: note «le modifiche al mirror sono annullate da `/sync !`»;
   la versione corrente (estratta dal frontmatter) deve risultare nel proprio
   CHANGELOG, non un numero pinato (stessa tecnica del caso learn, 2026-10-31).
3. learn >= 1.5.12 (versione corrente estratta dal frontmatter): sezione
   tool-pitfalls «Path dei comandi L0: canonico vs mirror generato» (include
   edit_file su path via symlink `agents/` e write_file fuori progetto ->
   heredoc terminale). Il contratto verifica che la `version` corrente di
   learn risulti nel proprio CHANGELOG, non un numero pinato (i bump patch
   legittimi — es. 1.5.13/1.5.14 del 2026-10-31 — non devono rompere la
   suite).
"""

from __future__ import annotations

import re
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
        self.assertIn("mai sugli specchi", text)
        self.assertIn("agents/a-agentzero/commands/<cmd>.md", text)

    def test_mirror_locale_assente(self) -> None:
        # 2026-11-20: nessun wrapper locale in .agents/skills — rigenerato da
        # link-workspace-skills.sh solo il globale via publish-global-commands.sh.
        self.assertFalse(
            VERSION_MIRROR.exists(),
            "mirror locale rimosso: la sede unica della skill-comando è globale",
        )


class TestSyncNoteMirror(unittest.TestCase):
    def test_sync_contiene_note_mirror(self) -> None:
        text = SYNC_SKILL.read_text(encoding="utf-8")
        self.assertIn("le modifiche al mirror sono annullate da", text)

    def test_sync_bump_e_changelog(self) -> None:
        skill = SYNC_SKILL.read_text(encoding="utf-8")
        m = re.search(r"^version: (\d+\.\d+\.\d+)$", skill, re.MULTILINE)
        self.assertIsNotNone(m, "campo version assente in sync/SKILL.md")
        assert m is not None  # stringimento pyright (assertIsNotNone non è TypeGuard)
        self.assertIn(f"[{m.group(1)}]", SYNC_CL.read_text(encoding="utf-8"))


class TestLearnPitfallPath(unittest.TestCase):
    def test_pitfalls_sezione_canonico_mirror(self) -> None:
        text = PITFALLS.read_text(encoding="utf-8")
        self.assertIn("## Path dei comandi L0: canonico vs mirror generato", text)

    def test_learn_bump_e_changelog(self) -> None:
        skill = LEARN_SKILL.read_text(encoding="utf-8")
        m = re.search(r"^version: (\d+\.\d+\.\d+)$", skill, re.MULTILINE)
        self.assertIsNotNone(m, "campo version assente in learn/SKILL.md")
        assert m is not None  # stringimento pyright (assertIsNotNone non è TypeGuard)
        self.assertGreaterEqual(
            tuple(int(x) for x in m.group(1).split(".")), (1, 5, 12)
        )
        self.assertIn(f"[{m.group(1)}]", LEARN_CL.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

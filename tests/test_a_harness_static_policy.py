"""Contratto RED->GREEN per la policy static-analysis-gate in a-harness (N11).

Il test legge solo i file della skill L1: nessuna dipendenza esterna, nessuno
scaffold System 2 dentro hal_gateway. I token cercati sono limitati al body di
SKILL.md (sotto il frontmatter) per evitare falsi positivi, come da rituale
RGR di harness-agentfactory.
"""

from __future__ import annotations

import unittest
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent / "agents" / "a-harness"
SKILL_MD = SKILL_DIR / "SKILL.md"
TEMPLATE = SKILL_DIR / "references" / "makefile-template.mk"
CHANGELOG = SKILL_DIR / "CHANGELOG.md"


def _frontmatter_and_body(text: str) -> tuple[str, str]:
    parts = text.split("---", 2)
    if len(parts) != 3:
        return "", text
    return parts[1], parts[2]


class TestStaticAnalysisPolicyL1(unittest.TestCase):
    def test_skill_body_contiene_policy_gate_statico(self) -> None:
        _, body = _frontmatter_and_body(SKILL_MD.read_text(encoding="utf-8"))
        self.assertIn("**Static analysis gate", body)
        for token in (
            "ruff",
            "pyright",
            "shellcheck",
            "check-static-diff",
            "Platform API",
        ):
            self.assertIn(token, body)

    def test_versione_skill_bumpata_con_changelog(self) -> None:
        frontmatter, _ = _frontmatter_and_body(SKILL_MD.read_text(encoding="utf-8"))
        version_line = next(
            line for line in frontmatter.splitlines() if line.startswith("version:")
        )
        version = version_line.split(":", 1)[1].strip()
        # La policy static-analysis è stata introdotta in 1.9.0: ogni bump successivo
        # deve restare >= 1.9.0 e avere la propria voce in CHANGELOG.
        self.assertGreaterEqual(tuple(int(p) for p in version.split(".")), (1, 9, 0))
        self.assertIn(f"## [{version}]", CHANGELOG.read_text(encoding="utf-8"))

    def test_template_makefile_espone_target_statici(self) -> None:
        text = TEMPLATE.read_text(encoding="utf-8")
        for target in ("lint:", "types:", "check-static:", "check-static-diff:"):
            self.assertIn(target, text)
        phony = next(line for line in text.splitlines() if line.startswith(".PHONY:"))
        self.assertIn("check-static-diff", phony)
        self.assertIn("pre-commit: check-parity check-static-diff", text)


if __name__ == "__main__":
    unittest.main()

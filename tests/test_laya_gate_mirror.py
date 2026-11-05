"""Guardia del mirror laya_gate: il symlink assoluto non risolve su CI.

Root cause (CI rossa 2026-11-04/05): ``laya_gate.py`` era tracciato come symlink
assoluto (mode 120000) verso ``hal_system1/laya_gate.py``; sul runner GitHub il
target non esiste, l'import fallisce ``ModuleNotFoundError`` e lo step
"Gateway unit tests" esplode al primo modulo.

Regole verificate:
1. il mirror deve essere un file regolare tracciato, mai un symlink (CI privata
   sul repo laya non clonabile);
2. dove il sorgente canonico esiste sul filesystem (layout locale
   ``../hal_system1/laya_gate.py``), i byte devono coincidere — drift =
   risincronizzare il mirror DAL canonico, mai il contrario.
"""

from __future__ import annotations

import hashlib
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MIRROR = REPO_ROOT / "laya_gate.py"
CANONICAL = REPO_ROOT.parent / "hal_system1" / "laya_gate.py"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class TestLayaGateMirror(unittest.TestCase):
    def test_mirror_is_regular_file(self) -> None:
        self.assertTrue(MIRROR.is_file(), f"mirror mancante: {MIRROR}")
        self.assertFalse(
            MIRROR.is_symlink(),
            "laya_gate.py deve essere una copia tracciata, non un symlink: su "
            "CI GitHub il target esterno (repo laya, privato) non esiste",
        )

    def test_mirror_matches_canonical_when_present(self) -> None:
        if not CANONICAL.is_file():
            self.skipTest(f"sorgente canonico assente ({CANONICAL}): runner CI o machine senza hal_system1")
        self.assertEqual(
            _sha(MIRROR),
            _sha(CANONICAL),
            "drift laya_gate: risincronizzare il mirror dal sorgente "
            f"(cp {CANONICAL} {MIRROR}); il canonico vive in laya (hal_system1)",
        )


if __name__ == "__main__":
    unittest.main()

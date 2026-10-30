"""Contratto RED->GREEN per gli apprendimenti del re-run graph `-y` rv6 (hal_system2, 2026-10-30).

Tre regole emerse in sessione, da persistere nella competenza `graph` e nel
comando L0 `graph`:

1. Gate umano/ops passivamente rilasciato tra un re-run e l'altro: prima di
   marcare skip, riverificare con misura diretta (data sistema, ricreazione
   container, porte); l'etichetta di skip della sessione precedente non e
   verita persistente.
2. `handoff-write` fonde i campi: `date`/`brief`/`acceptance` non passati
   restano dalla scrittura precedente (caso: handoff-todo con brief rv5 dopo
   re-run rv6).
3. Verifica pipe su tutte le righe della tabella a ogni re-run, non solo sulle
   righe scritte: la corruzione puo venire da run precedenti (caso 2026-10-30,
   righe N11/N14 con pipe grezzi dal 2026-10-25/26).

Il test legge solo i file delle skill: nessuna dipendenza esterna.
"""

from __future__ import annotations

import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
EXTENDED = REPO / "agents" / "a-harness" / "competencies" / "graph" / "references" / "graph-extended.md"
COMPETENCY = REPO / "agents" / "a-harness" / "competencies" / "graph" / "SKILL.md"
COMPETENCY_CL = REPO / "agents" / "a-harness" / "competencies" / "graph" / "CHANGELOG.md"
L0 = REPO / ".agents" / "skills" / "graph" / "SKILL.md"
L0_CL = REPO / ".agents" / "skills" / "graph" / "CHANGELOG.md"


class TestGatePassivoRilascio(unittest.TestCase):
    def test_extended_contiene_regola_gate_passivo(self) -> None:
        text = EXTENDED.read_text(encoding="utf-8")
        self.assertIn("Gate passivi", text)
        self.assertIn("misura diretta", text)


class TestHandoffFondeCampi(unittest.TestCase):
    def test_extended_contiene_regola_fusione_campi(self) -> None:
        text = EXTENDED.read_text(encoding="utf-8")
        self.assertIn("fonde i campi", text)
        self.assertIn("--field date=YYYY-MM-DD", text)


class TestVerificaTabelleReRun(unittest.TestCase):
    def test_notes_l0_contiene_verifica_tutte_le_righe(self) -> None:
        text = L0.read_text(encoding="utf-8")
        self.assertIn("tutte le righe della tabella", text)
        self.assertIn("N11/N14", text)

    def test_estensione_non_andare_a_capo(self) -> None:
        text = L0.read_text(encoding="utf-8")
        self.assertIn("mai a capo dentro la riga", text)


class TestVersioniBump(unittest.TestCase):
    def test_competenza_1_4_2_e_changelog(self) -> None:
        self.assertIn("version: 1.4.2", COMPETENCY.read_text(encoding="utf-8"))
        self.assertIn("[1.4.2]", COMPETENCY_CL.read_text(encoding="utf-8"))

    def test_l0_1_0_3_e_changelog(self) -> None:
        self.assertIn("version: 1.0.3", L0.read_text(encoding="utf-8"))
        self.assertIn("[1.0.3]", L0_CL.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

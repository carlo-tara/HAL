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

import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
EXTENDED = (
    REPO
    / "agents"
    / "a-harness"
    / "competencies"
    / "graph"
    / "references"
    / "graph-extended.md"
)
COMPETENCY = REPO / "agents" / "a-harness" / "competencies" / "graph" / "SKILL.md"
COMPETENCY_CL = (
    REPO / "agents" / "a-harness" / "competencies" / "graph" / "CHANGELOG.md"
)
# 2026-11-20: i mirror .agents/skills/<cmd> non esistono più (sede unica
# skill-comando: globale); il contratto legge il canone e il changelog
# canonico dei comandi L0.
L0 = REPO / "agents" / "a-agentzero" / "commands" / "graph.md"
L0_CL = REPO / "agents" / "a-agentzero" / "commands" / "CHANGELOG.md"


class TestGatePassivoRilascio(unittest.TestCase):
    def test_extended_contiene_regola_gate_passivo(self) -> None:
        text = EXTENDED.read_text(encoding="utf-8")
        self.assertIn("Gate passivi", text)
        self.assertIn("misura diretta", text)


class TestHandoffSchemaFisso(unittest.TestCase):
    """rv10 (2026-11-16): la nota «fonde i campi» del 2026-10-30 è stata
    sostituita da «Schema fisso, niente fusione» — chiave `date` fuori schema
    che cade; il guard blocca l'esempio vecchio per non reintrodurla."""

    def test_extended_contiene_regola_schema_fisso(self) -> None:
        text = EXTENDED.read_text(encoding="utf-8")
        self.assertIn("Schema fisso, niente fusione", text)
        self.assertNotIn("--field date=YYYY-MM-DD", text)


class TestVerificaTabelleReRun(unittest.TestCase):
    def test_notes_l0_contiene_verifica_tutte_le_righe(self) -> None:
        text = L0.read_text(encoding="utf-8")
        self.assertIn("tutte le righe della tabella", text)
        self.assertIn("N11/N14", text)

    def test_estensione_non_andare_a_capo(self) -> None:
        text = L0.read_text(encoding="utf-8")
        self.assertIn("mai a capo dentro la riga", text)


class TestVersioniBump(unittest.TestCase):
    def test_competenza_1_4_3_e_changelog(self) -> None:
        self.assertIn("version: 1.4.3", COMPETENCY.read_text(encoding="utf-8"))
        self.assertIn("[1.4.3]", COMPETENCY_CL.read_text(encoding="utf-8"))

    def test_l0_version_e_changelog(self) -> None:
        text = L0.read_text(encoding="utf-8")
        m = re.search(r"^version: (\d+\.\d+\.\d+)$", text, re.MULTILINE)
        self.assertIsNotNone(m, "campo version assente in commands/graph.md")
        assert m is not None  # stringimento pyright (assertIsNotNone non è TypeGuard)
        self.assertGreaterEqual(tuple(int(x) for x in m.group(1).split(".")), (1, 0, 4))
        self.assertIn(f"[{m.group(1)}]", L0_CL.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

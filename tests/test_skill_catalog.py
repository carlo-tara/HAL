"""Contratto P1 (ToDo 2026-10-28, voce catalogo skill compatto / tool-search):

~37 descrizioni complete esposte a ogni prompt = Tool Definition Bloat (token,
scelte errate di tool). Laya routing/noul è già un search_tools: il catalogo
compatto espone solo nome + keyword e carica il bundle completo su domanda.
"""

from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch

import router
from router import (
    catalog_token_report,
    load_skill_catalog,
    search_skills,
)


class TestCompactCatalog(unittest.TestCase):
    def test_una_riga_per_skill_con_keywords(self) -> None:
        catalog = load_skill_catalog()
        self.assertGreaterEqual(len(catalog), 10)
        for entry in catalog:
            self.assertTrue(entry["name"])
            self.assertIsInstance(entry["keywords"], list)
            # riga compatta: nome + keyword, mai la descrizione intera
            line = f"{entry['name']}: {', '.join(entry['keywords'])}"
            self.assertLess(len(line), 240)

    def test_keywords_derivate_dalle_descrizioni(self) -> None:
        catalog = {e["name"]: e for e in load_skill_catalog()}
        self.assertIn("a-seozoom", catalog)
        joined = " ".join(catalog["a-seozoom"]["keywords"]).lower()
        self.assertIn("seo", joined)

    def test_descrizione_completa_disponibile_on_demand(self) -> None:
        catalog = load_skill_catalog()
        entry = catalog[0]
        self.assertTrue(Path(entry["path"]).is_file())


class TestSkillSearch(unittest.TestCase):
    def test_subset_da_keyword_tag(self) -> None:
        hits = search_skills("audit SEO e keyword analysis")
        names = [h["name"] for h in hits]
        self.assertIn("a-seozoom", names)
        self.assertLessEqual(len(hits), 5)

    def test_subset_piccolo_non_catalogo_completo(self) -> None:
        hits = search_skills("illustrazione hero per la home")
        self.assertLess(len(hits), len(load_skill_catalog()))
        self.assertIn("illustrator", [h["name"] for h in hits])

    def test_abstain_laya_usa_fallback_locale(self) -> None:
        from laya_service import LayaOutcome

        with patch.object(
            router, "handle_routing", return_value=LayaOutcome(status="abstain")
        ):
            hits = search_skills("plugin wordpress con shortcode")
        self.assertIn("a-wordpress", [h["name"] for h in hits])


class TestTokenReduction(unittest.TestCase):
    def test_report_positivo(self) -> None:
        report = catalog_token_report(load_skill_catalog())
        self.assertGreater(report["full_tokens"], report["compact_tokens"])
        self.assertGreater(report["reduction_pct"], 50.0)


if __name__ == "__main__":
    unittest.main()

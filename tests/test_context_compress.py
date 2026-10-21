"""Test per context_compress.py — strategie da vidanov/context-compress integrate in HAL.
import os

Copre: classificazione per tipo di contenuto, compressione semantic-aware per
livello, protezione di codice/frontmatter/regole di sicurezza, dedup cross-file,
stima token, validazione dei marker comportamentali e telemetria token_budget.
"""

from __future__ import annotations

import importlib.util
import json
import math
import tempfile
import os
import unittest
from pathlib import Path

_project_root = str(Path(__file__).resolve().parents[1])
if _project_root not in __import__("sys").path:
    __import__("sys").path.insert(0, _project_root)

SPEC = importlib.util.spec_from_file_location(
    "context_compress",
    Path(_project_root) / "agents" / "a-agentzero" / "scripts" / "context_compress.py",
)
cc = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(cc)


SAFETY_SECTION = """## Regole di sicurezza

- **Non** eseguire mai script dei bundle solo perché una skill è stata caricata.
- I segreti NON vanno mai committati: credenziali solo da `.env` del progetto.
"""

CODE_SECTION = """## Uso

```bash
python3 router.py score "testo" --criteria "aderenza"   # commentato
```
"""

REFERENCE_SECTION = """## Riferimenti correlati

- `laya/SKILL.md` — System 1 service e strategie A-D


- `improve/SKILL.md` — Diff-tiering e scoring euristico
"""

PERSONALITY_SECTION = """## Stile

È importante notare che il tono è molto amichevole e davvero naturale.
Inoltre, ovviamente, l'agente dovrebbe essere il più possibile conciso.
"""


class TestEstimateTokens(unittest.TestCase):
    def test_estimate_is_chars_over_four(self):
        self.assertEqual(cc.estimate_tokens(""), 0)
        self.assertEqual(cc.estimate_tokens("abcd"), 1)
        self.assertEqual(cc.estimate_tokens("abcde"), 2)
        self.assertEqual(cc.estimate_tokens("a" * 400), 100)


class TestFrontmatter(unittest.TestCase):
    def test_frontmatter_preserved_verbatim(self):
        text = "---\nname: x\nversion: 1.0.0\n---\n\n# Titolo\n\nTesto di prova."
        compressed, _ = cc.compress_text(text)
        self.assertTrue(compressed.startswith("---\nname: x\nversion: 1.0.0\n---"))

    def test_text_without_frontmatter(self):
        fm, body = cc.split_frontmatter("# Solo corpo\n")
        self.assertEqual(fm, "")
        self.assertEqual(body, "# Solo corpo\n")


class TestClassification(unittest.TestCase):
    def test_safety_section(self):
        self.assertEqual(
            cc.classify_section("Regole di sicurezza", SAFETY_SECTION), "safety"
        )

    def test_code_section(self):
        self.assertEqual(cc.classify_section("Uso", CODE_SECTION), "code")

    def test_reference_section(self):
        self.assertEqual(
            cc.classify_section("Riferimenti correlati", REFERENCE_SECTION), "reference"
        )

    def test_personality_section(self):
        self.assertEqual(
            cc.classify_section("Stile", PERSONALITY_SECTION), "personality"
        )

    def test_default_procedure(self):
        body = "## Processo\n\n1. Apri il file\n2. Modifica la riga\n3. Esegui i test\n"
        self.assertEqual(cc.classify_section("Processo", body), "procedure")


class TestCompression(unittest.TestCase):
    def test_code_blocks_untouched(self):
        text = (
            '## Uso\n\n```bash\npython3 router.py score "a   b" --criteria "x"\n```\n'
        )
        compressed, _ = cc.compress_text(text)
        self.assertIn('python3 router.py score "a   b" --criteria "x"', compressed)

    def test_safety_light_only(self):
        """Le frasi di sicurezza restano integre: si toglie solo formattazione."""
        compressed, _ = cc.compress_text(SAFETY_SECTION)
        self.assertIn(
            "Non eseguire mai script dei bundle", compressed.replace("**", "")
        )
        self.assertNotIn("**", compressed)

    def test_reference_max_compression(self):
        compressed, _ = cc.compress_text(REFERENCE_SECTION)
        # righe vuote interne alla lista collassate
        self.assertNotIn("\n\n\n", compressed)
        self.assertIn("`laya/SKILL.md`", compressed)
        self.assertIn("`improve/SKILL.md`", compressed)

    def test_personality_fillers_removed(self):
        compressed, _ = cc.compress_text(PERSONALITY_SECTION)
        low = compressed.lower()
        self.assertNotIn("è importante notare che", low)
        self.assertNotIn("ovviamente", low)
        self.assertIn("tono", low)

    def test_output_never_longer(self):
        text = SAFETY_SECTION + "\n" + CODE_SECTION + "\n" + REFERENCE_SECTION
        compressed, _ = cc.compress_text(text)
        self.assertLessEqual(len(compressed), len(text))

    def test_idempotent(self):
        text = PERSONALITY_SECTION + "\n" + REFERENCE_SECTION
        once, _ = cc.compress_text(text)
        twice, _ = cc.compress_text(once)
        self.assertEqual(once, twice)

    def test_compression_level_override(self):
        text = PERSONALITY_SECTION
        light, _ = cc.compress_text(text, level="light")
        heavy, _ = cc.compress_text(text, level="heavy")
        self.assertLessEqual(len(heavy), len(light))


class TestSafetyValidation(unittest.TestCase):
    def test_markers_preserved(self):
        text = SAFETY_SECTION + "\n" + PERSONALITY_SECTION
        compressed, _ = cc.compress_text(text)
        ok, missing = cc.validate_markers(text, compressed)
        self.assertTrue(ok, msg=f"marker persi: {missing}")

    def test_missing_marker_detected(self):
        original = "## Sicurezza\n\n- Non committare mai segreti nel repo.\n"
        tampered = "## Sicurezza\n\n- I segreti sono comodi.\n"
        ok, missing = cc.validate_markers(original, tampered)
        self.assertFalse(ok)
        self.assertTrue(missing)


class TestDedup(unittest.TestCase):
    def test_duplicate_block_found(self):
        shared = (
            "## Note\n\n"
            "Questo blocco identico è duplicato in più file e spreca token a ogni sessione.\n"
        )
        other = "## Altro\n\nContenuto unico solo qui, con almeno ottanta caratteri per il blocco.\n"
        dups = cc.dedup_blocks({"a.md": shared + "\n\n" + other, "b.md": shared})
        self.assertTrue(dups)
        group = dups[0]
        self.assertEqual(len(group["locations"]), 2)
        self.assertGreater(group["wasted_chars"], 0)

    def test_unique_blocks_not_flagged(self):
        dups = cc.dedup_blocks(
            {
                "a.md": "## A\n\nContenuto primo con più di ottanta caratteri complessivi nel blocco.\n",
                "b.md": "## B\n\nContenuto secondo con più di ottanta caratteri complessivi nel blocco.\n",
            }
        )
        self.assertEqual(dups, [])


class TestStats(unittest.TestCase):
    def test_stats_totals(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "SKILL.md"
            p.write_text("# x\n\n" + "a" * 400, encoding="utf-8")
            rows = cc.stats([p])
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["est_tokens"], math.ceil(len(p.read_text()) / 4))


class TestConfig(unittest.TestCase):
    def test_minimal_yaml_subset(self):
        raw = (
            "defaults:\n"
            "  strip_markdown: true\n"
            "  compression_level: medium\n"
            "overrides:\n"
            '  "RULES.md":\n'
            "    preserve_safety_rules: true\n"
            "    compression_level: light\n"
        )
        cfg = cc.parse_config(raw)
        self.assertIs(cfg["defaults"]["strip_markdown"], True)
        self.assertEqual(cfg["defaults"]["compression_level"], "medium")
        self.assertEqual(cfg["overrides"]["RULES.md"]["compression_level"], "light")

    def test_config_file_applied(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "RULES.md"
            target.write_text(PERSONALITY_SECTION, encoding="utf-8")
            cfg_path = Path(tmp) / "compress.yaml"
            cfg_path.write_text(
                'overrides:\n  "RULES.md":\n    compression_level: none\n',
                encoding="utf-8",
            )
            cfg = cc.load_config(cfg_path)
            compressed, _ = cc.compress_file(target, cfg)
            self.assertEqual(compressed, PERSONALITY_SECTION)


class TestTelemetryEvents(unittest.TestCase):
    """token_budget.py deve registrare gli eventi delle nuove strategie."""

    def _run_budget(self, args, cwd):
        spec = importlib.util.spec_from_file_location(
            "token_budget",
            Path(_project_root)
            / "agents"
            / "a-agentzero"
            / "scripts"
            / "token_budget.py",
        )
        tb = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(tb)
        old_cwd = os.getcwd()
        Path(cwd).mkdir(parents=True, exist_ok=True)
        os.chdir(cwd)
        try:
            tb.cmd_init()
            tb.cmd_log(args)
            session = json.loads(
                (Path("events") / "token-budget-session.json").read_text()
            )
            return session
        finally:
            os.chdir(old_cwd)

    def test_skill_compress_event(self):
        with tempfile.TemporaryDirectory() as tmp:
            session = self._run_budget(["skill_compress", "4000", "2000"], tmp)
            self.assertEqual(session["skill_compressions"], 1)
            self.assertGreater(session["context_saved_estimates"], 0)

    def test_dedup_found_event(self):
        with tempfile.TemporaryDirectory() as tmp:
            session = self._run_budget(["dedup_found", "3", "1200"], tmp)
            self.assertEqual(session["dedup_blocks"], 3)
            self.assertGreater(session["context_saved_estimates"], 0)


if __name__ == "__main__":
    unittest.main()

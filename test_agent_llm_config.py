#!/usr/bin/env python3
"""Test unitario per la risoluzione e il feature flag di OrcaRouter per ogni agente di HAL."""
from __future__ import annotations

import json
import os
import unittest
from pathlib import Path

from global_config import (
    AGENT_EXTERNAL_MODELS,
    SystemTwoEngine,
    get_agent_llm_config,
    resolve_agent_model,
)

class TestAgentLLMConfig(unittest.TestCase):
    def setUp(self) -> None:
        # Pulisci eventuali variabili d'ambiente di test
        for key in list(os.environ.keys()):
            if "LLM_EXTERNAL" in key:
                del os.environ[key]

    def test_all_agents_have_external_mode_off_by_default(self) -> None:
        catalog_path = Path(__file__).parent / "agents" / "catalog.json"
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))

        for item in catalog["agents"]:
            agent_name = item["name"]
            cfg = get_agent_llm_config(agent_name)

            self.assertEqual(cfg["LLM_EXTERNAL_MODE"], 0, f"{agent_name} deve avere LLM_EXTERNAL_MODE = 0")
            self.assertEqual(cfg["provider"], "system2_default")
            self.assertEqual(cfg["active_model"], SystemTwoEngine.ACTIVE_MODEL_NAME)
            self.assertEqual(resolve_agent_model(agent_name), SystemTwoEngine.ACTIVE_MODEL_NAME)
            self.assertIn(agent_name, AGENT_EXTERNAL_MODELS)
            self.assertEqual(cfg["LLM_EXTERNAL_MODEL"], AGENT_EXTERNAL_MODELS[agent_name])

    def test_global_feature_flag_activation(self) -> None:
        os.environ["LLM_EXTERNAL_MODE"] = "1"
        os.environ["LLM_EXTERNAL_URI"] = "https://custom.orcarouter.local/v1"

        cfg = get_agent_llm_config("a-copywriter")
        self.assertEqual(cfg["LLM_EXTERNAL_MODE"], 1)
        self.assertEqual(cfg["provider"], "orcarouter")
        self.assertEqual(cfg["active_model"], "orcarouter/openai/gpt-4o-mini")
        self.assertEqual(cfg["LLM_EXTERNAL_URI"], "https://custom.orcarouter.local/v1")
        self.assertEqual(resolve_agent_model("a-copywriter"), "orcarouter/openai/gpt-4o-mini")

    def test_per_agent_override(self) -> None:
        # Globale spento (0), ma abilitato solo per a-seozoom
        os.environ["LLM_EXTERNAL_MODE"] = "0"
        os.environ["A_SEOZOOM_LLM_EXTERNAL_MODE"] = "1"
        os.environ["A_SEOZOOM_LLM_EXTERNAL_MODEL"] = "orcarouter/deepseek/deepseek-v4-custom"

        cfg_seo = get_agent_llm_config("a-seozoom")
        self.assertEqual(cfg_seo["LLM_EXTERNAL_MODE"], 1)
        self.assertEqual(cfg_seo["provider"], "orcarouter")
        self.assertEqual(cfg_seo["active_model"], "orcarouter/deepseek/deepseek-v4-custom")

        # Un altro agente rimane spento
        cfg_po = get_agent_llm_config("a-po")
        self.assertEqual(cfg_po["LLM_EXTERNAL_MODE"], 0)
        self.assertEqual(cfg_po["provider"], "system2_default")
        self.assertEqual(cfg_po["active_model"], SystemTwoEngine.ACTIVE_MODEL_NAME)

    def test_system_two_engine_execution(self) -> None:
        os.environ["LLM_EXTERNAL_MODE"] = "0"
        out_default = SystemTwoEngine.execute("coding", "test script", agent="a-harness")
        self.assertIn(SystemTwoEngine.ACTIVE_MODEL_NAME, out_default)

        os.environ["A_HARNESS_LLM_EXTERNAL_MODE"] = "1"
        out_external = SystemTwoEngine.execute("coding", "test script", agent="a-harness")
        self.assertIn("orcarouter/deepseek/deepseek-v4.1-flash", out_external)

if __name__ == "__main__":
    unittest.main()

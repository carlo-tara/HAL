"""Contratto P2 (ToDo 2026-10-28, voci Kimi/QwenCloud capability flag):

- flag ``dynamic_tools``/``prefix_caching`` per la validazione di frontiera:
  l'iniezione dinamica è supportata solo da kimi-k3/k3.1-pro e un messaggio
  ``system`` con ``tools`` non deve avere ``content`` (400);
- flag ``context_cache``: il resolver lo considera per i profili cost-oriented
  (cache automatica sui modelli Qwen-Max/Plus/Flash/Coder);
- flag ``streaming_only``: modello che supporta SOLO streaming — la chiamata
  non-streaming restituirebbe 200 vuoto (fallimento silenzioso), quindi la
  frontiera forza ``stream=True`` o rifiuta con errore esplicito.
"""

from __future__ import annotations

import unittest

from global_config import (
    MODEL_CAPABILITIES,
    resolve_model_for_profile,
    validate_chat_payload,
)


class TestCapabilityFlags(unittest.TestCase):
    def test_kimi_ha_dynamic_tools(self) -> None:
        kimi = [
            caps
            for model, caps in MODEL_CAPABILITIES.items()
            if "kimi" in model.lower()
        ]
        self.assertTrue(any(c["dynamic_tools"] for c in kimi))

    def test_qwen_flash_ha_context_cache(self) -> None:
        qwen = [
            caps
            for model, caps in MODEL_CAPABILITIES.items()
            if "qwen" in model.lower() and "flash" in model.lower()
        ]
        self.assertTrue(qwen, "nessun modello qwen flash in catalogo")
        self.assertTrue(any(c["context_cache"] for c in qwen))

    def test_default_capability_falso_per_modelli_ignoti(self) -> None:
        caps = MODEL_CAPABILITIES.get("modello-inesistente", None)
        self.assertIsNone(caps)  # catalogo chiuso: default gestito dal lookup helper

    def test_streaming_only_presente(self) -> None:
        self.assertTrue(any(c["streaming_only"] for c in MODEL_CAPABILITIES.values()))


class TestResolverWithCapabilities(unittest.TestCase):
    def test_context_cache_guida_selezione_cost_oriented(self) -> None:
        model = resolve_model_for_profile(
            "coding", required_capabilities=["context_cache"]
        )
        caps = MODEL_CAPABILITIES.get(model, {})
        self.assertTrue(caps.get("context_cache", False))

    def test_capability_non_supportate_esplicite(self) -> None:
        with self.assertRaises(ValueError):
            resolve_model_for_profile(
                "coding", required_capabilities=["capability-che-nessuno-ha"]
            )


class TestFrontierValidation(unittest.TestCase):
    def test_system_con_tools_e_content_rifiutato(self) -> None:
        payload = {
            "model": "orcarouter/kimi/kimi-k3",
            "messages": [
                {"role": "system", "content": "ciao", "tools": [{"name": "x"}]},
                {"role": "user", "content": "q"},
            ],
        }
        with self.assertRaises(ValueError) as ctx:
            validate_chat_payload(payload)
        self.assertIn("content", str(ctx.exception))

    def test_system_con_tools_senza_content_ok(self) -> None:
        payload = {
            "model": "orcarouter/kimi/kimi-k3",
            "messages": [
                {"role": "system", "content": "", "tools": [{"name": "x"}]},
                {"role": "user", "content": "q"},
            ],
        }
        validate_chat_payload(payload)  # non solleva

    def test_streaming_only_forza_stream(self) -> None:
        streaming_model = next(
            m for m, c in MODEL_CAPABILITIES.items() if c.get("streaming_only")
        )
        payload = {"model": streaming_model, "stream": False, "messages": []}
        result = validate_chat_payload(payload)
        self.assertTrue(result["stream"])

    def test_validazione_non_muta_payload_normali(self) -> None:
        payload = {
            "model": "Gemini 3.5 Flash-Lite",
            "stream": False,
            "messages": [{"role": "user", "content": "ciao"}],
        }
        result = validate_chat_payload(payload)
        self.assertFalse(result["stream"])


if __name__ == "__main__":
    unittest.main()

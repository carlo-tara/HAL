"""Gate 6: ridurre le chiamate Laya alle sole decisioni utili.

Acceptance:
- un preflight utile più le sole decisioni intermedie che possono cambiare il flusso
- test con limite di chiamate Laya per workflow
- contatore chiamate per run nel report

2026-11-09 (reverse port rv7): il vecchio monolite esponeva ``laya_call_count``
nel risultato di ``system1_guide``; il canonico non ha quel campo ne' un retry
loop. Il contatore reale e' ``workflow_summary["system1_decisions"]`` del
risultato di ``system2_workflow_call`` (conteggio delle decisioni Laya del
flusso) e i post a ``/predict`` osservabili sul client. I test sono riallineati
a questa verita' misurata, provando comunque un contatore vero.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock

_project_root = str(Path(__file__).resolve().parent.parent)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from benchmark.runner.benchmark_models import Settings, system2_workflow_call


def _make_settings(**overrides):
    base = {
        "ollama_base_url": "http://ollama.local:11434",
        "laya_base_url": "http://127.0.0.1:8091",
        "laya_api_key": "sk-test",
        "laya_timeout": 120,
        "laya_min_confidence": 0.7,
        "laya_model": "multilingual",
    }
    # 2026-11-09: Settings e' frozen nel canonico e laya_max_retries non esiste
    # piu': nessun retry loop, il tetto e' il singolo tentativo per decisione.
    base.update(overrides)
    return Settings(**base)


_MODEL = {"provider": "ollama", "model": "local:1b"}


def _guide(mode):
    return {
        "task_family": "general",
        "strategy": "direct_answer",
        "execution_mode": mode,
        "guidance": "Rispondi direttamente e verifica i vincoli.",
        "confidence": 0.9,
        "laya_called": mode == "plan_then_solve",
        "decision_source": "laya",
        "output_format": "text",
    }


def _workflow_client(decision_choices):
    """MagicMock client che instrada /predict (decisioni Laya) e /api/chat (System 2)."""
    counts = {"predict": 0, "system2": 0}

    def post(url, *args, **kwargs):
        response = MagicMock()
        response.raise_for_status = MagicMock()
        if url.endswith("/predict"):
            choice = decision_choices[min(counts["predict"], len(decision_choices) - 1)]
            response.json.return_value = {
                "answers": {"decision": {"choice": choice, "confidence": 0.9}}
            }
            counts["predict"] += 1
        else:
            response.json.return_value = {
                "done": True,
                "message": {"content": "testo di stage"},
                "done_reason": "stop",
                "prompt_eval_count": 10,
                "eval_count": 5,
            }
            counts["system2"] += 1
        return response

    client = MagicMock()
    client.post.side_effect = post
    client.counts = counts
    return client


class TestGate6LayaCallCounter(unittest.TestCase):
    """Verifica che il contatore decisioni Laya nel workflow risulti presente e accurato."""

    def test_laya_call_count_in_result(self):
        """Il risultato del workflow deve contenere il contatore decisioni Laya."""
        settings = _make_settings()
        prompt = {"id": "wf", "prompt": "Prepara un piano e rispondi"}

        client = _workflow_client(["proceed"])
        result = system2_workflow_call(
            _MODEL, prompt, settings, client, _guide("plan_then_solve")
        )

        # Contatore reale del canonico: una decisione Laya nel flusso.
        self.assertIn("system1_decisions", result["workflow_summary"])
        self.assertEqual(result["workflow_summary"]["system1_decisions"], 1)
        self.assertEqual(client.counts["predict"], 1)
        self.assertEqual(
            result["workflow_summary"],
            {
                "system1_decisions": 1,
                "system2_stages": 2,
                "execution_mode": "plan_then_solve",
            },
        )

    def test_laya_call_count_zero_when_skipped(self):
        """Workflow single-pass (nessuna decisione intermedia) → contatore 0."""
        settings = _make_settings()
        prompt = {"id": "wf", "prompt": "Risposta diretta"}

        client = _workflow_client([])
        result = system2_workflow_call(
            _MODEL, prompt, settings, client, _guide("single_pass")
        )

        # Nessun /predict: la modalita' atomica non consulta Laya a flusso avviato.
        self.assertEqual(result["workflow_summary"]["system1_decisions"], 0)
        self.assertEqual(client.counts["predict"], 0)
        self.assertEqual(result["workflow_summary"]["execution_mode"], "single_pass")

    def test_laya_call_count_counts_every_decision(self):
        """Con piano da revisionare il contatore somma tutte le decisioni Laya (2).

        2026-11-09: sostituisce il vecchio retry-counter: nel canonico le
        chiamate multiple nascono dai rami di decisione (revise → seconda
        verifica), non da re-poll su bassa confidenza.
        """
        settings = _make_settings()
        prompt = {"id": "wf", "prompt": "Prepara un piano e rispondi"}

        client = _workflow_client(["revise", "proceed"])
        result = system2_workflow_call(
            _MODEL, prompt, settings, client, _guide("plan_then_solve")
        )

        # 2 decisioni (valutazione piano + verifica piano revisionato).
        self.assertEqual(result["workflow_summary"]["system1_decisions"], 2)
        self.assertEqual(client.counts["predict"], 2)
        self.assertEqual(result["workflow_summary"]["system2_stages"], 3)


if __name__ == "__main__":
    unittest.main()

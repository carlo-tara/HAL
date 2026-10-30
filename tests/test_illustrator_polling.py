"""Contratto P1/P2 (ToDo 2026-10-28, doc QwenCloud async-task):

- T12: polling a backoff esponenziale con intervalli per modalta' e stati
  terminali COMPLETI (CANCELED e UNKNOWN escono subito, non girano fino al
  timeout sprecando chiamate contro il limite condiviso di 20 QPS);
- T26: successo parziale nei task multi-output: solo gli output con
  finish_reason == "stop" sono validi, i saltati sono segnalati (warning su
  stderr) e il JSON dello script porta il campo partial.
"""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPT = (
    Path(__file__).resolve().parent.parent
    / "agents"
    / "a-design"
    / "illustrator"
    / "scripts"
    / "generate-image.py"
)

_spec = importlib.util.spec_from_file_location("generate_image", SCRIPT)
assert _spec is not None and _spec.loader is not None
gi = importlib.util.module_from_spec(_spec)
sys.modules["generate_image"] = gi  # necessario per @dataclass nel modulo caricato
_spec.loader.exec_module(gi)


def _status(status: str, **output_extra):
    return {"output": {"task_status": status, **output_extra}}


class TestPollBackoff(unittest.TestCase):
    def test_sequenza_backoff_x15_con_cap(self) -> None:
        seq = [
            _status("RUNNING"),
            _status("RUNNING"),
            _status("RUNNING"),
            _status("SUCCEEDED", results=[{"url": "https://x/1.png"}]),
        ]
        sleeps: list[float] = []
        with patch.object(gi, "http_json", side_effect=seq), patch.object(
            gi.time, "sleep", side_effect=sleeps.append
        ):
            result = gi.poll_synthesis_task(
                "https://dashscope.aliyuncs.com/api/v1", {}, "task-1", modality="image"
            )
        # immagine: 3s iniziali x1.5, cap 15s (tabella doc)
        self.assertEqual(sleeps, [3.0, 4.5, 6.75])
        self.assertEqual(result.url, "https://x/1.png")
        self.assertFalse(result.partial)

    def test_cap_15_secondi(self) -> None:
        seq = [_status("RUNNING")] * 8 + [
            _status("SUCCEEDED", results=[{"url": "https://x/1.png"}])
        ]
        sleeps: list[float] = []
        with patch.object(gi, "http_json", side_effect=seq), patch.object(
            gi.time, "sleep", side_effect=sleeps.append
        ):
            gi.poll_synthesis_task("https://h/api", {}, "task-2", modality="image")
        self.assertTrue(all(s <= 15.0 for s in sleeps))
        self.assertIn(15.0, sleeps)


class TestTerminalStates(unittest.TestCase):
    def test_canceled_esce_subito(self) -> None:
        with (
            patch.object(gi, "http_json", side_effect=[_status("CANCELED")]),
            patch.object(gi.time, "sleep") as sleep,
            self.assertRaises(RuntimeError) as ctx,
        ):
            gi.poll_synthesis_task("https://h/api", {}, "task-3", modality="image")
        self.assertIn("CANCELED", str(ctx.exception))
        sleep.assert_not_called()

    def test_unknown_esce_subito(self) -> None:
        # UNKNOWN = task id scaduto/non interrogabile (retention 24h): girare
        # fino al timeout e' solo spreco contro il limite di 20 QPS
        with (
            patch.object(gi, "http_json", side_effect=[_status("UNKNOWN")]),
            patch.object(gi.time, "sleep") as sleep,
            self.assertRaises(RuntimeError) as ctx,
        ):
            gi.poll_synthesis_task("https://h/api", {}, "task-4", modality="image")
        self.assertIn("UNKNOWN", str(ctx.exception))
        sleep.assert_not_called()

    def test_video_usa_il_suolo_profillo(self) -> None:
        seq = [
            _status("RUNNING"),
            _status("SUCCEEDED", results=[{"url": "https://x/v.mp4"}]),
        ]
        sleeps: list[float] = []
        with patch.object(gi, "http_json", side_effect=seq), patch.object(
            gi.time, "sleep", side_effect=sleeps.append
        ):
            gi.poll_synthesis_task("https://h/api", {}, "task-5", modality="video")
        self.assertEqual(sleeps, [15.0])


class TestPartialSuccess(unittest.TestCase):
    def test_solo_stop_validi_partial_segnalato(self) -> None:
        payload = _status(
            "SUCCEEDED",
            choices=[
                {
                    "finish_reason": "stop",
                    "message": {"content": [{"image": "https://x/1.png"}]},
                },
                {
                    "finish_reason": "length",
                    "message": {"content": [{"image": "https://x/2.png"}]},
                },
            ],
        )
        with patch.object(gi, "http_json", side_effect=[payload]), patch.object(
            gi.time, "sleep"
        ):
            result = gi.poll_synthesis_task(
                "https://h/api", {}, "task-6", modality="image"
            )
        self.assertEqual(result.urls, ["https://x/1.png"])
        self.assertTrue(result.partial)

    def test_troncamento_4a2_non_accettato_in_silenzio(self) -> None:
        payload = _status(
            "SUCCEEDED",
            results=[
                {"url": "https://x/1.png"},
                {"url": "https://x/2.png"},
                {"code": "DataInspectionFailed"},
                {},
            ],
        )
        with patch.object(gi, "http_json", side_effect=[payload]), patch.object(
            gi.time, "sleep"
        ):
            result = gi.poll_synthesis_task(
                "https://h/api", {}, "task-7", modality="image"
            )
        self.assertEqual(result.urls, ["https://x/1.png", "https://x/2.png"])
        self.assertTrue(result.partial)
        self.assertEqual(len(result.warnings), 2)

    def test_extract_multimodal_ignora_non_stop(self) -> None:
        result = {
            "output": {
                "choices": [
                    {
                        "finish_reason": "stop",
                        "message": {"content": [{"image": "https://x/a.png"}]},
                    },
                    {
                        "finish_reason": "error",
                        "message": {"content": [{"image": "https://x/b.png"}]},
                    },
                ]
            }
        }
        urls = gi.extract_multimodal_image_urls(result)
        self.assertEqual(urls, ["https://x/a.png"])

    def test_extract_multimodal_tutti_non_stop_errore(self) -> None:
        result = {
            "output": {
                "choices": [
                    {
                        "finish_reason": "length",
                        "message": {"content": [{"image": "https://x/a.png"}]},
                    }
                ]
            }
        }
        with self.assertRaises(RuntimeError):
            gi.extract_multimodal_image_urls(result)


if __name__ == "__main__":
    unittest.main()

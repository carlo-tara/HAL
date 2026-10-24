"""Launcher della baseline a contesto pieno (senza middleware, num_ctx registrato)."""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = (
    Path(__file__).resolve().parent.parent / "benchmark/scripts/run_baseline_fullctx.sh"
)
STUB = """#!/bin/sh
# Stub del runner: crea la run-dir come farebbe il runner reale e registra i parametri.
prev=""
for arg in "$@"; do
  if [ "$prev" = "--run-dir" ]; then dir="$arg"; fi
  prev="$arg"
done
mkdir -p "$dir"
echo "$@" > "$dir/args.txt"
echo "${OLLAMA_NUM_CTX-unset}" > "$dir/env.txt"
pwd > "$dir/cwd.txt"
exit "${STUB_EXIT:-0}"
"""


class RunBaselineFullctxTest(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.history = self.root / "history"
        self.history.mkdir()
        self.stub = self.root / "stub_runner.sh"
        self.stub.write_text(STUB, encoding="utf-8")
        self.stub.chmod(0o755)

    def run_script(self, *args: str, **env: str) -> subprocess.CompletedProcess:
        environ = {
            **os.environ,
            "HISTORY_DIR": str(self.history),
            "RUNNER_CMD": str(self.stub),
            **env,
        }
        environ.pop("OLLAMA_NUM_CTX", None)
        return subprocess.run(
            ["bash", str(SCRIPT), *args], env=environ, capture_output=True, text=True
        )

    @staticmethod
    def config_from(stdout: str) -> dict:
        return json.loads(stdout.split("# run_config.json\n", 1)[1])

    def test_dry_run_prints_plan_without_calling_runner_or_creating_dir(self) -> None:
        result = self.run_script("--dry-run", "20261021_4")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((self.history / "20261021_4").exists())

    def test_command_has_full_context_and_no_middleware(self) -> None:
        out = self.run_script("--dry-run", "20261021_4").stdout
        self.assertNotIn("--system1", out)
        self.assertIn("OLLAMA_NUM_CTX=16384", out)
        self.assertIn("--provider ollama", out)
        self.assertIn("--model phi3:mini --model llama3.2:1b", out)
        self.assertIn("--prompt estrazione_json --prompt sintesi_traduzione", out)
        self.assertIn("--timeout 1800", out)
        self.assertIn("--cooldown 60", out)

    def test_dry_run_config_records_num_ctx_and_parameters(self) -> None:
        config = self.config_from(self.run_script("--dry-run", "20261021_4").stdout)
        self.assertEqual(config["run_id"], "20261021_4")
        self.assertEqual(config["num_ctx"], 16384)
        self.assertEqual(config["models"], ["phi3:mini", "llama3.2:1b"])
        self.assertEqual(config["prompts"], ["estrazione_json", "sintesi_traduzione"])
        self.assertEqual((config["timeout"], config["cooldown"]), (1800, 60))
        self.assertFalse(config["system1"])

    def test_env_overrides_parameters(self) -> None:
        result = self.run_script(
            "--dry-run",
            "20261021_4",
            NUM_CTX="8192",
            MODELS="qwen2.5:1.5b",
            PROMPTS="sintesi_traduzione",
            TIMEOUT="900",
        )
        config = self.config_from(result.stdout)
        self.assertEqual(config["num_ctx"], 8192)
        self.assertEqual(config["models"], ["qwen2.5:1.5b"])
        self.assertEqual(config["prompts"], ["sintesi_traduzione"])
        self.assertEqual(config["timeout"], 900)
        self.assertIn("OLLAMA_NUM_CTX=8192", result.stdout)

    def test_rejects_invalid_run_id(self) -> None:
        for bad in ("", "run1", "2026-10-21", "20261021_4/../x"):
            args = ("--dry-run", bad) if bad else ("--dry-run",)
            self.assertEqual(self.run_script(*args).returncode, 2, bad)

    def test_rejects_num_ctx_that_would_not_fit_the_source(self) -> None:
        for bad in ("abc", "0", "2048", "4095", "-1", ""):
            result = self.run_script("--dry-run", "20261021_4", NUM_CTX=bad)
            self.assertEqual(result.returncode, 2, bad)
            self.assertIn("NUM_CTX", result.stderr)

    def test_rejects_existing_run_dir(self) -> None:
        (self.history / "20261021_4").mkdir()
        result = self.run_script("20261021_4")
        self.assertEqual(result.returncode, 2)
        self.assertIn("esiste", result.stderr)

    def test_real_run_exports_num_ctx_and_writes_config(self) -> None:
        result = self.run_script("20261021_4", NUM_CTX="12288")
        self.assertEqual(result.returncode, 0, result.stderr)
        run_dir = self.history / "20261021_4"
        self.assertEqual((run_dir / "env.txt").read_text().strip(), "12288")
        args = (run_dir / "args.txt").read_text()
        self.assertNotIn("--system1", args)
        self.assertIn(f"--run-dir {run_dir}", args)
        config = json.loads((run_dir / "run_config.json").read_text())
        self.assertEqual(config["num_ctx"], 12288)

    def test_runner_dir_selects_working_directory(self) -> None:
        canonical = self.root / "canonical"
        canonical.mkdir()
        result = self.run_script("20261021_4", RUNNER_DIR=str(canonical))
        self.assertEqual(result.returncode, 0, result.stderr)
        cwd = (self.history / "20261021_4/cwd.txt").read_text().strip()
        self.assertEqual(Path(cwd).resolve(), canonical.resolve())

    def test_default_runner_dir_is_benchmark_folder(self) -> None:
        self.run_script("20261021_4")
        cwd = (self.history / "20261021_4/cwd.txt").read_text().strip()
        self.assertEqual(Path(cwd).resolve(), SCRIPT.parent.parent.resolve())

    def test_rejects_missing_runner_dir(self) -> None:
        result = self.run_script(
            "--dry-run", "20261021_4", RUNNER_DIR=str(self.root / "nope")
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("RUNNER_DIR", result.stderr)

    def test_failed_runner_keeps_config_and_exit_code(self) -> None:
        result = self.run_script("20261021_4", STUB_EXIT="3")
        self.assertEqual(result.returncode, 3)
        self.assertTrue((self.history / "20261021_4/run_config.json").exists())


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = (
    Path(__file__).resolve().parent.parent / "benchmark/scripts/sync_hal_system2.sh"
)
PAIRS = {
    "app/benchmark_models.py": "benchmark/runner/benchmark_models.py",
    "app/system2_metrics.py": "benchmark/runner/system2_metrics.py",
    "scripts/generate_benchmark_report.py": "benchmark/scripts/generate_benchmark_report.py",
}


class TestSyncHalSystem2(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.canonical = Path(self._tmp.name) / "hal_system2"
        self.gateway = Path(self._tmp.name) / "gateway"
        for canonical, mirror in PAIRS.items():
            for root, rel in ((self.canonical, canonical), (self.gateway, mirror)):
                path = root / rel
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(f"# {canonical}\n")

    def run_script(self, mode: str, canonical: Path | None = None):
        env = {
            **os.environ,
            "HAL_SYSTEM2_DIR": str(canonical or self.canonical),
            "GATEWAY_DIR": str(self.gateway),
        }
        return subprocess.run(
            ["bash", str(SCRIPT), mode], env=env, capture_output=True, text=True
        )

    def test_check_passes_when_identical(self) -> None:
        self.assertEqual(self.run_script("check").returncode, 0)

    def test_check_fails_on_divergence_and_apply_fixes_it(self) -> None:
        mirror = self.gateway / PAIRS["app/benchmark_models.py"]
        mirror.write_text("# modificato nel gateway\n")

        failed = self.run_script("check")
        self.assertEqual(failed.returncode, 1)
        self.assertIn("DIVERGE: benchmark/runner/benchmark_models.py", failed.stderr)

        self.assertEqual(self.run_script("apply").returncode, 0)
        self.assertEqual(mirror.read_text(), "# app/benchmark_models.py\n")
        self.assertEqual(self.run_script("check").returncode, 0)

    def test_apply_never_overwrites_canonical(self) -> None:
        canonical_file = self.canonical / "app/system2_metrics.py"
        canonical_file.write_text("# canonico\n")

        self.run_script("apply")

        self.assertEqual(canonical_file.read_text(), "# canonico\n")

    def test_missing_mirror_is_divergence(self) -> None:
        (self.gateway / PAIRS["scripts/generate_benchmark_report.py"]).unlink()

        self.assertEqual(self.run_script("check").returncode, 1)

    def test_missing_canonical_directory_exits_2(self) -> None:
        result = self.run_script("check", canonical=Path(self._tmp.name) / "assente")

        self.assertEqual(result.returncode, 2)

    def test_invalid_mode_exits_2(self) -> None:
        self.assertEqual(self.run_script("boh").returncode, 2)


if __name__ == "__main__":
    unittest.main()

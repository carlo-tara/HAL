import unittest  # noqa: I001
from bench_hot_paths import run_benchmarks

class TestHotPathBenchmarks(unittest.TestCase):
    def test_benchmark_execution(self) -> None:
        results = run_benchmarks()
        self.assertIn("normalization_avg_s", results)
        self.assertIn("redaction_avg_s", results)
        self.assertGreater(results["normalization_avg_s"], 0.0)
        self.assertGreater(results["redaction_avg_s"], 0.0)

if __name__ == "__main__":
    unittest.main()

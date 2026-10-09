#!/usr/bin/env python3
import timeit  # noqa: I001
from gateway_core import normalize_prompt, redact_text

def benchmark_normalization() -> float:
    sample_texts = [
        "Please analyze the metrics for domain example.com 2026-10-06T12:00:00Z",
        "Refactor this Python function to improve performance and concurrency.",
        "Check security vulnerabilities and dependencies in requirements.txt"
    ]
    def run() -> None:
        for t in sample_texts:
            normalize_prompt(t)
    
    t = timeit.timeit(run, number=1000)
    return t / 1000.0

def benchmark_redaction() -> float:
    sample_text = "Connect to API with key sk-proj-1234567890abcdefghijklmnopqrstuvwxyz and AWS key AKIA1234567890ABCDEF." # synthetic fixture
    def run() -> None:
        redact_text(sample_text)
    
    t = timeit.timeit(run, number=1000)
    return t / 1000.0

def run_benchmarks() -> dict[str, float]:
    norm_time = benchmark_normalization()
    redact_time = benchmark_redaction()
    results = {
        "normalization_avg_s": norm_time,
        "redaction_avg_s": redact_time
    }
    print("=== Hot Path Benchmarks ===")
    for k, v in results.items():
        print(f"{k}: {v * 1000:.4f} ms")
    return results

if __name__ == "__main__":
    run_benchmarks()

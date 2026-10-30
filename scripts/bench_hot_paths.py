#!/usr/bin/env python3
import argparse
import timeit  # noqa: I001

from gateway_core import normalize_prompt, redact_text

REUSE_WARN_THRESHOLD = 0.95  # target doc QwenCloud §Performance monitoring


def benchmark_normalization() -> float:
    sample_texts = [
        "Please analyze the metrics for domain example.com 2026-10-06T12:00:00Z",
        "Refactor this Python function to improve performance and concurrency.",
        "Check security vulnerabilities and dependencies in requirements.txt",
    ]

    def run() -> None:
        for t in sample_texts:
            normalize_prompt(t)

    t = timeit.timeit(run, number=1000)
    return t / 1000.0


def benchmark_redaction() -> float:
    sample_text = "Connect to API with key sk-proj-1234567890abcdefghijklmnopqrstuvwxyz and AWS key AKIA1234567890ABCDEF."  # synthetic fixture

    def run() -> None:
        redact_text(sample_text)

    t = timeit.timeit(run, number=1000)
    return t / 1000.0


def _pool_totals(session) -> tuple[int, int]:
    """(richieste, connessioni nuove) aggregate sui pool urllib3 della sessione."""
    requests_total = conns_total = 0
    seen_pm: set[int] = set()
    for adapter in session.adapters.values():
        pm = getattr(adapter, "poolmanager", None)
        if id(pm) in seen_pm:  # lo stesso adapter è montato su http e https
            continue
        seen_pm.add(id(pm))
        pools = getattr(pm, "pools", None)
        # RecentlyUsedContainer (urllib3 >=2): .values() passa da __iter__ che
        # solleva; si itera il container interno (OrderedDict).
        container = getattr(pools, "_container", pools)
        try:
            pool_list = (
                list(container.values())
                if hasattr(container, "values")
                else list(container or [])
            )
        except NotImplementedError:
            pool_list = []
        for item in pool_list:
            pool = item[1] if isinstance(item, tuple) else item
            requests_total += getattr(pool, "num_requests", 0)
            conns_total += getattr(pool, "num_connections", 0)
    return requests_total, conns_total


def benchmark_connection_reuse(calls: int = 24) -> dict[str, float] | None:
    """Spike N26 (ToDo, doc QwenCloud §Performance monitoring): conteggio
    richieste vs connessioni nuove dai pool stats urllib3 della sessione Laya.
    Richiede il servizio raggiungibile; None se non disponibile."""
    import requests

    import laya_service

    url = f"{laya_service.LAYA_BASE_URL}/systemone"
    headers = {"Authorization": f"Bearer {laya_service.get_laya_api_key()}"}
    before = _pool_totals(laya_service._session)
    ok = 0
    for i in range(calls):
        try:
            resp = laya_service._session.post(
                url,
                json={"task_type": "noul", "text": f"reuse probe {i}"},
                headers=headers,
                timeout=laya_service.get_timeout_tuple(),
                verify=laya_service.get_tls_verify(),
            )
            ok += 1 if resp.status_code == 200 else 0
        except requests.RequestException as exc:
            print(f"reuse bench: servizio non raggiungibile ({exc})")
            return None
    after = _pool_totals(laya_service._session)
    new_requests = after[0] - before[0]
    new_conns = after[1] - before[1]
    # Connection reuse ratio alla QwenCloud: quota di richieste servite su
    # connessione già esistente (1 - conn_nuove/richieste).
    reuse = 1.0 - (new_conns / new_requests) if new_requests else 0.0
    results = {
        "calls_ok": float(ok),
        "requests_measured": float(new_requests),
        "new_connections": float(new_conns),
        "reuse_ratio": max(reuse, 0.0),
    }
    print("=== Laya Connection Reuse (spike N26) ===")
    for k, v in results.items():
        print(f"{k}: {v:.3f}")
    warn = results["reuse_ratio"] < REUSE_WARN_THRESHOLD
    print(
        f"reuse ratio {results['reuse_ratio']:.3f} "
        f"{'SOTTO' if warn else 'sopra'} soglia {REUSE_WARN_THRESHOLD}"
    )
    return results


def run_benchmarks() -> dict[str, float]:
    norm_time = benchmark_normalization()
    redact_time = benchmark_redaction()
    results = {"normalization_avg_s": norm_time, "redaction_avg_s": redact_time}
    print("=== Hot Path Benchmarks ===")
    for k, v in results.items():
        print(f"{k}: {v * 1000:.4f} ms")
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hot path benchmarks HAL")
    parser.add_argument(
        "--reuse", action="store_true", help="spike N26: connection reuse Laya"
    )
    args = parser.parse_args()
    if args.reuse:
        benchmark_connection_reuse()
    else:
        run_benchmarks()

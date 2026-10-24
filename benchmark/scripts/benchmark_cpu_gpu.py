#!/usr/bin/env python3
"""Benchmark CPU vs GPU — estrazione tempi per chiamata da JSON."""

import glob
import json
import os
import sys
from statistics import median


def load_run(run_dir):
    results = []
    for f in sorted(glob.glob(os.path.join(run_dir, "**/*.json"), recursive=True)):
        base = os.path.basename(f)
        if "executive" in base or base == "results.json":
            continue
        try:
            with open(f) as fh:
                d = json.load(fh)
                if "seconds" in d and "model" in d and "test_id" in d:
                    results.append(
                        {
                            "file": base,
                            "model": d["model"],
                            "test_id": d["test_id"],
                            "status": d.get("status", "unknown"),
                            "seconds": d["seconds"],
                            "tokens": d.get("tokens", {}).get("total", 0),
                            "score": d.get("quality", {}).get("score", 0),
                        }
                    )
        except (OSError, ValueError) as exc:
            print(f"errore lettura {f}: {exc}", file=sys.stderr)
    return results


base = os.path.join(os.getcwd(), "benchmark/history")
runs = {}
for name in ["20261019_3", "20261020_1", "20261020_2"]:
    path = os.path.join(base, name)
    runs[name] = load_run(path)
    print(f"{name}: {len(runs[name])} risultati")

cpu = runs["20261019_3"]
gpu1 = runs["20261020_1"]
gpu2 = runs["20261020_2"]

# Index by (model, test_id)
cpu_idx = {(r["model"], r["test_id"]): r for r in cpu}
gpu1_idx = {(r["model"], r["test_id"]): r for r in gpu1}
gpu2_idx = {(r["model"], r["test_id"]): r for r in gpu2}

print()
print("=" * 85)
print("CONFRONTO PER COPPIA (modello, test) — CPU (20261019_3) vs GPU (20261020_1)")
print("=" * 85)
print(
    f"{'Modello':<15} {'Test':<25} {'CPU(s)':>8} {'GPU(s)':>8} {'Delta':>8} {'Ratio':>6}"
)
print("-" * 85)

pairs = sorted(set(cpu_idx.keys()) & set(gpu1_idx.keys()))
for m, t in pairs:
    c = cpu_idx[(m, t)]
    g = gpu1_idx[(m, t)]
    delta = g["seconds"] - c["seconds"]
    ratio = g["seconds"] / c["seconds"] if c["seconds"] > 0 else 0
    flag = " **TIMEOUT**" if g["seconds"] > 600 else ""
    print(
        f"{m:<15} {t:<25} {c['seconds']:>7.1f}s {g['seconds']:>7.1f}s {delta:>+7.1f}s {ratio:>5.2f}x{flag}"
    )

# GPU replications
print()
print("=" * 85)
print("REPLICHE GPU — (20261020_2) vs (20261020_1)")
print("=" * 85)
print(
    f"{'Modello':<15} {'Test':<25} {'GPU1(s)':>9} {'GPU2(s)':>9} {'Delta':>8} {'Ratio':>6}"
)
print("-" * 85)

pairs2 = sorted(set(gpu1_idx.keys()) & set(gpu2_idx.keys()))
for m, t in pairs2:
    g1 = gpu1_idx[(m, t)]
    g2 = gpu2_idx[(m, t)]
    delta = g2["seconds"] - g1["seconds"]
    ratio = g2["seconds"] / g1["seconds"] if g1["seconds"] > 0 else 0
    print(
        f"{m:<15} {t:<25} {g1['seconds']:>8.1f}s {g2['seconds']:>8.1f}s {delta:>+7.1f}s {ratio:>5.2f}x"
    )

# Per-model medians
print()
print("=" * 85)
print("MEDIANE PER MODELLO")
print("=" * 85)
print(
    f"{'Modello':<15} {'CPU n':>6} {'CPU mediana':>12} {'GPU1 n':>6} {'GPU1 mediana':>13} {'GPU2 n':>6} {'GPU2 mediana':>13}"
)
print("-" * 85)

models = sorted({r["model"] for r in cpu + gpu1 + gpu2})
for m in models:
    cpu_secs = [r["seconds"] for r in cpu if r["model"] == m]
    gpu1_secs = [r["seconds"] for r in gpu1 if r["model"] == m]
    gpu2_secs = [r["seconds"] for r in gpu2 if r["model"] == m]
    line = f"{m:<15}"
    if cpu_secs:
        line += f" {len(cpu_secs):>6} {median(cpu_secs):>11.1f}s"
    if gpu1_secs:
        line += f" {len(gpu1_secs):>6} {median(gpu1_secs):>12.1f}s"
    if gpu2_secs:
        line += f" {len(gpu2_secs):>6} {median(gpu2_secs):>12.1f}s"
    print(line)

# Conclusioni
print()
print("=" * 85)
print("CONCLUSIONI")
print("=" * 85)

# Calcola delta mediano complessivo
if pairs:
    deltas = []
    for m, t in pairs:
        c = cpu_idx[(m, t)]
        g = gpu1_idx[(m, t)]
        if g["seconds"] < 600 and c["seconds"] > 0:  # escludi timeout
            deltas.append((g["seconds"] - c["seconds"]) / c["seconds"] * 100)
    if deltas:
        avg_delta = sum(deltas) / len(deltas)
        med_delta = median(deltas)
        print(f"Delta medio tempo CPU→GPU: {avg_delta:+.1f}%")
        print(f"Delta mediano tempo CPU→GPU: {med_delta:+.1f}%")
        if abs(avg_delta) < 20:
            print(
                "=> Laya CPU/GPU NON spiega variazioni significative nel tempo per chiamata."
            )
        else:
            print(
                "=> Laya CPU/GPU mostra un effetto misurabile (da verificare con più repliche)."
            )

print()
print(
    "Nota: i tempi registrati includono l'inferenza Ollama + middleware, non solo Laya."
)
print("Laya è System 1 (routing/choice/score) e opera prima dell'inferenza.")
print(
    "Il timeout di 600s su alcuni test suggerisce che il tempo dominante è Ollama, non Laya."
)

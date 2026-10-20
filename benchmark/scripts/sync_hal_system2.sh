#!/usr/bin/env bash
# Mantiene allineate le copie del gateway con la sorgente canonica hal_system2.
#
# Usage:
#   sync_hal_system2.sh check   # exit 0 se identiche, 1 se divergono, 2 se hal_system2 manca
#   sync_hal_system2.sh apply   # copia canonico -> gateway (mai nel verso opposto)
#
# Variabili: HAL_SYSTEM2_DIR (default /var/www/hal_system2), GATEWAY_DIR (default: root del repo).
set -euo pipefail

GATEWAY_DIR="${GATEWAY_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"
HAL_SYSTEM2_DIR="${HAL_SYSTEM2_DIR:-/var/www/hal_system2}"

# canonico (relativo a HAL_SYSTEM2_DIR) | mirror (relativo a GATEWAY_DIR)
PAIRS=(
  "app/benchmark_models.py|benchmark/runner/benchmark_models.py"
  "app/system2_metrics.py|benchmark/runner/system2_metrics.py"
  "scripts/generate_benchmark_report.py|benchmark/scripts/generate_benchmark_report.py"
)

mode="${1:-}"
if [[ "$mode" != "check" && "$mode" != "apply" ]]; then
  echo "usage: $(basename "$0") check|apply" >&2
  exit 2
fi
if [[ ! -d "$HAL_SYSTEM2_DIR" ]]; then
  echo "hal_system2 non trovato: $HAL_SYSTEM2_DIR" >&2
  exit 2
fi

diverged=0
for pair in "${PAIRS[@]}"; do
  source_file="$HAL_SYSTEM2_DIR/${pair%%|*}"
  mirror_file="$GATEWAY_DIR/${pair##*|}"
  if [[ ! -f "$source_file" ]]; then
    echo "MANCANTE nel canonico: ${pair%%|*}" >&2
    exit 2
  fi
  if [[ "$mode" == "apply" ]]; then
    mkdir -p "$(dirname "$mirror_file")"
    cp "$source_file" "$mirror_file"
    echo "copiato: ${pair##*|}"
  elif [[ ! -f "$mirror_file" ]] || ! cmp -s "$source_file" "$mirror_file"; then
    echo "DIVERGE: ${pair##*|}" >&2
    diverged=1
  else
    echo "ok: ${pair##*|}"
  fi
done

exit "$diverged"

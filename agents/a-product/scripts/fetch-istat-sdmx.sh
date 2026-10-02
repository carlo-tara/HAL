#!/usr/bin/env bash
# Fetch a slice of ISTAT SDMX data as CSV.
# Usage: fetch-istat-sdmx.sh <flowRef> [startPeriod] [endPeriod] [out.csv]
# Example: fetch-istat-sdmx.sh 'IT1,22_289' 2020 2024 /tmp/istat.csv
set -euo pipefail

FLOW_REF="${1:?flowRef required (e.g. IT1,22_289 or documented id)}"
START="${2:-}"
END="${3:-}"
OUT="${4:-}"

BASE="https://esploradati.istat.it/SDMXWS/rest/data"
QS=""
if [[ -n "$START" ]]; then QS+="startPeriod=${START}&"; fi
if [[ -n "$END" ]]; then QS+="endPeriod=${END}&"; fi
QS+="lastNObservations=200"
URL="${BASE}/${FLOW_REF}?${QS}"

ACCEPT='application/vnd.sdmx.data+csv;version=1.0.0'

echo "GET ${URL}" >&2
echo "(ISTAT rate limit ~5 req/min — avoid tight loops)" >&2

if [[ -n "$OUT" ]]; then
  curl -fsSL -H "Accept: ${ACCEPT}" "$URL" -o "$OUT"
  echo "Wrote ${OUT}" >&2
else
  curl -fsSL -H "Accept: ${ACCEPT}" "$URL"
fi

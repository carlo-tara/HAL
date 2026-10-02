#!/usr/bin/env bash
# Report (and optionally apply) [sync:safe] extends-version bumps on consumer L2 STALE chains.
# Usage:
#   bash scripts/sync-consumer-stale.sh --dry-run
#   bash scripts/sync-consumer-stale.sh --apply   # only bump extends-version + patch version + CHANGELOG stub
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
APPLY=0
PROJECTS=(
  /var/www/piratesstraps
  /var/www/WTP_App
  /var/www/GiocoStrategico
  /var/www/liberating.it
  /var/www/the-verde.it
  /var/www/stiliattaccamento
  /var/www/InnerCircle
  /var/www/carlogandolfo
  /var/www/pierrehouben
  /var/www/cambiapasso
)

for arg in "$@"; do
  case "$arg" in
    --apply) APPLY=1 ;;
    --dry-run) APPLY=0 ;;
    --projects=*) IFS=' ' read -r -a PROJECTS <<< "${arg#--projects=}" ;;
  esac
done

echo "=== sync-consumer-stale (APPLY=$APPLY) ==="
bash "$ROOT/a-agentzero/scripts/sync-agents.sh" --dry-run --projects "${PROJECTS[@]}" 2>&1 | tee /tmp/af-sync-stale.txt | tail -30

if [[ "$APPLY" -ne 1 ]]; then
  echo
  echo "Dry-run only. Review STALE above, then:"
  echo "  bash scripts/sync-consumer-stale.sh --apply"
  echo "Applies only mechanical extends-version bumps where pending is [sync:safe]-only is still MANUAL per agent-versioning — this script lists targets."
  echo "For each STALE L2, preferred flow: open that consumer repo → RGR slice → bump extends-version + patch + CHANGELOG."
  exit 0
fi

echo "--apply: generating bump checklist (no auto-edit of [sync:breaking] gaps)"
python3 - <<'PY'
from pathlib import Path
import re
text = Path("/tmp/af-sync-stale.txt").read_text(errors="replace")
# L2: name @ ver STALE (padre parent @ pver)
pat = re.compile(r"L2: (\S+) @ (\S+) STALE \(padre (\S+) @ ([^)]+)\)")
seen=set()
for m in pat.finditer(text):
    key=m.groups()
    if key in seen: continue
    seen.add(key)
    print(f"- {key[0]} {key[1]} → extends {key[2]}@{key[3]}")
print(f"Total unique STALE L2: {len(seen)}")
print("Apply bumps in each consumer repo with RGR; do not bulk-edit from HAL without per-repo slice.")
PY

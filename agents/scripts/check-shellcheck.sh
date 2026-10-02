#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SC=""
if command -v shellcheck >/dev/null 2>&1; then
  SC="$(command -v shellcheck)"
elif [[ -x "$ROOT/.tools/shellcheck" ]]; then
  SC="$ROOT/.tools/shellcheck"
else
  echo "FAIL: shellcheck not found. Run: make tools-shellcheck" >&2
  exit 1
fi

echo ">>> shellcheck ($SC)"
mapfile -t uniq < <(
  {
    printf '%s\n' "$ROOT/deploy-all.sh"
    printf '%s\n' "$ROOT"/scripts/*.sh
    printf '%s\n' "$ROOT"/a-agentzero/scripts/*.sh
    printf '%s\n' "$ROOT"/a-*/deploy.sh
    printf '%s\n' "$ROOT"/.cursor/hooks/*.sh
  } | sort -u
)

fail=0
for f in "${uniq[@]}"; do
  [[ -f "$f" ]] || continue
  echo "  shellcheck $f"
  if ! "$SC" -x -S error "$f"; then
    fail=1
  fi
done
if [[ "$fail" -ne 0 ]]; then exit 1; fi
echo "shellcheck-ok OK"

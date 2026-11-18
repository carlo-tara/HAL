#!/usr/bin/env bash
# check-line-length.sh — cap di lunghezza righe sui registry/riferimenti (regola 7).
# Motivo: il merge 3-way di git è a righe; una riga da 7k char non dà un conflitto
# parziale, dà un conflitto intero manuale — uccide la mergeabilità dei registri.
# Scope: references delle skill, CHANGELOG (bundle + root), session-learnings.
set -euo pipefail

CAP="${CAP:-3000}"
ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

fail=0
for f in agents/a-*/references/*.md \
         agents/a-agentzero/*/references/*.md \
         agents/project-skills/*/references/*.md \
         agents/a-*/CHANGELOG.md \
         agents/a-agentzero/*/CHANGELOG.md \
         agents/project-skills/*/CHANGELOG.md \
         CHANGELOG.md docs/harness-CHANGELOG.md product/session-learnings.md; do
  [ -f "$f" ] || continue
  hits="$(awk -v cap="$CAP" -v file="$f" 'length($0) > cap {printf "%s:%d len=%d\n", file, NR, length($0)}' "$f")"
  if [ -n "$hits" ]; then
    echo "$hits"
    fail=1
  fi
done
[ "$fail" -eq 0 ] && echo "check-line-length OK (cap=${CAP})"
exit "$fail"

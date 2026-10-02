#!/usr/bin/env bash
# Frontmatter gate: every HAL bundle and project skill must have version;
# extends requires extends-version.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
fail=0

check_skill() {
  local f="$1"
  local v e ev
  v=$(awk 'BEGIN{fm=0} /^---$/{if(fm){exit} fm=1; next} fm && $1=="version:"{sub(/^[^:]*:[[:space:]]*/,""); print; exit}' "$f")
  e=$(awk 'BEGIN{fm=0} /^---$/{if(fm){exit} fm=1; next} fm && $1=="extends:"{sub(/^[^:]*:[[:space:]]*/,""); print; exit}' "$f")
  ev=$(awk 'BEGIN{fm=0} /^---$/{if(fm){exit} fm=1; next} fm && $1=="extends-version:"{sub(/^[^:]*:[[:space:]]*/,""); print; exit}' "$f")
  if [[ -z "$v" ]]; then
    echo "FAIL $f: missing version" >&2
    return 1
  fi
  if [[ -n "$e" && -z "$ev" ]]; then
    echo "FAIL $f: extends without extends-version" >&2
    return 1
  fi
  echo "  OK $f (version=$v${e:+ extends=$e@$ev})"
  return 0
}

echo ">>> Frontmatter: all SKILL.md (L0/L1/L2 + competencies)"
while IFS= read -r -d '' f; do
  check_skill "$f" || fail=1
done < <(find "$ROOT" \( -path "$ROOT/a-*" -o -path "$ROOT/project-skills/*" -o -path "$ROOT/.agents/skills/*" -o -path "$ROOT/.cursor/skills/*" \) \
  -name SKILL.md -print0 2>/dev/null | sort -zu)

if [[ "$fail" -ne 0 ]]; then
  exit 1
fi
echo "frontmatter-all OK"

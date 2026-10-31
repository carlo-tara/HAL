#!/usr/bin/env bash
# Frontmatter gate: every HAL bundle and project skill must have a valid name
# (regex + dir match, per Zed skill loader), version; extends requires extends-version.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
fail=0
NAME_RE='^[a-z0-9]+(-[a-z0-9]+)*$'

check_skill() {
  local f="$1"
  local n v e ev d
  n=$(awk 'BEGIN{fm=0} /^---$/{if(fm){exit} fm=1; next} fm && $1=="name:"{sub(/^[^:]*:[[:space:]]*/,""); print; exit}' "$f")
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
  # Zed loader contract: name required, kebab-case, must equal directory name.
  d=$(basename "$(dirname "$f")")
  if [[ -z "$n" ]]; then
    echo "FAIL $f: missing name" >&2
    return 1
  fi
  if [[ ! "$n" =~ $NAME_RE ]]; then
    echo "FAIL $f: invalid name '$n' (Zed requires ^[a-z0-9]+(-[a-z0-9]+)*\$)" >&2
    return 1
  fi
  if [[ "$n" != "$d" ]]; then
    echo "FAIL $f: name '$n' != directory '$d'" >&2
    return 1
  fi
  echo "  OK $f (name=$n version=$v${e:+ extends=$e@$ev})"
  return 0
}

echo ">>> Frontmatter: all SKILL.md (L0/L1/L2 + competencies)"
while IFS= read -r -d '' f; do
  check_skill "$f" || fail=1
done < <(
  {
    find "$ROOT" \( -path "$ROOT/a-*" -o -path "$ROOT/project-skills/*" \) \
      -name SKILL.md -print0 2>/dev/null
    # L2 consumer mirror (real dir in .agents/skills/harness-*); symlinked
    # bundles point into $ROOT and are already covered by the scan above.
    find "$ROOT/../.agents/skills" -mindepth 2 -maxdepth 2 -type f \
      -path "*/harness-*/SKILL.md" -print0 2>/dev/null
  } | sort -zu
)

if [[ "$fail" -ne 0 ]]; then
  exit 1
fi
echo "frontmatter-all OK"

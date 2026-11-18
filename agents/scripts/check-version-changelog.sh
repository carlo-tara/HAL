#!/usr/bin/env bash
# check-version-changelog.sh — guardia della transazione bump↔changelog (regola 6).
# Ogni SKILL.md con un CHANGELOG.md sorella deve avere un header "## [<version>]"
# nel proprio changelog. --fix inserisce lo stub mancante (solo header + nota),
# cosi l'archeologia post-gara ([1.6.16], [1.11.0]) diventa un check, non un turno.
set -euo pipefail

FIX=0
ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"
for arg in "$@"; do [ "$arg" = "--fix" ] && FIX=1; done

fail=0
for skill in agents/a-*/SKILL.md agents/a-agentzero/*/SKILL.md agents/project-skills/*/SKILL.md; do
  [ -f "$skill" ] || continue
  dir="$(dirname "$skill")"; cl="$dir/CHANGELOG.md"
  [ -f "$cl" ] || continue
  v="$(awk '/^version:/{print $2; exit}' "$skill")"
  [ -n "$v" ] || continue
  if grep -q "^## \[$v\]" "$cl"; then continue; fi
  if [ "$FIX" -eq 1 ]; then
    python3 - "$cl" "$v" <<'PYEOF'
import sys, datetime
cl, v = sys.argv[1], sys.argv[2]
t = open(cl, encoding="utf-8").read()
stub = (f"## [{v}] - {datetime.date.today().isoformat()}\n\n"
        "### Changed\n\n"
        "- Header di convalida (check-version-changelog.sh --fix): il bump era nel "
        "frontmatter senza registro — voce da integrare a mano.\n\n")
i = t.find("\n## [")
if i == -1:
    t = t.rstrip("\n") + "\n\n" + stub.rstrip("\n") + "\n"
else:
    t = t[:i+1] + stub + t[i+1:]
open(cl, "w", encoding="utf-8").write(t)
print(f"FIX {cl} [{v}]")
PYEOF
  else
    echo "MISS $skill v=$v → header [## $v] assente in $cl"
    fail=1
  fi
done
exit "$fail"

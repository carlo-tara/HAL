#!/usr/bin/env bash
# ready-proof — mechanical RGR checks for HAL skill edits (local + CI optional)
# - If any a-*/ or .cursor/skills/** SKILL.md is dirty/staged with version bump → CHANGELOG must change
# - Fail if >4 skill paths dirty without waiver:
#     env WAIVER_FILES_GT4=1  → allow
#     env WAIVER_FILES_GT4=0  → deny (CI)
#     env unset → allow if latest progress session has `- WAIVER_FILES_GT4: 1`
# - Fail if skill dirty and no open (or just-closed) progress session referencing slice
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
PROGRESS="$ROOT/.cursor/product/agent-progress.md"
fail=0

if ! command -v git >/dev/null 2>&1; then
  echo "ready-proof: git missing — skip"
  exit 0
fi

mapfile -t dirty < <(git status --porcelain 2>/dev/null | awk '{print $NF}' | grep -E '^(a-[^/]+/|\.cursor/skills/)' || true)

echo ">>> ready-proof (${#dirty[@]} dirty agent/skill paths)"

if [[ ${#dirty[@]} -eq 0 ]]; then
  echo "ready-proof OK (no dirty agent/skill paths)"
  exit 0
fi

# Resolve >4-file waiver: env wins; else latest agent-progress session
waiver_ok=0
waiver_src=""
case "${WAIVER_FILES_GT4:-}" in
  1)
    waiver_ok=1
    waiver_src="env"
    ;;
  0)
    waiver_ok=0
    waiver_src="env=0"
    ;;
  *)
    if [[ -f "$PROGRESS" ]] && python3 - "$PROGRESS" <<'PY'
import re, sys
from pathlib import Path
text = Path(sys.argv[1]).read_text(encoding="utf-8", errors="replace")
parts = text.split("# Agent progress")
last = parts[-1] if len(parts) > 1 else text
# header list item or inline in events
if re.search(r"(?m)^-\s*WAIVER_FILES_GT4:\s*1\b", last):
    sys.exit(0)
if re.search(r"WAIVER_FILES_GT4\s*=\s*1", last):
    sys.exit(0)
sys.exit(1)
PY
    then
      waiver_ok=1
      waiver_src="progress(latest session)"
    fi
    ;;
esac

if [[ ${#dirty[@]} -gt 4 && "$waiver_ok" -ne 1 ]]; then
  echo "FAIL: ${#dirty[@]} agent/skill paths dirty (>4). Set WAIVER_FILES_GT4=1 (env) or document '- WAIVER_FILES_GT4: 1' in the latest agent-progress session, or split slices." >&2
  fail=1
elif [[ ${#dirty[@]} -gt 4 && "$waiver_ok" -eq 1 ]]; then
  echo "ready-proof: WAIVER_FILES_GT4 via ${waiver_src} (${#dirty[@]} paths)"
fi

# version bump without CHANGELOG in same agent dir
python3 - "$ROOT" <<'PY' || fail=1
import re, subprocess, sys
from pathlib import Path
root = Path(sys.argv[1])
out = subprocess.check_output(["git", "status", "--porcelain"], cwd=root, text=True)
paths = []
for line in out.splitlines():
    parts = line.split()
    if len(parts) >= 2:
        p = parts[-1]
        if p.startswith("a-") or p.startswith(".cursor/skills/"):
            paths.append(p)

skill_files = [p for p in paths if p.endswith("SKILL.md")]
fail = 0
for skill in skill_files:
    sp = root / skill
    if not sp.exists():
        continue
    # detect version line change vs HEAD
    try:
        old = subprocess.check_output(["git", "show", f"HEAD:{skill}"], cwd=root, text=True, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        old = ""
    new = sp.read_text(encoding="utf-8", errors="replace")
    def ver(text):
        m = re.search(r"^version:\s*(\S+)", text, re.M)
        return m.group(1) if m else None
    ov, nv = ver(old), ver(new)
    if ov and nv and ov != nv:
        changelog_dirty = False
        for p in paths:
            if p.endswith("CHANGELOG.md") and (
                str(sp.parent) in str(root / p) or p.startswith(skill.split("/")[0] + "/")
            ):
                changelog_dirty = True
        if not changelog_dirty:
            # also accept agent-level CHANGELOG dirty
            top = skill.split("/")[0]
            if any(p == f"{top}/CHANGELOG.md" or p.startswith(f"{top}/") and p.endswith("CHANGELOG.md") for p in paths):
                changelog_dirty = True
        if not changelog_dirty:
            print(f"FAIL {skill}: version {ov}→{nv} without CHANGELOG in dirty set", file=sys.stderr)
            fail = 1
sys.exit(fail)
PY

# progress must exist and mention a recent slice (open or closed today)
if [[ ! -f "$PROGRESS" ]]; then
  echo "FAIL: missing $PROGRESS while agent/skill dirty" >&2
  fail=1
else
  if ! grep -qE '\| slice \|.*accepted' "$PROGRESS"; then
    echo "FAIL: agent-progress has no slice|accepted while skill dirty" >&2
    fail=1
  fi
fi

if [[ "$fail" -ne 0 ]]; then
  exit 1
fi
echo "ready-proof OK"

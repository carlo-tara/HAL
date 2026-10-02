#!/usr/bin/env bash
# Check relative markdown links in skill/docs canons (not agents/ plans/ vendor PDFs).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

python3 - "$ROOT" <<'PY'
import re, sys
from pathlib import Path
from urllib.parse import unquote

root = Path(sys.argv[1]).resolve()
link_re = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")
fail = 0
checked = 0

def collect():
    files = []
    docs = root / "docs"
    if docs.exists():
        files += list(docs.rglob("*.md"))
    for skill in root.glob("a-*/SKILL.md"):
        files.append(skill)
    for ext in root.glob("a-*/extension-template.md"):
        files.append(ext)
    for ref in root.glob("a-*/references/**/*.md"):
        files.append(ref)
    for comp in root.glob("a-*/competencies/**/SKILL.md"):
        files.append(comp)
    for l2 in root.glob("project-skills/**/*.md"):
        files.append(l2)
    for l2 in root.glob(".agents/skills/**/*.md"):
        if "GuideStile" in str(l2) or "PremioStrega" in str(l2):
            continue
        files.append(l2)
    for l2 in root.glob(".cursor/skills/**/*.md"):
        if "GuideStile" in str(l2) or "PremioStrega" in str(l2):
            continue
        files.append(l2)
    return files

for md in collect():
    text = md.read_text(encoding="utf-8", errors="replace")
    for m in link_re.finditer(text):
        target = m.group(2).strip().strip("<>")
        if not target or target.startswith(("#", "http://", "https://", "mailto:", "vscode:")):
            continue
        target = target.split()[0]
        path_part = unquote(target.split("#", 1)[0])
        if not path_part or path_part.endswith(".pdf"):
            continue
        checked += 1
        dest = (md.parent / path_part).resolve()
        try:
            dest.relative_to(root)
        except ValueError:
            continue
        if not dest.exists():
            print(f"FAIL {md.relative_to(root)}: broken link -> {target}", file=sys.stderr)
            fail = 1

print(f"checked {checked} relative links")
if fail:
    sys.exit(1)
print("md-links OK")
PY

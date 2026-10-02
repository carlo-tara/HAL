#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENTS_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
WORKSPACE_ROOT="$(cd "${AGENTS_ROOT}/.." && pwd)"
AGENT_IDS=(
  a-agentzero a-b2b a-copywriter a-design a-harness
  a-product a-seozoom a-wordpress
)
L0_COMMANDS=(version document review improve commit todo slice cycle graph)

check_link() {
  local link="$1" source="$2"
  if [[ ! -L "${link}" ]]; then
    echo "FAIL: expected symlink ${link}" >&2
    return 1
  fi
  if [[ "$(readlink -f "${link}")" != "$(readlink -f "${source}")" ]]; then
    echo "FAIL: ${link} resolves to $(readlink -f "${link}"), expected ${source}" >&2
    return 1
  fi
}

for agent in "${AGENT_IDS[@]}"; do
  check_link "${WORKSPACE_ROOT}/.agents/skills/${agent}" "${AGENTS_ROOT}/${agent}"
  [[ -f "${WORKSPACE_ROOT}/.agents/skills/${agent}/SKILL.md" ]]
  check_link "${WORKSPACE_ROOT}/.cursor/agents/${agent}.md" "${AGENTS_ROOT}/${agent}/agents/${agent}.md"
done

for skill in learn sync; do
  check_link "${WORKSPACE_ROOT}/.agents/skills/${skill}" "${AGENTS_ROOT}/a-agentzero/${skill}"
done
check_link "${WORKSPACE_ROOT}/.agents/skills/enrichment" "${AGENTS_ROOT}/a-b2b/enrichment"

for skill in personas jtbd gherkin; do
  check_link "${WORKSPACE_ROOT}/.agents/skills/${skill}" "${AGENTS_ROOT}/a-product/${skill}"
done

for skill in charts illustrator uiux; do
  check_link "${WORKSPACE_ROOT}/.agents/skills/${skill}" "${AGENTS_ROOT}/a-design/${skill}"
done

check_link "${WORKSPACE_ROOT}/.agents/skills/harness-agentfactory" \
  "${AGENTS_ROOT}/project-skills/harness-agentfactory"
check_link "${WORKSPACE_ROOT}/.agents/skills/laya" \
  "${AGENTS_ROOT}/project-skills/laya"

for command in "${L0_COMMANDS[@]}"; do
  check_link "${WORKSPACE_ROOT}/.cursor/commands/${command}.md" \
    "${AGENTS_ROOT}/a-agentzero/commands/${command}.md"
done
check_link "${WORKSPACE_ROOT}/.cursor/commands/laya.md" \
  "${AGENTS_ROOT}/project-skills/laya/commands/laya.md"

python3 - "${WORKSPACE_ROOT}" "${AGENTS_ROOT}" <<'PY'
import json
import re
import sys
from pathlib import Path

workspace = Path(sys.argv[1])
root = Path(sys.argv[2])
catalog = json.loads((root / "catalog.json").read_text(encoding="utf-8"))
expected = {
    "a-agentzero", "a-b2b", "a-copywriter", "a-design", "a-harness",
    "a-product", "a-seozoom", "a-wordpress",
}
actual = {agent["name"] for agent in catalog["agents"]}
if actual != expected:
    raise SystemExit(f"FAIL: catalog agent mismatch; missing={sorted(expected-actual)}, extra={sorted(actual-expected)}")
if catalog.get("execution_model") != "SystemTwoEngine.ACTIVE_MODEL_NAME":
    raise SystemExit("FAIL: catalog does not delegate execution to the System 2 default")

entrypoints = sorted(expected | {
    "enrichment", "personas", "jtbd", "gherkin", "charts", "illustrator", "uiux",
    "learn", "sync", "harness-agentfactory", "laya",
})
for name in entrypoints:
    skill = workspace / ".agents" / "skills" / name / "SKILL.md"
    text = skill.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise SystemExit(f"FAIL: {skill}: missing YAML frontmatter")
    frontmatter = text.split("---\n", 2)[1]
    fields = {}
    lines = frontmatter.splitlines()
    description_lines = []
    in_description = False
    for line in lines:
        if line.startswith("name:"):
            fields["name"] = line.partition(":")[2].strip().strip("'\"")
        elif line.startswith("description:"):
            value = line.partition(":")[2].strip().strip("'\"")
            if value in {">", ">-", ">+", "|", "|-", "|+"}:
                in_description = True
            else:
                description_lines.append(value)
        elif in_description:
            if line and not line[0].isspace():
                in_description = False
            else:
                description_lines.append(line.strip())
    fields["description"] = " ".join(part for part in description_lines if part)
    if fields.get("name") != name:
        raise SystemExit(f"FAIL: {skill}: name must be {name!r}, got {fields.get('name')!r}")
    description = fields.get("description", "")
    if not description or len(description) > 1024:
        raise SystemExit(f"FAIL: {skill}: missing or >1024-character description")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name) or len(name) > 64:
        raise SystemExit(f"FAIL: non-portable Agent Skills name: {name}")

print("editor-links OK (Zed/Cursor skills, Cursor subagents/commands, catalog)")
PY

#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENTS_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
WORKSPACE_ROOT="$(cd "${AGENTS_ROOT}/.." && pwd)"

AGENT_IDS=(
  a-agentzero
  a-b2b
  a-copywriter
  a-design
  a-harness
  a-product
  a-seozoom
  a-wordpress
)
L0_COMMANDS=(version document review improve commit todo slice cycle graph)

link_path() {
  local source="$1" target="$2" destination="$3"
  if [[ ! -e "${source}" ]]; then
    echo "Missing source: ${source}" >&2
    return 1
  fi
  if [[ -e "${destination}" && ! -L "${destination}" ]]; then
    echo "Refusing to replace existing non-symlink: ${destination}" >&2
    return 1
  fi
  mkdir -p "$(dirname "${destination}")"
  ln -sfn "${target}" "${destination}"
}

for agent in "${AGENT_IDS[@]}"; do
  link_path "${AGENTS_ROOT}/${agent}" "../../agents/${agent}" "${WORKSPACE_ROOT}/.agents/skills/${agent}"
  link_path "${AGENTS_ROOT}/${agent}/agents/${agent}.md" "../../agents/${agent}/agents/${agent}.md" "${WORKSPACE_ROOT}/.cursor/agents/${agent}.md"
done

for skill in learn sync; do
  link_path "${AGENTS_ROOT}/a-agentzero/${skill}" "../../agents/a-agentzero/${skill}" "${WORKSPACE_ROOT}/.agents/skills/${skill}"
done

link_path "${AGENTS_ROOT}/a-b2b/enrichment" "../../agents/a-b2b/enrichment" "${WORKSPACE_ROOT}/.agents/skills/enrichment"

for skill in personas jtbd gherkin; do
  link_path "${AGENTS_ROOT}/a-product/${skill}" "../../agents/a-product/${skill}" "${WORKSPACE_ROOT}/.agents/skills/${skill}"
done

for skill in charts illustrator uiux; do
  link_path "${AGENTS_ROOT}/a-design/${skill}" "../../agents/a-design/${skill}" "${WORKSPACE_ROOT}/.agents/skills/${skill}"
done

link_path "${AGENTS_ROOT}/project-skills/harness-agentfactory" "../../agents/project-skills/harness-agentfactory" \
  "${WORKSPACE_ROOT}/.agents/skills/harness-agentfactory"

link_path "${AGENTS_ROOT}/project-skills/laya" "../../agents/project-skills/laya" \
  "${WORKSPACE_ROOT}/.agents/skills/laya"

link_zed_prompt() {
  local source="$1" target="$2"
  if [[ ! -e "${source}" ]]; then
    echo "Missing source: ${source}" >&2
    return 1
  fi
  mkdir -p "$(dirname "${target}")"
  rm -f "${target}"
  python3 -c "
import re
with open('${source}', 'r', encoding='utf-8') as f:
    content = f.read()
content = re.sub(r'^---\s*\n.*?\n---\s*\n', '', content, flags=re.DOTALL)
with open('${target}', 'w', encoding='utf-8') as f:
    f.write(content)
"
}

link_zed_skill() {
  local source="$1"
  local name="$2"
  local skill_dir="${WORKSPACE_ROOT}/.agents/skills/${name}"
  mkdir -p "${skill_dir}"
  python3 -c "
import re
with open('${source}', 'r', encoding='utf-8') as f:
    content = f.read()
content = re.sub(r'^---\s*\n.*?\n---\s*\n', '', content, flags=re.DOTALL)
skill_content = '''---
name: ${name}
version: 1.0.0
description: Command ${name} for HAL workspace.
---\n\n''' + content
with open('${skill_dir}/SKILL.md', 'w', encoding='utf-8') as f:
    f.write(skill_content)
"
}

for command in "${L0_COMMANDS[@]}"; do
  link_path "${AGENTS_ROOT}/a-agentzero/commands/${command}.md" "../../agents/a-agentzero/commands/${command}.md" \
    "${WORKSPACE_ROOT}/.cursor/commands/${command}.md"
  link_zed_prompt "${AGENTS_ROOT}/a-agentzero/commands/${command}.md" \
    "${WORKSPACE_ROOT}/.zed/prompts/${command}.md"
  link_zed_skill "${AGENTS_ROOT}/a-agentzero/commands/${command}.md" "${command}"
done

if [[ -f "${AGENTS_ROOT}/project-skills/laya/commands/laya.md" ]]; then
  link_path "${AGENTS_ROOT}/project-skills/laya/commands/laya.md" "../../agents/project-skills/laya/commands/laya.md" \
    "${WORKSPACE_ROOT}/.cursor/commands/laya.md"
  link_zed_prompt "${AGENTS_ROOT}/project-skills/laya/commands/laya.md" \
    "${WORKSPACE_ROOT}/.zed/prompts/laya.md"
  link_zed_skill "${AGENTS_ROOT}/project-skills/laya/commands/laya.md" "laya-cmd"
fi

printf 'HAL skills linked for Zed and Cursor: %s\n' "${WORKSPACE_ROOT}/.agents/skills"
printf 'Cursor subagents linked: %s\n' "${WORKSPACE_ROOT}/.cursor/agents"
printf 'Cursor commands linked: %s\n' "${WORKSPACE_ROOT}/.cursor/commands"
printf 'Zed prompts linked: %s\n' "${WORKSPACE_ROOT}/.zed/prompts"

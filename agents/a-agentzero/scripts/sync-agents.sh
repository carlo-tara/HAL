#!/usr/bin/env bash
# Verifica le catene L0/L1/L2 e gli entrypoint HAL per Zed e Cursor.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENTZERO_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
HAL_AGENTS_ROOT="$(cd "${AGENTZERO_DIR}/.." && pwd)"
WORKSPACE_ROOT="$(cd "${HAL_AGENTS_ROOT}/.." && pwd)"
VERSION_SH="${SCRIPT_DIR}/agent-version.sh"
DEPLOY_ALL="${HAL_AGENTS_ROOT}/deploy-all.sh"
L0_COMMANDS=(version document review improve commit todo slice cycle graph)
AGENTS=(
  a-agentzero
  a-b2b
  a-copywriter
  a-design
  a-harness
  a-product
  a-seozoom
  a-wordpress
)

usage() {
  cat <<'EOF'
Usage:
  sync-agents.sh [--dry-run] [--projects DIR ...]

  --dry-run     Solo report versioni e link locali; non modifica file.
  --projects    Root di repository consumer: controlla L2 in .agents/skills/
                e .cursor/skills/ (compatibilità Cursor legacy).

Senza --dry-run ricrea gli entrypoint Zed/Cursor del workspace HAL, poi verifica le catene.
EOF
}

resolve_link() {
  local path="$1"
  if command -v readlink >/dev/null 2>&1; then
    readlink -f "${path}" 2>/dev/null || readlink "${path}" 2>/dev/null || printf '%s\n' "${path}"
  else
    printf '%s\n' "${path}"
  fi
}

report_workspace_links() {
  echo ">>> Skill condivise Zed/Cursor (.agents/skills)"
  local agent destination expected actual status
  local missing=0 drift=0
  for agent in "${AGENTS[@]}" learn sync harness-agentfactory laya enrichment personas jtbd gherkin charts illustrator uiux; do
    case "${agent}" in
      learn|sync) expected="${AGENTZERO_DIR}/${agent}" ;;
      harness-agentfactory|laya) expected="${HAL_AGENTS_ROOT}/project-skills/${agent}" ;;
      enrichment) expected="${HAL_AGENTS_ROOT}/a-b2b/enrichment" ;;
      personas|jtbd|gherkin) expected="${HAL_AGENTS_ROOT}/a-product/${agent}" ;;
      charts|illustrator|uiux) expected="${HAL_AGENTS_ROOT}/a-design/${agent}" ;;
      *) expected="${HAL_AGENTS_ROOT}/${agent}" ;;
    esac
    destination="${WORKSPACE_ROOT}/.agents/skills/${agent}"
    if [[ ! -e "${destination}" ]]; then
      status="MISSING"
      missing=$((missing + 1))
    elif [[ ! -L "${destination}" ]]; then
      status="DRIFT (not a symlink)"
      drift=$((drift + 1))
    else
      actual="$(resolve_link "${destination}")"
      if [[ "${actual}" == "${expected}" ]]; then status="OK"; else status="DRIFT -> ${actual}"; drift=$((drift + 1)); fi
    fi
    echo "  ${agent}: ${status}"
  done
  echo
  echo ">>> Adapter Cursor commands (.cursor/commands)"
  for agent in "${L0_COMMANDS[@]}"; do
    destination="${WORKSPACE_ROOT}/.cursor/commands/${agent}.md"
    expected="${AGENTZERO_DIR}/commands/${agent}.md"
    if [[ ! -e "${destination}" ]]; then
      echo "  ${agent}: MISSING"
      missing=$((missing + 1))
    elif [[ ! -L "${destination}" ]]; then
      echo "  ${agent}: DRIFT (not a symlink)"
      drift=$((drift + 1))
    else
      actual="$(resolve_link "${destination}")"
      if [[ "${actual}" == "${expected}" ]]; then echo "  ${agent}: OK"; else echo "  ${agent}: DRIFT -> ${actual}"; drift=$((drift + 1)); fi
    fi
  done
  if [[ "${missing}" -gt 0 || "${drift}" -gt 0 ]]; then
    echo "  Link mancanti o divergenti: bash agents/scripts/link-workspace-skills.sh"
  fi
  echo
}

report_project_command_overrides() {
  local root="$1" cmd
  echo "--- Comandi Cursor L0 (override vs assenza) ---"
  for cmd in "${L0_COMMANDS[@]}"; do
    if [[ -e "${root}/.cursor/commands/${cmd}.md" ]]; then
      echo "  ${cmd}: override (${root}/.cursor/commands/${cmd}.md)"
    else
      echo "  ${cmd}: nessun override"
    fi
  done
}

DRY_RUN=0
PROJECTS=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY_RUN=1; shift ;;
    --projects)
      shift
      while [[ $# -gt 0 && "$1" != --* ]]; do PROJECTS+=("$1"); shift; done
      ;;
    -h|--help|help) usage; exit 0 ;;
    *) echo "Argomento sconosciuto: $1" >&2; usage; exit 1 ;;
  esac
done

if [[ ! -f "${VERSION_SH}" ]]; then
  echo "Errore: manca ${VERSION_SH}" >&2
  exit 1
fi

echo "=== HAL sync agenti ==="
echo "Canonical root: ${HAL_AGENTS_ROOT}"
echo "L0: $("${VERSION_SH}" show "${AGENTZERO_DIR}/SKILL.md" 2>/dev/null | tr '\n' ' ' | sed 's/  */ /g')"
echo

if [[ "${DRY_RUN}" -eq 0 ]]; then
  bash "${DEPLOY_ALL}"
else
  echo ">>> Link invariati (--dry-run)"
fi
report_workspace_links

echo ">>> Catene L1 ← L0"
stale_count=0
for agent in "${AGENTS[@]:1}"; do
  skill="${HAL_AGENTS_ROOT}/${agent}/SKILL.md"
  echo
  echo "--- ${agent} ---"
  output="$("${VERSION_SH}" chain "${skill}" 2>&1)" || true
  echo "${output}"
  if grep -q 'STALE' <<<"${output}"; then
    stale_count=$((stale_count + 1))
    echo "Pending CHANGELOG:"
    "${VERSION_SH}" pending "${skill}" 2>&1 || true
  fi
done

echo
for root in "${PROJECTS[@]}"; do
  if [[ ! -d "${root}" ]]; then echo "SKIP progetto (non directory): ${root}"; continue; fi
  echo "=== Progetto: ${root} ==="
  report_project_command_overrides "${root}"
  skills=()
  for skills_root in "${root}/.agents/skills" "${root}/.cursor/skills"; do
    if [[ -d "${skills_root}" ]]; then
      while IFS= read -r -d '' skill; do skills+=("${skill}"); done < <(find "${skills_root}" -mindepth 2 -maxdepth 2 -name SKILL.md -print0)
    fi
  done
  if [[ ${#skills[@]} -eq 0 ]]; then echo "(nessuna skill L2 trovata)"; continue; fi
  for skill in "${skills[@]}"; do
    echo "--- L2 $(basename "$(dirname "${skill}")") ---"
    output="$("${VERSION_SH}" chain "${skill}" 2>&1)" || true
    echo "${output}"
    if grep -q 'STALE' <<<"${output}"; then stale_count=$((stale_count + 1)); fi
  done
done

echo
echo "=== Riepilogo ==="
if [[ "${stale_count}" -eq 0 ]]; then
  echo "Nessuna catena STALE rilevata."
else
  echo "Catene STALE: ${stale_count}; consultare agents/a-agentzero/references/agent-versioning.md."
fi

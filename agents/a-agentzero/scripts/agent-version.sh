#!/usr/bin/env bash
# Report versioni agenti HAL (L0/L1/L2) e voci CHANGELOG pending per sync selettivo.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
AGENTZERO_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
HAL_AGENTS_ROOT="$(cd "${AGENTZERO_DIR}/.." && pwd)"

usage() {
  cat <<'EOF'
Usage:
  agent-version.sh show <path>              Mostra version e extends-version
  agent-version.sh chain <SKILL.md>         Catena agente L2→L1→L0 con flag STALE
  agent-version.sh competency-chain <path>  Catena competenza L0/L1/L2 (stessa id)
  agent-version.sh pending <SKILL.md>       Voci CHANGELOG padre > extends-version

Path: SKILL.md o directory (contiene SKILL.md).
EOF
}

resolve_skill() {
  local path="$1"
  if [[ -d "${path}" ]]; then
    path="${path%/}/SKILL.md"
  fi
  if [[ ! -f "${path}" ]]; then
    echo "Errore: file non trovato: ${path}" >&2
    exit 1
  fi
  printf '%s' "${path}"
}

get_field() {
  local file="$1" field="$2"
  awk -v f="${field}" '
    BEGIN { in_fm=0 }
    /^---$/ {
      if (in_fm) { exit }
      in_fm=1
      next
    }
    in_fm && $1 == f":" {
      sub(/^[^:]*:[[:space:]]*/, "")
      print
      exit
    }
  ' "${file}"
}

semver_cmp() {
  # stdout: 0 se equal, 1 se $1 > $2, 2 se $1 < $2
  local a="${1#v}" b="${2#v}"
  local IFS=.
  local -a av bv
  read -r -a av <<< "${a}"
  read -r -a bv <<< "${b}"
  local i max="${#av[@]}"
  if (( ${#bv[@]} > max )); then max="${#bv[@]}"; fi
  for (( i=0; i<max; i++ )); do
    local ai="${av[i]:-0}" bi="${bv[i]:-0}"
    if (( 10#${ai} > 10#${bi} )); then echo 1; return; fi
    if (( 10#${ai} < 10#${bi} )); then echo 2; return; fi
  done
  echo 0
}

resolve_parent_skill() {
  local file="$1"
  local parent
  parent="$(get_field "${file}" "extends")"
  if [[ -z "${parent}" ]]; then
    return 1
  fi

  local candidates=(
    "${HOME}/.agents/skills/${parent}/SKILL.md"
    "${HOME}/.cursor/skills/${parent}/SKILL.md"
    "${HAL_AGENTS_ROOT}/${parent}/SKILL.md"
  )
  local c
  for c in "${candidates[@]}"; do
    if [[ -f "${c}" ]]; then
      printf '%s' "${c}"
      return 0
    fi
  done
  echo "Errore: padre '${parent}' non trovato per ${file}" >&2
  exit 1
}

resolve_changelog() {
  local skill_file="$1"
  local dir
  dir="$(cd "$(dirname "${skill_file}")" && pwd)"
  if [[ -f "${dir}/CHANGELOG.md" ]]; then
    printf '%s' "${dir}/CHANGELOG.md"
    return 0
  fi
  return 1
}

cmd_show() {
  local path skill name version extends extends_version
  skill="$(resolve_skill "$1")"
  name="$(get_field "${skill}" "name")"
  version="$(get_field "${skill}" "version")"
  extends="$(get_field "${skill}" "extends")"
  extends_version="$(get_field "${skill}" "extends-version")"

  echo "Agente: ${name:-?}"
  echo "File:   ${skill}"
  echo "Version: ${version:-—}"
  if [[ -n "${extends}" ]]; then
    echo "Extends: ${extends}"
    echo "Extends-version: ${extends_version:-—}"
  fi
}

print_level() {
  local label="$1" skill_file="$2"
  local name version extends extends_version stale=""
  name="$(get_field "${skill_file}" "name")"
  version="$(get_field "${skill_file}" "version")"
  extends="$(get_field "${skill_file}" "extends")"
  extends_version="$(get_field "${skill_file}" "extends-version")"

  if [[ -n "${extends}" && -n "${extends_version}" && -n "${version:-}" ]]; then
    local parent_file parent_version cmp_result
    if parent_file="$(resolve_parent_skill "${skill_file}" 2>/dev/null)"; then
      parent_version="$(get_field "${parent_file}" "version")"
      if [[ -n "${parent_version}" ]]; then
        cmp_result="$(semver_cmp "${parent_version}" "${extends_version}")"
        if [[ "${cmp_result}" == "1" ]]; then
          stale=" STALE (padre ${extends} @ ${parent_version})"
        fi
      fi
    fi
  fi

  echo "${label}: ${name:-?} @ ${version:-?}${stale}"
  if [[ -n "${extends}" ]]; then
    echo "  extends: ${extends} @ ${extends_version:-?}"
  fi
}

cmd_chain() {
  local path skill levels=()
  skill="$(resolve_skill "$1")"
  levels+=("${skill}")

  local current="${skill}" parent
  while parent="$(resolve_parent_skill "${current}" 2>/dev/null || true)"; [[ -n "${parent}" ]]; do
    levels+=("${parent}")
    current="${parent}"
  done

  local i label
  for (( i=${#levels[@]}-1; i>=0; i-- )); do
    case $((${#levels[@]}-1-i)) in
      0) label="L0" ;;
      1) label="L1" ;;
      2) label="L2" ;;
      *) label="L$(( ${#levels[@]}-1-i ))" ;;
    esac
    print_level "${label}" "${levels[i]}"
  done
}

cmd_pending() {
  local path skill extends extends_version parent_skill changelog
  skill="$(resolve_skill "$1")"
  extends="$(get_field "${skill}" "extends")"
  extends_version="$(get_field "${skill}" "extends-version")"

  if [[ -z "${extends}" ]]; then
    echo "Nessun padre (L0) — niente pending."
    return 0
  fi
  if [[ -z "${extends_version}" ]]; then
    echo "Attenzione: extends-version mancante in ${skill}" >&2
    extends_version="0.0.0"
  fi

  parent_skill="$(resolve_parent_skill "${skill}")"
  if ! changelog="$(resolve_changelog "${parent_skill}")"; then
    echo "CHANGELOG padre non trovato per ${parent_skill}" >&2
    exit 1
  fi

  echo "Figlio:  $(get_field "${skill}" "name") @ $(get_field "${skill}" "version") (extends-version: ${extends_version})"
  echo "Padre:   $(get_field "${parent_skill}" "name") @ $(get_field "${parent_skill}" "version")"
  echo "CHANGELOG: ${changelog}"
  echo
  echo "Voci pending (> ${extends_version}):"
  echo "---"

  awk -v ev="${extends_version}" '
    function cmp_semver(a, b,    na, nb, i, max, ai, bi) {
      sub(/^v/, "", a); sub(/^v/, "", b)
      n = split(a, na, ".")
      m = split(b, nb, ".")
      max = (n > m ? n : m)
      for (i = 1; i <= max; i++) {
        ai = (i <= n ? na[i] + 0 : 0)
        bi = (i <= m ? nb[i] + 0 : 0)
        if (ai > bi) return 1
        if (ai < bi) return -1
      }
      return 0
    }
    /^## \[/ {
      ver = $2
      sub(/^\[/, "", ver)
      sub(/\].*$/, "", ver)
      if (ver == "Unreleased") { show=0; next }
      show = (cmp_semver(ver, ev) > 0)
      if (show) { print ""; print $0 }
      next
    }
    show { print }
  ' "${changelog}"

  echo "---"
}

# Risolve path competenza stessa id: L0, L1 (dominio), L2 (se path L2)
resolve_competency_levels() {
  local skill="$1"
  local id kind
  id="$(get_field "${skill}" "name")"
  kind="$(get_field "${skill}" "kind")"
  if [[ "${kind}" != "competency" ]]; then
    echo "Errore: non è una competenza (kind != competency): ${skill}" >&2
    exit 1
  fi
  if [[ -z "${id}" ]]; then
    echo "Errore: name (id) mancante in ${skill}" >&2
    exit 1
  fi

  local abs dir
  abs="$(cd "$(dirname "${skill}")" && pwd)/SKILL.md"
  dir="$(dirname "${abs}")"

  local l0="${AGENTZERO_DIR}/competencies/${id}/SKILL.md"
  local -a out=()

  # Sempre L0 se esiste
  if [[ -f "${l0}" ]]; then
    out+=("${l0}")
  fi

  # L2: .../.cursor/skills/{figlio}/competencies/{id}/
  if [[ "${dir}" == *"/.agents/skills/"*"/competencies/${id}" || "${dir}" == *"/.cursor/skills/"*"/competencies/${id}" ]]; then
    local figlio_dir l1="" parent_agent
    figlio_dir="$(cd "${dir}/../.." && pwd)"
    if [[ -f "${figlio_dir}/SKILL.md" ]]; then
      parent_agent="$(get_field "${figlio_dir}/SKILL.md" "extends")"
      for cand in \
        "${HAL_AGENTS_ROOT}/${parent_agent}/competencies/${id}/SKILL.md" \
        "${HOME}/.agents/skills/${parent_agent}/competencies/${id}/SKILL.md" \
        "${HOME}/.cursor/skills/${parent_agent}/competencies/${id}/SKILL.md"; do
        if [[ -f "${cand}" ]]; then
          l1="${cand}"
          break
        fi
      done
    fi
    if [[ -n "${l1}" ]]; then
      out+=("${l1}")
    fi
    out+=("${abs}")
    printf '%s\n' "${out[@]}"
    return 0
  fi

  # Input è L0: stampa solo L0 (già in out)
  if [[ "${abs}" == "${l0}" ]]; then
    printf '%s\n' "${out[@]}"
    return 0
  fi

  # L1 (o path sotto competencies/{id} non L2)
  if [[ "${dir}" == *"/competencies/${id}" ]]; then
    # Preferisci il bundle canonico HAL se abs arriva da un link editor
    local l1="${abs}"
    if [[ "${abs}" == "${HOME}/.cursor/skills/"* || "${abs}" == "${HOME}/.agents/skills/"* ]]; then
      local agent_name
      agent_name="$(basename "$(cd "${dir}/../.." && pwd)")"
      if [[ -f "${HAL_AGENTS_ROOT}/${agent_name}/competencies/${id}/SKILL.md" ]]; then
        l1="${HAL_AGENTS_ROOT}/${agent_name}/competencies/${id}/SKILL.md"
      fi
    fi
    if [[ "${l1}" != "${l0}" ]]; then
      out+=("${l1}")
    fi
    printf '%s\n' "${out[@]}"
    return 0
  fi

  echo "Errore: path competenza non riconosciuto: ${skill}" >&2
  exit 1
}

print_competency_level() {
  local label="$1" skill_file="$2" lower_file="${3:-}"
  local name version extends_version stale=""
  name="$(get_field "${skill_file}" "name")"
  version="$(get_field "${skill_file}" "version")"
  extends_version="$(get_field "${skill_file}" "extends-version")"

  if [[ -n "${lower_file}" && -n "${extends_version}" ]]; then
    local lower_version cmp_result
    lower_version="$(get_field "${lower_file}" "version")"
    if [[ -n "${lower_version}" ]]; then
      cmp_result="$(semver_cmp "${lower_version}" "${extends_version}")"
      if [[ "${cmp_result}" == "1" ]]; then
        stale=" STALE (livello inferiore @ ${lower_version})"
      fi
    fi
  fi

  echo "${label}: ${name:-?} @ ${version:-?}${stale}"
  if [[ -n "${extends_version}" ]]; then
    echo "  extends-version: ${extends_version}"
  fi
  echo "  file: ${skill_file}"
}

cmd_competency_chain() {
  local skill
  skill="$(resolve_skill "$1")"
  local -a levels=()
  mapfile -t levels < <(resolve_competency_levels "${skill}")

  if [[ ${#levels[@]} -eq 0 ]]; then
    echo "Nessun livello trovato" >&2
    exit 1
  fi

  local i label lower=""
  for (( i=0; i<${#levels[@]}; i++ )); do
    case "${i}" in
      0) label="L0" ;;
      1) label="L1" ;;
      2) label="L2" ;;
      *) label="L${i}" ;;
    esac
    if [[ ${i} -eq 0 ]]; then
      print_competency_level "${label}" "${levels[i]}"
    else
      print_competency_level "${label}" "${levels[i]}" "${levels[i-1]}"
    fi
  done
}

main() {
  local cmd="${1:-}"
  shift || true
  case "${cmd}" in
    show)   [[ $# -eq 1 ]] || { usage; exit 1; }; cmd_show "$1" ;;
    chain)  [[ $# -eq 1 ]] || { usage; exit 1; }; cmd_chain "$1" ;;
    competency-chain) [[ $# -eq 1 ]] || { usage; exit 1; }; cmd_competency_chain "$1" ;;
    pending) [[ $# -eq 1 ]] || { usage; exit 1; }; cmd_pending "$1" ;;
    -h|--help|help|"") usage ;;
    *) echo "Comando sconosciuto: ${cmd}" >&2; usage; exit 1 ;;
  esac
}

main "$@"

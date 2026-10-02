#!/usr/bin/env bash
# Deterministic lean prompt + compact handoff for /graph /slice /cycle /todo.
# Stack: bash (HAL meta-repo). No agentic orchestration inside this tool.
#
# Usage:
#   harness-prompt-builder.sh estimate TEXT
#   harness-prompt-builder.sh render [--max-tokens N] [--set KEY=VAL ...] -- TEMPLATE
#   harness-prompt-builder.sh handoff-write KIND [--out PATH] [--field KEY=VAL ...]
#   harness-prompt-builder.sh handoff-read [PATH|KIND]
#   harness-prompt-builder.sh self-test
#
# Token estimate ≈ ceil(chars/4). Default budget: 200 tokens.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEFAULT_MAX=200
HANDOFF_DIR="${HANDOFF_DIR:-$ROOT/.cursor/product}"

estimate_tokens() {
  local text="$1"
  local n=${#text}
  echo $(( (n + 3) / 4 ))
}

truncate_to_tokens() {
  local text="$1"
  local max="$2"
  local tok
  tok="$(estimate_tokens "$text")"
  if (( tok <= max )); then
    printf '%s' "$text"
    return 0
  fi
  local max_chars=$(( max * 4 - 3 ))
  if (( max_chars < 1 )); then
    max_chars=1
  fi
  printf '%s...' "${text:0:max_chars}"
}

subst_template() {
  local out="$1"
  shift
  local kv key val
  for kv in "$@"; do
    [[ "$kv" == *=* ]] || continue
    key="${kv%%=*}"
    val="${kv#*=}"
    # Escape sed-sensitive chars in val minimally; prefer bash replace
    out="${out//\{$key\}/$val}"
  done
  printf '%s' "$out"
}

cmd_estimate() {
  if [[ $# -lt 1 ]]; then
    echo "usage: estimate TEXT" >&2
    return 2
  fi
  estimate_tokens "$*"
}

cmd_render() {
  local max="$DEFAULT_MAX"
  local -a sets=()
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --max-tokens)
        max="${2:?}"
        shift 2
        ;;
      --set)
        sets+=("${2:?}")
        shift 2
        ;;
      --)
        shift
        break
        ;;
      *)
        break
        ;;
    esac
  done
  if [[ $# -lt 1 ]]; then
    echo "usage: render [--max-tokens N] [--set K=V ...] -- TEMPLATE" >&2
    return 2
  fi
  local tpl="$*"
  local rendered
  if ((${#sets[@]} > 0)); then
    rendered="$(subst_template "$tpl" "${sets[@]}")"
  else
    rendered="$tpl"
  fi
  truncate_to_tokens "$rendered" "$max"
  printf '\n'
}

handoff_path() {
  local kind_or_path="$1"
  case "$kind_or_path" in
    */* | *.json)
      printf '%s' "$kind_or_path"
      ;;
    graph|slice|cycle|todo)
      printf '%s/handoff-%s.json' "$HANDOFF_DIR" "$kind_or_path"
      ;;
    *)
      printf '%s/handoff-%s.json' "$HANDOFF_DIR" "$kind_or_path"
      ;;
  esac
}

json_escape() {
  local s="$1"
  s="${s//\\/\\\\}"
  s="${s//\"/\\\"}"
  s="${s//$'\n'/\\n}"
  s="${s//$'\r'/\\r}"
  s="${s//$'\t'/\\t}"
  printf '%s' "$s"
}

cmd_handoff_write() {
  local kind="${1:?kind required (graph|slice|cycle|todo)}"
  shift
  local out=""
  local -a fields=()
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --out)
        out="${2:?}"
        shift 2
        ;;
      --field)
        fields+=("${2:?}")
        shift 2
        ;;
      *)
        echo "unknown arg: $1" >&2
        return 2
        ;;
    esac
  done
  if [[ -z "$out" ]]; then
    out="$(handoff_path "$kind")"
  fi
  mkdir -p "$(dirname "$out")"
  local ts
  ts="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  local brief=""
  local acceptance=""
  local files=""
  local node_id=""
  local next=""
  local flags_y="false"
  local summary=""
  local kv key val
  for kv in "${fields[@]}"; do
    key="${kv%%=*}"
    val="${kv#*=}"
    case "$key" in
      brief) brief="$val" ;;
      acceptance) acceptance="$val" ;;
      files) files="$val" ;;
      node_id) node_id="$val" ;;
      next) next="$val" ;;
      y|auto_accept) flags_y="$val" ;;
      summary) summary="$val" ;;
    esac
  done
  if [[ -n "$brief" ]]; then
    brief="$(truncate_to_tokens "$brief" "$DEFAULT_MAX")"
  fi
  {
    printf '{\n'
    printf '  "kind": "%s",\n' "$(json_escape "$kind")"
    printf '  "cmd": "/%s",\n' "$(json_escape "$kind")"
    printf '  "ts": "%s",\n' "$ts"
    printf '  "flags": {"y": %s},\n' "$flags_y"
    printf '  "acceptance": "%s",\n' "$(json_escape "$acceptance")"
    printf '  "files": "%s",\n' "$(json_escape "$files")"
    printf '  "node_id": "%s",\n' "$(json_escape "$node_id")"
    printf '  "next": "%s",\n' "$(json_escape "$next")"
    printf '  "summary": "%s",\n' "$(json_escape "$summary")"
    printf '  "brief": "%s",\n' "$(json_escape "$brief")"
    printf '  "token_budget": %s\n' "$DEFAULT_MAX"
    printf '}\n'
  } >"$out"
  printf '%s\n' "$out"
}

cmd_handoff_read() {
  local target="${1:-}"
  if [[ -z "$target" ]]; then
    echo "usage: handoff-read PATH|KIND" >&2
    return 2
  fi
  local path
  path="$(handoff_path "$target")"
  if [[ ! -f "$path" ]]; then
    echo "FAIL: missing handoff $path" >&2
    return 1
  fi
  cat "$path"
}

cmd_self_test() {
  local fail=0
  local e
  e="$(estimate_tokens "abcd")"
  [[ "$e" == "1" ]] || { echo "FAIL estimate abcd=$e" >&2; fail=1; }

  local long
  long="$(printf 'x%.0s' {1..1000})"
  local out
  out="$(truncate_to_tokens "$long" 10)"
  local ot
  ot="$(estimate_tokens "$out")"
  if (( ot > 12 )); then
    echo "FAIL truncate ot=$ot" >&2
    fail=1
  fi
  [[ "$out" == *... ]] || { echo "FAIL truncate ellipsis" >&2; fail=1; }

  local rendered
  rendered="$(cmd_render --max-tokens 50 --set name=World -- "Hello {name}")"
  rendered="${rendered//$'\n'/}"
  [[ "$rendered" == "Hello World" ]] || { echo "FAIL render got=$rendered" >&2; fail=1; }

  local tmp
  tmp="$(mktemp -d)"
  HANDOFF_DIR="$tmp" cmd_handoff_write slice \
    --field 'acceptance=tests pass' \
    --field 'files=a.md,b.md' \
    --field 'brief=lean brief for slice' >/dev/null
  [[ -f "$tmp/handoff-slice.json" ]] || { echo "FAIL handoff write" >&2; fail=1; }
  grep -q '"kind": "slice"' "$tmp/handoff-slice.json" || { echo "FAIL handoff kind" >&2; fail=1; }
  grep -q 'tests pass' "$tmp/handoff-slice.json" || { echo "FAIL handoff acceptance" >&2; fail=1; }
  rm -rf "$tmp"

  if [[ "$fail" -ne 0 ]]; then
    echo "self-test: FAIL" >&2
    return 1
  fi
  echo "self-test: OK"
  return 0
}

main() {
  local cmd="${1:-}"
  shift || true
  case "$cmd" in
    estimate) cmd_estimate "$@" ;;
    render) cmd_render "$@" ;;
    handoff-write) cmd_handoff_write "$@" ;;
    handoff-read) cmd_handoff_read "$@" ;;
    self-test) cmd_self_test "$@" ;;
    -h|--help|help|"")
      cat <<'EOF'
harness-prompt-builder.sh — deterministic lean prompts + handoff JSON

  estimate TEXT
  render [--max-tokens N] [--set K=V ...] -- TEMPLATE
  handoff-write KIND [--out PATH] [--field K=V ...]
  handoff-read PATH|KIND
  self-test

Default token budget: 200. Handoff dir: .cursor/product/handoff-<kind>.json
Kinds: graph | slice | cycle | todo
EOF
      [[ -n "$cmd" ]] || return 2
      ;;
    *)
      echo "unknown command: $cmd" >&2
      return 2
      ;;
  esac
}

main "$@"

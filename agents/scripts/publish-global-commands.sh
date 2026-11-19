#!/usr/bin/env bash
set -euo pipefail

# Pubblica i comandi L0 HAL come skill globali di Zed (~/.agents/skills),
# dove l'agente le vede in OGNI progetto (docs zed: "Returns the global skills
# directory: ~/.agents/skills", priorità sotto le skill locali di progetto).
# Esecuzione ammessa solo da hal_gateway, come link-workspace-skills.sh.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_PHYS="$(cd "${SCRIPT_DIR}" && pwd -P)"
AGENTS_PHYS="$(cd "${SCRIPT_DIR}/.." && pwd -P)"
HAL_PHYS="$(cd "${AGENTS_PHYS}/.." && pwd -P)"

# Guardia: lo script deve risiedere fisicamente dentro hal_gateway (rifiuta
# mount di fortuna che risolverebbero altrove) e deve essere invocato dal
# workspace canonico.
CANON="/var/www/hal_gateway"
if [[ "${AGENTS_PHYS}" != "${CANON}/agents" ]]; then
  echo "Guardia HAL: script non in esecuzione dal canonico ${CANON}:" >&2
  echo "  resolved: ${AGENTS_PHYS}" >&2
  exit 1
fi

TARGET_HOME="${HOME}/.agents/skills"
COMMANDS=(version document review improve commit todo slice cycle graph)
L0_SRC="${AGENTS_PHYS}/a-agentzero/commands"
LAYA_SRC="${AGENTS_PHYS}/project-skills/laya/commands/laya.md"

gen_skill() { # $1 src comando, $2 nome skill
  local src="$1" name="$2" ver body tmp
  [[ -f "$src" ]] || { echo "MANCANTE: $src" >&2; return 1; }
  ver="$(awk 'BEGIN{fm=0} /^---$/{if(fm){exit} fm=1; next} fm && $1=="version:"{print $2; exit}' "$src")"
  ver="${ver:-1.0.0}"
  tmp="$(mktemp)"
  # Strip del frontmatter con la STESSA regex del canonico (link_zed_skill):
  # a differenza di sed, un frontmatter orfano senza chiusura viene lasciato
  # nel corpo invece di cancellare tutto il resto del file.
  python3 - "$src" "$name" "$ver" "$tmp" <<'PYSTRIP'
import re, sys
source, name, ver, target = sys.argv[1:5]
with open(source, encoding="utf-8") as f:
    content = f.read()
content = re.sub(r'^---\s*\n.*?\n---\s*\n', '', content, count=1, flags=re.DOTALL)
with open(target, "w", encoding="utf-8") as f:
    # ATTENZIONE: lo scalar `description` non deve contenere la sequenza ": "
    # (non quotato = YAML invalido: "mapping values are not allowed here").
    f.write(
        f"---\nname: {name}\nversion: {ver}\n"
        f"description: Command {name} for HAL workspace (global, published by hal_gateway).\n---\n\n"
        + content
    )
PYSTRIP
  printf '%s' "$tmp"
}

mkdir -p "$TARGET_HOME"
PUBLISHED=()
for cmd in "${COMMANDS[@]}"; do
  tmp="$(gen_skill "${L0_SRC}/${cmd}.md" "$cmd")"
  dest="${TARGET_HOME}/${cmd}"
  mkdir -p "$dest"
  if ! cmp -s "$tmp" "${dest}/SKILL.md"; then
    mv "$tmp" "${dest}/SKILL.md"
    echo "published: ${cmd}"
  else
    rm -f "$tmp"
    echo "unchanged: ${cmd}"
  fi
  PUBLISHED+=("$cmd")
done
if [[ -f "$LAYA_SRC" ]]; then
  tmp="$(gen_skill "$LAYA_SRC" "laya-cmd")"
  mkdir -p "${TARGET_HOME}/laya-cmd"
  if ! cmp -s "$tmp" "${TARGET_HOME}/laya-cmd/SKILL.md"; then
    mv "$tmp" "${TARGET_HOME}/laya-cmd/SKILL.md"
    echo "published: laya-cmd"
  else
    rm -f "$tmp"
    echo "unchanged: laya-cmd"
  fi
  PUBLISHED+=("laya-cmd")
fi

# Prune: rimuove dai globali i comandi HAL non più pubblicati (solo quelli
# con marker nel description, per non toccare skill altrui).
for d in "$TARGET_HOME"/*/; do
  n="$(basename "$d")"
  if [[ -f "${d}SKILL.md" ]] && grep -q "published by hal_gateway" "${d}SKILL.md"; then
    keep=0
    for p in "${PUBLISHED[@]}"; do [[ "$p" = "$n" ]] && keep=1; done
    if [[ "$keep" = "0" ]]; then rm -r "$d"; echo "pruned: $n"; fi
  fi
done
echo "target: $TARGET_HOME (${#PUBLISHED[@]} comandi)"

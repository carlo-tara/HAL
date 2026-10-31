#!/usr/bin/env bash
# RED contract (RGR) — naming skill L2 + copertura gate.
# Origine: sessione 2026-10-31, 4 L2 scaffoldate con underscore (harness-hal_mcp_docs|_mcp_tools|
# _translate|_tts) scartate in silenzio dal loader Zed; check-frontmatter-all.sh in vacuous pass.
# Verifica presenza delle regole promosse nella catena:
#   (1) L0 agents/a-agentzero/references/extension-scaffold.md: contratto naming kebab-case per L2;
#   (2) L1 agents/a-harness/SKILL.md: policy «Copertura gate (policy L1)».
# Enforcement dei nomi veri: agents/scripts/check-frontmatter-all.sh (name, regex, match directory).
# Exit 0 = GREEN.
set -euo pipefail
HAL="$(cd "$(dirname "$0")/../.." && pwd)"
fail=0
grep -q "kebab-case" "$HAL/agents/a-agentzero/references/extension-scaffold.md" \
  || { echo "FAIL: manca la regola naming (kebab-case) in L0 extension-scaffold.md" >&2; fail=1; }
grep -q "Copertura gate (policy L1)" "$HAL/agents/a-harness/SKILL.md" \
  || { echo "FAIL: manca la policy «Copertura gate» in a-harness" >&2; fail=1; }
if [[ "$fail" -ne 0 ]]; then
  echo "check-harness-skill-naming: RED" >&2
  exit 1
fi
echo "check-harness-skill-naming: GREEN"

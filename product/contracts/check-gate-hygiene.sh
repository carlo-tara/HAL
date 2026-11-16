#!/usr/bin/env bash
# RED contract (RGR) — «Costo del gate» + «prova del verde su stdout=file» in L1 a-harness.
# Origine: sessione brainbeez 2026-11-16, catena S131-bis/S132 (promozione /sync < da
# L2 harness-brainbeez 1.5.33). Lezioni misurate: uv run risincronizza nei container
# effimeri (11,0s→2,6s con UV_NO_SYNC); fixture DB migrate×595 test dominava la suite
# (5'15"→76" con template+clone per worker); i runner sono TTY-adaptive (-qq sopprime
# «N passed», reporter dot senza totali su pipe → spec); exit reali solo da file .ec.
# Copertura (policy L1 «Copertura gate»): i tre file target DEVONO esistere e ogni
# regola ha la sua asserzione; una sola assenza = RED, mai vacuous pass.
# Exit 0 = GREEN.
set -euo pipefail
HAL="$(cd "$(dirname "$0")/../.." && pwd)"
SKILL="$HAL/agents/a-harness/SKILL.md"
EXT="$HAL/agents/a-harness/references/harness-extended.md"
TMPL="$HAL/agents/a-harness/references/makefile-template.mk"
fail=0
checked=0
for f in "$SKILL" "$EXT" "$TMPL"; do
  if [[ ! -f "$f" ]]; then
    echo "FAIL: target mancante: $f (il gate non può girare vacuo)" >&2
    exit 1
  fi
done
chk() { # chk <file> <stringa-fissa> <descrizione>
  checked=$((checked + 1))
  grep -qF -- "$2" "$1" || { echo "FAIL: manca «$3» in ${1#"$HAL/"}" >&2; fail=1; }
}
chk "$SKILL" "Costo del gate (policy L1)" "policy Costo del gate"
chk "$SKILL" "stdout=file" "corollario Verità del gate (stdout=file)"
chk "$EXT" "Prova del verde su stdout non-TTY" "§Quiet punto 3 (TTY-adaptive)"
chk "$EXT" "template migrato una volta" "§Quiet punto 4 (fixture template+clone)"
chk "$TMPL" "container persistente" "Note: sync esplicito sul contenitore persistente"
chk "$TMPL" "lock per lane" "Note: lane parallele con exit .ec"
chk "$TMPL" "lockfile" "Note: build pinnata al lockfile"
chk "$TMPL" "test-file" "Note: loop TDD mirato senza runner parallelo"
echo "check-gate-hygiene: asserzioni valutate: $checked (coverage ok)"
if [[ "$fail" -ne 0 ]]; then
  echo "check-gate-hygiene: RED" >&2
  exit 1
fi
echo "check-gate-hygiene: GREEN"

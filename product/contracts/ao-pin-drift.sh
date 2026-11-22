#!/usr/bin/env bash
# ao-pin-drift.sh — rileva il drift del pin di auto-ontology-mcp SENZA bumpare (AO-2.1 passo 1).
#
# Perché: upstream non pubblica tag né release (CONTRIBUTING reg. 5 — le release sono i commit
# che bump-ano `version` in pyproject.toml). Guardare solo `git log PIN..origin/main` fa credere
# che ogni commit sia una release: al 2026-11-22 i 3 commit oltre il pin (0fb5ecf) erano fix
# non rilasciati e `version` era ancora 0.6.1 → bumpare avrebbe violato il rituale.
# Questo script distingue i tre casi e non scrive nulla nel workspace HAL (solo `git fetch`
# nel clone, che tocca unicamente il suo .git).
#
# Uso:
#   ao-pin-drift.sh [--clone <dir>] [--pin-file <file>] [--strict]
#     --clone     clone locale (default $AO_CLONE o /home/carlo/auto-ontology-mcp)
#     --pin-file  pin file HAL (default <repo>/agents/a-knowledge/references/auto-ontology-source.md)
#     --strict    exit 2 se c'è una RELEASE disponibile (per agganciarlo a un gate)
#
# Verdict (stdout):
#   IN-SYNC             clone sul pin, origin/main non è avanti
#   DRIFT-NO-RELEASE    commit oltre il pin ma `version` invariata → il pin RESTA valido
#   RELEASE-AVAILABLE   `version` cambiata a monte → rituale AO-2.1 dovuto (7 passi)
# Exit: 0 = controllo eseguito; 2 = RELEASE-AVAILABLE con --strict; 1 = errore (clone/pin/rete).
set -euo pipefail

HAL="$(cd "$(dirname "$0")/../.." && pwd)"
CLONE="${AO_CLONE:-/home/carlo/auto-ontology-mcp}"
PIN_FILE="$HAL/agents/a-knowledge/references/auto-ontology-source.md"
STRICT=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --clone) [[ $# -ge 2 ]] || { echo "ao-pin-drift: --clone richiede un valore" >&2; exit 1; }
             CLONE="$2"; shift 2 ;;
    --pin-file) [[ $# -ge 2 ]] || { echo "ao-pin-drift: --pin-file richiede un valore" >&2; exit 1; }
             PIN_FILE="$2"; shift 2 ;;
    --strict) STRICT=1; shift ;;
    -h|--help) sed -n '2,22p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "ao-pin-drift: opzione sconosciuta '$1'" >&2; exit 1 ;;
  esac
done

die() { echo "ao-pin-drift: $*" >&2; exit 1; }

[[ -d "$CLONE/.git" ]] || die "clone non trovato o non git: $CLONE (usa --clone o AO_CLONE)"
[[ -f "$PIN_FILE" ]] || die "pin file non trovato: $PIN_FILE"

# Lo SHA del pin vive nel blocco PIN:START/END, riga "| Commit | `<40hex>` (`<short>`) |".
PIN="$(awk -F'`' '/^\| Commit \|/ { print $2; exit }' "$PIN_FILE")"
[[ -n "$PIN" ]] || die "nessuna riga '| Commit | \`sha\`' trovata in $PIN_FILE"
git -C "$CLONE" cat-file -e "${PIN}^{commit}" 2>/dev/null \
  || die "SHA del pin $PIN assente nel clone: git -C $CLONE fetch --tags --prune"

# Rete non interattiva e a tempo: niente prompt di credenziali, niente hang.
if command -v timeout >/dev/null 2>&1; then
  GIT_TERMINAL_PROMPT=0 timeout 90 git -C "$CLONE" fetch --quiet --prune origin \
    || die "fetch origin fallito (rete/permessi?) — riprova o controlla il remote"
else
  GIT_TERMINAL_PROMPT=0 git -C "$CLONE" fetch --quiet --prune origin \
    || die "fetch origin fallito (rete/permessi?) — riprova o controlla il remote"
fi

UPSTREAM="$(git -C "$CLONE" symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null || echo origin/main)"
git -C "$CLONE" rev-parse --verify --quiet "$UPSTREAM" >/dev/null \
  || die "upstream $UPSTREAM non risolto nel clone"

version_at() {  # $1 = rev
  git -C "$CLONE" show "$1:pyproject.toml" 2>/dev/null \
    | awk -F'"' '/^version[[:space:]]*=/ { print $2; exit }'
}

PIN_VERSION="$(version_at "$PIN")"
UP_VERSION="$(version_at "$UPSTREAM")"
[[ -n "$PIN_VERSION" ]] || die "version non letta al pin $PIN (pyproject.toml mancante?)"
[[ -n "$UP_VERSION" ]] || die "version non letta su $UPSTREAM"

BEHIND="$(git -C "$CLONE" rev-list --count "${PIN}..${UPSTREAM}")"
LOCAL_DRIFT="$(git -C "$CLONE" rev-list --count "HEAD..${UPSTREAM}" 2>/dev/null || echo '?')"

echo "ao-pin-drift: clone=$CLONE upstream=$UPSTREAM"
echo "  pin=${PIN:0:7} version=$PIN_VERSION | upstream version=$UP_VERSION | commit oltre il pin=$BEHIND (clone dietro di $LOCAL_DRIFT)"

if [[ "$BEHIND" -eq 0 ]]; then
  echo "  verdict: IN-SYNC — pin e $UPSTREAM coincidono"
  exit 0
fi

echo "  commit oltre il pin (i bump di pyproject.toml SONO le release):"
git -C "$CLONE" --no-pager log --format='    %h %s' "${PIN}..${UPSTREAM}" | head -20
REL_COMMITS="$(git -C "$CLONE" --no-pager log --format='%h' "${PIN}..${UPSTREAM}" -- pyproject.toml | head -5)"
if [[ -n "$REL_COMMITS" ]]; then
  echo "  commit che toccano pyproject.toml: $(echo "$REL_COMMITS" | tr '\n' ' ')"
fi

if [[ "$PIN_VERSION" == "$UP_VERSION" ]]; then
  echo "  verdict: DRIFT-NO-RELEASE — version invariata ($UP_VERSION): nessun bump upstream, il pin resta valido."
  echo "  nota: i fix a monte non sono rilasciati; adozione anticipata = decisione esplicita, non rituale."
  exit 0
fi

echo "  verdict: RELEASE-AVAILABLE — version $PIN_VERSION → $UP_VERSION: rituale AO-2.1 dovuto (7 passi)."
echo "  passi: diff --stat + 3 invarianti CONTRIBUTING → snapshot (export/export-wiki/cp -a store) →"
echo "         rehearsal AUTO_ONTOLOGY_HOME=/tmp/ao-dry + uv run pytest → pull --ff-only + uv sync →"
echo "         re-misura KPI-1 → nuova riga PIN → revert allo SHA precedente se regressione."
if [[ "$STRICT" -eq 1 ]]; then
  exit 2
fi
exit 0

#!/usr/bin/env bash
# Clone o aggiorna vendor/agent-skills-google-ads (sparse: skills/google-ads) e aggiorna il pin
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
VENDOR_DIR="${REPO_ROOT}/vendor/agent-skills-google-ads"
PIN_FILE="${REPO_ROOT}/a-seozoom/references/google-ads-agent-skills-source.md"
REMOTE_URL="https://github.com/itallstartedwithaidea/agent-skills.git"
BRANCH="${GOOGLE_ADS_AGENT_SKILLS_BRANCH:-main}"

mkdir -p "${REPO_ROOT}/vendor"

PREV_SHA=""
if [[ -d "${VENDOR_DIR}/.git" ]]; then
  PREV_SHA="$(git -C "${VENDOR_DIR}" rev-parse HEAD)"
  echo "Updating existing clone at ${VENDOR_DIR}…"
  git -C "${VENDOR_DIR}" fetch --tags --prune origin
  git -C "${VENDOR_DIR}" checkout "${BRANCH}"
  git -C "${VENDOR_DIR}" pull --ff-only origin "${BRANCH}"
else
  echo "Cloning ${REMOTE_URL} → ${VENDOR_DIR} (sparse skills/google-ads)…"
  git clone --filter=blob:none --sparse --branch "${BRANCH}" --single-branch \
    "${REMOTE_URL}" "${VENDOR_DIR}"
  git -C "${VENDOR_DIR}" sparse-checkout set skills/google-ads
fi

# Ensure sparse paths after update
git -C "${VENDOR_DIR}" sparse-checkout set skills/google-ads

NEW_SHA="$(git -C "${VENDOR_DIR}" rev-parse HEAD)"
NEW_DATE="$(git -C "${VENDOR_DIR}" log -1 --format='%ci')"
NEW_SUBJECT="$(git -C "${VENDOR_DIR}" log -1 --format='%s')"
SHORT_SHA="$(git -C "${VENDOR_DIR}" rev-parse --short HEAD)"
UPDATED_AT="$(date '+%Y-%m-%d %H:%M %z')"

CHANGED_SKILLS=""
if [[ -n "${PREV_SHA}" && "${PREV_SHA}" != "${NEW_SHA}" ]]; then
  CHANGED_SKILLS="$(git -C "${VENDOR_DIR}" diff --name-only "${PREV_SHA}..${NEW_SHA}" -- skills/google-ads/ \
    | sed -n 's|^skills/google-ads/\([^/]*\)/.*|\1|p' | sort -u | paste -sd, -)"
elif [[ -z "${PREV_SHA}" ]]; then
  CHANGED_SKILLS="(clone iniziale)"
fi

if [[ ! -f "${PIN_FILE}" ]]; then
  echo "ERROR: manca ${PIN_FILE}" >&2
  exit 1
fi

TMP_PIN="$(mktemp)"
awk -v sha="${NEW_SHA}" -v short="${SHORT_SHA}" -v cdate="${NEW_DATE}" -v subject="${NEW_SUBJECT}" -v updated="${UPDATED_AT}" '
  BEGIN { in_pin=0 }
  /^<!-- PIN:START -->$/ {
    print
    print "| Campo | Valore |"
    print "|-------|--------|"
    print "| Commit | `" sha "` (`" short "`) |"
    print "| Data commit | " cdate " |"
    print "| Subject | " subject " |"
    print "| Aggiornato il | " updated " |"
    in_pin=1
    next
  }
  /^<!-- PIN:END -->$/ { in_pin=0; print; next }
  in_pin==1 { next }
  { print }
' "${PIN_FILE}" > "${TMP_PIN}"
mv "${TMP_PIN}" "${PIN_FILE}"

echo
echo "=== agent-skills google-ads aggiornato ==="
echo "  path:    ${VENDOR_DIR}"
echo "  commit:  ${SHORT_SHA} (${NEW_SHA})"
echo "  date:    ${NEW_DATE}"
if [[ -n "${PREV_SHA}" ]]; then
  if [[ "${PREV_SHA}" == "${NEW_SHA}" ]]; then
    echo "  delta:   già all'ultimo commit su ${BRANCH}"
  else
    echo "  prev:    ${PREV_SHA:0:7} → ${SHORT_SHA}"
    echo "  skills:  ${CHANGED_SKILLS:-nessun path skills/google-ads/}"
  fi
else
  echo "  delta:   clone nuovo"
fi
echo "  pin:     ${PIN_FILE}"
echo
echo "Prossimi step (manuali / agente):"
echo "  1. Confronta skills cambiate col mapping in google-ads-agent-skills-source.md"
echo "  2. Se upstream rilevante è cambiato: rivedi competenza google-ads (non copia grezza)"
echo "  3. Bump version competenza + CHANGELOG se aggiorni canoni"
echo "  4. /sync ! per deploy a-seozoom se hai modificato skill"

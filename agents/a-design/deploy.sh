#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HAL_AGENTS_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
exec bash "${HAL_AGENTS_ROOT}/deploy-all.sh"

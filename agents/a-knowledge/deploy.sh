#!/usr/bin/env bash
set -euo pipefail

AGENT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
bash "${AGENT_DIR}/../scripts/link-workspace-skills.sh"

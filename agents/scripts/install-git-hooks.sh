#!/usr/bin/env bash
# Install local git pre-commit → make pre-commit
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HOOK="$ROOT/.git/hooks/pre-commit"
mkdir -p "$ROOT/.git/hooks"
cat >"$HOOK" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"
echo ">>> git pre-commit: make pre-commit"
make pre-commit
EOF
chmod +x "$HOOK"
echo "Installed $HOOK"
echo "To bypass once: git commit --no-verify (not recommended)"

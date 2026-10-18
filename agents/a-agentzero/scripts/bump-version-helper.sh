#!/usr/bin/env bash
set -euo pipefail

bump() {
  local level="$1"
  local file="$2"

  if [[ ! -f "$file" ]]; then
    echo "File not found: $file" >&2
    return 1
  fi

  local current_version
  current_version=$(grep -m1 '^version:' "$file" | awk '{print $2}' || true)
  if [[ -z "$current_version" ]]; then
    echo "No version found in $file" >&2
    return 1
  fi

  IFS='.' read -r major minor patch <<< "$current_version"

  case "$level" in
    patch) patch=$((patch + 1)) ;;
    minor) minor=$((minor + 1)); patch=0 ;;
    major) major=$((major + 1)); minor=0; patch=0 ;;
    *) echo "Invalid bump level: $level" >&2; return 1 ;;
  esac

  local new_version="$major.$minor.$patch"

  # Replace in file using sed
  sed -i "s/^version: $current_version/version: $new_version/" "$file"
  echo "Bumped $file: $current_version -> $new_version"

  # Attempt changelog bump
  local dir
  dir=$(dirname "$file")
  local changelog="$dir/CHANGELOG.md"
  if [[ -f "$changelog" ]]; then
    echo "Notice: update $changelog manually with '## [$new_version]'"
  fi
}

bump "$1" "$2"

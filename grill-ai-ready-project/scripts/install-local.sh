#!/usr/bin/env bash
set -euo pipefail

SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET_DIR="${HOME}/.claude/skills/grill-ai-ready-project"

mkdir -p "${HOME}/.claude/skills"
rm -rf "${TARGET_DIR}"
cp -R "${SOURCE_DIR}" "${TARGET_DIR}"

echo "Installed grill-ai-ready-project to ${TARGET_DIR}"
echo "Try: /grill-ai-ready-project --audit-existing"

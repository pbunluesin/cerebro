#!/usr/bin/env bash
# set-codex-model.sh
# Switch the top-level `model` (and optionally `model_reasoning_effort`)
# in ~/.codex/config.toml — idempotent, timestamped backup, before/after diff.
#
# Usage:
#   ./set-codex-model.sh                       # default: gpt-5.6-sol, keep effort
#   ./set-codex-model.sh gpt-5.6-terra         # set model only
#   ./set-codex-model.sh gpt-5.6-sol xhigh     # set model + reasoning effort
#   ./set-codex-model.sh --revert              # restore latest .bak.* backup
#
# Override config path: CODEX_CONFIG=/path/to/config.toml ./set-codex-model.sh
set -euo pipefail

CONFIG="${CODEX_CONFIG:-$HOME/.codex/config.toml}"

# ---------- revert mode ----------
if [[ "${1:-}" == "--revert" ]]; then
  LATEST_BAK=$(ls -1t "${CONFIG}".bak.* 2>/dev/null | head -1 || true)
  [[ -n "$LATEST_BAK" ]] || { echo "ERROR: no backup found (${CONFIG}.bak.*)"; exit 1; }
  cp -p "$CONFIG" "${CONFIG}.pre-revert.$(date +%Y%m%d_%H%M%S)"   # keep current state too (reversible)
  cp -p "$LATEST_BAK" "$CONFIG"
  echo "Reverted from: $LATEST_BAK"
  grep -E '^(model|model_reasoning_effort) = ' "$CONFIG"
  exit 0
fi

NEW_MODEL="${1:-gpt-5.6-sol}"
NEW_EFFORT="${2:-}"   # optional: low | medium | high | xhigh (empty = keep existing)

[[ -f "$CONFIG" ]] || { echo "ERROR: $CONFIG not found"; exit 1; }

CURRENT_MODEL=$(sed -nE 's/^model = "(.*)"[[:space:]]*$/\1/p' "$CONFIG" | head -1)
CURRENT_EFFORT=$(sed -nE 's/^model_reasoning_effort = "(.*)"[[:space:]]*$/\1/p' "$CONFIG" | head -1)

echo "== BEFORE =="
echo "model                  : ${CURRENT_MODEL:-<not set>}"
echo "model_reasoning_effort : ${CURRENT_EFFORT:-<not set>}"
echo

# ---------- idempotency check ----------
if [[ "$CURRENT_MODEL" == "$NEW_MODEL" ]] && { [[ -z "$NEW_EFFORT" ]] || [[ "$CURRENT_EFFORT" == "$NEW_EFFORT" ]]; }; then
  echo "Already set to target values — no changes made."
  exit 0
fi

# ---------- timestamped backup (never overwrite an existing backup) ----------
TS=$(date +%Y%m%d_%H%M%S)
BACKUP="${CONFIG}.bak.${TS}"
n=1
while [[ -e "$BACKUP" ]]; do
  BACKUP="${CONFIG}.bak.${TS}.${n}"
  n=$((n + 1))
done
cp -p "$CONFIG" "$BACKUP"
echo "Backup created: $BACKUP"
echo

# ---------- edit (temp file in same dir, then atomic mv) ----------
TMP="${CONFIG}.tmp.$$"
trap 'rm -f "$TMP"' EXIT

if [[ -n "$NEW_EFFORT" ]]; then
  sed -E \
    -e "s|^model = \".*\"[[:space:]]*$|model = \"${NEW_MODEL}\"|" \
    -e "s|^model_reasoning_effort = \".*\"[[:space:]]*$|model_reasoning_effort = \"${NEW_EFFORT}\"|" \
    "$CONFIG" > "$TMP"
else
  sed -E \
    -e "s|^model = \".*\"[[:space:]]*$|model = \"${NEW_MODEL}\"|" \
    "$CONFIG" > "$TMP"
fi

mv "$TMP" "$CONFIG"
trap - EXIT

# ---------- after verification ----------
echo "== AFTER =="
grep -E '^(model|model_reasoning_effort) = ' "$CONFIG"
echo
echo "== DIFF (backup -> current) =="
diff "$BACKUP" "$CONFIG" || true
echo
echo "Done. Revert anytime with: $0 --revert"

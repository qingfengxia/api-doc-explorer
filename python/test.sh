#!/usr/bin/env bash
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== Python: test ==="

EXPLORER="python_api_explorer.py"
PASS=0
FAIL=0

check() {
  local name="$1"
  local output="$2"
  local pattern="$3"
  if [[ "$output" == *"$pattern"* ]]; then
    echo "    PASS: $name"
    PASS=$((PASS + 1))
  else
    echo "    FAIL: $name (expected '$pattern')"
    echo "    Output: $(echo "$output" | head -5)"
    FAIL=$((FAIL + 1))
  fi
}

echo "  Test 1: script loads and shows help"
OUTPUT=$(python3 "$EXPLORER" --help 2>&1 || true)
check "help" "$OUTPUT" "usage:" 

echo ""
if [ $FAIL -eq 0 ]; then
  echo "=== Python: all $PASS tests passed ==="
else
  echo "=== Python: $FAIL tests FAILED ==="
  exit 1
fi

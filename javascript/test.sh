#!/usr/bin/env bash
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== JavaScript: test ==="

EXPLORER="javascript-api-explorer.js"
DOCS="example/docs"
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
    echo "    Output: $(echo "$output" | head -3)"
    FAIL=$((FAIL + 1))
  fi
}

echo "  Test 1: explicit --doc-path UserService.findUser"
OUTPUT=$(node "$EXPLORER" --doc-path "$DOCS" UserService.findUser 2>&1 || true)
check "findUser method" "$OUTPUT" "findUser"

echo "  Test 2: class query ProductService (with --doc-path)"
OUTPUT=$(node "$EXPLORER" --doc-path "$DOCS" ProductService 2>&1 || true)
check "ProductService" "$OUTPUT" "ProductService"

echo "  Test 3: non-existent symbol"
OUTPUT=$(node "$EXPLORER" --doc-path "$DOCS" NonExistentSymbol 2>&1 || true)
check "not-found" "$OUTPUT" "No API found"

echo ""
if [ $FAIL -eq 0 ]; then
  echo "=== JavaScript: all $PASS tests passed ==="
else
  echo "=== JavaScript: $FAIL tests FAILED ==="
  exit 1
fi

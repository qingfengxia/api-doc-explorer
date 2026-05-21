#!/usr/bin/env bash
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== Rust: test ==="

EXPLORER="rust-api-explorer.py"
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
    echo "    Output: $(echo "$output" | head -5)"
    FAIL=$((FAIL + 1))
  fi
}

echo "  Test 1: struct method query LogEntry.new"
OUTPUT=$(python3 "$EXPLORER" --doc-path "$DOCS" LogEntry.new 2>&1 || true)
check "LogEntry.new method" "$OUTPUT" "message: String"

echo "  Test 2: class query LoggerService (with --doc-path)"
OUTPUT=$(python3 "$EXPLORER" --doc-path "$DOCS" LoggerService 2>&1 || true)
check "LoggerService" "$OUTPUT" "LoggerService"

echo "  Test 3: function query add"
OUTPUT=$(python3 "$EXPLORER" --doc-path "$DOCS" add 2>&1 || true)
check "add function" "$OUTPUT" "fn add"

echo "  Test 4: non-existent symbol"
OUTPUT=$(python3 "$EXPLORER" --doc-path "$DOCS" NonExistentSymbol 2>&1 || true)
check "not-found" "$OUTPUT" "No API found"

echo ""
if [ $FAIL -eq 0 ]; then
  echo "=== Rust: all $PASS tests passed ==="
else
  echo "=== Rust: $FAIL tests FAILED ==="
  exit 1
fi

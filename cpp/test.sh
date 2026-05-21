#!/usr/bin/env bash
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== C++: test ==="

EXPLORER="cpp-api-explorer.py"
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

# Check docs exist
if [ ! -f "$DOCS/index.xml" ]; then
  echo "SKIP: No docs found. Run build.sh first."
  exit 0
fi

echo "  Test 1: namespace example"
OUTPUT=$(python3 "$EXPLORER" --doc-path "$DOCS" example 2>&1 || true)
check "example namespace" "$OUTPUT" "example"

echo "  Test 2: class query UserService"
OUTPUT=$(python3 "$EXPLORER" --doc-path "$DOCS" UserService 2>&1 || true)
check "UserService" "$OUTPUT" "findUser"

echo "  Test 3: method query UserService::findUser"
OUTPUT=$(python3 "$EXPLORER" --doc-path "$DOCS" example::UserService::findUser 2>&1 || true)
check "findUser method" "$OUTPUT" "findUser"

echo "  Test 4: struct query User"
OUTPUT=$(python3 "$EXPLORER" --doc-path "$DOCS" User 2>&1 || true)
check "User struct" "$OUTPUT" "User"

echo "  Test 5: enum query LogLevel"
OUTPUT=$(python3 "$EXPLORER" --doc-path "$DOCS" LogLevel 2>&1 || true)
check "LogLevel enum" "$OUTPUT" "LogLevel"

echo "  Test 6: non-existent symbol"
OUTPUT=$(python3 "$EXPLORER" --doc-path "$DOCS" NonExistentSymbol 2>&1 || true)
check "not-found" "$OUTPUT" "No API found"

echo ""
if [ $FAIL -eq 0 ]; then
  echo "=== C++: all $PASS tests passed ==="
else
  echo "=== C++: $FAIL tests FAILED ==="
  exit 1
fi

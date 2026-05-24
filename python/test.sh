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

echo "  Test 2: module-level query example.UserService"
OUTPUT=$(python3 "$EXPLORER" example.UserService 2>&1 || true)
check "UserService class" "$OUTPUT" "UserService"
check "UserService kind" "$OUTPUT" "Kind:"
check "UserService qualified" "$OUTPUT" "example.user_service.UserService"

echo "  Test 3: method query example.UserService.find_user"
OUTPUT=$(python3 "$EXPLORER" example.UserService.find_user 2>&1 || true)
check "find_user method" "$OUTPUT" "find_user"
check "find_user kind" "$OUTPUT" "method"
check "find_user qualified" "$OUTPUT" "example.user_service.UserService.find_user"

echo "  Test 4: enum query example.LogLevel"
OUTPUT=$(python3 "$EXPLORER" example.LogLevel 2>&1 || true)
check "LogLevel enum" "$OUTPUT" "LogLevel"
check "LogLevel kind" "$OUTPUT" "enum"

echo "  Test 5: non-existent module"
OUTPUT=$(python3 "$EXPLORER" nonexistent.module 2>&1 || true)
check "not-found" "$OUTPUT" "Error"

echo "  Test 6: --output-json flag"
OUTPUT=$(python3 "$EXPLORER" example.UserService.find_user --output-json 2>&1 || true)
check "json output" "$OUTPUT" '"qualifiedName"'
check "json kind" "$OUTPUT" '"kind"'
check "json method" "$OUTPUT" '"method"'

echo "  Test 7: module-level query with human-readable output"
OUTPUT=$(python3 "$EXPLORER" example 2>&1 || true)
check "module found" "$OUTPUT" "Found:"
check "module children" "$OUTPUT" "Children"

echo ""
if [ $FAIL -eq 0 ]; then
  echo "=== Python: all $PASS tests passed ==="
else
  echo "=== Python: $FAIL tests FAILED ==="
  exit 1
fi

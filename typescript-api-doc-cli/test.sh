#!/usr/bin/env bash
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== TypeScript: test ==="

EXPLORER="typescript-api-explorer.js"
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

echo "  Test 2: class-level query LoggerService"
OUTPUT=$(node "$EXPLORER" --doc-path "$DOCS" LoggerService 2>&1 || true)
check "LoggerService" "$OUTPUT" "LoggerService"

echo "  Test 3: non-existent symbol"
OUTPUT=$(node "$EXPLORER" --doc-path "$DOCS" NonExistentSymbol 2>&1 || true)
check "not-found" "$OUTPUT" "No API found"

echo "  Test 4: .d.ts fallback - class query"
OUTPUT=$(cd example/dist-dts && node ../../typescript-api-explorer.js UserService 2>&1 || true)
check "dts UserService" "$OUTPUT" "UserService"
check "dts Kind" "$OUTPUT" "Class"
check "dts method" "$OUTPUT" "findUser"

echo "  Test 5: .d.ts fallback - method query"
OUTPUT=$(cd example/dist-dts && node ../../typescript-api-explorer.js UserService.findUser 2>&1 || true)
check "dts findUser" "$OUTPUT" "findUser"
check "dts method kind" "$OUTPUT" "Method"
check "dts param" "$OUTPUT" "id"

echo "  Test 6: .d.ts fallback - enum query"
OUTPUT=$(cd example/dist-dts && node ../../typescript-api-explorer.js LogLevel 2>&1 || true)
check "dts LogLevel" "$OUTPUT" "LogLevel"

echo ""
if [ $FAIL -eq 0 ]; then
  echo "=== TypeScript: all $PASS tests passed ==="
else
  echo "=== TypeScript: $FAIL tests FAILED ==="
  exit 1
fi

#!/usr/bin/env bash
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== Java: test ==="

EXPLORER="JavaApiExplorer"
DOCS_CP="example/target/classes"
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

# Check compiled explorer
if [ ! -f "JavaApiExplorer.class" ]; then
  echo "  Compiling JavaApiExplorer..."
  javac --release 17 -d . -encoding UTF-8 JavaApiExplorer.java 2>&1 || true
fi

# Check docs exist
if [ ! -f "$DOCS_CP/api-doc.json" ]; then
  echo "SKIP: No docs found. Run build.sh first."
  exit 0
fi

echo "  Test 1: class query UserService"
OUTPUT=$(java -cp ".:$DOCS_CP" "$EXPLORER" UserService 2>&1 || true)
check "UserService class" "$OUTPUT" "UserService"

echo "  Test 2: enum query ProductCategory"
OUTPUT=$(java -cp ".:$DOCS_CP" "$EXPLORER" ProductCategory 2>&1 || true)
check "ProductCategory enum" "$OUTPUT" "ProductCategory"

echo "  Test 3: logger service"
OUTPUT=$(java -cp ".:$DOCS_CP" "$EXPLORER" LoggerService 2>&1 || true)
check "LoggerService" "$OUTPUT" "LoggerService"

echo ""
if [ $FAIL -eq 0 ]; then
  echo "=== Java: all $PASS tests passed ==="
else
  echo "=== Java: $FAIL tests FAILED ==="
  exit 1
fi

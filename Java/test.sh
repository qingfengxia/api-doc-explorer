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

echo "  Test 1: JSON doc mode - class query UserService"
OUTPUT=$(java -cp ".:$DOCS_CP" "$EXPLORER" UserService 2>&1 || true)
check "UserService class" "$OUTPUT" "UserService"

echo "  Test 2: JSON doc mode - enum query ProductCategory"
OUTPUT=$(java -cp ".:$DOCS_CP" "$EXPLORER" ProductCategory 2>&1 || true)
check "ProductCategory enum" "$OUTPUT" "ProductCategory"

echo "  Test 3: JSON doc mode - logger service"
OUTPUT=$(java -cp ".:$DOCS_CP" "$EXPLORER" LoggerService 2>&1 || true)
check "LoggerService" "$OUTPUT" "LoggerService"

echo "  Test 4: JSON mode - full qualified class"
OUTPUT=$(java -cp ".:$DOCS_CP" "$EXPLORER" com.example.service.UserService 2>&1 || true)
check "UserService FQ" "$OUTPUT" "UserService"
check "UserService methods" "$OUTPUT" "findUser"

echo "  Test 5: JSON mode - full qualified method"
OUTPUT=$(java -cp ".:$DOCS_CP" "$EXPLORER" com.example.service.UserService.findUser 2>&1 || true)
check "findUser FQ" "$OUTPUT" "findUser"

echo "  Test 6: Reflection mode - class query"
OUTPUT=$(java -cp ".:$DOCS_CP" "$EXPLORER" --reflect com.example.service.UserService 2>&1 || true)
check "reflect UserService" "$OUTPUT" "UserService"
check "reflect Kind" "$OUTPUT" "class"
check "reflect methods" "$OUTPUT" "findUser"

echo "  Test 7: Reflection mode - method query"
OUTPUT=$(java -cp ".:$DOCS_CP" "$EXPLORER" --reflect com.example.service.UserService.findUser 2>&1 || true)
check "reflect findUser" "$OUTPUT" "findUser"
check "reflect method kind" "$OUTPUT" "method"
check "reflect returns" "$OUTPUT" "Returns"

echo "  Test 8: Reflection mode - enum query"
OUTPUT=$(java -cp ".:$DOCS_CP" "$EXPLORER" --reflect com.example.product.ProductCategory 2>&1 || true)
check "reflect ProductCategory" "$OUTPUT" "ProductCategory"
check "reflect enum" "$OUTPUT" "enum"
check "reflect values" "$OUTPUT" "ELECTRONICS"

echo "  Test 9: Reflection fallback for class not in JSON"
OUTPUT=$(java -cp ".:$DOCS_CP" "$EXPLORER" java.lang.String 2>&1 || true)
check "reflect String" "$OUTPUT" "String"
check "reflect String kind" "$OUTPUT" "class"

echo "  Test 10: Package query without ClassGraph"
OUTPUT=$(java -cp ".:$DOCS_CP" "$EXPLORER" --reflect com.example.service 2>&1 || true)
check "package no ClassGraph" "$OUTPUT" "ClassGraph"

echo ""
if [ $FAIL -eq 0 ]; then
  echo "=== Java: all $PASS tests passed ==="
else
  echo "=== Java: $FAIL tests FAILED ==="
  exit 1
fi

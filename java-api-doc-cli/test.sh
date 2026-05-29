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

echo "  Test 10: Package query via jar tf fallback (no ClassGraph)"
OUTPUT=$(java -cp ".:$DOCS_CP" "$EXPLORER" --reflect com.example.service 2>&1 || true)
check "package jar tf" "$OUTPUT" "com.example.service"
check "package jar tf UserService" "$OUTPUT" "UserService"

# ==================== ClassGraph tests ====================
CG_JAR="lib/classgraph-4.8.184.jar"
if [ -f "$CG_JAR" ]; then
  CG_CP=".:$CG_JAR"

  echo "  Test 11: ClassGraph - package scan io.github.classgraph"
  OUTPUT=$(java -cp "$CG_CP" "$EXPLORER" --reflect io.github.classgraph 2>&1 || true)
  check "ClassGraph pkg scan" "$OUTPUT" "ClassGraph"
  check "ClassGraph pkg kind" "$OUTPUT" "package"
  check "ClassGraph pkg ScanResult" "$OUTPUT" "ScanResult"

  echo "  Test 12: ClassGraph - class query ClassGraph"
  OUTPUT=$(java -cp "$CG_CP" "$EXPLORER" --reflect io.github.classgraph.ClassGraph 2>&1 || true)
  check "ClassGraph class" "$OUTPUT" "ClassGraph"
  check "ClassGraph kind" "$OUTPUT" "class"
  check "ClassGraph scan method" "$OUTPUT" "scan"

  echo "  Test 13: ClassGraph - method query ClassGraph.scan"
  OUTPUT=$(java -cp "$CG_CP" "$EXPLORER" --reflect io.github.classgraph.ClassGraph.scan 2>&1 || true)
  check "scan method" "$OUTPUT" "scan"
  check "scan returns" "$OUTPUT" "ScanResult"

  echo "  Test 14: ClassGraph - class query ScanResult"
  OUTPUT=$(java -cp "$CG_CP" "$EXPLORER" --reflect io.github.classgraph.ScanResult 2>&1 || true)
  check "ScanResult class" "$OUTPUT" "ScanResult"
  check "ScanResult getAllClasses" "$OUTPUT" "getAllClasses"
else
  echo "  SKIP: ClassGraph tests (lib/classgraph-4.8.184.jar not found)"
fi

# ==================== JAR exploration tests ====================
EXAMPLE_JAR="example/target/example-1.0.0.jar"
if [ -f "$EXAMPLE_JAR" ]; then
  echo "  Test 16: JAR explore - overview"
  OUTPUT=$(java -cp "." "$EXPLORER" --jar "$EXAMPLE_JAR" 2>&1 || true)
  check "JAR overview" "$OUTPUT" "example-1.0.0.jar"
  check "JAR packages" "$OUTPUT" "com"

  echo "  Test 17: JAR explore - package query"
  OUTPUT=$(java -cp "." "$EXPLORER" --jar "$EXAMPLE_JAR" com.example.service 2>&1 || true)
  check "JAR pkg UserService" "$OUTPUT" "UserService"

  echo "  Test 18: JAR explore - sub-package navigation"
  OUTPUT=$(java -cp "." "$EXPLORER" --jar "$EXAMPLE_JAR" com.example 2>&1 || true)
  check "JAR sub-packages" "$OUTPUT" "com.example.service"
else
  echo "  SKIP: JAR explore tests (example JAR not found)"
fi

# ==================== Auto-fallback test ====================
echo "  Test 19: Auto-fallback to reflect mode (no api-doc.json)"
OUTPUT=$(java -cp "." "$EXPLORER" java.lang.String 2>&1 || true)
check "auto-fallback message" "$OUTPUT" "auto-fallback"
check "auto-fallback String" "$OUTPUT" "String"

# ==================== JDK module path test (Linux) ====================
OS_NAME="$(uname -s 2>/dev/null || echo unknown)"
if [[ "$OS_NAME" == "Linux" ]]; then
  JAVA_HOME="$(dirname "$(dirname "$(readlink -f "$(which java)")")")"
  JDK_MODULES="$JAVA_HOME/jmods"
  if [ -d "$JDK_MODULES" ]; then
    echo "  Test 15: JDK module - explore java.base/java.lang (module-path)"
    OUTPUT=$(java -cp "." --module-path "$JDK_MODULES" --add-modules java.base "$EXPLORER" --reflect java.lang.String 2>&1 || true)
    check "JDK String" "$OUTPUT" "String"
    check "JDK String kind" "$OUTPUT" "class"
  else
    echo "  SKIP: JDK module test (jmods not found at $JDK_MODULES)"
  fi
else
  echo "  SKIP: JDK module test (not Linux, OS=$OS_NAME)"
fi

echo ""
if [ $FAIL -eq 0 ]; then
  echo "=== Java: all $PASS tests passed ==="
else
  echo "=== Java: $FAIL tests FAILED ==="
  exit 1
fi

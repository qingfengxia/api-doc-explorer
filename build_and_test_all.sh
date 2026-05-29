#!/usr/bin/env bash
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=============================================="
echo "  API Explorer Skill — Build & Test All"
echo "=============================================="
echo ""

OVERALL_PASS=0
OVERALL_FAIL=0
FAILED_LANGS=()

run_lang() {
  local lang="$1"
  local dir="$2"
  local build_cmd="$3"
  local test_cmd="$4"

  echo ""
  echo "────────── $lang ──────────"
  
  if [ ! -d "$dir" ]; then
    echo "  SKIP: directory $dir not found"
    return
  fi

  cd "$SCRIPT_DIR/$dir"

  # Build
  set +e
  echo "  >>> Building..."
  bash "$build_cmd" 2>&1
  BUILD_STATUS=$?
  set -e

  if [ $BUILD_STATUS -ne 0 ]; then
    echo "  !! BUILD FAILED (exit code $BUILD_STATUS)"
    OVERALL_FAIL=$((OVERALL_FAIL + 1))
    FAILED_LANGS+=("$lang (build)")
    cd "$SCRIPT_DIR"
    return
  fi

  # Test
  set +e
  echo "  >>> Testing..."
  bash "$test_cmd" 2>&1
  TEST_STATUS=$?
  set -e

  if [ $TEST_STATUS -eq 0 ]; then
    echo "  ✅ $lang: build + test passed"
    OVERALL_PASS=$((OVERALL_PASS + 1))
  else
    echo "  !! TEST FAILED (exit code $TEST_STATUS)"
    OVERALL_FAIL=$((OVERALL_FAIL + 1))
    FAILED_LANGS+=("$lang (test)")
  fi

  cd "$SCRIPT_DIR"
}

# Run each language
run_lang "TypeScript" "typescript-api-doc-cli" "build.sh" "test.sh"
run_lang "JavaScript" "javascript-api-doc-cli" "build.sh" "test.sh"
run_lang "Rust"       "rust-api-doc-cli"       "build.sh" "test.sh"
run_lang "C++"        "cpp-api-doc-cli"        "build.sh" "test.sh"
run_lang "Java"       "java-api-doc-cli"       "build.sh" "test.sh"
run_lang "Python"     "python-api-doc-cli"     "build.sh" "test.sh"

echo ""
echo "=============================================="
echo "  Summary"
echo "=============================================="
echo "  Passed: $OVERALL_PASS"
echo "  Failed: $OVERALL_FAIL"
if [ ${#FAILED_LANGS[@]} -gt 0 ]; then
  echo "  Failed languages:"
  for f in "${FAILED_LANGS[@]}"; do
    echo "    - $f"
  done
fi
echo ""
echo "=============================================="

exit $OVERALL_FAIL

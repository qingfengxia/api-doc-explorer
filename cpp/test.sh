#!/usr/bin/env bash
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== C++: test ==="

EXPLORER="cpp-api-explorer.py"
DOCS="docs"
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

echo "  Test 1: namespace ROS2"
OUTPUT=$(python3 "$EXPLORER" --doc-path "$DOCS" ROS2 2>&1 || true)
check "ROS2 namespace" "$OUTPUT" "Classes / Structs"

echo "  Test 2: struct query TopicConfiguration"
OUTPUT=$(python3 "$EXPLORER" --doc-path "$DOCS" TopicConfiguration 2>&1 || true)
check "TopicConfiguration" "$OUTPUT" "m_type"

echo "  Test 3: method query QoS::GetQoS"
OUTPUT=$(python3 "$EXPLORER" --doc-path "$DOCS" ROS2::QoS::GetQoS 2>&1 || true)
check "GetQoS method" "$OUTPUT" "GetQoS"

echo "  Test 4: non-existent symbol"
OUTPUT=$(python3 "$EXPLORER" --doc-path "$DOCS" NonExistentSymbol 2>&1 || true)
check "not-found" "$OUTPUT" "No API found"

echo ""
if [ $FAIL -eq 0 ]; then
  echo "=== C++: all $PASS tests passed ==="
else
  echo "=== C++: $FAIL tests FAILED ==="
  exit 1
fi

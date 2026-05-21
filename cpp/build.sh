#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== C++: build ==="

# Check dependencies
command -v doxygen >/dev/null 2>&1 || { echo "ERROR: doxygen is not installed"; exit 1; }
echo "  doxygen $(doxygen --version 2>&1)"

# Delete old docs
echo "  Deleting old docs..."
rm -rf docs

# Check input source
INPUT_SRC="/d/Repositories/o3de-extras/Gems/ROS2/Code/Include"
if [ ! -d "$INPUT_SRC" ]; then
  echo "ERROR: Source directory not found at $INPUT_SRC"
  echo "  Please ensure the o3de-extras repository is cloned."
  exit 1
fi
echo "  Source: $INPUT_SRC ($(find "$INPUT_SRC" -name '*.h' -o -name '*.hpp' 2>/dev/null | wc -l) header files)"

# Generate docs
echo "  Generating Doxygen XML documentation..."
doxygen Doxyfile 2>&1
echo "  Generated $(ls docs/*.xml 2>/dev/null | wc -l) XML files"

echo "=== C++: build done ==="

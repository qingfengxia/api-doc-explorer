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
rm -rf example/docs

# Generate docs from the self-contained example
echo "  Generating Doxygen XML documentation..."
cd example && doxygen Doxyfile 2>&1 && cd ..
echo "  Generated $(ls example/docs/*.xml 2>/dev/null | wc -l) XML files"

echo "=== C++: build done ==="

#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== Python: build ==="

# Check dependencies
command -v python3 >/dev/null 2>&1 || { echo "ERROR: python3 is not installed"; exit 1; }
echo "  python3 $(python3 --version 2>&1)"

# Delete old docs
echo "  Deleting old docs..."
rm -rf example/docs

# Generate docs from the example module using runtime introspection
echo "  Generating Python documentation (gen_docs.py)..."
python3 gen_docs.py example -o example/docs/api-docs.json

echo "=== Python: build done ==="

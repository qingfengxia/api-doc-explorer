#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== JavaScript: build ==="

# Check dependencies
command -v node >/dev/null 2>&1 || { echo "ERROR: node is not installed"; exit 1; }
command -v jsdoc >/dev/null 2>&1 || { echo "ERROR: jsdoc is not installed"; exit 1; }
echo "  node $(node --version)"
echo "  jsdoc $(jsdoc --version 2>&1 | head -1)"

# Delete old docs
echo "  Deleting old docs..."
rm -rf example/docs

# Generate docs
echo "  Generating JSDoc documentation..."
cd example && jsdoc -c jsdoc.json -d docs && jsdoc -X -c jsdoc.json > docs/api-docs.json && cd ..

# Dry-run package
echo "  Dry-run npm pack..."
cd example && npm pack --dry-run 2>&1 | head -5 && cd ..

echo "=== JavaScript: build done ==="

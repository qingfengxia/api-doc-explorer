#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== TypeScript: build ==="

# Check dependencies
command -v node >/dev/null 2>&1 || { echo "ERROR: node is not installed"; exit 1; }
command -v npx >/dev/null 2>&1 || { echo "ERROR: npx is not installed"; exit 1; }
echo "  node $(node --version)"

# Delete old docs
echo "  Deleting old docs..."
rm -rf example/docs

# Install dependencies if needed
if [ ! -d "example/node_modules" ]; then
  echo "  Installing npm dependencies..."
  cd example && npm install && cd ..
fi

# Generate docs
echo "  Generating TypeDoc documentation..."
cd example && npx typedoc && cd ..

# Dry-run package
echo "  Dry-run npm pack..."
cd example && npm pack --dry-run 2>&1 | head -5 && cd ..

echo "=== TypeScript: build done ==="

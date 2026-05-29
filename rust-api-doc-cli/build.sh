#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== Rust: build ==="

# Check dependencies
command -v python3 >/dev/null 2>&1 || { echo "ERROR: python3 is not installed"; exit 1; }
echo "  python3 $(python3 --version 2>&1)"

# Delete old docs
echo "  Deleting old docs..."
rm -rf example/docs

# Generate docs using gen_docs.py (stable fallback)
echo "  Generating Rust documentation (gen_docs.py)..."
python3 gen_docs.py example/src/lib.rs -o example/docs/api-docs.json

# If cargo is available, also try cargo package --dry-run
if command -v cargo >/dev/null 2>&1; then
  echo "  Dry-run cargo package (--list)..."
  cd example && cargo package --list 2>&1 | head -10 && cd ..
else
  echo "  (cargo not installed, skipping dry-run)"
fi

echo "=== Rust: build done ==="

#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== Python: build ==="

# Check dependencies
command -v python3 >/dev/null 2>&1 || { echo "ERROR: python3 is not installed"; exit 1; }
echo "  python3 $(python3 --version 2>&1)"

# Python uses runtime introspection - no documentation generation needed.
# Just validate the explorer script loads correctly.
echo "  Validating python_api_explorer.py..."
python3 -c "
import sys
sys.path.insert(0, '.')
# Quick syntax check by parsing
import py_compile
py_compile.compile('python_api_explorer.py', doraise=True)
print('  Syntax OK')
"

echo "=== Python: build done ==="

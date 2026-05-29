#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== Java: build ==="

# Check dependencies
command -v java >/dev/null 2>&1 || { echo "ERROR: java is not installed"; exit 1; }
command -v javac >/dev/null 2>&1 || { echo "ERROR: javac is not installed"; exit 1; }
command -v mvn >/dev/null 2>&1 || { echo "ERROR: mvn is not installed"; exit 1; }
echo "  java $(java --version 2>&1 | head -1)"
echo "  mvn $(mvn --version 2>&1 | head -1)"

# Delete old docs
echo "  Deleting old docs..."
rm -rf example/docs

# Build example Maven project (generates api-doc.json)
echo "  Building example Maven project..."
cd example && mvn clean package -DskipTests -q && cd ..
echo "  Generated: example/target/classes/api-doc.json"

# Copy api-doc.json to docs/
mkdir -p example/docs
cp example/target/classes/api-doc.json example/docs/api-doc.json

# Dry-run: list JAR contents
echo "  Dry-run: JAR contents (first 5 entries)"
jar tf example/target/example-1.0.0.jar 2>/dev/null | head -5 || true

# Compile JavaApiExplorer and ApiDoclet
echo "  Compiling JavaApiExplorer and ApiDoclet..."
javac --release 17 -d . -parameters --add-modules jdk.javadoc -encoding UTF-8 ApiDoclet.java JavaApiExplorer.java 2>&1

echo "=== Java: build done ==="

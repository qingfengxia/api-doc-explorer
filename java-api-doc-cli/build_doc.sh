#!/bin/bash

# 用 ApiDoclet 对自身 (JavaApiExplorer.java) 生成 api-doc.json
# 然后用 JavaApiExplorer 阅读该 JSON

DOCLET_CLASS="."
SRC_PATH="."

echo "=== Step 1: Generate api-doc.json ==="
javadoc \
  -doclet ApiDoclet \
  -docletpath ${DOCLET_CLASS} \
  --add-modules jdk.javadoc \
  -sourcepath ${SRC_PATH} \
  JavaApiExplorer.java

echo ""
echo "=== Step 2: Verify JSON exists ==="
ls -la api-doc.json
echo ""

echo "=== Step 3: Query by package ==="
java JavaApiExplorer JavaApiExplorer

echo ""
echo "=== Step 4: Query by method ==="
java JavaApiExplorer JavaApiExplorer.JavaApiExplorer.main

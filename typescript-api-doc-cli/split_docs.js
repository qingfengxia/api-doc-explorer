import fs from 'fs';
import path from 'path';

const raw = JSON.parse(fs.readFileSync('docs/api-docs.json', 'utf-8'));
const outDir = 'docs/modules';
fs.mkdirSync(outDir, { recursive: true });

function walk(node: any, depth = 0) {
  if (node.kindString === 'Module') {
    const name = node.name.replace(/\//g, '.');
    fs.writeFileSync(
      path.join(outDir, `${name}.json`),
      JSON.stringify(node, null, 2)
    );
  }
  if (node.children) {
    node.children.forEach((c: any) => walk(c, depth + 1));
  }
}

walk(raw);
#!/usr/bin/env node
/*
node typescript-api-explorer.js --doc-path ./docs/ example
--doc-path 支持目录
  传入目录时自动拼接 api-docs.json，所以 --doc-path ./docs/ 
  和 --doc-path ./docs/api-docs.json 都可以

未提供 --doc-path 时：
  自动从 package.json + node_modules/<pkg>/ 发现文档路径
  支持多文件文档，按 subpackage/module.json 组织
*/

const fs = require('fs');
const path = require('path');

// --- 1. 命令行参数解析 ---
function parseArgs(argv) {
  const args = argv.slice(2);
  let docPath = null;
  const positional = [];

  for (let i = 0; i < args.length; i++) {
    if ((args[i] === '-p' || args[i] === '--doc-path') && i + 1 < args.length) {
      docPath = args[++i];
    } else if (args[i] === '-h' || args[i] === '--help') {
      printUsage();
      process.exit(0);
    } else if (args[i] === '-v' || args[i] === '--version') {
      console.log('typescript-api-explorer v2.0.0');
      process.exit(0);
    } else {
      positional.push(args[i]);
    }
  }

  return { docPath, query: positional.join(' ') };
}

function printUsage() {
  console.log(`
Usage: typescript-api-explorer [options] <query>

Explore TypeDoc generated JSON files.

Arguments:
  query                API query string (e.g., "UserService.findUser")

Options:
  -p, --doc-path <path>  Path to the TypeDoc JSON file or directory (default: auto-discover)
  -h, --help             Display this help message
  -v, --version          Display the version number

If --doc-path is omitted, the tool auto-discovers docs from:
  1. cwd's package.json → look in node_modules/<name>/docs/
  2. cwd's ./docs/api-docs.json (fallback)
`);
}

// --- 1b. 自动发现文档路径 ---
function resolveDocPath() {
  // Walk up to find package.json
  let dir = process.cwd();
  let pkgJson = null;

  while (true) {
    const pkgPath = path.join(dir, 'package.json');
    if (fs.existsSync(pkgPath)) {
      try {
        pkgJson = JSON.parse(fs.readFileSync(pkgPath, 'utf-8'));
      } catch (e) { /* ignore */ }
      if (pkgJson) break;
    }
    const parent = path.dirname(dir);
    if (parent === dir) break;
    dir = parent;
  }

  // Check node_modules/<name>/ for docs
  if (pkgJson && pkgJson.name) {
    const pkgName = pkgJson.name;
    const nodeModulesDir = path.join(dir, 'node_modules', pkgName);

    if (fs.existsSync(nodeModulesDir)) {
      const candidates = [
        path.join(nodeModulesDir, 'docs'),
        path.join(nodeModulesDir, 'dist', 'docs'),
        path.join(nodeModulesDir, 'docs', 'api-docs.json'),
        path.join(nodeModulesDir, 'dist', 'docs', 'api-docs.json'),
      ];
      for (const candidate of candidates) {
        if (fs.existsSync(candidate)) {
          return candidate;
        }
      }
    }

    // Also check if current project has a docs dir
    const localDocs = path.join(dir, 'docs');
    if (fs.existsSync(localDocs)) {
      return localDocs;
    }
  }

  // Fallback
  return null;
}

// --- 1c. 加载文档数据（支持单文件和多文件） ---
function loadDocData(docPath) {
  // 如果 docPath 是 null，不匹配任何路径
  if (!docPath) return null;

  // 解析为绝对路径
  const absPath = path.resolve(docPath);

  if (!fs.existsSync(absPath)) {
    return null;
  }

  // 如果是文件，直接加载
  if (fs.statSync(absPath).isFile()) {
    return loadSingleJson(absPath);
  }

  // 如果是目录
  // 先检查是否有 api-docs.json
  const mainJson = path.join(absPath, 'api-docs.json');
  if (fs.existsSync(mainJson)) {
    return loadSingleJson(mainJson);
  }

  // 没有 api-docs.json，加载目录下所有 json 文件
  return loadAllJsonFiles(absPath);
}

function loadSingleJson(filePath) {
  try {
    const raw = fs.readFileSync(filePath, 'utf-8');
    return JSON.parse(raw);
  } catch (err) {
    console.error(`\u274c Error parsing JSON file ${filePath}: ${err.message}`);
    process.exit(1);
  }
}

function loadAllJsonFiles(dirPath) {
  const allItems = [];
  const visited = new Set();

  function walkDir(currentDir) {
    let entries;
    try {
      entries = fs.readdirSync(currentDir, { withFileTypes: true });
    } catch (e) {
      return;
    }
    for (const entry of entries) {
      const fullPath = path.join(currentDir, entry.name);
      if (fs.statSync(fullPath).isDirectory()) {
        walkDir(fullPath);
      } else if (entry.name.endsWith('.json')) {
        // 避免重复加载
        const realPath = fs.realpathSync(fullPath);
        if (visited.has(realPath)) continue;
        visited.add(realPath);

        const data = loadSingleJson(fullPath);
        if (data) {
          // 每个文件代表一个模块节点（有 name 和 children）
          // 将整个模块作为顶层子节点加入
          allItems.push(data);
        }
      }
    }
  }

  walkDir(dirPath);

  // 合并为一个根节点
  return {
    name: 'merged',
    children: allItems,
  };
}

// --- 2. 主逻辑 ---
function main(queryString, docPath) {
  // 加载文档数据
  const docJson = loadDocData(docPath);

  if (!docJson) {
    console.error(`\u274c Error: Documentation not found at ${docPath}`);
    process.exit(1);
  }

  // 解析查询字符串 (例如: "UserService.findUser" 或 "MyModule.UserService.findUser")
  const parts = queryString.split('.');

  // 在 JSON 树中查找
  const result = searchInTree(docJson, parts);

  // 输出结果
  if (result) {
    printFormattedResult(result);
  } else {
    console.log(`\uD83D\uDD0D No API found for query: "${queryString}"`);
    console.log('   Tip: Check if the module/class/method name is correct in the JSON.');
  }
}

// --- 3. 递归搜索逻辑 ---
function searchInTree(currentNode, partsRemaining) {
  if (!currentNode || partsRemaining.length === 0) {
    return null;
  }

  const currentPart = partsRemaining[0];
  const nextParts = partsRemaining.slice(1);

  // 检查当前节点的子节点
  const children = currentNode.children || [];

  // 尝试在子节点中找到匹配项
  let foundNode = children.find(child => child.name === currentPart);

  // 如果没找到，可能是因为 JSON 结构嵌套较深，或者这是一个属性/方法查找
  if (!foundNode && nextParts.length === 0) {
      return deepFindByName(currentNode, currentPart);
  }

  if (foundNode) {
    if (nextParts.length === 0) {
      return foundNode;
    } else {
      return searchInTree(foundNode, nextParts);
    }
  }

  return null;
}

// --- 4. 深度优先搜索（用于查找方法/属性） ---
function deepFindByName(node, name) {
  if (!node) return null;
  if (node.name === name) return node;

  const children = node.children || [];
  for (const child of children) {
    const found = deepFindByName(child, name);
    if (found) return found;
  }

  return null;
}

// --- 5. 美化输出 ---
function printFormattedResult(node) {
  console.log('\n\u2705 Found API:');
  console.log('='.repeat(60));

  console.log(`\uD83D\uDCCC Name:       ${node.name}`);
  console.log(`\uD83C\uDFF7\uFE0F  Kind:       ${node.kindString || 'N/A'}`);

  if (node.comment) {
    if (node.comment.summary) {
      const text = node.comment.summary.map(s => s.text).join('');
      console.log(`\uD83D\uDCDD Description: ${text.trim()}`);
    }
    if (node.comment.tags) {
        node.comment.tags.forEach(tag => {
            const tagText = tag.text?.map(t => t.text).join('') || '';
            console.log(`   @${tag.tag}: ${tagText.trim()}`);
        });
    }
  }

  if (node.signatures && node.signatures.length > 0) {
    const sig = node.signatures[0];
    console.log(`\n\uD83D\uDD27 Signature:  ${sig.name}(...)`);

    if (sig.parameters && sig.parameters.length > 0) {
      console.log('   Parameters:');
      sig.parameters.forEach(p => {
        const type = getTypeString(p.type);
        const desc = p.comment?.summary?.map(s => s.text).join('') || 'No description';
        console.log(`     - ${p.name}: ${type}`);
        console.log(`       \u21B3 ${desc.trim()}`);
      });
    }

    if (sig.returns) {
      const returnType = getTypeString(sig.returns.type);
      const returnDesc = sig.returns.comment?.summary?.map(s => s.text).join('') || '';
      console.log(`   \u21A9\uFE0F  Returns:    ${returnType}`);
      if (returnDesc) console.log(`       \u21B3 ${returnDesc.trim()}`);
    }
  }

  console.log('='.repeat(60) + '\n');
}

// --- 6. 辅助：类型字符串解析 ---
function getTypeString(typeObj) {
  if (!typeObj) return 'any';

  switch (typeObj.type) {
    case 'intrinsic':
      return typeObj.name;
    case 'reference':
      return typeObj.name + (typeObj.typeArguments ? `<${typeObj.typeArguments.map(getTypeString).join(', ')}>` : '');
    case 'union':
      return typeObj.types.map(getTypeString).join(' | ');
    case 'array':
      return `${getTypeString(typeObj.elementType)}[]`;
    default:
      return typeObj.name || typeObj.type || 'unknown';
  }
}

// --- 入口 ---
const { docPath: rawDocPath, query } = parseArgs(process.argv);
const resolvedDocPath = rawDocPath || resolveDocPath() || 'docs/api-docs.json';

if (!query) {
  console.error('\u274c Error: Missing required argument <query>');
  printUsage();
  process.exit(1);
}

if (!rawDocPath && !fs.existsSync(path.resolve(resolvedDocPath)) && !fs.existsSync(path.resolve('docs/api-docs.json'))) {
  console.log('\u2139\uFE0F  No --doc-path given, auto-discovering...');
}

// 标准化：目录自动补 api-docs.json
let finalDocPath = resolvedDocPath;
if (fs.existsSync(finalDocPath) && fs.statSync(finalDocPath).isDirectory()) {
  const joined = path.join(finalDocPath, 'api-docs.json');
  if (fs.existsSync(joined)) {
    finalDocPath = joined;
  }
  // 如果是目录但没有 api-docs.json，loadDocData 会处理多文件场景
}

main(query, finalDocPath);

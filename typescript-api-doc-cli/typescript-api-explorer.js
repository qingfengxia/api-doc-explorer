#!/usr/bin/env node
/*
node typescript-api-explorer.js --doc-path ./docs/ example
--doc-path 支持目录
  传入目录时自动拼接 api-docs.json，所以 --doc-path ./docs/ 
  和 --doc-path ./docs/api-docs.json 都可以

未提供 --doc-path 时：
  自动从 package.json + node_modules/<pkg>/ 发现文档路径
  支持多文件文档，按 subpackage/module.json 组织

当没有 api-docs.json 时：
  自动搜索 .d.ts 文件，解析出 module/class/method 层级
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
      console.log('typescript-api-explorer v2.1.0');
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

Explore TypeDoc generated JSON files, or fall back to .d.ts parsing.

Arguments:
  query                API query string (e.g., "UserService.findUser")

Options:
  -p, --doc-path <path>  Path to the TypeDoc JSON file or directory (default: auto-discover)
  -h, --help             Display this help message
  -v, --version          Display the version number

Doc discovery order:
  1. --doc-path (explicit)
  2. cwd's package.json → node_modules/<name>/docs/
  3. cwd's ./docs/api-docs.json
  4. .d.ts file search (fallback when no JSON docs available)
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
    console.error(`❌ Error parsing JSON file ${filePath}: ${err.message}`);
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

// ====================================================================
// --- .d.ts FALLBACK PARSER ---
// ====================================================================

/**
 * 从 .d.ts 文件中解析出 API 结构。
 * 
 * 支持的声明:
 *   - declare module "xxx" { ... }
 *   - export declare class ClassName { method(...): ReturnType; }
 *   - export declare interface InterfaceName { property: Type; method(...): ReturnType; }
 *   - export declare enum EnumName { Member = value, }
 *   - export declare function funcName(...): ReturnType;
 *   - export declare type TypeName = ...;
 *   - export declare const/let/var name: Type;
 */
function parseDtsFile(filePath) {
  const content = fs.readFileSync(filePath, 'utf-8');
  const fileName = path.basename(filePath, '.d.ts');
  const children = [];

  // Remove comments
  const cleaned = content
    .replace(/\/\*[\s\S]*?\*\//g, '')   // block comments
    .replace(/\/\/.*$/gm, '');           // line comments

  // --- Parse top-level declarations ---

  // 1. export declare class
  const classRegex = /export\s+declare\s+class\s+(\w+)(?:<[^>]*>)?(?:\s+extends\s+\w+(?:<[^>]*>)?)?(?:\s+implements\s+[\w,\s<>]+)?\s*\{/g;
  let match;
  while ((match = classRegex.exec(cleaned)) !== null) {
    const className = match[1];
    const classStart = match.index + match[0].length;
    const body = extractBlock(cleaned, classStart - 1);
    const classNode = {
      name: className,
      kind: 128,           // TypeDoc Class kind
      kindString: 'Class',
      children: [],
    };

    // Parse class body for methods, properties
    parseClassBody(body, classNode.children);
    children.push(classNode);
  }

  // 2. export declare interface
  const ifaceRegex = /export\s+declare\s+interface\s+(\w+)(?:<[^>]*>)?(?:\s+extends\s+[\w,\s<>]+)?\s*\{/g;
  while ((match = ifaceRegex.exec(cleaned)) !== null) {
    const ifaceName = match[1];
    const ifaceStart = match.index + match[0].length;
    const body = extractBlock(cleaned, ifaceStart - 1);
    const ifaceNode = {
      name: ifaceName,
      kind: 256,           // TypeDoc Interface kind
      kindString: 'Interface',
      children: [],
    };
    parseClassBody(body, ifaceNode.children);
    children.push(ifaceNode);
  }

  // 3. export declare enum
  const enumRegex = /export\s+declare\s+enum\s+(\w+)\s*\{/g;
  while ((match = enumRegex.exec(cleaned)) !== null) {
    const enumName = match[1];
    const enumStart = match.index + match[0].length;
    const body = extractBlock(cleaned, enumStart - 1);
    const enumNode = {
      name: enumName,
      kind: 8,             // TypeDoc Enum kind
      kindString: 'Enumeration',
      children: [],
    };
    // Parse enum members
    const memberRegex = /^\s*(\w+)\s*(?:=\s*([^,]+))?/gm;
    let mMatch;
    while ((mMatch = memberRegex.exec(body)) !== null) {
      enumNode.children.push({
        name: mMatch[1],
        kind: 16,           // TypeDoc EnumMember kind
        kindString: 'Enumeration Member',
        value: mMatch[2] ? mMatch[2].trim().replace(/,?\s*$/, '') : undefined,
      });
    }
    children.push(enumNode);
  }

  // 4. export declare function
  const funcRegex = /export\s+declare\s+function\s+(\w+)\s*([^;]*)/g;
  while ((match = funcRegex.exec(cleaned)) !== null) {
    const funcName = match[1];
    const funcSig = match[2].trim();
    const funcNode = {
      name: funcName,
      kind: 64,            // TypeDoc Function kind
      kindString: 'Function',
      signatures: [{
        name: funcName,
        kind: 4096,
        kindString: 'Call signature',
        _rawSignature: funcSig,
      }],
    };
    parseSignatureParams(funcSig, funcNode.signatures[0]);
    children.push(funcNode);
  }

  // 5. export declare type
  const typeRegex = /export\s+declare\s+type\s+(\w+)(?:<[^>]*>)?\s*=/g;
  while ((match = typeRegex.exec(cleaned)) !== null) {
    children.push({
      name: match[1],
      kind: 4194304,       // TypeDoc TypeAlias kind
      kindString: 'Type Alias',
    });
  }

  // 6. export declare const/let/var
  const varRegex = /export\s+declare\s+(?:const|let|var)\s+(\w+)\s*:\s*([^;]*)/g;
  while ((match = varRegex.exec(cleaned)) !== null) {
    children.push({
      name: match[1],
      kind: 2097152,       // TypeDoc Variable kind
      kindString: 'Variable',
      type: { name: match[2].trim().replace(/;?\s*$/, ''), type: 'intrinsic' },
    });
  }

  return {
    name: fileName,
    kind: 2,               // TypeDoc Module kind
    kindString: 'Module',
    children,
  };
}

/**
 * Extract a balanced { } block from position.
 */
function extractBlock(text, startPos) {
  if (text[startPos] !== '{') return '';
  let depth = 0;
  let i = startPos;
  for (; i < text.length; i++) {
    if (text[i] === '{') depth++;
    else if (text[i] === '}') {
      depth--;
      if (depth === 0) break;
    }
  }
  return text.substring(startPos + 1, i);
}

/**
 * Parse class/interface body for methods and properties.
 */
function parseClassBody(body, children) {
  // Split by lines, track state for multi-line signatures
  const lines = body.split('\n');
  let currentDecl = '';

  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith('//') || trimmed.startsWith('/*')) continue;

    currentDecl += (currentDecl ? ' ' : '') + trimmed;

    // Check if this is a complete declaration (ends with ; or { })
    if (currentDecl.endsWith(';') || currentDecl.endsWith('}')) {
      parseDeclaration(currentDecl, children);
      currentDecl = '';
    }
  }
  // Handle any remaining
  if (currentDecl.trim()) {
    parseDeclaration(currentDecl, children);
  }
}

/**
 * Parse a single declaration line within a class/interface body.
 */
function parseDeclaration(decl, children) {
  decl = decl.replace(/;$/, '').trim();

  // Method: name(params): ReturnType
  // Also handle: abstract name(params): ReturnType
  const methodMatch = decl.match(/^(?:abstract\s+)?(?:readonly\s+)?(\w+)(?:<[^>]*>)?\s*\(([^)]*)\)\s*(?::\s*(.+))?$/);
  if (methodMatch) {
    const name = methodMatch[1];
    // Skip constructor overloads or private methods
    if (name === 'constructor' || name.startsWith('#')) return;

    const paramsStr = methodMatch[2];
    const returnType = methodMatch[3] ? methodMatch[3].trim() : undefined;
    const sig = {
      name,
      kind: 4096,
      kindString: 'Call signature',
      _rawSignature: `(${paramsStr})${returnType ? ': ' + returnType : ''}`,
    };
    parseSignatureParams(`(${paramsStr})${returnType ? ': ' + returnType : ''}`, sig);

    children.push({
      name,
      kind: 2048,           // TypeDoc Method kind
      kindString: 'Method',
      signatures: [sig],
    });
    return;
  }

  // Property: name?: Type or name: Type
  const propMatch = decl.match(/^(?:abstract\s+)?(?:readonly\s+)?(\w+)(?:\?)?:\s*(.+)$/);
  if (propMatch) {
    const name = propMatch[1];
    if (name.startsWith('#')) return;
    children.push({
      name,
      kind: 1024,           // TypeDoc Property kind
      kindString: 'Property',
      type: { name: propMatch[2].trim(), type: 'intrinsic' },
    });
    return;
  }

  // Getter/setter
  const getterMatch = decl.match(/^(?:get|set)\s+(\w+)\s*\(/);
  if (getterMatch) {
    const name = getterMatch[1];
    // Avoid duplicates
    if (!children.find(c => c.name === name)) {
      children.push({
        name,
        kind: 262144,       // TypeDoc Accessor kind
        kindString: 'Accessor',
      });
    }
  }
}

/**
 * Parse parameter types from a signature string like (a: string, b?: number): ReturnType
 */
function parseSignatureParams(sigStr, sigObj) {
  const paramsMatch = sigStr.match(/\(([^)]*)\)/);
  if (!paramsMatch || !paramsMatch[1].trim()) return;

  const params = paramsMatch[1].split(',').map(p => p.trim()).filter(p => p);
  if (params.length === 0) return;

  sigObj.parameters = params.map(p => {
    // Parse: name?: Type or name: Type = default
    const pMatch = p.match(/^(\.\.\.)?(\w+)(\?)?(?:\s*:\s*(.+?))?(?:\s*=\s*(.+))?$/);
    if (!pMatch) return { name: p, type: { type: 'intrinsic', name: 'any' } };

    const isRest = !!pMatch[1];
    const name = pMatch[2];
    const isOptional = !!pMatch[3];
    let typeName = pMatch[4] ? pMatch[4].trim() : 'any';
    const defaultValue = pMatch[5] ? pMatch[5].trim() : undefined;

    // Clean up type
    typeName = typeName.replace(/;$/, '').trim();

    return {
      name,
      type: { type: 'intrinsic', name: typeName },
      ...(isOptional ? { flags: { isOptional: true } } : {}),
      ...(defaultValue ? { defaultValue } : {}),
    };
  });

  // Extract return type
  const retMatch = sigStr.match(/\)\s*:\s*(.+)$/);
  if (retMatch) {
    const retType = retMatch[1].trim().replace(/;$/, '');
    sigObj.returns = {
      type: retType.includes('<') || retType.includes('.')
        ? { type: 'reference', name: retType.replace(/<.*>,?/, '') }
        : { type: 'intrinsic', name: retType },
    };
  }
}

/**
 * Search for .d.ts files in common locations.
 */
function findDtsFiles(searchDir) {
  const results = [];
  const visited = new Set();

  function walk(dir, depth) {
    if (depth > 5) return; // limit depth
    let entries;
    try {
      entries = fs.readdirSync(dir, { withFileTypes: true });
    } catch (e) {
      return;
    }

    for (const entry of entries) {
      // Skip node_modules internals, .d.ts.map, test dirs
      if (entry.name.startsWith('.') || entry.name === 'node_modules' || entry.name === 'test' || entry.name === '__tests__') continue;

      const fullPath = path.join(dir, entry.name);
      if (entry.isDirectory()) {
        walk(fullPath, depth + 1);
      } else if (entry.name.endsWith('.d.ts') && !entry.name.endsWith('.d.ts.map')) {
        const realPath = fs.realpathSync(fullPath);
        if (!visited.has(realPath)) {
          visited.add(realPath);
          results.push(fullPath);
        }
      }
    }
  }

  walk(searchDir, 0);
  return results;
}

/**
 * Build a virtual doc tree from .d.ts files.
 */
function buildDtsDocTree(query) {
  const searchDir = process.cwd();
  
  // Try to find .d.ts files in src/, dist/, lib/, types/, or root
  const searchPaths = ['src', 'dist', 'lib', 'types', '.'].map(p => path.join(searchDir, p));
  
  let dtsFiles = [];
  for (const sp of searchPaths) {
    if (fs.existsSync(sp)) {
      dtsFiles = findDtsFiles(sp);
      if (dtsFiles.length > 0) break;
    }
  }

  // Also check node_modules for the query's package
  if (dtsFiles.length === 0 && query.includes('.')) {
    const pkgName = query.split('.')[0];
    const nmPath = path.join(searchDir, 'node_modules', pkgName);
    if (fs.existsSync(nmPath)) {
      dtsFiles = findDtsFiles(nmPath);
    }
  }

  if (dtsFiles.length === 0) {
    return null;
  }

  console.log(`ℹ️  No api-docs.json found, using .d.ts fallback (${dtsFiles.length} file(s))`);

  // Parse all .d.ts files
  const allModules = [];
  for (const f of dtsFiles) {
    const moduleNode = parseDtsFile(f);
    if (moduleNode.children.length > 0) {
      allModules.push(moduleNode);
    }
  }

  if (allModules.length === 0) {
    return null;
  }

  // If there's only one module, return it directly
  if (allModules.length === 1) {
    return allModules[0];
  }

  // Merge into a virtual root
  return {
    name: 'merged-dts',
    kind: 0,
    kindString: 'Project',
    children: allModules,
  };
}

// --- 2. 主逻辑 ---
function main(queryString, docPath) {
  // 加载文档数据
  let docJson = loadDocData(docPath);

  if (!docJson) {
    // Fallback: try .d.ts parsing
    docJson = buildDtsDocTree(queryString);
  }

  if (!docJson) {
    console.error(`❌ Error: Documentation not found at ${docPath}`);
    console.error('   No api-docs.json or .d.ts files found.');
    console.error('   Tip: Run TypeDoc first, or ensure .d.ts files exist in src/ or dist/.');
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
    console.log(`🔍 No API found for query: "${queryString}"`);
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
  console.log('\n✅ Found API:');
  console.log('='.repeat(60));

  console.log(`📌 Name:       ${node.name}`);
  const kindStr = node.kindString || kindNumberToString(node.kind) || 'N/A';
  console.log(`🏷️  Kind:       ${kindStr}`);

  if (node.comment) {
    if (node.comment.summary) {
      const text = node.comment.summary.map(s => s.text).join('');
      console.log(`📝 Description: ${text.trim()}`);
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
    // Prefer _rawSignature from .d.ts fallback
    const sigDisplay = sig._rawSignature
      ? `${sig.name}${sig._rawSignature}`
      : `${sig.name}(...)`;
    console.log(`\n🔧 Signature:  ${sigDisplay}`);

    if (sig.parameters && sig.parameters.length > 0) {
      console.log('   Parameters:');
      sig.parameters.forEach(p => {
        const type = getTypeString(p.type);
        const desc = p.comment?.summary?.map(s => s.text).join('') || '';
        const optional = p.flags?.isOptional ? '?' : '';
        const defVal = p.defaultValue ? ` = ${p.defaultValue}` : '';
        console.log(`     - ${p.name}${optional}: ${type}${defVal}`);
        if (desc) console.log(`       ↳ ${desc.trim()}`);
      });
    }

    if (sig.returns) {
      const returnType = getTypeString(sig.returns.type);
      const returnDesc = sig.returns.comment?.summary?.map(s => s.text).join('') || '';
      console.log(`   ↩️  Returns:    ${returnType}`);
      if (returnDesc) console.log(`       ↳ ${returnDesc.trim()}`);
    }
  }

  // Children (for class/interface level)
  const children = node.children || [];
  if (children.length > 0) {
    console.log(`\n📦 Members (${children.length}):`);
    for (const child of children) {
      const ck = child.kindString || kindNumberToString(child.kind) || '?';
      let sigPreview = '';
      if (child.signatures && child.signatures[0]) {
        sigPreview = child.signatures[0]._rawSignature || '(...)';
      } else if (child.type) {
        sigPreview = `: ${getTypeString(child.type)}`;
      }
      console.log(`   ▸ ${child.name}${sigPreview} — ${ck}`);
    }
  }

  console.log('='.repeat(60) + '\n');
}

/**
 * Convert TypeDoc kind number to string.
 */
function kindNumberToString(kind) {
  const map = {
    1: 'Project', 2: 'Module', 4: 'Namespace', 8: 'Enumeration',
    16: 'Enumeration Member', 32: 'Variable', 64: 'Function',
    128: 'Class', 256: 'Interface', 512: 'Constructor',
    1024: 'Property', 2048: 'Method', 4096: 'Call signature',
    16384: 'Package', 2097152: 'Variable', 262144: 'Accessor',
    4194304: 'Type Alias',
  };
  return map[kind] || undefined;
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
    case 'reflection':
      return typeObj.declaration?.name || 'object';
    default:
      return typeObj.name || typeObj.type || 'unknown';
  }
}

// --- 入口 ---
const { docPath: rawDocPath, query } = parseArgs(process.argv);
const resolvedDocPath = rawDocPath || resolveDocPath() || 'docs/api-docs.json';

if (!query) {
  console.error('❌ Error: Missing required argument <query>');
  printUsage();
  process.exit(1);
}

if (!rawDocPath && !fs.existsSync(path.resolve(resolvedDocPath)) && !fs.existsSync(path.resolve('docs/api-docs.json'))) {
  console.log('ℹ️  No --doc-path given, auto-discovering...');
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

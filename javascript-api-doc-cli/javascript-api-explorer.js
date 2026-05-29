#!/usr/bin/env node
/*
node javascript-api-explorer.js --doc-path ./docs/ example
--doc-path 支持目录或文件
  传入目录时自动拼接 api-docs.json

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
      console.log('javascript-api-explorer v2.0.0');
      process.exit(0);
    } else {
      positional.push(args[i]);
    }
  }

  return { docPath, query: positional.join(' ') };
}

function printUsage() {
  console.log(`
Usage: javascript-api-explorer [options] <query>

Explore JSDoc generated JSON files.

Arguments:
  query                API query string (e.g., "UserService.findUser")

Options:
  -p, --doc-path <path>  Path to the JSDoc JSON file or directory (default: auto-discover)
  -h, --help             Display this help message
  -v, --version          Display the version number

If --doc-path is omitted, the tool auto-discovers docs from:
  1. cwd's package.json → look in node_modules/<name>/docs/
  2. cwd's ./docs/api-docs.json (fallback)
`);
}

// --- 1b. 自动发现文档路径 ---
function resolveDocPath() {
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

    const localDocs = path.join(dir, 'docs');
    if (fs.existsSync(localDocs)) {
      return localDocs;
    }
  }

  return null;
}

// --- 1c. 加载文档数据（支持单文件和多文件） ---
function loadDocData(docPath) {
  if (!docPath) return null;

  const absPath = path.resolve(docPath);
  if (!fs.existsSync(absPath)) return null;

  if (fs.statSync(absPath).isFile()) {
    return loadSingleJson(absPath);
  }

  // 目录
  const mainJson = path.join(absPath, 'api-docs.json');
  if (fs.existsSync(mainJson)) {
    return loadSingleJson(mainJson);
  }

  // 加载所有 json 文件并合并
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
  const merged = [];
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
        const realPath = fs.realpathSync(fullPath);
        if (visited.has(realPath)) continue;
        visited.add(realPath);

        const data = loadSingleJson(fullPath);
        // JSDoc JSON 是数组
        if (Array.isArray(data)) {
          merged.push(...data);
        }
        // 也可能是对象（类型定义等）
        else if (data && typeof data === 'object') {
          // 如果是对象且有 classes/methods 结构，也尝试合并
          if (data.classes) {
            merged.push(...data.classes);
          } else {
            // 尝试展开顶层键
            for (const val of Object.values(data)) {
              if (Array.isArray(val)) {
                merged.push(...val);
              }
            }
          }
        }
      }
    }
  }

  walkDir(dirPath);
  return merged;
}

// doclet 优先级（数字越小越优先）
const KIND_PRIORITY = {
  class: 1,
  namespace: 2,
  constant: 3,
  typedef: 3,
  function: 4,
  enum: 5,
  member: 10,
  event: 10,
};

function pickBestDoclet(doclets) {
  if (!doclets || doclets.length === 0) return null;
  if (doclets.length === 1) return doclets[0];
  return doclets.reduce((best, d) =>
    (KIND_PRIORITY[d.kind] || 99) < (KIND_PRIORITY[best.kind] || 99) ? d : best
  );
}

// --- 2. 主逻辑 ---
function main(queryString, docPath) {
  const doclets = loadDocData(docPath);

  if (!doclets) {
    console.error(`\u274c Error: Documentation not found at ${docPath}`);
    process.exit(1);
  }

  // JSDoc JSON 是数组
  const docletArray = Array.isArray(doclets) ? doclets : [];

  if (docletArray.length === 0) {
    console.error('\u274c Error: No doclets found in the documentation.');
    process.exit(1);
  }

  // 构建 longname -> doclet[] 多值索引
  const index = {};
  for (const d of docletArray) {
    const key = d.longname;
    if (key) {
      if (!index[key]) index[key] = [];
      index[key].push(d);
      if (key.includes('#') || key.includes('~')) {
        const dotKey = key.replace('#', '.').replace('~', '.');
        if (!index[dotKey]) index[dotKey] = [];
        index[dotKey].push(d);
      }
    }
  }

  // 按 parent 分组成员
  const membersByParent = {};
  for (const d of docletArray) {
    if (d.memberof) {
      if (!membersByParent[d.memberof]) membersByParent[d.memberof] = [];
      membersByParent[d.memberof].push(d);
    }
  }

  const result = searchInDoclets(queryString, docletArray, index, membersByParent);

  if (result) {
    printFormattedResult(result, membersByParent);
  } else {
    console.log(`\uD83D\uDD0D No API found for query: "${queryString}"`);
    console.log('   Tip: Use the exact symbol name or dotted path (e.g. "UserService.findUser").');
  }
}

// --- 3. 搜索逻辑 ---
function searchInDoclets(query, doclets, index, membersByParent) {
  if (index[query]) {
    const best = pickBestDoclet(index[query]);
    if (best) return best;
  }

  const parts = query.split('.');
  const topName = parts[0];
  const rest = parts.slice(1);

  const candidates = doclets.filter(d =>
    d.name === topName &&
    (d.kind !== 'member' || !d.memberof)
  );

  let top = pickBestDoclet(candidates);

  if (!top) {
    const member = doclets.find(d => d.name === topName && d.memberof === topName);
    if (member) {
      top = { name: member.memberof, kind: 'class', longname: member.memberof };
    }
  }

  if (!top) return null;
  if (rest.length === 0) return top;

  return findMember(top, rest, membersByParent);
}

function findMember(parent, parts, membersByParent) {
  const currentPart = parts[0];
  const nextParts = parts.slice(1);

  const parentName = parent.longname || parent.name;
  const children = membersByParent[parentName] || [];

  const child = children.find(c => c.name === currentPart);
  if (!child) return null;
  if (nextParts.length === 0) return child;

  return findMember(child, nextParts, membersByParent);
}

// --- 4. 美化输出 ---
function printFormattedResult(doclet, membersByParent) {
  console.log('\n\u2705 Found API:');
  console.log('='.repeat(60));

  console.log(`\uD83D\uDCCC Name:       ${doclet.name || doclet.longname}`);
  console.log(`\uD83C\uDFF7\uFE0F  Kind:       ${doclet.kind || 'N/A'}`);

  if (doclet.scope && doclet.memberof) {
    console.log(`\uD83D\uDCC2 Member of:  ${doclet.memberof} (${doclet.scope})`);
  }

  if (doclet.description) {
    console.log(`\uD83D\uDCDD Description: ${doclet.description.trim()}`);
  }
  if (doclet.classdesc) {
    console.log(`   Class desc: ${doclet.classdesc.trim()}`);
  }

  if (doclet.tags && doclet.tags.length > 0) {
    doclet.tags.forEach(tag => {
      const tagText = tag.text ? ` ${tag.text.trim()}` : '';
      console.log(`   @${tag.tag}:${tagText}`);
    });
  }

  if (doclet.type && doclet.type.names) {
    console.log(`\uD83D\uDD24 Type:        ${doclet.type.names.join(' | ')}`);
  }

  if (doclet.params && doclet.params.length > 0) {
    console.log(`\n\uD83D\uDD27 Signature:  ${doclet.name}(${doclet.params.map(p => p.name).join(', ')})`);
    console.log('   Parameters:');
    doclet.params.forEach(p => {
      const type = p.type && p.type.names ? p.type.names.join(' | ') : 'any';
      const desc = p.description || 'No description';
      const optional = p.optional ? ' (optional)' : '';
      const defaultVal = p.defaultvalue !== undefined ? ` = ${p.defaultvalue}` : '';
      console.log(`     - ${p.name}: ${type}${optional}${defaultVal}`);
      console.log(`       \u21B3 ${desc.trim()}`);
    });
  }

  if (doclet.returns && doclet.returns.length > 0) {
    const ret = doclet.returns[0];
    const returnType = ret.type && ret.type.names ? ret.type.names.join(' | ') : 'void';
    const returnDesc = ret.description || '';
    console.log(`   \u21A9\uFE0F  Returns:    ${returnType}`);
    if (returnDesc) console.log(`       \u21B3 ${returnDesc.trim()}`);
  }

  if (doclet.kind === 'class' || doclet.kind === 'namespace') {
    const parentName = doclet.longname || doclet.name;
    if (membersByParent && membersByParent[parentName]) {
      const members = membersByParent[parentName];
      const publicMembers = members.filter(m => !m.access || m.access !== 'private');
      if (publicMembers.length > 0) {
        console.log(`\n\uD83D\uDCE6 Members (${publicMembers.length}):`);
        publicMembers.forEach(m => {
          const prefix = m.scope === 'static' ? '\u25B8 static' : '\u25B8 instance';
          console.log(`   ${prefix} ${m.name}${m.kind === 'function' ? '()' : ''}`);
        });
      }
    }
  }

  console.log('='.repeat(60) + '\n');
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
}

main(query, finalDocPath);

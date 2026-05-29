## JavaScript API Explorer

> **CLI usage examples**: See [SKILL.md](SKILL.md) for full CLI reference and query examples.

For JavaScript projects, the skill leverages **JSDoc** to generate documentation in JSON format, which is then queried by the **`javascript-api-explorer`** CLI tool.

## Prerequisites

Make sure JSDoc is installed globally:

```bash
npm install -g jsdoc
```

## How to Generate Docs for a JavaScript Project

Below is the step-by-step process for adding documentation to a JavaScript project that currently has none.

### 1. Create `jsdoc.json` Configuration

Create a `jsdoc.json` in the project root to control source scanning:

```json
{
  "source": {
    "include": ["src"],
    "includePattern": ".+\\.js$"
  },
  "opts": {
    "destination": "docs",
    "recurse": true
  },
  "plugins": []
}
```

| Field | Purpose |
|---|---|
| `source.include` | Directories or files to scan for documentation. |
| `source.includePattern` | Only scan `.js` files. |
| `opts.destination` | Directory for generated HTML documentation. |
| `opts.recurse` | Scan subdirectories recursively. |

### 2. Add JSDoc Annotations to Source Code

Document your API using JSDoc tags. The `javascript-api-explorer` uses the JSON output from `jsdoc -X`, which parses these annotations:

```javascript
/**
 * A brief description of the function.
 *
 * @param {string} name - Description of the parameter.
 * @param {number} [age] - Optional parameter with description.
 * @returns {Object} Description of the return value.
 * @throws {Error} When something goes wrong.
 * @example
 * const result = myFunction("hello", 25);
 */
function myFunction(name, age) { ... }
```

Common JSDoc annotations:

| Tag | Purpose |
|---|---|
| `@param {type} name - desc` | Document a parameter. Wrap optional params in `[]`. |
| `@returns {type} desc` | Document the return value. |
| `@throws {type} desc` | Document possible errors. |
| `@class` | Mark a function as a class (constructor). |
| `@constructor` | Same as `@class`. |
| `@static` | Mark a method as static. |
| `@private` | Hide from generated docs. |
| `@public` | Explicitly mark as public. |
| `@typedef {Object} Name` | Define a custom type. |
| `@property {type} name - desc` | Define a property on a `@typedef`. |
| `@enum {type}` | Define an enum-like constant. |
| `@readonly` | Mark as read-only. |
| `@example` | Provide usage example. |

> **Tip**: For class methods, JSDoc automatically detects instance vs static scope. For complex types, use `@typedef` to define them separately.

### 3. Generate Documentation

Run JSDoc to generate both HTML and JSON:

```bash
# Generate HTML docs (to ./docs/)
jsdoc -c jsdoc.json -d docs

# Generate JSON doc data (the file consumed by api-explorer)
jsdoc -X -c jsdoc.json > docs/api-docs.json
```

> **Note**: The `-X` flag tells JSDoc to output the raw doclet JSON array to stdout, which we redirect into `api-docs.json`.

This generates:
- `docs/index.html` and HTML pages — viewable in a browser
- `docs/api-docs.json` — the JSON file consumed by `javascript-api-explorer`

### 4. Query with `javascript-api-explorer`

See [SKILL.md](SKILL.md) for complete CLI usage and query examples.

```bash
node path/to/javascript-api-explorer.js --doc-path ./docs/ ClassName.methodName
```

## The JSON Format

`jsdoc -X` produces a flat array of doclet objects. Each doclet represents one documented symbol:

```json
[
  {
    "kind": "class",
    "name": "UserService",
    "longname": "UserService",
    "description": "用户服务类...",
    "params": [],
    "returns": []
  },
  {
    "kind": "function",
    "name": "findUser",
    "longname": "UserService#findUser",
    "memberof": "UserService",
    "scope": "instance",
    "description": "根据 ID 查找用户。",
    "params": [
      {
        "name": "id",
        "type": { "names": ["string"] },
        "description": "要查找的用户 ID"
      }
    ],
    "returns": [
      {
        "type": { "names": ["Promise.<(User|null)>"] },
        "description": "返回用户对象..."
      }
    ]
  }
]
```

Key fields:
- `longname` — dotted path for static (`UserService.getInstance`), `#`-separated for instance (`UserService#findUser`)
- `kind` — `class`, `function`, `constant`, `member`, `typedef`, `enum`, `event`
- `scope` — `global`, `static`, `instance`, `inner`
- `memberof` — the parent class/namespace name
- `params` — array of parameter objects with `name`, `type.names`, `description`
- `returns` — array of return objects

## Example Project

A fully configured example is available at `javascript-api-doc-cli/example/`. It contains:

- **3 modules**: `UserService`, `LoggerService`, `ProductService` (in a subfolder `src/product/`)
- **`jsdoc.json`** configured for recursive source scanning
- **`package.json`** with `"docs"` script

To regenerate its docs:

```bash
cd javascript-api-doc-cli/example
npm run docs
```

Then explore:

See [SKILL.md](SKILL.md) for more query examples.

```bash
node ../javascript-api-explorer.js --doc-path ./docs/ UserService
node ../javascript-api-explorer.js --doc-path ./docs/ UserService.findUser
node ../javascript-api-explorer.js --doc-path ./docs/ ProductService.createProduct
node ../javascript-api-explorer.js --doc-path ./docs/ LoggerService.info
node ../javascript-api-explorer.js --doc-path ./docs/ LogLevel
```

### package the docs

add this lines into project's package.json
```json
  "files": [
    "dist",
    "docs"  // 把 docs 目录加进来
  ],
```

### Expected Output

```
✅ Found API:
============================================================
📌 Name:       UserService
🏷️  Kind:       class
   Class desc: 用户服务类，负责处理用户的增删改查。

📦 Members (6):
   ▸ static getInstance()
   ▸ static _instance
   ▸ instance findUser()
   ▸ instance listUsers()
   ▸ instance createUser()
   ▸ instance deleteUser()
============================================================
```

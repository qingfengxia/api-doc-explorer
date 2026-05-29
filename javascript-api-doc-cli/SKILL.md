```yaml
- name: JavaScript API Doc Explorer CLI
- description: Query pre-built JSDoc JSON documentation for JavaScript projects. Supports class and method level queries.
- version: "0.2.0"
```

## When to Use

- Explore a JavaScript SDK you were not trained on
- Look up exact method signatures, parameters, return types, or doc comments
- Discover what classes/functions a module exports

---

## CLI Usage

```bash
node javascript-api-explorer.js [--doc-path <path>] <query>
```

### Options

| Option | Description |
|--------|-------------|
| `--doc-path <dir>` | Directory containing `api-docs.json`. If omitted, auto-discovers from `node_modules/<pkg>/docs/` |
| `--help` | Show help message |

### Query Format

Dotted query narrows scope: `Class.method`

### Examples

```bash
# Class level — show doc + all member signatures
node javascript-api-explorer.js --doc-path ./docs/ UserService

# Method level — full signature, params, return type, doc
node javascript-api-explorer.js --doc-path ./docs/ UserService.findUser
node javascript-api-explorer.js --doc-path ./docs/ ProductService.createProduct
node javascript-api-explorer.js --doc-path ./docs/ LoggerService.info
node javascript-api-explorer.js --doc-path ./docs/ LogLevel
```

---

## Prerequisite: Generate Documentation

See [Readme.md](Readme.md) for how to generate `api-docs.json` using JSDoc `-X`.

---

## Query Levels

| Level | Example | Returns |
|-------|---------|---------|
| Class | `UserService` | Doc + all member signatures |
| Method | `UserService.findUser` | Full signature, params, return type, doc |

If a specific query fails, **broaden it** (drop the method name) to discover what's available.

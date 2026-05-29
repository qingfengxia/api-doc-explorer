```yaml
- name: TypeScript API Doc Explorer CLI
- description: Query pre-built TypeDoc JSON documentation for TypeScript/JavaScript projects. Supports module, class, and method level queries.
- version: "0.2.0"
```

## When to Use

- Explore a TypeScript/JavaScript SDK you were not trained on
- Look up exact method signatures, parameters, return types, or doc comments
- Discover what classes/functions a module exports
- Fallback: explore `.d.ts` declaration files when no docs JSON is available

---

## CLI Usage

```bash
node typescript-api-explorer.js [--doc-path <path>] <query>
```

### Options

| Option | Description |
|--------|-------------|
| `--doc-path <dir>` | Directory containing `api-docs.json`. If omitted, auto-discovers from `node_modules/<pkg>/docs/` |
| `--help` | Show help message |

### Query Format

Dotted query narrows scope: `Module.Class.method`

### Examples

```bash
# Module level — list all classes in a module
node typescript-api-explorer.js --doc-path ./docs/ UserService

# Class level — show doc + all member signatures
node typescript-api-explorer.js --doc-path ./docs/ UserService

# Method level — full signature, params, return type, doc
node typescript-api-explorer.js --doc-path ./docs/ UserService.findUser

# .d.ts fallback — auto-searches src/, dist/, lib/, types/ for .d.ts files
node typescript-api-explorer.js --doc-path ./docs/ ProductService
```

---

## Prerequisite: Generate Documentation

See [Readme.md](Readme.md) for how to generate `api-docs.json` using TypeDoc.

---

## Query Levels

| Level | Example | Returns |
|-------|---------|---------|
| Module | `UserService` | All exported classes/interfaces/enums |
| Class | `UserService` | Doc + all member signatures |
| Method | `UserService.findUser` | Full signature, params, return type, doc |

If a specific query fails, **broaden it** (drop the method name) to discover what's available.

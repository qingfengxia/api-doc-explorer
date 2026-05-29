```yaml
- name: Rust API Doc Explorer CLI
- description: Query pre-built rustdoc JSON documentation for Rust projects. Supports struct, enum, function, and method level queries.
- version: "0.2.0"
```

## When to Use

- Explore a Rust crate/SDK you were not trained on
- Look up exact function signatures, parameters, return types, or doc comments
- Discover what structs/enums/functions a crate exports

---

## CLI Usage

```bash
python3 rust-api-explorer.py [--doc-path <path>] <query>
```

### Options

| Option | Description |
|--------|-------------|
| `--doc-path <dir>` | Directory containing `api-docs.json`. If omitted, defaults to `./docs/` |
| `--help` | Show help message |

### Query Format

Dotted query narrows scope: `Struct.method`

### Examples

```bash
# Struct level — doc + fields + all method signatures
python3 rust-api-explorer.py --doc-path ./docs/ LoggerService

# Method level — full signature, params, return type, doc
python3 rust-api-explorer.py --doc-path ./docs/ LogEntry.new

# Function level
python3 rust-api-explorer.py --doc-path ./docs/ add

# Enum level — doc + variants
python3 rust-api-explorer.py --doc-path ./docs/ ProductCategory

# Field level
python3 rust-api-explorer.py --doc-path ./docs/ Product.id
```

---

## Prerequisite: Generate Documentation

See [Readme.md](Readme.md) for how to generate `api-docs.json` using `rustdoc --output-format json` (nightly) or `gen_docs.py` (stable).

---

## Query Levels

| Level | Example | Returns |
|-------|---------|---------|
| Struct | `LoggerService` | Doc + fields + method signatures |
| Enum | `ProductCategory` | Doc + variants |
| Function | `add` | Full signature, params, return type, doc |
| Method | `LoggerService.info` | Full signature, params, return type, doc |

If a specific query fails, **broaden it** (drop the method name) to discover what's available.

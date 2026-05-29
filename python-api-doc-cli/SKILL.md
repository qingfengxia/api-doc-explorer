```yaml
- name: Python API Doc Explorer CLI
- description: Query Python API documentation via runtime introspection (inspect module). Supports module, class, and method level queries. No doc generation required.
- version: "0.2.0"
```

## When to Use

- Explore a Python SDK/library you were not trained on
- Look up exact method signatures, parameters, return types, or docstrings
- Discover what classes/functions a module exports
- Works with any installed Python package (including complex packages like `torch.distributed`)

---

## CLI Usage

```bash
python3 python_api_explorer.py [--output-json] <query>
```

### Options

| Option | Description |
|--------|-------------|
| `--output-json` | Output in JSON format (for programmatic use). Default: human-readable |
| `--help` | Show help message |

### Query Format

Dotted path narrows scope: `module.Class.method`

### Examples

```bash
# Module level — list all classes/functions
python3 python_api_explorer.py json
python3 python_api_explorer.py torch.distributed

# Class level — doc + all method signatures
python3 python_api_explorer.py json.JSONEncoder
python3 python_api_explorer.py torch.distributed.Backend

# Method level — full signature, params, return type, doc
python3 python_api_explorer.py json.dumps
python3 python_api_explorer.py torch.distributed.Backend.register_backend

# JSON output (for programmatic use)
python3 python_api_explorer.py --output-json json.dumps
```

---

## No Prerequisite: Runtime Introspection

Python keeps API doc inside the module at runtime, so no doc generation step is needed. Just install the package and query.

If a `api-docs.json` is required, see [Readme.md](Readme.md) for how to generate it using `gen_docs.py`.

---

## Query Levels

| Level | Example | Returns |
|-------|---------|---------|
| Module | `json` / `torch.distributed` | All classes/functions in the module |
| Class | `json.JSONEncoder` | Docstring + all method signatures |
| Method | `json.dumps` | Full signature, params, return type, docstring |

If a specific query fails, **broaden it** (drop the method name) to discover what's available.

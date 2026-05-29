```yaml
- name: C/C++ API Doc Explorer CLI
- description: Query pre-built Doxygen XML documentation for C/C++ projects. Supports namespace, class, and method level queries.
- version: "0.2.0"
```

## When to Use

- Explore a C/C++ SDK/library you were not trained on
- Look up exact method signatures, parameters, return types, or doc comments
- Discover what classes/namespaces a library exports

---

## CLI Usage

```bash
python3 cpp-api-explorer.py [--doc-path <path>] <query>
```

### Options

| Option | Description |
|--------|-------------|
| `--doc-path <dir>` | Directory containing Doxygen XML output (`docs/xml/`). If omitted, defaults to `./docs/` |
| `--help` | Show help message |

### Query Format

Both `::` and `.` are accepted as separators; `::` is the standard C++ notation.

### Examples

```bash
# Namespace level — list all types inside
python3 cpp-api-explorer.py --doc-path ./docs/ ROS2

# Class level — doc + all member signatures
python3 cpp-api-explorer.py --doc-path ./docs/ ROS2::RobotComponent
python3 cpp-api-explorer.py --doc-path ./docs/ RobotComponent   # simple name fallback

# Method level — full signature, params, return type, doc
python3 cpp-api-explorer.py --doc-path ./docs/ ROS2::RobotComponent::Initialize
python3 cpp-api-explorer.py --doc-path ./docs/ ROS2::RobotComponent.Initialize
```

---

## Prerequisite: Generate Documentation

See [Readme.md](Readme.md) for how to generate Doxygen XML documentation.

---

## Query Levels

| Level | Example | Returns |
|-------|---------|---------|
| Namespace | `ROS2` | All classes/structs in the namespace |
| Class | `ROS2::RobotComponent` | Doc + all member signatures |
| Method | `ROS2::RobotComponent::Initialize` | Full signature, params, return type, doc |

If a specific query fails, **broaden it** (drop the method name) to discover what's available.

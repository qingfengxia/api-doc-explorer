```yaml
- name: API Documentation Explorer
- description: A code-agent skill for instant, structured API documentation retrieval across 6 languages. Agents query pre-built JSON docs instead of scanning source code.
- version: "0.2.0"
```

## When to Use

- Understand a private SDK/library you were not trained on
- Look up exact method signatures, parameters, return types, or doc comments
- Discover what classes/functions a package exposes
- Avoid reading large source files for one API detail

## Prerequisite: Generate Documentation First

If the project has no `docs/` folder or packaged JSON docs, generate them. See each language's README:

| Language | Doc Generator | Guide |
|---|---|---|
| TypeScript | TypeDoc | [typescript/Readme.md](typescript/Readme.md) |
| JavaScript | JSDoc `-X` | [javascript/Readme.md](javascript/Readme.md) |
| Java | Custom Doclet | [Java/Readme.md](Java/Readme.md) |
| Rust | rustdoc JSON / gen_docs.py | [rust/Readme.md](rust/Readme.md) |
| C/C++ | Doxygen (XML) | [cpp/Readme.md](cpp/Readme.md) |
| Python | *(none — runtime introspection)* | — |

---

## API Explorer CLI Usage

All explorers follow the pattern: `<explorer-cli> [--doc-path <path>] <dotted.query>`

- `--doc-path` — directory containing the generated docs. If omitted, TS/JS explorers auto-discover from `node_modules/<pkg>/docs/`.
- Dotted query narrows scope: package → class → method.

### TypeScript

```bash
node typescript-api-explorer.js --doc-path ./docs/ UserService
node typescript-api-explorer.js --doc-path ./docs/ UserService.findUser
```

### JavaScript

```bash
node javascript-api-explorer.js --doc-path ./docs/ UserService
node javascript-api-explorer.js --doc-path ./docs/ UserService.findUser
```

### Java

if apidocs.json provided by javadoc + doclet, three levels of API is suported `package/module->class->method`
```bash
# if GlassGraph is available, children class/subpackage/module can be explored
java -cp target/classes JavaApiExplorer com.example.service
# via java reflection mechanism, class API can be explored, without api-docs
java -cp target/classes JavaApiExplorer com.example.service.UserService.createUser
# if apidocs.json provided, details
java -cp target/classes JavaApiExplorer com.example.service.UserService.createUser

```

### OpenAPI

For Java OpenAPI, swagger cli can be used to explore API documentation


### Rust

```bash
python3 rust-api-explorer.py --doc-path ./docs/ LoggerService
python3 rust-api-explorer.py --doc-path ./docs/ LoggerService.info
```

### C/C++

```bash
python3 cpp-api-explorer.py --doc-path ./docs/ ROS2::RobotComponent
python3 cpp-api-explorer.py --doc-path ./docs/ ROS2::RobotComponent::Initialize
python3 cpp-api-explorer.py --doc-path ./docs/ RobotComponent              # simple name fallback
```

### Python

```bash
python3 python_api_explorer.py json
python3 python_api_explorer.py json.dumps
```

---

## Query Levels

| Level | Example | Returns |
|---|---|---|
| Package/Module | `com.example.service` / `json` | All classes/APIs in the scope |
| Class/Struct | `UserService` / `LoggerService` | Doc + all member signatures |
| Method/Function | `UserService.findUser` / `add` | Full signature, params, return type, doc |

If a specific query fails, **broaden it** (drop the method name) to discover what's available, then query again.

---

## Quick Reference

| Language | Explorer CLI | Query Format |
|---|---|---|
| TypeScript | `node typescript-api-explorer.js` | `Module.Class.method` |
| JavaScript | `node javascript-api-explorer.js` | `Class.method` |
| Java | `java JavaApiExplorer` | `pkg.Class.method` |
| Rust | `python3 rust-api-explorer.py` | `Struct.method` |
| C/C++ | `python3 cpp-api-explorer.py` | `ns::Class::method` or `ns::Class.method` |
| Python | `python3 python_api_explorer.py` | `module.Class.method` |

```yaml
- name: api-doc-explorer
- description: A code-agent CLI skill for instant, structured API documentation retrieval across 6 languages. Agents query pre-built JSON docs instead of scanning source code.
- version: "0.2.0"
```

## When to Use

- Understand a private SDK/library you were not trained on
- Look up exact method signatures, parameters, return types, or doc comments
- Discover what classes/functions a package exposes
- Avoid reading large source files for one API detail

---

## Per-Language CLI Skills

Each language subfolder is a self-contained skill with its own `SKILL.md`:

| Language | Skill Path | Explorer CLI |
|----------|-----------|--------------|
| TypeScript | [typescript-api-doc-cli/SKILL.md](typescript-api-doc-cli/SKILL.md) | `node typescript-api-explorer.js` |
| JavaScript | [javascript-api-doc-cli/SKILL.md](javascript-api-doc-cli/SKILL.md) | `node javascript-api-explorer.js` |
| Java | [java-api-doc-cli/SKILL.md](java-api-doc-cli/SKILL.md) | `java JavaApiExplorer` |
| Rust | [rust-api-doc-cli/SKILL.md](rust-api-doc-cli/SKILL.md) | `python3 rust-api-explorer.py` |
| C/C++ | [cpp-api-doc-cli/SKILL.md](cpp-api-doc-cli/SKILL.md) | `python3 cpp-api-explorer.py` |
| Python | [python-api-doc-cli/SKILL.md](python-api-doc-cli/SKILL.md) | `python3 python_api_explorer.py` |

---

## Prerequisite: Generate Documentation First

If the project has no `docs/` folder or packaged JSON docs, generate them. See each language's README:

| Language | Doc Generator | Guide |
|----------|--------------|-------|
| TypeScript | TypeDoc | [typescript-api-doc-cli/Readme.md](typescript-api-doc-cli/Readme.md) |
| JavaScript | JSDoc `-X` | [javascript-api-doc-cli/Readme.md](javascript-api-doc-cli/Readme.md) |
| Java | Custom Doclet | [java-api-doc-cli/Readme.md](java-api-doc-cli/Readme.md) |
| Rust | rustdoc JSON / gen_docs.py | [rust-api-doc-cli/Readme.md](rust-api-doc-cli/Readme.md) |
| C/C++ | Doxygen (XML) | [cpp-api-doc-cli/Readme.md](cpp-api-doc-cli/Readme.md) |
| Python | *(none — runtime introspection)* | — |

> NOTE: 
> If Java and typescript docs are not generated, basic info can still be extracted from Java reflection or typescript d.ts file downloadable
---

## Query Levels

All explorers follow the same pattern: `<explorer-cli> [--doc-path <path>] <dotted.query>`

| Level | Example | Returns |
|-------|---------|---------|
| Package/Module | `com.example.service` / `json` | All classes/APIs in the scope |
| Class/Struct | `UserService` / `LoggerService` | Doc + all member signatures |
| Method/Function | `UserService.findUser` / `add` | Full signature, params, return type, doc |

If a specific query fails, **broaden it** (drop the method name) to discover what's available, then query again.

---

## Quick Reference

| Language | Explorer CLI | Query Format |
|----------|-------------|--------------|
| TypeScript | `node typescript-api-explorer.js` | `Module.Class.method` |
| JavaScript | `node javascript-api-explorer.js` | `Class.method` |
| Java | `java JavaApiExplorer` | `pkg.Class.method` |
| Rust | `python3 rust-api-explorer.py` | `Struct.method` |
| C/C++ | `python3 cpp-api-explorer.py` | `ns::Class::method` or `ns::Class.method` |
| Python | `python3 python_api_explorer.py` | `module.Class.method` |

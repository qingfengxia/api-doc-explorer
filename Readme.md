# API Doc Explorer Skill

**Runtime API documentation retrieval for AI agents — no source code scanning required.**

When an LLM-based agent works with a private SDK or large-scale codebase it was never trained on, it faces a fundamental problem: it doesn't know the APIs. Searching source files is slow, blows up the context window, and often returns stale or ambiguous results. **API Doc Explorer** solves this by shipping pre-built JSON documentation alongside packages, then querying it instantly at runtime.

> Successfully used in production on a **1.5 M-line** private project.

---

## Install This Skill

```bash
# cd to your  agent's skills folder
git clone https://github.com/qingfengxia/api-doc-explorer.git
```

## Why You Need This

| Pain Point | Without API Doc Explorer | With API Doc Explorer |
|---|---|---|
| Context bloat | Agent must read hundreds of source files | Single targeted JSON query |
| Stale / broken APIs | Agent guesses from outdated training data | Docs are built and version-locked with the package |
| Slow retrieval | Full-text search across codebase | Sub-second structured lookup |
| Writing N skills | One skill per SDK/API | One universal skill for all languages |

Instead of writing dozens of teaching skills for every private SDK, just ship `ModuleArch.md` + `CodeStructure.md` and let the agent explore APIs on demand.

---

## How It Works

```
Source Code + Doc Comments
         ↓
   Doc Generator (typedoc / jsdoc / javadoc / rustdoc / doxygen / Python inspect)
         ↓
   api-docs.json  ←  shipped inside the package
         ↓
   xxx-api-explorer CLI  ←  agent calls this at runtime
         ↓
   Structured API info returned instantly
```

1. **Build time** — documentation is generated from source code comments and packaged as JSON.
2. **Install time** — the JSON file ships inside the published package (npm, Maven, crates.io, etc.).
3. **Runtime** — the agent invokes the language-specific explorer CLI to query exactly the API it needs.

---

## Supported Languages

| Language | Doc Generator | Packaged Doc Path | Explorer CLI |
|---|---|---|---|
| **TypeScript** | [TypeDoc](https://typedoc.org/) | `docs/api-docs.json` | `node typescript-api-explorer.js --doc-path ./docs/ ModuleName.method` |
| **JavaScript** | [JSDoc](https://jsdoc.app/) (`-X` flag) | `docs/api-docs.json` | `node javascript-api-explorer.js --doc-path ./docs/ ClassName.method` |
| **Java** | Custom [Doclet](Java/ApiDoclet.java) + `javadoc` | `target/classes/api-doc.json` | `java JavaApiExplorer com.example.ClassName.method` |
| **Rust** | `rustdoc --output-format json` (nightly) or `gen_docs.py` (stable) | `docs/api-docs.json` | `python3 rust-api-explorer.py --doc-path ./docs/ StructName.method` |
| **C/C++** | [Doxygen](https://www.doxygen.nl/) (XML output) | `docs/xml/` | `python3 cpp-api-explorer.py --doc-path ./docs/ namespace::Class::method` |
| **Python** | Runtime introspection (`inspect` module) | *(none — live reflection)* | `python3 python_api_explorer.py module_path.ClassName.method` |

### Key Features

- **Zero third-party runtime deps** — Node.js explorers use only the built-in runtime; Python explorers need only Python 3.6+.
- **Auto-discovery** — if `--doc-path` is omitted, TS/JS explorers search `node_modules/<pkg>/docs/` automatically.
- **Split-doc support** — handles multi-file JSON docs (`subpackage/module.json` pattern) out of the box.
- **Cross-platform** — Python-based explorers (Rust, C++) work on any OS with Python installed.

---

## Quick Start

### TypeScript

```bash
cd your-ts-project
npm install --save-dev typedoc
npx typedoc                        # generates docs/api-docs.json
node typescript-api-explorer.js --doc-path ./docs/ UserService.findUser
```

### JavaScript

```bash
cd your-js-project
npm install -g jsdoc
jsdoc -X -c jsdoc.json > docs/api-docs.json
node javascript-api-explorer.js --doc-path ./docs/ UserService.findUser
```

### Java

```bash
cd your-maven-project
mvn package                       # runs ApiDoclet, produces api-doc.json
java -cp target/classes com.example.JavaApiExplorer com.example.UserService.createUser
```

### Rust

```bash
cd your-crate
RUSTDOCFLAGS="-Z unstable-options --output-format json" cargo +nightly doc --no-deps --lib
cp target/doc/your_crate.json docs/api-docs.json
python3 rust-api-explorer.py --doc-path ./docs/ LoggerService.info
```

### C/C++

```bash
doxygen Doxyfile                   # generates docs/xml/
python3 cpp-api-explorer.py --doc-path ./docs/ namespace::Class::method
# Both '::' and '.' separators work: namespace::Class.method is equivalent
```

### Python

```bash
python3 python_api_explorer.py json.dumps
python3 python_api_explorer.py collections.abc.Iterable
```

---

## Project Structure

```
api-explorer-skill/
├── SKILL.md                       # Agent skill definition
├── build_and_test_all.sh          # CI orchestrator
├── typescript/
│   ├── typescript-api-explorer.js
│   ├── build.sh / test.sh
│   ├── Readme.md
│   └── example/                   # Full TS project with typedoc.json
```
other language has a similar subfolder structure as `typescript`
---

## Adding a New Language

1. Follow the pattern of an existing language folder.
2. Create: `xxx-api-explorer` CLI, `build.sh`, `test.sh`, `Readme.md`, and an `example/` project.
3. Add a line in `build_and_test_all.sh` for the new language.
4. Update this Readme's supported-languages table.

The entire project was built by vibe-coding — adding another language is straightforward.

---

## Roadmap

- [ ] Unified `api-explorer` CLI wrapper for all languages
- [ ] GitHub CI pipeline for per-language build & test
- [ ] English-first example code across all languages
- [ ] performance:  split api-docs.json into multiple files (partially supported)
- [ ] robustness: not all language feature is suported

---

## License

MIT

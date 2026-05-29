# API Doc Explorer Skill and CLI for AI Code Agent

**Runtime API documentation retrieval for AI agents — no source code scanning required.**

When an LLM-based agent works with a private SDK or large-scale codebase it was never trained on, it faces a fundamental problem: it doesn't know the APIs. Searching source files is slow, blows up the context window, and often returns stale or ambiguous results. **API Doc Explorer** solves this by shipping pre-built JSON documentation alongside packages, then querying it instantly at runtime.

> Successfully used in production on a **1.5 M-line** private project.

Instead of tens of skills to describe a private SDK, an `Arch.md` (with module and code structure) assisted by this api-explorer skill will let the LLM understand how to use the API.

---

## Install This Skill (All language CLI include)

```bash
# cd to your agent's skills folder
git clone https://github.com/qingfengxia/api-doc-explorer.git
```

## Why You Need This

| Pain Point | Without API Doc Explorer | With API Doc Explorer |
|---|---|---|
| Context bloat | Agent must read hundreds of source files | Single targeted JSON query |
| Stale / broken APIs | Agent guesses from outdated training data | Docs are built and version-locked with the package |
| Slow retrieval | Full-text search across codebase | Sub-second structured lookup |
| Writing N skills | One skill per SDK/API | One universal skill for all languages |

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
| **Java** | Custom Doclet + `javadoc` | `target/classes/api-doc.json` | `java JavaApiExplorer com.example.ClassName.method` |
| **Rust** | `rustdoc --output-format json` (nightly) or `gen_docs.py` (stable) | `docs/api-docs.json` | `python3 rust-api-explorer.py --doc-path ./docs/ StructName.method` |
| **C/C++** | [Doxygen](https://www.doxygen.nl/) (XML output) | `docs/xml/` | `python3 cpp-api-explorer.py --doc-path ./docs/ namespace::Class::method` |
| **Python** | Runtime introspection (`inspect` module) | *(none — live reflection)* | `python3 python_api_explorer.py module_path.ClassName.method` |

### Key Design Features

- **Zero third-party runtime deps** — Node.js explorers use only the built-in runtime; Python explorers need only Python 3.6+.
- **Auto-discovery** — if `--doc-path` is omitted, TS/JS explorers search `node_modules/<pkg>/docs/` automatically.
- **Split-doc support** — handles multi-file JSON docs (`subpackage/module.json` pattern) out of the box.
- **Cross-platform** — Python-based explorers (Rust, C++) work on any OS with Python installed.
- **Reflection fallback** — Java explorer can fall back to runtime reflection when no JSON doc is available.
- **JAR exploration** — Java explorer supports `--jar` to explore any JAR file's packages and classes.

---

## Per-Language Skills

Each language subfolder is a self-contained skill with its own `SKILL.md` for CLI usage and `Readme.md` for design/doc-generation details:

| Language | Skill | Design & Doc Generation |
|----------|-------|------------------------|
| TypeScript | [typescript-api-doc-cli/SKILL.md](typescript-api-doc-cli/SKILL.md) | [typescript-api-doc-cli/Readme.md](typescript-api-doc-cli/Readme.md) |
| JavaScript | [javascript-api-doc-cli/SKILL.md](javascript-api-doc-cli/SKILL.md) | [javascript-api-doc-cli/Readme.md](javascript-api-doc-cli/Readme.md) |
| Java | [java-api-doc-cli/SKILL.md](java-api-doc-cli/SKILL.md) | [java-api-doc-cli/Readme.md](java-api-doc-cli/Readme.md) |
| Rust | [rust-api-doc-cli/SKILL.md](rust-api-doc-cli/SKILL.md) | [rust-api-doc-cli/Readme.md](rust-api-doc-cli/Readme.md) |
| C/C++ | [cpp-api-doc-cli/SKILL.md](cpp-api-doc-cli/SKILL.md) | [cpp-api-doc-cli/Readme.md](cpp-api-doc-cli/Readme.md) |
| Python | [python-api-doc-cli/SKILL.md](python-api-doc-cli/SKILL.md) | [python-api-doc-cli/Readme.md](python-api-doc-cli/Readme.md) |

---

## Project Structure

```
api-explorer-skill/
├── SKILL.md                       # Agent skill definition (this project)
├── README.md                      # Design & principles (this file)
├── build_and_test_all.sh          # CI orchestrator
├── typescript-api-doc-cli/
│   ├── SKILL.md                   # TypeScript CLI skill
│   ├── Readme.md                  # Doc generation guide
│   ├── typescript-api-explorer.js
│   ├── build.sh / test.sh
│   └── example/
├── javascript-api-doc-cli/
│   └── ... (similar structure)
├── java-api-doc-cli/
│   └── ... (similar structure)
├── rust-api-doc-cli/
│   └── ... (similar structure)
├── cpp-api-doc-cli/
│   └── ... (similar structure)
└── python-api-doc-cli/
    └── ... (similar structure)
```

---

## Adding a New Language (prompt template)

1. Follow the pattern of an existing language folder such as `typescript-api-doc-cli`.
2. Create: `xxx-api-explorer` CLI, `SKILL.md`, `Readme.md`, `build.sh`, `test.sh`, and an `example/` project.
3. Add a line in `build_and_test_all.sh` for the new language.
4. Update this README's supported-languages table.
5. Update root `SKILL.md` with the new language entry.

The entire project was built by vibe-coding — adding another language is straightforward.

---

## Standardization of api-docs.json and CLI

More details in [Readme_ZH.md](Readme_ZH.md)

---

## Roadmap

- [X] Unified `api-explorer` CLI wrapper for all languages
- [X] Java reflection fallback and JAR exploration
- [X] Python human-readable + JSON dual output
- [X] TypeScript `.d.ts` fallback
- [ ] GitHub CI pipeline for per-language build & test
- [ ] English-first example code across all languages
- [ ] Performance: split api-docs.json into multiple files (partially supported)
- [ ] Robustness: not all language features are supported

---

## License

MIT

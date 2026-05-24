# API文档探索器 Skill

**面向 AI Agent 的运行时 API 文档检索——无需扫描源代码。**

当基于大语言模型的 Agent 面对一个从未训练过的私有 SDK 或大规模代码库时，它面临一个根本性问题：不了解 API。搜索源文件速度慢、上下文窗口爆炸，且经常返回过时或模糊的结果。**API Doc Explorer** 通过将预构建的 JSON 文档随包发布，并在运行时即时查询，彻底解决了这一问题。

> 已在一个 **150 万行**的私有项目中成功投入生产使用。

---

## 为什么你需要它

| 痛点 | 没有 API Doc Explorer | 有 API Doc Explorer |
|---|---|---|
| 上下文膨胀 | Agent 必须阅读数百个源文件 | 单次精准 JSON 查询 |
| API 过时/损坏 | Agent 根据过时训练数据猜测 | 文档随包构建、版本锁定 |
| 检索缓慢 | 全文搜索整个代码库 | 亚秒级结构化查询 |
| 编写 N 个 Skill | 每个 SDK/API 需要一个 Skill | 一个通用 Skill 覆盖所有语言 |

与其为每个私有 SDK 编写数十个API教程Skill/和documentation到skill的转化，只需提供 `ModuleArch.md` + `CodeStructure.md`，让 Agent 按需探索 API doc。

---

## 工作原理

```
源代码 + 文档注释
         ↓
   文档生成器（typedoc / jsdoc / javadoc / rustdoc / doxygen / Python inspect）
         ↓
   api-docs.json  ←  随包发布
         ↓
   xxx-api-explorer CLI  ←  Agent 运行时调用
         ↓
   即时返回结构化 API 信息
```

1. **构建期** — 从源代码注释生成文档，打包为 JSON。
2. **安装期** — JSON 文件随发布包一起分发（npm、Maven、crates.io 等）。
3. **运行时** — Agent 调用各语言的 Explorer CLI 精确查询所需 API。

---

## 支持的语言

| 语言 | 文档生成器 | 打包文档路径 | Explorer CLI |
|---|---|---|---|
| **TypeScript** | [TypeDoc](https://typedoc.org/) | `docs/api-docs.json` | `node typescript-api-explorer.js --doc-path ./docs/ ModuleName.method` |
| **JavaScript** | [JSDoc](https://jsdoc.app/)（`-X` 参数） | `docs/api-docs.json` | `node javascript-api-explorer.js --doc-path ./docs/ ClassName.method` |
| **Java** | 自定义 [Doclet](Java/ApiDoclet.java) + `javadoc` | `target/classes/api-doc.json` | `java JavaApiExplorer com.example.ClassName.method` |
| **Rust** | `rustdoc --output-format json`（nightly）或 `gen_docs.py`（stable） | `docs/api-docs.json` | `python3 rust-api-explorer.py --doc-path ./docs/ StructName.method` |
| **C/C++** | [Doxygen](https://www.doxygen.nl/)（XML 输出） | `docs/xml/` | `python3 cpp-api-explorer.py --doc-path ./docs/ namespace::Class::method` |
| **Python** | 运行时反射（`inspect` 模块） | *（无需——实时反射）* | `python3 python_api_explorer.py module_path.ClassName.method` |

更多的语言可以通过agentic coding拓展, 见后续章节(直接给出prompt模板)

### 核心特性

- **零第三方运行时依赖** — Node.js Explorer 仅使用内置运行时；Python Explorer 仅需 Python 3.6+。
- **自动发现** — 省略 `--doc-path` 时，TS/JS Explorer 自动搜索 `node_modules/<pkg>/docs/`。
- **分片文档支持** — 开箱即支持多文件 JSON 文档（`subpackage/module.json` 模式）。
- **跨平台** — 基于 Python 的 Explorer（Rust、C++）可在任何安装了 Python 的操作系统上运行。

---

## 快速开始

### TypeScript

```bash
cd your-ts-project
npm install --save-dev typedoc
npx typedoc                        # 生成 docs/api-docs.json
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
mvn package                       # 运行 ApiDoclet，生成 docs/api-doc.json
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
doxygen Doxyfile                   # 生成 docs/xml/
python3 cpp-api-explorer.py --doc-path ./docs/ namespace::Class::method
# '::' 和 '.' 分隔符均可使用：namespace::Class.method 等效
```

### Python

```bash
python3 python_api_explorer.py json.dumps
python3 python_api_explorer.py collections.abc.Iterable
```

---

## 项目结构

```
api-explorer-skill/
├── SKILL.md                       # Agent Skill 定义
├── build_and_test_all.sh          # CI 编排器
├── typescript/
│   ├── typescript-api-explorer.js
│   ├── build.sh / test.sh
│   ├── Readme.md
│   └── example/                   # 含 typedoc.json 的完整 TS 项目
├── javascript/
│   ├── javascript-api-explorer.js
│   ├── build.sh / test.sh
│   ├── Readme.md
│   └── example/                   # 含 jsdoc.json 的完整 JS 项目
├── Java/
│   ├── ApiDoclet.java / JavaApiExplorer.java
│   ├── build.sh / test.sh
│   ├── Readme.md
│   └── example/                   # 含 exec-maven-plugin 的 Maven 项目
├── rust/
│   ├── rust-api-explorer.py / gen_docs.py
│   ├── build.sh / test.sh
│   ├── Readme.md
│   └── example/                   # 含 api-docs.json 的 Cargo 项目
├── cpp/
│   ├── cpp-api-explorer.py / Doxyfile
│   ├── build.sh / test.sh
│   └── Readme.md
└── python/
    ├── python_api_explorer.py
    ├── build.sh / test.sh
    └── Readme.md
```

---

## 添加新语言api-explorer的指南(prompt模板)

1. 参照现有语言文件夹(比如typescript)的模式。
2. 创建：`xxx-api-explorer` CLI、`build.sh`、`test.sh`、`Readme.md` 及 `example/` 项目。
3. 在 `build_and_test_all.sh` 中为新语言添加对应语言的CLI构建和example的文档生成脚本, 和单元测试脚本。
4. 更新本 Readme 的支持语言表格。

整个项目均通过 vibe-coding 构建——添加新语言非常简单。

---

## 标准化倡议

见: 知乎文章:  [Agentic Coding 时代的软件工程文档: HTML 给人类，JSON 给 Agents - 知乎](https://zhuanlan.zhihu.com/p/2041867755104752257)

1. 各种文档的代码中API Doc都有标准, 生成的json的文档schema, 理想中应该是语言中性(多语言共用).
2. 单文件文档数据库api-docs.json , 在发布二进制包中的位置, 方便运行时CLI自动查询
3. api-explorer CLI的arguments和输出格式:
4. 大型软件工程的文档拆分为多个json和模块结构index.json (TODO: 未设计)

## 路线图

- [x] 统一的 `api-explorer` CLI 包装器，覆盖所有语言
- [ ] GitHub CI 流水线，按语言构建和测试
- [ ] 所有语言示例代码统一为英文
- [ ] 更多测试, 提升CLI软件质量
- [ ] 大型项目的文档多文件拆分

---

## 许可证

MIT license

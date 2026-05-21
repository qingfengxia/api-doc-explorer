## Rust API Explorer

For Rust projects, documentation is extracted from doc comments (`///` and `//!`) and exported as JSON using `rustdoc`'s `--output-format json` feature. The resulting JSON can then be queried by the **`rust-api-explorer.py`** CLI tool.

## Workflow Overview

```
Rust 源码 (/// 文档注释)
    ↓
rustdoc --output-format json     ← JSON 文档生成
    ↓
api-docs.json                     ← 核心资产
    ↓
rust-api-explorer.py              ← 查询工具
    ↓
终端输出 API 信息
```

## Method 1: Using `rustdoc` with JSON output (Nightly toolchain)

Rustdoc's JSON output is an unstable feature and requires the **nightly** toolchain.

### 1. Install Nightly Toolchain

```bash
rustup toolchain install nightly
```

### 2. Generate JSON Documentation

```bash
cd rust/example
RUSTDOCFLAGS="-Z unstable-options --output-format json" cargo +nightly doc --no-deps --lib
```

This generates a JSON file at `target/doc/example.json`.

### 3. Copy to the Project's `docs/` Directory

```bash
mkdir -p docs
cp target/doc/example.json docs/api-docs.json
```

### 4. Confirm the JSON Path in `Cargo.toml`

The `Cargo.toml` already contains metadata that tracks this path:

```toml
[package.metadata.docs]
json-path = "docs/api-docs.json"
```

And the `include` field ensures it's bundled when publishing:

```toml
include = ["src/**/*", "Cargo.toml", "Cargo.lock", "docs/api-docs.json"]
```

## Method 2: Using `gen_docs.py` (Stable Fallback)

If nightly cannot be installed, the included Python script `gen_docs.py` can parse the source file directly:

```bash
cd rust
python3 gen_docs.py example/src/lib.rs -o example/docs/api-docs.json
```

This produces JSON in the same format expected by the explorer, without requiring nightly.

## How to Explore with `rust-api-explorer.py`

### Prerequisites

- Python 3.6+

### Query Examples

```bash
cd rust

# View a struct
python3 rust-api-explorer.py --doc-path ./example/docs/ LoggerService

# View a method
python3 rust-api-explorer.py --doc-path ./example/docs/ LogEntry.new

# View a function
python3 rust-api-explorer.py --doc-path ./example/docs/ add

# View an enum
python3 rust-api-explorer.py --doc-path ./example/docs/ ProductCategory

# View a struct field
python3 rust-api-explorer.py --doc-path ./example/docs/ Product.id
```

### Output Example

```
✅ Found API:
============================================================
📌 Name:       LoggerService
🏷️  Kind:       struct
📝 Description: 日志服务，提供分级日志记录功能。
                支持设定最低输出级别...

📦 Fields (2):
   ▸ min_level: LogLevel
   ▸ entries: Vec<LogEntry>

📦 Methods (8):
   ▸ pub fn new(min_level: LogLevel) -> Self {
   ▸ pub fn info(&mut self, message: &str) {
   ▸ pub fn error(&mut self, message: &str) {
   ...
============================================================
```

## Adding JSDoc-Style Doc Comments

Rust uses `///` for item-level docs and `//!` for module-level docs:

```rust
/// 计算两个数字的和。
///
/// # Arguments
///
/// * `a` - 第一个加数
/// * `b` - 第二个加数
///
/// # Returns
///
/// 返回 `a + b` 的结果。
///
/// # Example
///
/// ```rust
/// assert_eq!(add(2, 3), 5);
/// ```
pub fn add(a: i32, b: i32) -> i32 {
    a + b
}
```

### Common Doc Comment Tags

| Tag | Purpose |
|---|---|
| `# Arguments` | Describe parameters |
| `# Returns` | Describe return value |
| `# Panics` | Document possible panics |
| `# Errors` | Document error conditions |
| `# Safety` | Document unsafe function safety |
| `# Example` | Usage example (also run as a test) |
| `# Fields` | Describe struct fields |

## The JSON Format

The JSON produced by both `rustdoc --output-format json` and `gen_docs.py` follows this structure:

```json
{
  "crate": {
    "name": "example",
    "mod_docs": "...",
    "items": [
      {
        "name": "LoggerService",
        "kind": "struct",
        "comment": "日志服务...",
        "fields": [
          { "name": "min_level", "type": "LogLevel", "comment": "..." }
        ],
        "methods": [
          {
            "name": "new",
            "kind": "method",
            "comment": "...",
            "signature": "pub fn new(min_level: LogLevel) -> Self {"
          }
        ]
      },
      {
        "name": "add",
        "kind": "function",
        "comment": "...",
        "signature": "pub fn add(a: i32, b: i32) -> i32 {",
        "returns": "i32"
      },
      {
        "name": "ProductCategory",
        "kind": "enum",
        "comment": "...",
        "variants": [
          { "name": "Electronics", "comment": "..." }
        ]
      }
    ]
  }
}
```

## Project Structure

```
rust/
├── gen_docs.py                   # Python 脚本：从 .rs 源码解析文档生成 JSON（stable 备选）
├── rust-api-explorer.py          # Python 查询工具
├── Readme.md                     # 本文件
└── example/                      # Cargo 示例项目
    ├── Cargo.toml
    └── src/
        ├── lib.rs                # 库代码（所有公开 API）
        └── main.rs               # 可执行入口（示例使用）
    └── docs/
        └── api-docs.json         # 预生成的 JSON 文档
```

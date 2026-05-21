#!/usr/bin/env python3
"""
gen_docs.py — 从 Rust 源文件解析文档注释并输出 JSON。

用法:
  python3 gen_docs.py example.rs -o docs/api-docs.json

输出 JSON 格式与 rustdoc --output-format json 兼容。
使用 - 开头的选项如 --doc-path 会被忽略，仅用于 explorer 兼容。
"""

import argparse
import json
import os
import re
import sys

# ─── 正则表达式 ───────────────────────────────────────────────

# 文档注释行：/// ... 或 //! ...
RE_DOC_LINE = re.compile(r'^\s*//[!/!]\s?(.*)$')

# 模块级 doc: //!
RE_MOD_DOC = re.compile(r'^\s*//!\s?(.*)$')

# pub fn / fn
RE_FN_START = re.compile(
    r'^\s*'
    r'(?:pub\s+)?'
    r'(?:async\s+)?'
    r'(?:unsafe\s+)?'
    r'fn\s+'
    r'(\w+)'
    r'(?:\s*<[^>]*>)?'
    r'\s*\('
)

# pub struct ...
RE_STRUCT = re.compile(
    r'^\s*(?:pub\s+)?struct\s+(\w+)'
)

# pub enum ...
RE_ENUM = re.compile(
    r'^\s*(?:pub\s+)?enum\s+(\w+)'
)

# pub trait ...
RE_TRAIT = re.compile(
    r'^\s*(?:pub\s+)?trait\s+(\w+)'
)

# impl ... { }
RE_IMPL = re.compile(
    r'^\s*impl\s*(?:<[^>]*>\s*)?(\w+(?:\s*<[^>]+>)?)(?:\s+for\s+(\w+(?:\s*<[^>]+>)?))?\s*\{'
)

# pub const ...
RE_CONST = re.compile(
    r'^\s*(?:pub\s+)?const\s+(\w+)\s*:\s*([^=]+)='
)

# pub type ...
RE_TYPE = re.compile(
    r'^\s*(?:pub\s+)?type\s+(\w+)'
)

# 结构体字段：pub name: Type,
RE_FIELD = re.compile(
    r'^\s*(?:pub\s+)?(\w+)\s*:\s*([^,{]+)'
)

# 枚举变体：Name, 或 Name(Type), 或 Name { ... }
RE_ENUM_VARIANT = re.compile(
    r'^\s*(\w+)(?:\([^)]*\)|\s*\{[^}]*\})?\s*,?\s*$'
)

# 分配方法调用 (method calls): self.xxx(...)
RE_METHOD_FN_START = re.compile(
    r'^\s*'
    r'(?:pub\s+)?'
    r'(?:async\s+)?'
    r'(?:unsafe\s+)?'
    r'fn\s+'
    r'(\w+)'
    r'(?:\s*<[^>]*>)?'
    r'\s*\('
)


def parse_type_simple(line: str) -> str:
    """从一行中提取类型。"""
    m = re.search(r':\s*([^=,{]+)', line)
    return m.group(1).strip() if m else "()"


def read_until_brace(lines, start, max_lookahead=20):
    """从 start 开始读取行，直到遇到 { 或 ;，返回 (结束行号, 拼接文本)。"""
    parts = []
    for offset in range(max_lookahead):
        idx = start + offset
        if idx >= len(lines):
            return idx, "\n".join(parts)
        line = lines[idx]
        parts.append(line.rstrip())
        stripped = line.strip()
        if stripped.endswith('{') or stripped.endswith(';'):
            return idx, "\n".join(parts)
        # 如果遇到 } 且只有一行则退出
        if stripped == '}':
            return idx, "\n".join(parts)
    return start + max_lookahead - 1, "\n".join(parts)


def parse_rust_source(filepath: str) -> dict:
    """解析 Rust 源文件，返回文档结构字典。"""
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    items = []
    mod_docs = []
    current_docs = []
    in_impl = False
    impl_for = None
    impl_start = 0
    brace_depth = 0
    in_struct = False
    struct_fields = []
    struct_name = None
    in_enum = False
    enum_variants = []
    enum_name = None
    top_level_fn = True  # 是否在顶层 (不是 impl 里)

    def flush_docs():
        nonlocal current_docs
        current_docs = []

    def add_item(name: str, kind: str, docs: str, extra: dict = None):
        item = {
            "name": name,
            "kind": kind,
            "comment": docs.strip(),
        }
        if extra:
            item.update(extra)
        items.append(item)

    i = 0
    while i < len(lines):
        line = lines[i]

        # ── 跟踪花括号深度 ──
        for ch in line:
            if ch == '{':
                brace_depth += 1
            elif ch == '}':
                brace_depth -= 1
                if brace_depth < 0:
                    brace_depth = 0

        # ── 模块级文档 ──
        m_mod = RE_MOD_DOC.match(line)
        if m_mod:
            mod_docs.append(m_mod.group(1))
            i += 1
            continue

        # ── 收集文档注释 ──
        m_doc = RE_DOC_LINE.match(line)
        if m_doc:
            current_docs.append(m_doc.group(1))
            i += 1
            continue

        # ── 检查 impl ──
        m_impl = RE_IMPL.match(line)
        if m_impl and brace_depth <= 1:
            impl_for = m_impl.group(2) or m_impl.group(1)  # impl Trait for Type → Type; impl Type → Type
            in_impl = True
            # 读取整个 impl 块
            j = i + 1
            depth = 1
            impl_methods = []
            while j < len(lines):
                jline = lines[j]
                for ch in jline:
                    if ch == '{': depth += 1
                    elif ch == '}': depth -= 1
                if depth == 0:
                    break
                m_fn = RE_METHOD_FN_START.match(jline)
                if m_fn:
                    fn_name = m_fn.group(1)
                    end_idx, sig_block = read_until_brace(lines, j)
                    fn_docs = []
                    k = j - 1
                    while k >= 0 and RE_DOC_LINE.match(lines[k]):
                        fn_docs.insert(0, RE_DOC_LINE.match(lines[k]).group(1))
                        k -= 1
                    sig = " ".join(sig_block.split())
                    impl_methods.append({
                        "name": fn_name,
                        "kind": "method",
                        "comment": " ".join(fn_docs).strip(),
                        "signature": sig,
                    })
                    j = end_idx + 1
                else:
                    j += 1
            if impl_methods:
                for item in items:
                    if item["name"] == impl_for and item["kind"] in ("struct", "enum", "trait"):
                        if "methods" not in item:
                            item["methods"] = []
                        item["methods"].extend(impl_methods)
                        break
            flush_docs()
            i = j  # 跳过整个 impl 块
            # 恢复 brace_depth（外层已计入了 {，但 } 被跳过了）
            brace_depth -= 1
            if brace_depth < 0:
                brace_depth = 0
            in_impl = False
            impl_for = None
            continue

        # ── 顶层 struct ──
        m_struct = RE_STRUCT.match(line)
        if m_struct and not in_impl:
            struct_name = m_struct.group(1)
            docs = " ".join(current_docs)
            flush_docs()
            item = {
                "name": struct_name,
                "kind": "struct",
                "comment": docs.strip(),
                "fields": [],
            }
            # 查找字段
            brace_found = line.find('{')
            if brace_found >= 0:
                in_struct = True
                j = i + 1
                depth = 1
                while j < len(lines):
                    jline = lines[j]
                    for ch in jline:
                        if ch == '{': depth += 1
                        elif ch == '}': depth -= 1
                    if depth == 0:
                        break
                    m_f = RE_FIELD.match(jline)
                    if m_f:
                        field_docs = []
                        k = j - 1
                        while k >= 0 and RE_DOC_LINE.match(lines[k]):
                            field_docs.insert(0, RE_DOC_LINE.match(lines[k]).group(1))
                            k -= 1
                        item["fields"].append({
                            "name": m_f.group(1),
                            "type": m_f.group(2).strip().rstrip(','),
                            "comment": " ".join(field_docs).strip(),
                        })
                    j += 1
            items.append(item)
            i += 1
            continue

        # ── 顶层 enum ──
        m_enum = RE_ENUM.match(line)
        if m_enum and not in_impl:
            enum_name = m_enum.group(1)
            docs = " ".join(current_docs)
            flush_docs()
            item = {
                "name": enum_name,
                "kind": "enum",
                "comment": docs.strip(),
                "variants": [],
            }
            brace_found = line.find('{')
            if brace_found >= 0:
                j = i + 1
                depth = 1
                while j < len(lines):
                    jline = lines[j]
                    for ch in jline:
                        if ch == '{': depth += 1
                        elif ch == '}': depth -= 1
                    if depth == 0:
                        break
                    m_v = RE_ENUM_VARIANT.match(jline)
                    if m_v:
                        variant_docs = []
                        k = j - 1
                        while k >= 0 and RE_DOC_LINE.match(lines[k]):
                            variant_docs.insert(0, RE_DOC_LINE.match(lines[k]).group(1))
                            k -= 1
                        item["variants"].append({
                            "name": m_v.group(1),
                            "comment": " ".join(variant_docs).strip(),
                        })
                    j += 1
            items.append(item)
            i += 1
            continue

        # ── 顶层 trait ──
        m_trait = RE_TRAIT.match(line)
        if m_trait and not in_impl:
            trait_name = m_trait.group(1)
            docs = " ".join(current_docs)
            flush_docs()
            items.append({
                "name": trait_name,
                "kind": "trait",
                "comment": docs.strip(),
            })
            i += 1
            continue

        # ── 顶层函数 ──
        m_fn = RE_FN_START.match(line)
        if m_fn and not in_impl:
            fn_name = m_fn.group(1)
            if fn_name != "main":
                end_idx, sig_block = read_until_brace(lines, i)
                docs = " ".join(current_docs)
                flush_docs()
                sig = " ".join(sig_block.split())
                # 尝试获取返回类型
                ret = "()"
                arrow = sig_block.rfind("->")
                if arrow >= 0:
                    ret = sig_block[arrow+2:].strip().rstrip('{').strip()
                items.append({
                    "name": fn_name,
                    "kind": "function",
                    "comment": docs.strip(),
                    "signature": sig,
                    "returns": ret,
                })
                i = end_idx + 1
            else:
                flush_docs()
                i += 1
            continue

        # ── 跳过非匹配行 ──
        # 如果遇到非 doc 且非结构行，清空 doc 缓存
        stripped = line.strip()
        if stripped and not stripped.startswith('//') and not stripped.startswith('/*') and not stripped.startswith('*'):
            # 检查是否是 impl 的结束
            if in_impl and stripped == '}':
                in_impl = False
                impl_for = None
            flush_docs()

        i += 1

    return {
        "crate": {
            "name": os.path.splitext(os.path.basename(filepath))[0],
            "mod_docs": " ".join(mod_docs).strip(),
            "items": items,
        }
    }


def main():
    parser = argparse.ArgumentParser(description="Generate JSON docs from Rust source")
    parser.add_argument("source", help="Path to the Rust source file (.rs)")
    parser.add_argument("-o", "--output", default="docs/api-docs.json",
                        help="Output JSON path (default: docs/api-docs.json)")
    args, _ = parser.parse_known_args()

    result = parse_rust_source(args.source)

    out_path = args.output
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"Documentation generated: {out_path}")
    print(f"  Items: {len(result['crate']['items'])}")


if __name__ == "__main__":
    main()

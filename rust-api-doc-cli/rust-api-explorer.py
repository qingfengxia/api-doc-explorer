#!/usr/bin/env python3
"""
rust-api-explorer.py — 查询 Rust 文档 JSON，用法参考 TypeScript api-explorer。

用法:
  python3 rust-api-explorer.py [options] <query>

选项:
  -p, --doc-path <path>   JSON 文档路径或目录（默认: ./docs/api-docs.json）
  -h, --help              显示帮助
  -v, --version           显示版本

查询示例:
  python3 rust-api-explorer.py UserService
  python3 rust-api-explorer.py UserService.find_user
  python3 rust-api-explorer.py LoggerService.info
  python3 rust-api-explorer.py add
"""

import json
import os
import sys


def parse_args(argv):
    args = argv[1:]
    doc_path = "./docs/api-docs.json"
    positional = []

    i = 0
    while i < len(args):
        if args[i] in ("-p", "--doc-path") and i + 1 < len(args):
            doc_path = args[i + 1]
            i += 2
        elif args[i] in ("-h", "--help"):
            print_usage()
            sys.exit(0)
        elif args[i] in ("-v", "--version"):
            print("rust-api-explorer v1.0.0")
            sys.exit(0)
        else:
            positional.append(args[i])
            i += 1

    return doc_path, " ".join(positional)


def print_usage():
    print("""
Usage: rust-api-explorer.py [options] <query>

Explore Rust documentation JSON.

Arguments:
  query                API query string (e.g., "UserService.find_user")

Options:
  -p, --doc-path <path>  Path to the JSON doc file or directory (default: ./docs/api-docs.json)
  -h, --help             Display this help message
  -v, --version          Display the version number

Examples:
  python3 rust-api-explorer.py --doc-path ./docs/ UserService.find_user
  python3 rust-api-explorer.py -p ./docs/api-docs.json add
""")


def build_index(data):
    """构建 longname → item 和 name → item 的索引。"""
    index = {}      # name -> [item]
    longname_map = {}  # name.kind -> item
    items = data.get("crate", {}).get("items", [])
    crate_name = data.get("crate", {}).get("name", "crate")

    for item in items:
        name = item["name"]
        # 按 name 索引
        if name not in index:
            index[name] = []
        index[name].append(item)

        # 长路径索引
        for prefix in (crate_name,):
            longname = f"{prefix}::{name}"
            longname_map[longname] = item

        # 方法索引
        for method in item.get("methods", []):
            mname = method["name"]
            dotted = f"{name}.{mname}"
            longname_map[dotted] = method
            longname_map[f"{name}::{mname}"] = method

    return index, longname_map


def search(data, query):
    """在文档数据中搜索查询。"""
    index, longname_map = build_index(data)
    mod_docs = data.get("crate", {}).get("mod_docs", "")

    # 1) 尝试长路径精确匹配
    if query in longname_map:
        return longname_map[query]

    # 2) 按名称搜索
    parts = query.split(".")
    top_name = parts[0]
    rest = parts[1:]

    if top_name in index:
        candidates = index[top_name]
        # 优先选择 struct/enum/trait/function
        priority = {"struct": 0, "enum": 1, "trait": 2, "function": 3}
        candidates.sort(key=lambda x: priority.get(x.get("kind", ""), 99))
        top = candidates[0]

        if not rest:
            return top

        # 查找方法
        for m in top.get("methods", []):
            if m["name"] == rest[0]:
                return m
        # 查找字段
        for f in top.get("fields", []):
            if f["name"] == rest[0]:
                return f
        # 查找变体
        for v in top.get("variants", []):
            if v["name"] == rest[0]:
                return v

    return None


def print_result(node):
    """格式化输出结果。"""
    kind = node.get("kind", "?")
    name = node.get("name", "?")
    comment = node.get("comment", "")

    print("\n✅ Found API:")
    print("=" * 60)
    print(f"📌 Name:       {name}")
    print(f"🏷️  Kind:       {kind}")

    if comment:
        print(f"📝 Description: {comment}")

    # 函数/方法签名
    sig = node.get("signature", "")
    if sig:
        print(f"\n🔧 Signature:  {sig}")

    # 返回值
    ret = node.get("returns")
    if ret:
        print(f"   ↩️  Returns:    {ret}")

    # 参数 (从 signature 中提取)
    if kind in ("function", "method") and sig:
        params_start = sig.find("(")
        params_end = sig.rfind(")")
        if params_start >= 0 and params_end > params_start:
            params_str = sig[params_start+1:params_end]
            if params_str.strip():
                print("   Parameters:")
                for p in params_str.split(","):
                    p = p.strip()
                    if p:
                        print(f"     - {p}")

    # 结构体字段
    fields = node.get("fields", [])
    if fields:
        print(f"\n📦 Fields ({len(fields)}):")
        for f in fields:
            desc = f.get("comment", "")
            desc_str = f" — {desc}" if desc else ""
            print(f"   ▸ {f['name']}: {f.get('type', '?')}{desc_str}")

    # 枚举变体
    variants = node.get("variants", [])
    if variants:
        print(f"\n📦 Variants ({len(variants)}):")
        for v in variants:
            desc = v.get("comment", "")
            desc_str = f" — {desc}" if desc else ""
            print(f"   ▸ {v['name']}{desc_str}")

    # 方法列表
    methods = node.get("methods", [])
    if methods:
        print(f"\n📦 Methods ({len(methods)}):")
        for m in methods:
            desc = m.get("comment", "")
            desc_str = f" — {desc}" if desc else ""
            sig_preview = m.get("signature", m["name"] + "(...)")
            print(f"   ▸ {sig_preview}{desc_str}")

    print("=" * 60 + "\n")


def build_member_index(data):
    """构建 parent -> [members] 索引供 class 展示用。"""
    members = {}
    items = data.get("crate", {}).get("items", [])
    for item in items:
        for m in item.get("methods", []):
            pname = item["name"]
            if pname not in members:
                members[pname] = []
            members[pname].append(m)
        for f in item.get("fields", []):
            pname = item["name"]
            if pname not in members:
                members[pname] = []
            # Add fields too
    return members


def main():
    doc_path, query = parse_args(sys.argv)
    if not query:
        print("❌ Error: Missing required argument <query>")
        print_usage()
        sys.exit(1)

    # 支持目录输入
    if os.path.isdir(doc_path):
        doc_path = os.path.join(doc_path, "api-docs.json")

    if not os.path.exists(doc_path):
        print(f"❌ Error: Documentation file not found at {doc_path}")
        sys.exit(1)

    try:
        with open(doc_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Error parsing JSON file: {e}")
        sys.exit(1)

    result = search(data, query)
    if result:
        print_result(result)
    else:
        print(f"🔍 No API found for query: \"{query}\"")
        print("   Tip: Use the exact symbol name or dotted path (e.g. \"UserService.find_user\").")


if __name__ == "__main__":
    main()

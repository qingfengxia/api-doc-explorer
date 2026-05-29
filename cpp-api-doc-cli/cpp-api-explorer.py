#!/usr/bin/env python3
"""
cpp-api-explorer.py — 查询 Doxygen XML 文档。

用法:
  python cpp-api-explorer.py --doc-path ./docs/ namespace::class_name::method
  python cpp-api-explorer.py --doc-path ./docs/ namespace::class_name.method
  python cpp-api-explorer.py --doc-path ./docs/ ROS2::QoS::GetQoS
  python cpp-api-explorer.py --doc-path ./docs/ ROS2           # 列出命名空间下所有类型
  python cpp-api-explorer.py --doc-path ./docs/ QoS            # 搜索类名（无前缀）
  python cpp-api-explorer.py --doc-path ./docs/ NonExistent    # 未找到

Both '::' and '.' are accepted as separators; '::' is the standard C++ notation.

依赖: Python 3.6+ 标准库 (xml.etree.ElementTree)
"""

import os
import sys
import xml.etree.ElementTree as ET

# ─── 命令行参数解析 ──────────────────────────────────────────

def parse_args(argv):
    args = argv[1:]
    doc_path = None
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
            print("cpp-api-explorer v1.0.0")
            sys.exit(0)
        else:
            positional.append(args[i])
            i += 1

    return doc_path or "./docs", "::".join(positional)


def print_usage():
    print("""
Usage: cpp-api-explorer.py [options] <query>

Explore Doxygen XML documentation.

Arguments:
  query                API query (e.g., "ROS2::QoS::GetQoS", "ROS2::QoS.GetQoS", or "TopicConfiguration")

Options:
  -p, --doc-path <path>  Path to Doxygen XML output directory (default: ./docs)
  -h, --help             Display this help message
  -v, --version          Display the version number

Examples:
  python cpp-api-explorer.py --doc-path ./docs/ ROS2
  python cpp-api-explorer.py --doc-path ./docs/ ROS2::QoS
  python cpp-api-explorer.py --doc-path ./docs/ ROS2::QoS::GetQoS
  python cpp-api-explorer.py --doc-path ./docs/ QoS
""")


# ─── 索引加载 ───────────────────────────────────────────────

def load_index(doc_dir):
    """Parse index.xml and build compound lookup tables."""
    index_path = os.path.join(doc_dir, "index.xml")
    if not os.path.exists(index_path):
        print(f"\u274c Error: index.xml not found in {doc_dir}")
        print("   Run 'doxygen' first to generate XML docs.")
        sys.exit(1)

    tree = ET.parse(index_path)
    root = tree.getroot()

    # qualified_name → { refid, kind, members: [name, ...] }
    by_qualified = {}
    # simple_name → [compounds]
    by_simple = {}

    for compound in root.findall("compound"):
        refid = compound.get("refid", "")
        kind = compound.get("kind", "")
        name_el = compound.find("name")
        if name_el is None or not name_el.text:
            continue
        qualified = name_el.text.strip()
        simple = qualified.split("::")[-1] if "::" in qualified else qualified

        members = []
        for member in compound.findall("member"):
            mname_el = member.find("name")
            if mname_el is not None and mname_el.text:
                members.append(mname_el.text.strip())

        entry = {"refid": refid, "kind": kind, "qualified": qualified,
                 "simple": simple, "members": members}
        by_qualified[qualified] = entry

        if simple not in by_simple:
            by_simple[simple] = []
        by_simple[simple].append(entry)

    return by_qualified, by_simple


def find_compound(doc_dir, by_qualified, by_simple, query_parts):
    """Find the compound definition XML for a query."""
    # Try each prefix of the query as a compound name
    for end in range(len(query_parts), 0, -1):
        qualified = "::".join(query_parts[:end])
        if qualified in by_qualified:
            return by_qualified[qualified], end

    # Try by simple name
    simple = query_parts[0]
    if simple in by_simple:
        candidates = by_simple[simple]
        if len(candidates) == 1:
            return candidates[0], 1
        # Multiple matches: prefer exact kind or alphabetically
        print(f"\u2139\uFE0F  Multiple matches for '{simple}':")
        for c in candidates:
            print(f"     {c['kind']:8s} {c['qualified']}")
        print("   Use a more specific query (e.g., namespace::name).")
        sys.exit(0)

    return None, 0


# ─── XML 详情解析 ───────────────────────────────────────────

def get_text(el):
    """Get all text content from an element (including children)."""
    if el is None:
        return ""
    return "".join(el.itertext()).strip()


def parse_compound_xml(doc_dir, refid, kind):
    """Parse a compound XML file and return structured dict."""
    xml_path = os.path.join(doc_dir, f"{refid}.xml")
    if not os.path.exists(xml_path):
        return None

    tree = ET.parse(xml_path)
    root = tree.getroot()
    compound = root.find("compounddef")
    if compound is None:
        return None

    result = {
        "name": get_text(compound.find("compoundname")),
        "kind": compound.get("kind", kind),
        "brief": get_text(compound.find("briefdescription")),
        "details": get_text(compound.find("detaileddescription")),
        "includes": get_text(compound.find("includes")),
        "sections": [],
    }

    for section in compound.findall("sectiondef"):
        section_kind = section.get("kind", "")
        members = []
        for member in section.findall("memberdef"):
            mkind = member.get("kind", "")
            mname = get_text(member.find("name"))
            mtype = get_text(member.find("type"))
            mdefinition = get_text(member.find("definition"))
            margs = get_text(member.find("argsstring"))
            mbrief = get_text(member.find("briefdescription"))
            mdetails = get_text(member.find("detaileddescription"))

            params = []
            for param in member.findall("param"):
                ptype = get_text(param.find("type"))
                pname = get_text(param.find("declname"))
                pdefval = get_text(param.find("defval"))
                params.append({"type": ptype, "name": pname,
                               "default": pdefval})

            members.append({
                "kind": mkind,
                "name": mname,
                "type": mtype,
                "definition": mdefinition,
                "args": margs,
                "brief": mbrief,
                "details": mdetails,
                "params": params,
            })

        if members:
            result["sections"].append({"kind": section_kind, "members": members})

    return result


# ─── 美化输出 ───────────────────────────────────────────────

def print_compound_info(compound_xml):
    """Print compound details."""
    name = compound_xml["name"]
    kind = compound_xml["kind"]
    brief = compound_xml["brief"]
    details = compound_xml["details"]

    print(f"\n\u2705 Found: {name}")
    print("=" * 60)
    print(f"\U0001f4cc Kind:        {kind}")

    if brief:
        print(f"\U0001f4dd Description: {brief}")
    if details:
        print(f"   Details:    {details}")

    for section in compound_xml["sections"]:
        skind = section["kind"]
        members = section["members"]
        label = section_label(skind)
        if not members:
            continue

        print(f"\n\U0001f4e6 {label} ({len(members)}):")
        for m in members:
            prefix = ""
            if m["kind"] == "function":
                sig = f"{m['name']}({m['args']})"
                prefix = f"  \U0001f527 "
                if m["type"]:
                    sig = f"{m['type']} {sig}"
            elif m["kind"] == "variable":
                sig = f"{m['type']} {m['name']}"
                prefix = f"  \U0001f4a0 "
            elif m["kind"] == "typedef":
                sig = f"using {m['name']} = {m['type']}"
                prefix = f"  \U0001f4cb "
            else:
                sig = f"{m['name']}"
                prefix = f"  \u2022 "

            print(f"{prefix}{sig}")
            if m["brief"]:
                print(f"      \u21B3 {m['brief']}")
            if m["params"]:
                for p in m["params"]:
                    pdefault = f" = {p['default']}" if p["default"] else ""
                    print(f"        param {p['name']}: {p['type']}{pdefault}")

    print("=" * 60 + "\n")


def section_label(kind):
    labels = {
        "public-func": "Public Methods",
        "public-type": "Public Types",
        "public-attrib": "Public Attributes",
        "public-static-func": "Public Static Methods",
        "public-static-attrib": "Public Static Attributes",
        "protected-func": "Protected Methods",
        "private-func": "Private Methods",
        "private-attrib": "Private Attributes",
        "func": "Functions",
        "typedef": "Type Definitions",
        "enum": "Enumerations",
        "var": "Variables",
    }
    return labels.get(kind, kind)


def print_namespace_members(doc_dir, qualified_name):
    """List all types in a namespace."""
    ns_file = os.path.join(doc_dir, f"namespace{qualified_name.replace('::', '_1_1')}.xml")
    if not os.path.exists(ns_file):
        # Try the simple name
        ns_file = os.path.join(doc_dir, f"namespace{qualified_name}.xml")
    if not os.path.exists(ns_file):
        print(f"\u274c Namespace file not found: {ns_file}")
        return

    tree = ET.parse(ns_file)
    root = tree.getroot()
    compound = root.find("compounddef")
    if compound is None:
        return

    cname = get_text(compound.find("compoundname"))
    print(f"\n\u2705 Namespace: {cname}")
    print("=" * 60)

    # Inner classes
    inner_classes = compound.findall("innerclass")
    if inner_classes:
        print(f"\n\U0001f4e6 Classes / Structs ({len(inner_classes)}):")
        for ic in inner_classes:
            prot = ic.get("prot", "")
            visibility = "" if prot == "public" else f" ({prot})"
            print(f"   \U0001f4a0 {ic.text}{visibility}")

    # Inner namespaces
    inner_namespaces = compound.findall("innernamespace")
    if inner_namespaces:
        print(f"\n\U0001f4e6 Namespaces ({len(inner_namespaces)}):")
        for ns in inner_namespaces:
            print(f"   \U0001f4c1 {ns.text}")

    # Section members (typedefs, enums, etc.)
    for section in compound.findall("sectiondef"):
        for member in section.findall("memberdef"):
            mkind = member.get("kind", "")
            mname = get_text(member.find("name"))
            mtype = get_text(member.find("type"))
            mbrief = get_text(member.find("briefdescription"))

            if mkind == "typedef":
                print(f"\n   \U0001f4cb typedef {mname} = {mtype}")
                if mbrief:
                    print(f"       \u21B3 {mbrief}")

    print("\n" + "=" * 60 + "\n")


# ─── 辅助 ───────────────────────────────────────────────────

def get_text(el):
    if el is None:
        return ""
    return "".join(el.itertext()).strip()


# ─── 主逻辑 ─────────────────────────────────────────────────

def main():
    doc_dir, query = parse_args(sys.argv)
    if not query:
        print("\u274c Error: Missing required argument <query>")
        print_usage()
        sys.exit(1)

    if not os.path.isdir(doc_dir):
        print(f"\u274c Error: Docs directory not found at {doc_dir}")
        sys.exit(1)

    # Load index
    by_qualified, by_simple = load_index(doc_dir)

    # Parse query into parts — normalize '.' to '::' so both separators work
    normalized = query.replace(".", "::")
    query_parts = [p for p in normalized.split("::") if p]
    if not query_parts:
        print("\u274c Error: Invalid query")
        sys.exit(1)

    # Check if first part is a namespace → list its types
    first_part = query_parts[0]
    if first_part in by_qualified and by_qualified[first_part]["kind"] == "namespace":
        if len(query_parts) == 1:
            print_namespace_members(doc_dir, first_part)
            return
        # User wants something inside a namespace, continue to compound search

    # Find compound
    entry, consumed = find_compound(doc_dir, by_qualified, by_simple, query_parts)
    if entry is None:
        print(f"\U0001F50D No API found for query: \"{query}\"")
        print("   Tip: Check spelling or try a different query format.")
        sys.exit(1)

    # If we consumed all parts, show the compound
    remaining = query_parts[consumed:]
    if not remaining:
        # If it's a namespace, list its members
        if entry["kind"] == "namespace":
            print_namespace_members(doc_dir, entry["qualified"])
        else:
            compound_xml = parse_compound_xml(doc_dir, entry["refid"], entry["kind"])
            if compound_xml:
                print_compound_info(compound_xml)
            else:
                print(f"\u274c Error: Could not parse {entry['refid']}.xml")
        return

    # We have remaining parts → search member
    member_name = remaining[0]
    if member_name in entry["members"]:
        # Show the specific compound with member highlighted
        compound_xml = parse_compound_xml(doc_dir, entry["refid"], entry["kind"])
        if not compound_xml:
            print(f"\u274c Error: Could not parse {entry['refid']}.xml")
            return
        member_detail = find_member_detail(compound_xml, member_name)
        if member_detail:
            print_member_detail(entry["qualified"], member_detail)
        else:
            print_compound_info(compound_xml)
    else:
        # Show the compound anyway with all members
        compound_xml = parse_compound_xml(doc_dir, entry["refid"], entry["kind"])
        if compound_xml:
            print_compound_info(compound_xml)
        else:
            print(f"\U0001F50D Member '{member_name}' not found in {entry['qualified']}")


def find_member_detail(compound_xml, member_name):
    """Find a specific member in the compound XML data."""
    for section in compound_xml["sections"]:
        for m in section["members"]:
            if m["name"] == member_name:
                return m
    return None


def print_member_detail(qualified_name, member):
    """Print detailed info about a single member."""
    print(f"\n\u2705 Found: {qualified_name}::{member['name']}")
    print("=" * 60)
    print(f"\U0001f4cc Kind:        {member['kind']}")

    if member['definition']:
        print(f"\U0001f527 Signature:  {member['definition']}")
    elif member['type']:
        print(f"\U0001f527 Type:        {member['type']}")

    if member['brief']:
        print(f"\U0001f4dd Description: {member['brief']}")
    if member['details']:
        print(f"   Details:    {member['details']}")

    if member['params']:
        print("\n   Parameters:")
        for p in member['params']:
            pdefault = f" = {p['default']}" if p['default'] else ""
            print(f"     - {p['name']}: {p['type']}{pdefault}")

    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()

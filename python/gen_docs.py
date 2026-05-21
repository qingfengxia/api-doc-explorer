#!/usr/bin/env python3
"""
gen_docs.py — 从 Python 模块运行时内省生成 api-docs.json。

用法:
  python3 gen_docs.py example -o example/docs/api-docs.json
"""

import argparse
import importlib
import inspect
import json
import os
import sys
from enum import Enum
from dataclasses import fields as dataclass_fields, is_dataclass
from typing import Any, Dict, List, Optional, get_type_hints


def get_type_name(obj: Any) -> str:
    """获取对象类型名称。"""
    if inspect.isclass(obj):
        if issubclass(obj, Enum):
            return "enum"
        if is_dataclass(obj):
            return "dataclass"
        return "class"
    elif inspect.isfunction(obj):
        return "function"
    elif inspect.isbuiltin(obj):
        return "builtin"
    elif isinstance(obj, property):
        return "property"
    elif inspect.ismodule(obj):
        return "module"
    return "unknown"


def get_signature_str(obj: Any) -> Optional[str]:
    """获取函数/方法的签名。"""
    try:
        sig = inspect.signature(obj)
        return str(sig)
    except (ValueError, TypeError):
        return None


def get_one_line_doc(doc: Optional[str]) -> Optional[str]:
    """从文档字符串中提取第一行。"""
    if not doc:
        return None
    lines = [line.strip() for line in doc.split('\n') if line.strip()]
    return lines[0] if lines else None


def extract_params_from_sig(obj: Any) -> List[Dict]:
    """从函数签名提取参数信息。"""
    try:
        sig = inspect.signature(obj)
    except (ValueError, TypeError):
        return []

    params = []
    for name, param in sig.parameters.items():
        if name in ('self', 'cls'):
            continue
        p: Dict[str, Any] = {"name": name}
        if param.annotation != inspect.Parameter.empty:
            p["type"] = _annotation_to_str(param.annotation)
        if param.default != inspect.Parameter.empty:
            p["default"] = repr(param.default)
        params.append(p)
    return params


def _annotation_to_str(annotation: Any) -> str:
    """将类型标注转换为字符串。"""
    if hasattr(annotation, '__name__'):
        return annotation.__name__
    return str(annotation).replace('typing.', '')


def get_return_type(obj: Any) -> Optional[str]:
    """获取函数的返回类型。"""
    try:
        sig = inspect.signature(obj)
        if sig.return_annotation != inspect.Signature.empty:
            return _annotation_to_str(sig.return_annotation)
    except (ValueError, TypeError):
        pass
    return None


def extract_enum_members(cls: type) -> List[Dict]:
    """提取枚举成员。"""
    members = []
    for name, value in cls.__members__.items():
        members.append({
            "name": name,
            "value": value.value if isinstance(value, Enum) else value,
        })
    return members


def extract_dataclass_fields(cls: type) -> List[Dict]:
    """提取 dataclass 字段。"""
    result = []
    try:
        hints = get_type_hints(cls)
    except Exception:
        hints = {}
    import dataclasses as dc
    for f in dataclass_fields(cls):
        field_info: Dict[str, Any] = {"name": f.name}
        if f.name in hints:
            field_info["type"] = _annotation_to_str(hints[f.name])
        if f.default is not dc.MISSING:
            field_info["default"] = repr(f.default)
        elif f.default_factory is not dc.MISSING:
            field_info["default"] = "..."
        result.append(field_info)
    return result


def introspect_module(module_path: str) -> Dict:
    """内省 Python 模块并生成文档结构。"""
    # Add the parent directory to sys.path for relative imports
    parent_dir = os.path.dirname(os.path.abspath(module_path if os.path.exists(module_path) else '.'))
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)

    # module_path 可以是 "example" 或文件路径
    if os.path.isdir(module_path):
        module_name = os.path.basename(module_path)
    else:
        module_name = module_path

    try:
        mod = importlib.import_module(module_name)
    except ImportError as e:
        print(f"Error importing module '{module_name}': {e}", file=sys.stderr)
        sys.exit(1)

    module_doc = inspect.getdoc(mod) or ""
    items = []

    for name, obj in inspect.getmembers(mod):
        if name.startswith('_'):
            continue

        # Skip re-exports from other modules
        if hasattr(obj, '__module__') and obj.__module__ and not obj.__module__.startswith(module_name):
            continue

        item: Dict[str, Any] = {
            "name": name,
            "kind": get_type_name(obj),
            "description": get_one_line_doc(inspect.getdoc(obj)),
            "full_doc": inspect.getdoc(obj),
        }

        if inspect.isclass(obj):
            item["module"] = getattr(obj, '__module__', module_name)

            if issubclass(obj, Enum):
                item["members"] = extract_enum_members(obj)
            elif is_dataclass(obj):
                item["fields"] = extract_dataclass_fields(obj)

            # 提取方法
            methods = []
            for m_name, m_obj in inspect.getmembers(obj):
                if m_name.startswith('_'):
                    continue
                if inspect.isfunction(m_obj) or inspect.ismethod(m_obj):
                    method_info: Dict[str, Any] = {
                        "name": m_name,
                        "kind": "method",
                        "signature": get_signature_str(m_obj),
                        "description": get_one_line_doc(inspect.getdoc(m_obj)),
                        "full_doc": inspect.getdoc(m_obj),
                        "returns": get_return_type(m_obj),
                    }
                    params = extract_params_from_sig(m_obj)
                    if params:
                        method_info["parameters"] = params
                    methods.append(method_info)
            if methods:
                item["methods"] = methods

        elif inspect.isfunction(obj):
            item["signature"] = get_signature_str(obj)
            item["returns"] = get_return_type(obj)
            params = extract_params_from_sig(obj)
            if params:
                item["parameters"] = params
            item["module"] = getattr(obj, '__module__', module_name)

        items.append(item)

    return {
        "module": module_name,
        "description": get_one_line_doc(module_doc),
        "full_doc": module_doc,
        "children": items,
    }


def main():
    parser = argparse.ArgumentParser(description="Generate JSON docs from Python module introspection")
    parser.add_argument("module", help="Module path (e.g., 'example' or path to package)")
    parser.add_argument("-o", "--output", default="example/docs/api-docs.json",
                        help="Output JSON path (default: example/docs/api-docs.json)")
    args = parser.parse_args()

    result = introspect_module(args.module)

    out_path = args.output
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"Documentation generated: {out_path}")
    print(f"  Items: {len(result['children'])}")


if __name__ == "__main__":
    main()

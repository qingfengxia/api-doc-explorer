#!/usr/bin/env python3
"""
Python API Explorer - CLI to explore API DOC

USAGE:
  python3 python_api_explorer.py example
  python3 python_api_explorer.py example.UserService
  python3 python_api_explorer.py example.UserService.find_user
  python3 python_api_explorer.py example --output-json
"""

import importlib
import inspect
import json
import sys
import types
from typing import Any, Dict, List, Optional, Union
from enum import Enum
from dataclasses import dataclass, asdict
from pathlib import Path


class PythonApiExplorer:
    """Python API探索器类"""
    
    def __init__(self, module_path: str):
        """
        初始化PythonApiExplorer
        
        Args:
            module_path: 模块路径，可以是简单模块名或带点的模块路径
        """
        self.module_path = module_path
        self.module = None
        self._load_module()
    
    def _load_module(self) -> None:
        """加载指定模块"""
        try:
            self.module = importlib.import_module(self.module_path)
        except ImportError as e:
            # 如果包含点，尝试导入父模块
            if '.' in self.module_path:
                parts = self.module_path.split('.')
                parent_path = '.'.join(parts[:-1])
                attr_name = parts[-1]
                try:
                    parent = importlib.import_module(parent_path)
                    self.module = getattr(parent, attr_name, None)
                    if self.module is None:
                        raise ImportError(f"Cannot import {attr_name} from {parent_path}")
                except ImportError:
                    raise ImportError(f"Failed to import module: {self.module_path}. Error: {e}")
            else:
                raise ImportError(f"Failed to import module: {self.module_path}. Error: {e}")
    
    def _get_type_name(self, obj: Any) -> str:
        """获取对象类型名称"""
        if inspect.isclass(obj):
            if issubclass(type(obj), type(Enum)):
                return "enum"
            return "class"
        elif inspect.isfunction(obj):
            return "function"
        elif inspect.ismethod(obj):
            return "method"
        elif inspect.isbuiltin(obj):
            return "builtin"
        elif isinstance(obj, property):
            return "property"
        elif inspect.ismodule(obj):
            return "module"
        elif isinstance(obj, (int, float, str, bool, list, dict, tuple)):
            return "constant"
        else:
            return "unknown"
    
    def _get_signature(self, obj: Any) -> Optional[str]:
        """获取函数/方法的签名"""
        try:
            if inspect.isclass(obj) or inspect.isfunction(obj) or inspect.ismethod(obj):
                sig = inspect.signature(obj)
                return str(sig)
        except (ValueError, TypeError):
            pass
        return None
    
    def _get_one_line_description(self, doc: Optional[str]) -> Optional[str]:
        """从文档字符串中提取第一行描述"""
        if not doc:
            return None
        
        # 获取第一行非空行
        lines = [line.strip() for line in doc.split('\n') if line.strip()]
        if lines:
            return lines[0]
        return None
    
    def _get_qualified_name(self, obj: Any, name: str) -> str:
        """获取对象的完全限定名"""
        if inspect.isclass(obj):
            mod = getattr(obj, '__module__', self.module_path)
            return f"{mod}.{name}"
        elif inspect.isfunction(obj):
            mod = getattr(obj, '__module__', self.module_path)
            return f"{mod}.{name}"
        elif inspect.ismodule(obj):
            return getattr(obj, '__name__', name)
        return f"{self.module_path}.{name}"
    
    def _get_api_members(self, api_name: str, obj: Any) -> Optional[List[Dict]]:
        """获取类/枚举的成员信息"""
        if not inspect.isclass(obj):
            return None
        
        members = []
        
        # 获取所有公共成员（不以下划线开头）
        for name, member in inspect.getmembers(obj):
            if name.startswith('_'):
                continue
            
            member_type = self._get_type_name(member)
            member_info = {
                "name": name,
                "type": member_type,
                "qualifiedName": f"{self.module_path}.{api_name}.{name}",
            }
            sig = self._get_signature(member) if callable(member) else None
            if sig:
                member_info["signature"] = sig
            members.append(member_info)
        
        return members if members else None
    
    def list_api(self) -> Dict:
        """
        列出模块中的所有API
        
        Returns:
            包含API列表的字典
        """
        if not self.module:
            return {"error": f"Module {self.module_path} not found"}
        
        api_list = []
        
        # 获取模块的公共成员
        for name, obj in inspect.getmembers(self.module):
            # 跳过私有成员和特殊成员
            if name.startswith('_'):
                continue
            
            api_type = self._get_type_name(obj)
            signature = self._get_signature(obj) if callable(obj) else None
            doc = inspect.getdoc(obj)
            description = self._get_one_line_description(doc)
            qualified_name = self._get_qualified_name(obj, name)
            
            api_info = {
                "name": name,
                "qualifiedName": qualified_name,
                "kind": api_type,
                "signature": signature,
                "description": description
            }
            api_list.append(api_info)
        
        result = {
            "module": self.module_path,
            "api_count": len(api_list),
            "children": api_list
        }
        
        return result
    
    def get_api_doc(self, api_name: str) -> Dict:
        """
        获取指定API的详细文档
        
        Args:
            api_name: API名称
            
        Returns:
            包含API文档的字典
        """
        if not self.module:
            return {"error": f"Module {self.module_path} not found"}
        
        # 获取API对象
        if not hasattr(self.module, api_name):
            return {"error": f"API '{api_name}' not found in module '{self.module_path}'"}
        
        obj = getattr(self.module, api_name)
        api_type = self._get_type_name(obj)
        signature = self._get_signature(obj)
        full_doc = inspect.getdoc(obj)
        description = self._get_one_line_description(full_doc)
        qualified_name = self._get_qualified_name(obj, api_name)
        
        # 构建结果
        result = {
            "name": api_name,
            "qualifiedName": qualified_name,
            "kind": api_type,
        }
        
        if signature:
            result["signature"] = signature
        if description:
            result["description"] = description
        if full_doc:
            result["full_doc"] = full_doc
        result["module"] = self.module_path
        
        # 获取类/枚举的成员
        if inspect.isclass(obj):
            if issubclass(type(obj), type(Enum)):
                # 枚举成员
                enum_members = []
                for m_name, m_val in obj.__members__.items():
                    enum_members.append({"name": m_name, "value": m_val.value})
                if enum_members:
                    result["members"] = enum_members
            else:
                # 类方法
                methods = []
                for m_name, m_obj in inspect.getmembers(obj):
                    if m_name.startswith('_'):
                        continue
                    if not (inspect.isfunction(m_obj) or inspect.ismethod(m_obj)):
                        continue
                    m_sig = self._get_signature(m_obj)
                    m_doc = inspect.getdoc(m_obj)
                    m_desc = self._get_one_line_description(m_doc)
                    m_qualified = f"{qualified_name}.{m_name}"
                    m_info = {
                        "name": m_name,
                        "qualifiedName": m_qualified,
                        "kind": "method",
                    }
                    if m_sig:
                        m_info["signature"] = m_sig
                    if m_desc:
                        m_info["description"] = m_desc
                    if m_doc:
                        m_info["full_doc"] = m_doc
                    # 返回类型
                    try:
                        sig_obj = inspect.signature(m_obj)
                        if sig_obj.return_annotation != inspect.Signature.empty:
                            m_info["returns"] = str(sig_obj.return_annotation).replace('typing.', '')
                    except (ValueError, TypeError):
                        pass
                    # 参数
                    params = []
                    try:
                        sig_obj = inspect.signature(m_obj)
                        for p_name, param in sig_obj.parameters.items():
                            if p_name in ('self', 'cls'):
                                continue
                            p_info = {"name": p_name}
                            if param.annotation != inspect.Parameter.empty:
                                p_info["type"] = str(param.annotation).replace('typing.', '')
                            if param.default != inspect.Parameter.empty:
                                p_info["default"] = repr(param.default)
                            params.append(p_info)
                    except (ValueError, TypeError):
                        pass
                    if params:
                        m_info["parameters"] = params
                    methods.append(m_info)
                if methods:
                    result["methods"] = methods
                # dataclass 字段
                from dataclasses import fields as dc_fields, is_dataclass
                if is_dataclass(obj):
                    fields = []
                    try:
                        from typing import get_type_hints
                        hints = get_type_hints(obj)
                    except Exception:
                        hints = {}
                    for f in dc_fields(obj):
                        f_info = {"name": f.name}
                        if f.name in hints:
                            f_info["type"] = str(hints[f.name]).replace('typing.', '')
                        if f.default is not f.__class__.__mro__[0].__dataclass_fields__.get(f.name, f).__class__.__mro__[0].__dataclass_fields__:
                            pass  # complex defaults handled below
                        import dataclasses as dc
                        if f.default is not dc.MISSING:
                            f_info["default"] = repr(f.default)
                        elif f.default_factory is not dc.MISSING:
                            f_info["default"] = "..."
                        fields.append(f_info)
                    if fields:
                        result["fields"] = fields
        
        elif inspect.isfunction(obj):
            result["module"] = getattr(obj, '__module__', self.module_path)
            # 返回类型
            try:
                sig_obj = inspect.signature(obj)
                if sig_obj.return_annotation != inspect.Signature.empty:
                    result["returns"] = str(sig_obj.return_annotation).replace('typing.', '')
            except (ValueError, TypeError):
                pass
            # 参数
            params = []
            try:
                sig_obj = inspect.signature(obj)
                for p_name, param in sig_obj.parameters.items():
                    if p_name in ('self', 'cls'):
                        continue
                    p_info = {"name": p_name}
                    if param.annotation != inspect.Parameter.empty:
                        p_info["type"] = str(param.annotation).replace('typing.', '')
                    if param.default != inspect.Parameter.empty:
                        p_info["default"] = repr(param.default)
                    params.append(p_info)
            except (ValueError, TypeError):
                pass
            if params:
                result["parameters"] = params
        
        return result


# ─── 格式化输出 ───────────────────────────────────────────────

def format_result(data: Dict, query: str) -> str:
    """将 API 查询结果格式化为人类可读的 CLI 输出。"""
    lines = []
    
    # 错误处理
    if "error" in data:
        return f"\n❌ Error: {data['error']}\n"
    
    kind = data.get("kind", "?")
    name = data.get("name", "?")
    qualified_name = data.get("qualifiedName", name)
    
    # ── 方法/函数级查询 ──
    if kind in ("method", "function"):
        lines.append(f"\n✅ Found: {qualified_name}")
        lines.append("=" * 60)
        lines.append(f"📌 Name:       {name}")
        lines.append(f"🏷️  Kind:       {kind}")
        
        description = data.get("description")
        if description:
            lines.append(f"📝 Description: {description}")
        
        signature = data.get("signature")
        if signature:
            lines.append(f"\n🔧 Signature:  {name}{signature}")
        
        parameters = data.get("parameters")
        if parameters:
            lines.append("   Parameters:")
            for p in parameters:
                p_type = p.get("type", "any")
                p_default = f" = {p['default']}" if "default" in p else ""
                lines.append(f"     - {p['name']}: {p_type}{p_default}")
                p_desc = p.get("description")
                if p_desc:
                    lines.append(f"       ↳ {p_desc}")
        
        returns = data.get("returns")
        if returns:
            lines.append(f"   ↩️  Returns:    {returns}")
        
        lines.append("=" * 60)
        return "\n".join(lines)
    
    # ── 类/枚举/dataclass 级查询 ──
    elif kind in ("class", "enum", "dataclass"):
        lines.append(f"\n✅ Found: {qualified_name}")
        lines.append("=" * 60)
        lines.append(f"📌 Name:       {name}")
        lines.append(f"🏷️  Kind:       {kind}")
        
        description = data.get("description")
        if description:
            lines.append(f"📝 Description: {description}")
        
        # 枚举成员
        members = data.get("members")
        if members:
            lines.append(f"\n📦 Members ({len(members)}):")
            for m in members:
                val = m.get("value")
                val_str = f" = {val!r}" if val is not None else ""
                lines.append(f"   ▸ {m['name']}{val_str}")
        
        # dataclass 字段
        fields = data.get("fields")
        if fields:
            lines.append(f"\n📦 Fields ({len(fields)}):")
            for f in fields:
                f_type = f.get("type", "?")
                f_default = f" = {f['default']}" if "default" in f else ""
                lines.append(f"   ▸ {f['name']}: {f_type}{f_default}")
        
        # 方法列表
        methods = data.get("methods")
        if methods:
            lines.append(f"\n📦 Methods ({len(methods)}):")
            for m in methods:
                m_desc = m.get("description", "")
                desc_str = f" — {m_desc}" if m_desc else ""
                sig = m.get("signature", "(...)")
                # 截取签名中的参数部分
                lines.append(f"   ▸ {m['name']}{sig}{desc_str}")
        
        lines.append("=" * 60)
        return "\n".join(lines)
    
    # ── 模块级查询 ──
    elif kind == "module" or "api_count" in data:
        mod_name = data.get("module", name)
        api_count = data.get("api_count", 0)
        children = data.get("children", data.get("apis", []))
        
        lines.append(f"\n✅ Found: {mod_name}")
        lines.append("=" * 60)
        lines.append(f"🏷️  Kind:       module")
        lines.append(f"📊 API Count:  {api_count}")
        
        if children:
            lines.append(f"\n📦 Children ({len(children)}):")
            for c in children:
                c_kind = c.get("kind", c.get("type", "?"))
                c_name = c.get("name", "?")
                c_desc = c.get("description", "")
                desc_str = f" — {c_desc}" if c_desc else ""
                lines.append(f"   ▸ {c_name} ({c_kind}){desc_str}")
        
        lines.append("=" * 60)
        return "\n".join(lines)
    
    # ── 其他 ──
    else:
        lines.append(f"\n✅ Found: {qualified_name}")
        lines.append("=" * 60)
        lines.append(f"📌 Name:       {name}")
        lines.append(f"🏷️  Kind:       {kind}")
        description = data.get("description")
        if description:
            lines.append(f"📝 Description: {description}")
        lines.append("=" * 60)
        return "\n".join(lines)


# ─── CLI 入口 ───────────────────────────────────────────────

def main():
    """主函数，处理命令行参数"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Python API Explorer - 探索Python模块的API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 python_api_explorer.py example.UserService
  python3 python_api_explorer.py example.UserService.find_user
  python3 python_api_explorer.py example.LogLevel
  python3 python_api_explorer.py example --output-json
"""
    )
    
    parser.add_argument(
        "query",
        help="查询字符串，格式: module.Class.method (e.g., 'example.UserService.find_user')"
    )
    
    parser.add_argument(
        "--output-json",
        action="store_true",
        help="以 JSON 格式输出（默认为人类可读格式）"
    )
    
    parser.add_argument(
        "--test",
        action="store_true",
        help="运行测试"
    )
    
    args = parser.parse_args()
    
    if args.test:
        _run_tests()
        return
    
    try:
        # 解析查询字符串: module.Class.method
        result = _resolve_query(args.query)
        
        if args.output_json:
            # JSON 输出模式
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            # 人类可读格式输出（默认）
            print(format_result(result, args.query))
        
    except ImportError as e:
        if args.output_json:
            print(json.dumps({"error": str(e)}, indent=2, ensure_ascii=False))
        else:
            print(f"\n❌ Error: {e}\n")
        sys.exit(1)
    except Exception as e:
        if args.output_json:
            print(json.dumps({"error": f"Unexpected error: {str(e)}"}, indent=2, ensure_ascii=False))
        else:
            print(f"\n❌ Error: {str(e)}\n")
        sys.exit(1)


def _resolve_query(query: str) -> Dict:
    """解析查询字符串并返回结果字典。
    
    支持的查询格式:
      - module                    → 模块级查询
      - module.Class              → 类级查询
      - module.Class.method       → 方法级查询
      - module.submodule.Class    → 类级查询
    """
    parts = query.split('.')
    
    # 策略：从最长路径逐步拆分，找到可以导入的模块前缀，
    # 然后将剩余部分作为属性链解析。
    
    for i in range(len(parts), 0, -1):
        module_path = '.'.join(parts[:i])
        attr_parts = parts[i:]
        
        # 尝试导入模块
        try:
            mod = importlib.import_module(module_path)
        except ImportError:
            continue
        
        if not attr_parts:
            # 无属性部分 → 模块级查询
            explorer = PythonApiExplorer.__new__(PythonApiExplorer)
            explorer.module_path = module_path
            explorer.module = mod
            return explorer.list_api()
        
        # 逐层解析属性
        current_obj = mod
        resolved_objs = []  # 保存每一层的解析结果
        for attr_name in attr_parts:
            if hasattr(current_obj, attr_name):
                resolved_objs.append((attr_name, current_obj))
                current_obj = getattr(current_obj, attr_name)
            else:
                current_obj = None
                break
        
        if current_obj is None:
            continue
        
        # 根据属性层级决定返回内容
        if len(attr_parts) == 1:
            # module.Class → 类/枚举/函数级查询
            name = attr_parts[0]
            if inspect.isclass(current_obj):
                return _build_class_doc(current_obj, name, module_path)
            elif inspect.isfunction(current_obj):
                return _build_function_doc(current_obj, name, module_path)
            else:
                return {"error": f"Unsupported type for '{name}'"}
        
        elif len(attr_parts) == 2:
            # module.Class.method → 方法级查询
            class_name = attr_parts[0]
            method_name = attr_parts[1]
            
            # 获取父类对象（倒数第二层解析的对象）
            parent_obj = resolved_objs[-1][1]  # 倒数第二层解析时的 current_obj
            parent_name = resolved_objs[-1][0]  # attr_parts[-1] 对应的属性名
            
            if not inspect.isclass(parent_obj):
                # 如果父不是类，尝试从模块获取
                parent_obj = getattr(mod, class_name, None)
            
            if parent_obj is None or not inspect.isclass(parent_obj):
                return {"error": f"'{class_name}' is not a class"}
            
            class_qualified = f"{getattr(parent_obj, '__module__', module_path)}.{class_name}"
            qualified_name = f"{class_qualified}.{method_name}"
            
            # 构建方法信息
            result = {
                "name": method_name,
                "qualifiedName": qualified_name,
                "kind": "method",
            }
            sig = None
            try:
                sig = str(inspect.signature(current_obj))
            except (ValueError, TypeError):
                pass
            if sig:
                result["signature"] = sig
            doc = inspect.getdoc(current_obj)
            desc = None
            if doc:
                lines = [l.strip() for l in doc.split('\n') if l.strip()]
                desc = lines[0] if lines else None
            if desc:
                result["description"] = desc
            if doc:
                result["full_doc"] = doc
            # 返回类型
            try:
                sig_obj = inspect.signature(current_obj)
                if sig_obj.return_annotation != inspect.Signature.empty:
                    result["returns"] = str(sig_obj.return_annotation).replace('typing.', '')
            except (ValueError, TypeError):
                pass
            # 参数
            params = []
            try:
                sig_obj = inspect.signature(current_obj)
                for p_name, param in sig_obj.parameters.items():
                    if p_name in ('self', 'cls'):
                        continue
                    p_info = {"name": p_name}
                    if param.annotation != inspect.Parameter.empty:
                        p_info["type"] = str(param.annotation).replace('typing.', '')
                    if param.default != inspect.Parameter.empty:
                        p_info["default"] = repr(param.default)
                    params.append(p_info)
            except (ValueError, TypeError):
                pass
            if params:
                result["parameters"] = params
            return result
        
        elif len(attr_parts) >= 3:
            # 更深层属性，如 module.submodule.Class.method
            # 取最后两部分作为 Class.method
            parent_obj = resolved_objs[-1][1]  # 倒数第二层解析时的 current_obj
            member_name = attr_parts[-1]
            
            # 尝试在父对象中找成员
            if hasattr(parent_obj, member_name):
                member_obj = getattr(parent_obj, member_name)
                result = {
                    "name": member_name,
                    "qualifiedName": query,
                    "kind": _get_simple_type_name(member_obj),
                }
                doc = inspect.getdoc(member_obj)
                if doc:
                    lines = [l.strip() for l in doc.split('\n') if l.strip()]
                    result["description"] = lines[0] if lines else None
                return result
            
            return {"error": f"Could not resolve '{member_name}' in '{'.'.join(attr_parts[:-1])}'"}
    
    return {"error": f"Could not resolve query: '{query}'"}


def _get_simple_type_name(obj: Any) -> str:
    """简单类型名判断"""
    if inspect.isclass(obj):
        if issubclass(obj, Enum):
            return "enum"
        return "class"
    elif inspect.isfunction(obj):
        return "function"
    elif inspect.ismethod(obj):
        return "method"
    return "unknown"


def _build_class_doc(cls: type, name: str, module_path: str) -> Dict:
    """构建类的文档字典"""
    qualified_name = f"{getattr(cls, '__module__', module_path)}.{name}"
    
    doc = inspect.getdoc(cls)
    desc = None
    if doc:
        lines = [l.strip() for l in doc.split('\n') if l.strip()]
        desc = lines[0] if lines else None
    
    result = {
        "name": name,
        "qualifiedName": qualified_name,
        "kind": "enum" if issubclass(cls, Enum) else "class",
    }
    if desc:
        result["description"] = desc
    if doc:
        result["full_doc"] = doc
    result["module"] = getattr(cls, '__module__', module_path)
    
    # 枚举成员
    if issubclass(cls, Enum):
        enum_members = []
        for m_name, m_val in cls.__members__.items():
            enum_members.append({"name": m_name, "value": m_val.value})
        if enum_members:
            result["members"] = enum_members
        return result
    
    # 类方法
    methods = []
    for m_name, m_obj in inspect.getmembers(cls):
        if m_name.startswith('_'):
            continue
        if not (inspect.isfunction(m_obj) or inspect.ismethod(m_obj)):
            continue
        m_qualified = f"{qualified_name}.{m_name}"
        m_info = {
            "name": m_name,
            "qualifiedName": m_qualified,
            "kind": "method",
        }
        m_sig = None
        try:
            m_sig = str(inspect.signature(m_obj))
        except (ValueError, TypeError):
            pass
        if m_sig:
            m_info["signature"] = m_sig
        m_doc = inspect.getdoc(m_obj)
        m_desc = None
        if m_doc:
            m_lines = [l.strip() for l in m_doc.split('\n') if l.strip()]
            m_desc = m_lines[0] if m_lines else None
        if m_desc:
            m_info["description"] = m_desc
        if m_doc:
            m_info["full_doc"] = m_doc
        # 返回类型
        try:
            sig_obj = inspect.signature(m_obj)
            if sig_obj.return_annotation != inspect.Signature.empty:
                m_info["returns"] = str(sig_obj.return_annotation).replace('typing.', '')
        except (ValueError, TypeError):
            pass
        # 参数
        params = []
        try:
            sig_obj = inspect.signature(m_obj)
            for p_name, param in sig_obj.parameters.items():
                if p_name in ('self', 'cls'):
                    continue
                p_info = {"name": p_name}
                if param.annotation != inspect.Parameter.empty:
                    p_info["type"] = str(param.annotation).replace('typing.', '')
                if param.default != inspect.Parameter.empty:
                    p_info["default"] = repr(param.default)
                params.append(p_info)
        except (ValueError, TypeError):
            pass
        if params:
            m_info["parameters"] = params
        methods.append(m_info)
    if methods:
        result["methods"] = methods
    
    # dataclass 字段
    from dataclasses import fields as dc_fields, is_dataclass
    if is_dataclass(cls):
        fields = []
        try:
            from typing import get_type_hints
            hints = get_type_hints(cls)
        except Exception:
            hints = {}
        import dataclasses as dc
        for f in dc_fields(cls):
            f_info = {"name": f.name}
            if f.name in hints:
                f_info["type"] = str(hints[f.name]).replace('typing.', '')
            if f.default is not dc.MISSING:
                f_info["default"] = repr(f.default)
            elif f.default_factory is not dc.MISSING:
                f_info["default"] = "..."
            fields.append(f_info)
        if fields:
            result["fields"] = fields
    
    return result


def _build_function_doc(func, name: str, module_path: str) -> Dict:
    """构建函数的文档字典"""
    qualified_name = f"{getattr(func, '__module__', module_path)}.{name}"
    
    doc = inspect.getdoc(func)
    desc = None
    if doc:
        lines = [l.strip() for l in doc.split('\n') if l.strip()]
        desc = lines[0] if lines else None
    
    result = {
        "name": name,
        "qualifiedName": qualified_name,
        "kind": "function",
    }
    sig = None
    try:
        sig = str(inspect.signature(func))
    except (ValueError, TypeError):
        pass
    if sig:
        result["signature"] = sig
    if desc:
        result["description"] = desc
    if doc:
        result["full_doc"] = doc
    result["module"] = getattr(func, '__module__', module_path)
    # 返回类型
    try:
        sig_obj = inspect.signature(func)
        if sig_obj.return_annotation != inspect.Signature.empty:
            result["returns"] = str(sig_obj.return_annotation).replace('typing.', '')
    except (ValueError, TypeError):
        pass
    # 参数
    params = []
    try:
        sig_obj = inspect.signature(func)
        for p_name, param in sig_obj.parameters.items():
            if p_name in ('self', 'cls'):
                continue
            p_info = {"name": p_name}
            if param.annotation != inspect.Parameter.empty:
                p_info["type"] = str(param.annotation).replace('typing.', '')
            if param.default != inspect.Parameter.empty:
                p_info["default"] = repr(param.default)
            params.append(p_info)
    except (ValueError, TypeError):
        pass
    if params:
        result["parameters"] = params
    
    return result


def _run_tests() -> None:
    """测试函数"""
    print("=== PythonApiExplorer 测试 ===")
    
    # 测试1: 使用标准库模块
    print("\n1. 测试 json 模块:")
    explorer = PythonApiExplorer("json")
    result = explorer.list_api()
    print(f"  找到 {result.get('api_count', 0)} 个API")
    
    # 测试2: 获取特定API
    print("\n2. 获取 json.dumps 的文档:")
    result = explorer.get_api_doc("dumps")
    print(format_result(result, "json.dumps"))
    
    # 测试3: 测试类
    print("\n3. 获取 json.JSONDecoder 的文档:")
    result = explorer.get_api_doc("JSONDecoder")
    print(format_result(result, "json.JSONDecoder"))
    
    # 测试4: 错误处理
    print("\n4. 测试不存在的API:")
    result = explorer.get_api_doc("nonexistent_function")
    print(format_result(result, "json.nonexistent_function"))
    
    print("\n=== 测试完成 ===")


if __name__ == "__main__":
    main()

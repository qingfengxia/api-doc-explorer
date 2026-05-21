#!/usr/bin/env python3
"""
Python API Explorer - 用于探索Python模块API的命令行工具
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


@dataclass
class ApiInfo:
    """API信息数据结构"""
    name: str
    type: str
    signature: Optional[str] = None
    description: Optional[str] = None
    full_doc: Optional[str] = None
    module: Optional[str] = None
    members: Optional[List[Dict]] = None
    

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
            members.append({
                "name": name,
                "type": member_type,
                "signature": self._get_signature(member) if callable(member) else None
            })
        
        return members if members else None
    
    def list_api(self) -> str:
        """
        列出模块中的所有API
        
        Returns:
            格式化的JSON字符串
        """
        if not self.module:
            return json.dumps({"error": f"Module {self.module_path} not found"}, indent=2)
        
        api_list = []
        
        # 获取模块的所有公共成员
        for name, obj in inspect.getmembers(self.module):
            # 跳过私有成员和特殊成员
            if name.startswith('_'):
                continue
            
            api_type = self._get_type_name(obj)
            signature = self._get_signature(obj) if callable(obj) else None
            doc = inspect.getdoc(obj)
            description = self._get_one_line_description(doc)
            
            api_info = {
                "name": name,
                "type": api_type,
                "signature": signature,
                "description": description
            }
            api_list.append(api_info)
        
        result = {
            "module": self.module_path,
            "api_count": len(api_list),
            "apis": api_list
        }
        
        return json.dumps(result, indent=2, ensure_ascii=False)
    
    def get_api_doc(self, api_name: str) -> str:
        """
        获取指定API的详细文档
        
        Args:
            api_name: API名称
            
        Returns:
            格式化的JSON字符串
        """
        if not self.module:
            return json.dumps({"error": f"Module {self.module_path} not found"}, indent=2)
        
        # 获取API对象
        if not hasattr(self.module, api_name):
            return json.dumps({"error": f"API '{api_name}' not found in module '{self.module_path}'"}, indent=2)
        
        obj = getattr(self.module, api_name)
        api_type = self._get_type_name(obj)
        signature = self._get_signature(obj)
        full_doc = inspect.getdoc(obj)
        description = self._get_one_line_description(full_doc)
        
        # 获取类/枚举的成员
        members = None
        if inspect.isclass(obj):
            members = self._get_api_members(api_name, obj)
        
        api_info = ApiInfo(
            name=api_name,
            type=api_type,
            signature=signature,
            description=description,
            full_doc=full_doc,
            module=self.module_path,
            members=members
        )
        
        # 转换为字典
        result = asdict(api_info)
        
        # 移除None值
        result = {k: v for k, v in result.items() if v is not None}
        
        return json.dumps(result, indent=2, ensure_ascii=False)


def test() -> None:
    """测试函数"""
    print("=== PythonApiExplorer 测试 ===")
    
    # 测试1: 使用标准库模块
    print("\n1. 测试 json 模块:")
    explorer = PythonApiExplorer("json")
    print(explorer.list_api())
    
    # 测试2: 获取特定API
    print("\n2. 获取 json.dumps 的文档:")
    print(explorer.get_api_doc("dumps"))
    
    # 测试3: 测试类
    print("\n3. 获取 json.JSONDecoder 的文档:")
    print(explorer.get_api_doc("JSONDecoder"))
    
    # 测试4: 测试嵌套模块
    print("\n4. 测试 collections.abc 模块:")
    explorer2 = PythonApiExplorer("collections.abc")
    list_result = json.loads(explorer2.list_api())
    print(f"找到 {list_result['api_count']} 个API")
    
    # 测试5: 获取类的成员
    print("\n5. 获取 Iterable 类的成员:")
    print(explorer2.get_api_doc("Iterable"))
    
    # 测试6: 错误处理
    print("\n6. 测试不存在的模块:")
    try:
        explorer3 = PythonApiExplorer("nonexistent.module")
    except ImportError as e:
        print(f"错误捕获成功: {e}")
    
    print("\n7. 测试不存在的API:")
    print(explorer.get_api_doc("nonexistent_function"))
    
    print("\n=== 测试完成 ===")


def main():
    """主函数，处理命令行参数"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Python API Explorer - 探索Python模块的API",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "module_path",
        help="模块路径，例如 'json' 或 'collections.abc'"
    )
    
    parser.add_argument(
        "api_name",
        nargs="?",
        default=None,
        help="可选的API名称，如果提供则获取该API的详细文档"
    )
    
    parser.add_argument(
        "--test",
        action="store_true",
        help="运行测试"
    )
    
    args = parser.parse_args()
    
    if args.test:
        test()
        return
    
    try:
        explorer = PythonApiExplorer(args.module_path)
        
        if args.api_name:
            # 获取特定API的文档
            result = explorer.get_api_doc(args.api_name)
        else:
            # 列出所有API
            result = explorer.list_api()
        
        print(result)
        
    except ImportError as e:
        error_result = {"error": str(e)}
        print(json.dumps(error_result, indent=2))
        sys.exit(1)
    except Exception as e:
        error_result = {"error": f"Unexpected error: {str(e)}"}
        print(json.dumps(error_result, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
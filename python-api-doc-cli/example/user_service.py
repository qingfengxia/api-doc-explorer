"""
用户服务模块，负责处理用户的增删改查。
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class User:
    """代表一个用户的实体。

    Attributes:
        id: 用户的唯一标识符
        name: 用户的显示名称
        age: 用户年龄，如果不提供则为 None
        email: 用户邮箱地址
    """
    id: str
    name: str
    age: Optional[int] = None
    email: Optional[str] = None


@dataclass
class UserFilter:
    """用户查询过滤条件。

    Attributes:
        name_contains: 按名称模糊搜索
        min_age: 按最小年龄筛选
    """
    name_contains: Optional[str] = None
    min_age: Optional[int] = None


class UserService:
    """用户服务类，负责处理用户的增删改查。

    这是一个单例服务，通常不需要实例化。

    Example::

        svc = UserService.get_instance()
        user = svc.find_user("123")
        print(user.name)
    """

    _instance: Optional[UserService] = None
    _users: dict[str, User] = field(default_factory=dict)

    def __init__(self) -> None:
        self._users: dict[str, User] = {}

    @classmethod
    def get_instance(cls) -> UserService:
        """获取服务实例（单例模式）。

        Returns:
            UserService: 单例实例
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def find_user(self, id: str) -> Optional[User]:
        """根据 ID 查找用户。

        Args:
            id: 要查找的用户 ID

        Returns:
            找到的用户对象，如果未找到则返回 None

        Raises:
            ValueError: 当 ID 为空时抛出错误
        """
        if not id:
            raise ValueError("ID is required")
        return self._users.get(id)

    def list_users(self, filter: Optional[UserFilter] = None) -> List[User]:
        """根据过滤条件查询用户列表。

        Args:
            filter: 查询过滤条件

        Returns:
            匹配的用户列表
        """
        results = list(self._users.values())
        if filter and filter.name_contains:
            results = [u for u in results if filter.name_contains.lower() in u.name.lower()]
        if filter and filter.min_age is not None:
            results = [u for u in results if u.age is not None and u.age >= filter.min_age]
        return results

    def create_user(self, name: str, age: Optional[int] = None,
                    email: Optional[str] = None) -> User:
        """创建新用户。

        Args:
            name: 用户名称
            age: 用户年龄（可选）
            email: 用户邮箱（可选）

        Returns:
            创建完成的用户对象（含自动生成的 id）
        """
        import time
        user = User(id=str(int(time.time() * 1000)), name=name, age=age, email=email)
        self._users[user.id] = user
        return user

    def delete_user(self, id: str) -> bool:
        """删除指定用户。

        Args:
            id: 要删除的用户 ID

        Returns:
            是否删除成功
        """
        return self._users.pop(id, None) is not None

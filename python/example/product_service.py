"""
商品服务模块，负责商品的增删改查和库存管理。
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List
import time


class ProductCategory(Enum):
    """商品类别的枚举定义。"""
    ELECTRONICS = "electronics"  #: 电子产品
    CLOTHING = "clothing"       #: 服装
    FOOD = "food"               #: 食品
    BOOKS = "books"             #: 书籍


@dataclass
class Product:
    """商品实体的结构。

    Attributes:
        id: 商品唯一标识符
        name: 商品名称
        description: 商品描述
        price: 商品价格，单位为分
        category: 商品类目
        stock: 库存数量
        active: 商品是否上架
    """
    id: str
    name: str
    description: str
    price: int
    category: ProductCategory
    stock: int = 0
    active: bool = True


@dataclass
class CreateProductInput:
    """创建商品的输入参数，不含 id 和 active 字段。

    Attributes:
        name: 商品名称
        description: 商品描述
        price: 商品价格，单位为分
        category: 商品类目
        stock: 库存数量，默认为 0
    """
    name: str
    description: str
    price: int
    category: ProductCategory
    stock: Optional[int] = None


class ProductService:
    """商品服务类，负责商品的增删改查和库存管理。

    提供了完整的商品生命周期管理功能，包括创建、查询、上下架和库存调整。

    Example::

        svc = ProductService.get_instance()
        product = svc.create_product(CreateProductInput(
            name="TypeScript 实战",
            description="一本关于 TypeScript 的书",
            price=8900,
            category=ProductCategory.BOOKS,
        ))
    """

    _instance: Optional[ProductService] = None

    def __init__(self) -> None:
        self._products: dict[str, Product] = {}

    @classmethod
    def get_instance(cls) -> ProductService:
        """获取服务实例（单例模式）。

        Returns:
            ProductService: 单例实例
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def create_product(self, input: CreateProductInput) -> Product:
        """创建一个新商品。

        Args:
            input: 创建商品的输入参数

        Returns:
            新创建的商品对象

        Raises:
            ValueError: 当价格为负数时抛出错误
        """
        if input.price < 0:
            raise ValueError("Price cannot be negative")
        product = Product(
            id=f"prod_{int(time.time() * 1000)}",
            name=input.name,
            description=input.description,
            price=input.price,
            category=input.category,
            stock=input.stock or 0,
            active=True,
        )
        self._products[product.id] = product
        return product

    def find_product(self, id: str) -> Optional[Product]:
        """根据 ID 查找商品。

        Args:
            id: 商品 ID

        Returns:
            商品对象，未找到返回 None
        """
        return self._products.get(id)

    def list_by_category(self, category: ProductCategory) -> List[Product]:
        """按类目查询所有上架商品。

        Args:
            category: 商品类目

        Returns:
            该类目下的上架商品列表
        """
        return [p for p in self._products.values()
                if p.category == category and p.active]

    def adjust_stock(self, id: str, delta: int) -> Optional[Product]:
        """调整商品库存数量。

        Args:
            id: 商品 ID
            delta: 库存变化量（正数加库存，负数减库存）

        Returns:
            更新后的商品对象，未找到返回 None

        Raises:
            ValueError: 当库存调整后为负数时抛出错误
        """
        product = self._products.get(id)
        if product is None:
            return None
        new_stock = product.stock + delta
        if new_stock < 0:
            raise ValueError("Stock cannot be negative")
        product.stock = new_stock
        return product

    def set_active(self, id: str, active: bool) -> Optional[Product]:
        """上架或下架商品。

        Args:
            id: 商品 ID
            active: 是否上架

        Returns:
            更新后的商品，未找到返回 None
        """
        product = self._products.get(id)
        if product is None:
            return None
        product.active = active
        return product

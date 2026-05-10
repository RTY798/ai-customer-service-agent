"""电商数据模型与 Provider 抽象接口

自定义 Provider 只需继承 ECommerceDataProvider 并实现所有属性方法。
参考 demo_provider.py 和 docs/DATA_PROVIDER.md。
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from typing import Optional


# ── 数据模型 ──────────────────────────────────────────────


@dataclass(frozen=True)
class Order:
    order_id: str
    status: str
    product: str
    amount: float
    date: str


@dataclass(frozen=True)
class Shipment:
    order_id: str
    carrier: str
    tracking_no: str
    location: str
    estimated: str
    status: str


@dataclass(frozen=True)
class Product:
    product_id: str
    name: str
    price: float
    features: list[str]
    warranty: str


@dataclass(frozen=True)
class ReturnPolicy:
    category: str
    policy: str


@dataclass(frozen=True)
class KnowledgeDoc:
    id: str
    title: str
    content: str


# ── Provider 抽象接口 ─────────────────────────────────────


class ECommerceDataProvider(ABC):
    """电商数据提供者接口。

    实现此接口以接入真实数据源（数据库、第三方 API 等）。
    所有方法返回数据模型实例，调用方负责序列化。
    """

    # ── 订单 ──

    @abstractmethod
    def get_order(self, order_id: str) -> Optional[Order]:
        ...

    @abstractmethod
    def list_orders(self) -> list[Order]:
        ...

    # ── 物流 ──

    @abstractmethod
    def get_shipment(self, order_id: str) -> Optional[Shipment]:
        ...

    @abstractmethod
    def list_shipments(self) -> list[Shipment]:
        ...

    # ── 商品 ──

    @abstractmethod
    def get_product(self, product_id: str) -> Optional[Product]:
        ...

    @abstractmethod
    def list_products(self) -> list[Product]:
        ...

    # ── 退换货政策 ──

    @abstractmethod
    def get_return_policy(self, category: str) -> Optional[ReturnPolicy]:
        ...

    @abstractmethod
    def list_return_policy_categories(self) -> list[str]:
        ...

    # ── 知识库文档 ──

    @abstractmethod
    def get_all_knowledge_docs(self) -> list[KnowledgeDoc]:
        ...

    @abstractmethod
    def get_knowledge_doc(self, doc_id: str) -> Optional[KnowledgeDoc]:
        ...

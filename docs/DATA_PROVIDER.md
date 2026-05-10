# 自定义数据 Provider 接入指南

## 架构说明

```
tool_agent.py / vector_store.py
        │
        ▼
  get_data_provider()  ←  config.py (根据 DATA_PROVIDER 环境变量加载)
        │
        ▼
  ECommerceDataProvider  ←  你的自定义 Provider
        │
        ▼
  你的数据库 / 第三方 API / ERP 系统
```

系统通过 `ECommerceDataProvider` 抽象接口获取所有数据。默认使用内置的 `DemoDataProvider`（模拟数据）。替换为真实数据只需实现该接口并配置环境变量。

## 实现步骤

### 第一步：创建 Provider 类

```python
# myapp/providers.py
from typing import Optional
from app.data.base import ECommerceDataProvider, Order, Product, Shipment, ReturnPolicy, KnowledgeDoc


class MyCustomProvider(ECommerceDataProvider):
    """接入我的真实电商数据库"""

    # ── 订单 ──
    def get_order(self, order_id: str) -> Optional[Order]:
        # 从数据库查询
        row = db.query("SELECT * FROM orders WHERE id = ?", order_id)
        if row:
            return Order(order_id=row["id"], status=row["status"],
                        product=row["product"], amount=float(row["amount"]), date=row["date"])
        return None

    def list_orders(self) -> list[Order]:
        rows = db.query("SELECT * FROM orders LIMIT 100")
        return [Order(order_id=r["id"], status=r["status"], product=r["product"],
                      amount=float(r["amount"]), date=r["date"]) for r in rows]

    # ── 物流 ──
    def get_shipment(self, order_id: str) -> Optional[Shipment]:
        # 调用第三方物流 API
        ...

    def list_shipments(self) -> list[Shipment]:
        ...

    # ── 商品 ──
    def get_product(self, product_id: str) -> Optional[Product]:
        ...

    def list_products(self) -> list[Product]:
        ...

    # ── 退换货政策 ──
    def get_return_policy(self, category: str) -> Optional[ReturnPolicy]:
        ...

    def list_return_policy_categories(self) -> list[str]:
        ...

    # ── 知识库文档 ──
    def get_all_knowledge_docs(self) -> list[KnowledgeDoc]:
        ...

    def get_knowledge_doc(self, doc_id: str) -> Optional[KnowledgeDoc]:
        ...
```

### 第二步：配置环境变量

```ini
# .env
DATA_PROVIDER=myapp.providers:MyCustomProvider
```

格式为 `模块路径:类名`，与 uvicorn 的 worker 字符串格式一致。

### 第三步：安装你的模块

```bash
pip install myapp
# 或将 myapp/ 放在 backend/ 目录下
```

## 数据模型参考

所有数据模型定义在 `backend/app/data/base.py`：

| 模型 | 字段 |
|------|------|
| `Order` | order_id, status, product, amount, date |
| `Shipment` | order_id, carrier, tracking_no, location, estimated, status |
| `Product` | product_id, name, price, features, warranty |
| `ReturnPolicy` | category, policy |
| `KnowledgeDoc` | id, title, content |

## 完整示例：对接 SQLite

```python
import sqlite3
from typing import Optional
from app.data.base import ECommerceDataProvider, Order, Product, KnowledgeDoc


class SQLiteProvider(ECommerceDataProvider):
    def __init__(self, db_path: str = "shop.db"):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row

    def get_order(self, order_id: str) -> Optional[Order]:
        cur = self.conn.execute("SELECT * FROM orders WHERE id=?", (order_id,))
        row = cur.fetchone()
        if not row:
            return None
        return Order(order_id=row["id"], status=row["status"],
                    product=row["product_name"], amount=row["amount"], date=row["created_at"])

    def list_orders(self) -> list[Order]:
        cur = self.conn.execute("SELECT * FROM orders LIMIT 100")
        return [Order(...) for row in cur.fetchall()]

    # ... 实现其余方法 ...
```

## 注意事项

1. **不要修改 DemoDataProvider** — DemoDataProvider 保留为内置演示数据。自定义数据请新建类
2. **方法必须全部实现** — `ECommerceDataProvider` 的所有抽象方法都需要实现，否则运行时报错
3. **性能** — 接口返回 Python 对象，大数据量建议在 Provider 内部做分页
4. **错误处理** — Provider 内部异常会传播到 Agent 调用层，建议在 Provider 内部做好异常捕获和日志

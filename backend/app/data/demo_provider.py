"""演示数据 Provider — 使用内置模拟数据"""

from datetime import datetime, timedelta
from typing import Optional

from app.data.base import (
    ECommerceDataProvider,
    Order,
    Shipment,
    Product,
    ReturnPolicy,
    KnowledgeDoc,
)


# ── 内置模拟数据 ──────────────────────────────────────────

_ORDERS: dict[str, Order] = {
    "ORD-001": Order("ORD-001", "shipped", "智能蓝牙耳机 Pro", 299.00, "2026-05-01"),
    "ORD-002": Order("ORD-002", "processing", "无线充电板", 89.00, "2026-05-05"),
    "ORD-003": Order("ORD-003", "delivered", "机械键盘 K8", 459.00, "2026-04-20"),
}

_PRODUCTS: dict[str, Product] = {
    "P001": Product("P001", "智能蓝牙耳机 Pro", 299.00,
                    ["主动降噪", "30小时续航", "IPX5防水", "蓝牙5.3"], "12个月"),
    "P002": Product("P002", "无线充电板", 89.00,
                    ["15W快充", "兼容Qi标准", "LED指示灯", "过温保护"], "6个月"),
    "P003": Product("P003", "机械键盘 K8", 459.00,
                    ["87键紧凑布局", "热插拔轴座", "RGB背光", "Type-C键线分离"], "12个月"),
}

_POLICIES: dict[str, ReturnPolicy] = {
    "electronics": ReturnPolicy("electronics",
        "电子产品支持7天无理由退货，需保持包装完整、配件齐全。退款将在收到退货后3-5个工作日内原路返回。"),
    "clothing": ReturnPolicy("clothing",
        "服装类支持15天无理由退换，需保持吊牌完整、无穿着痕迹。换货免运费。"),
    "books": ReturnPolicy("books",
        "图书类支持7天无理由退货，需保持无污损、无笔记划线。"),
}

_KB_DOCS: list[KnowledgeDoc] = [
    KnowledgeDoc("faq_01", "退货政策",
        "支持7天无理由退货，商品需保持原状、包装完整。退款在收到退货后3-5个工作日内原路返还。部分商品如食品、内衣等不支持无理由退货。退货流程：登录账号→我的订单→申请退货→填写原因→寄回商品→退款。"),
    KnowledgeDoc("faq_02", "配送说明",
        "全国配送，标准时效3-5个工作日，偏远地区7-10个工作日。订单满99元包邮，不满99元收8元运费。配送时间周一至周日9:00-21:00。可在订单详情查看物流信息。"),
    KnowledgeDoc("faq_03", "账户安全",
        "支持手机号或邮箱注册，密码需字母+数字不少于8位。可开启双重验证提升安全性。忘记密码可通过注册手机号或邮箱找回。建议定期改密码，不与其他平台共用密码。"),
    KnowledgeDoc("faq_04", "支付方式",
        "支持微信支付、支付宝、银行卡、花呗分期（3/6/12期）。所有支付加密传输，不存储银行卡信息。订单完成后可申请电子发票，3个工作日内发送至邮箱。"),
    KnowledgeDoc("faq_05", "售后服务",
        "电子产品12个月质保，非人为损坏免费维修或更换。超出质保期或人为损坏提供有偿维修。维修时效7-15个工作日。可在线上提交售后申请。"),
    KnowledgeDoc("faq_06", "优惠券与积分",
        "优惠券不可叠加使用，每笔订单限用一张。部分有最低消费门槛。消费1元积1分，每日签到得2积分。100积分抵扣1元。积分有效期12个月，过期清零。"),
    KnowledgeDoc("prod_01", "智能蓝牙耳机 Pro",
        "售价299元。主动降噪，30小时续航，IPX5防水，蓝牙5.3芯片。支持快充（充电10分钟使用2小时）。附赠3种尺寸耳塞。"),
    KnowledgeDoc("prod_02", "机械键盘 K8",
        "售价459元。87键紧凑布局，热插拔轴座可更换轴体。全键RGB背光，Type-C键线分离。兼容Windows/Mac双系统。PBT键帽耐磨不打油。"),
    KnowledgeDoc("prod_03", "无线充电板",
        "售价89元。15W快充，兼容Qi标准。LED指示灯，过温保护。支持绝大多数支持无线充电的手机。"),
]


# ── 演示 Provider 实现 ───────────────────────────────────


class DemoDataProvider(ECommerceDataProvider):

    # ── 订单 ──

    def get_order(self, order_id: str) -> Optional[Order]:
        return _ORDERS.get(order_id)

    def list_orders(self) -> list[Order]:
        return list(_ORDERS.values())

    # ── 物流 ──

    def __init__(self):
        self._shipments_cache: Optional[dict[str, Shipment]] = None

    def _build_shipments(self) -> dict[str, Shipment]:
        today = datetime.now()
        return {
            "ORD-001": Shipment("ORD-001", "顺丰快递", "SF1234567890", "上海市分拣中心",
                               (today + timedelta(days=1)).strftime("%m月%d日"), "运输中"),
            "ORD-002": Shipment("ORD-002", "中通快递", "ZT9876543210", "已出库",
                               (today + timedelta(days=3)).strftime("%m月%d日"), "待揽收"),
        }

    def get_shipment(self, order_id: str) -> Optional[Shipment]:
        if self._shipments_cache is None:
            self._shipments_cache = self._build_shipments()
        return self._shipments_cache.get(order_id)

    def list_shipments(self) -> list[Shipment]:
        if self._shipments_cache is None:
            self._shipments_cache = self._build_shipments()
        return list(self._shipments_cache.values())

    # ── 商品 ──

    def get_product(self, product_id: str) -> Optional[Product]:
        return _PRODUCTS.get(product_id)

    def list_products(self) -> list[Product]:
        return list(_PRODUCTS.values())

    # ── 退换货政策 ──

    def get_return_policy(self, category: str) -> Optional[ReturnPolicy]:
        return _POLICIES.get(category)

    def list_return_policy_categories(self) -> list[str]:
        return list(_POLICIES.keys())

    # ── 知识库文档 ──

    def get_all_knowledge_docs(self) -> list[KnowledgeDoc]:
        return _KB_DOCS

    def get_knowledge_doc(self, doc_id: str) -> Optional[KnowledgeDoc]:
        for doc in _KB_DOCS:
            if doc.id == doc_id:
                return doc
        return None

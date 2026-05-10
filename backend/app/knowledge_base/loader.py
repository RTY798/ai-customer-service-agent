"""知识库初始化 — 使用轻量关键词检索，无需外部依赖"""

from app.knowledge_base.vector_store import _load_docs


def seed_knowledge_base():
    """初始化知识库（预热加载）"""
    docs = _load_docs()
    print(f"知识库加载完成：{len(docs)} 篇文档")


def seed_sample_orders():
    print("模拟订单数据已就绪")

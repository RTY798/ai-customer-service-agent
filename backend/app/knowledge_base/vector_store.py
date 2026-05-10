"""轻量级知识库检索 — 基于关键词匹配，无需外部向量数据库"""

import re
from app.data.config import get_data_provider

_documents = None


def _load_docs():
    """通过 Data Provider 加载知识库文档"""
    global _documents
    if _documents is not None:
        return _documents

    provider = get_data_provider()
    docs = provider.get_all_knowledge_docs()
    _documents = [{"id": d.id, "title": d.title, "content": d.content} for d in docs]
    return _documents


def _tokenize(text: str) -> set:
    """简单的分词：中文按字拆分 + 英文按空格"""
    text = text.lower()
    words = set(re.findall(r"[a-z]+", text))
    chars = set(re.findall(r"[一-鿿]", text))
    return words | chars


def _score(query_tokens: set, doc_tokens: set) -> float:
    """Jaccard 相似度"""
    if not query_tokens:
        return 0
    intersection = query_tokens & doc_tokens
    union = query_tokens | doc_tokens
    return len(intersection) / len(union)


def get_vector_store():
    """统一接口，返回 self 以兼容原有调用方式"""
    return _KnowledgeBase()


class _KnowledgeBase:
    """简单关键词检索知识库"""

    def query(self, query_texts, n_results=3):
        query = query_texts[0] if isinstance(query_texts, list) else query_texts
        docs = _load_docs()

        qt = _tokenize(query)
        scored = []
        for d in docs:
            dt = _tokenize(d["title"] + " " + d["content"])
            score = _score(qt, dt)
            scored.append((score, d))

        scored.sort(key=lambda x: -x[0])
        top = scored[:n_results]

        return {
            "documents": [[d["content"] for _, d in top]],
            "metadatas": [[{"source": d["title"]} for _, d in top]],
            "distances": [[1 - s for s, _ in top]],
        }

from app.agents.llm_client import call_llm
from app.knowledge_base.vector_store import get_vector_store
from app.util.message_utils import to_llm_messages

KNOWLEDGE_SYSTEM_PROMPT = """你是一个电商智能客服的知识库问答助手。根据用户的问题和检索到的相关文档，给出准确、友好的回答。

规则：
1. 如果检索到的文档足以回答问题，基于文档内容回答
2. 如果文档不足以回答，诚实告知并建议转向人工客服
3. 回答要简洁友好，不要过长
4. 引用文档内容时说明来源"""


def knowledge_node(state):
    user_msg = state["user_message"]

    vs = get_vector_store()
    results = vs.query(query_texts=[user_msg], n_results=3)
    documents = results["documents"][0] if results["documents"] else []
    metadatas = results["metadatas"][0] if results["metadatas"] else []

    context_parts = []
    for i, doc in enumerate(documents, 1):
        context_parts.append(f"[文档{i}] {doc}")

    context = "\n\n".join(context_parts)

    thought_input = f"检索到 {len(documents)} 条相关文档"
    thought_detail = "\n".join(
        [f"• {d[:80]}..." for d in documents]
    ) if documents else "未找到相关文档"

    summary = state.get("summary_message", [])
    full_history = state.get("messages", [])

    llm_messages = [
        {"role": "system", "content": KNOWLEDGE_SYSTEM_PROMPT}
    ]

    if summary:
        llm_messages.append({
            "role": "system",
            "content": f"可参考对话历史摘要回答用户问题，【对话历史摘要】{summary}\n"
        })

    recent_messages = full_history[-12:] if len(full_history) > 12 else full_history
    llm_messages += to_llm_messages(recent_messages)

    msg = call_llm(
        messages=llm_messages,
        temperature=0.3,
    )

    answer = msg["content"]

    thought = {
        "agent": "knowledge",
        "status": "completed",
        "input": thought_input,
        "output": answer,
        "detail": thought_detail,
    }

    existing_thoughts = state.get("thought_chain", [])
    return {
        "messages": [msg],
        "retrieved_docs": documents,
        "thought_chain": existing_thoughts + [thought],
    }

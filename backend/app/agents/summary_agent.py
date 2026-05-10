from app.agents.llm_client import call_llm

SUMMARY_SYSTEM_PROMPT = """你是一个电商智能客服的回复汇总助手。根据用户的问题和所有 Agent 的处理结果，生成最终回复。

规则：
1. 回复要友好、专业，带称呼
2. 如果问题已解决，给出清晰的答案
3. 如果生成了工单，告知用户已转接人工客服，并给出工单编号
4. 回复末尾询问是否还有其他问题
5. 控制在 200 字以内"""


def summary_node(state):
    user_msg = state["user_message"]
    intent = state.get("intent", "general")
    retrieved = state.get("retrieved_docs", [])
    tool_results = state.get("tool_results", [])
    ticket = state.get("escalation_ticket")

    context_parts = [f"用户问题: {user_msg}", f"意图分类: {intent}"]

    if retrieved:
        context_parts.append("\n知识库检索结果:\n" + "\n".join([f"- {d[:100]}..." for d in retrieved]))

    if tool_results:
        tool_lines = []
        for tr in tool_results:
            tool_lines.append(f"- 调用 {tr['name']}: {tr['result'][:200]}")
        context_parts.append("\n工具调用结果:\n" + "\n".join(tool_lines))

    if ticket:
        context_parts.append(f"\n升级工单已生成: {ticket.get('ticket_summary', '')}")

    context = "\n".join(context_parts)

    msg = call_llm(
        messages=[
            {"role": "system", "content": SUMMARY_SYSTEM_PROMPT},
            {"role": "user", "content": f"请根据以下上下文生成回复：\n\n{context}"},
        ],
        temperature=0.3,
    )

    final = msg["content"]

    thought = {
        "agent": "summary",
        "status": "completed",
        "input": f"整合 {len(retrieved)} 条知识库文档 + {len(tool_results)} 个工具结果" + (" + 1 个工单" if ticket else ""),
        "output": final,
        "detail": "已整合所有 Agent 输出生成最终回复",
    }

    existing_thoughts = state.get("thought_chain", [])
    return {
        "final_response": final,
        "thought_chain": existing_thoughts + [thought],
    }

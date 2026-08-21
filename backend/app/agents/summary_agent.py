from app.agents.llm_client import call_llm
from app.util.message_utils import to_llm_messages

SUMMARY_SYSTEM_PROMPT = """你是一个电商智能客服的回复汇总助手。根据用户的问题和所有 Agent 的处理结果，生成最终回复。

规则：
1. 回复要友好、专业，带称呼
2. 如果根据对话上下文，可以解决用户问题，给出清晰的答案，如果没有解决，提醒用户信息是否填写完整
3. 如果生成了工单，告知用户已转接人工客服，并给出工单编号
4. 回复末尾询问是否还有其他问题
5. 回答用户问题可以参考历史对话摘要
6. 控制在 200 字以内"""

SUMMARY_HISTORY_PROMPT = """你是一个电商智能客服的历史对话摘要汇总助手。根据之前的摘要，以及当前几轮的对话，生成新的摘要。

规则：
1、需要保留历史摘要中和当前几轮对话的关键信息，比如，用户身份，用户咨询了哪些问题
2、其他你觉得需要保留的重要信息
3、尽可能的简洁
"""


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

    summary = state.get("summary_message", "")
    full_history = state.get("messages", [])

    llm_messages = [
        {"role": "system", "content": SUMMARY_SYSTEM_PROMPT}
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

    final = msg["content"]

    thought = {
        "agent": "summary",
        "status": "completed",
        "input": f"整合 {len(retrieved)} 条知识库文档 + {len(tool_results)} 个工具结果" + (" + 1 个工单" if ticket else ""),
        "output": final,
        "detail": "已整合所有 Agent 输出生成最终回复",
    }

    existing_thoughts = state.get("thought_chain", [])

    old_summary = state.get("summary_message", "")

    if len(full_history) % 12 == 0:
        old_summary = _generate_incremental_summary(full_history, old_summary)

    return {
        "messages": [msg],
        "summary_message": old_summary,
        "final_response": final,
        "thought_chain": existing_thoughts + [thought],
    }


def _generate_incremental_summary(full_history: list, old_summary: str) -> str:
    """
    增量更新摘要：只取旧摘要 + 最新的几轮对话消息，生成新摘要
    """
    # 1. 取出最近新增的对话
    new_messages = full_history[-12:]

    # 2. 格式化为文本
    new_text = "\n".join([f"{msg.type}: {msg.content}" for msg in new_messages])

    # 3. 构造提示词（只带旧摘要 + 新增消息）
    if old_summary:
        prompt = f"""已有摘要：{old_summary}，\n 最新对话：{new_text}"""
    else:
        prompt = f"""最近几轮对话：{new_text}"""

    # 4. 调用 LLM（此时输入的 token 极短）
    response = call_llm([
        {"role": "system", "content": SUMMARY_HISTORY_PROMPT},
        {"role": "user", "content": prompt}
    ], temperature=0.1)
    return response["content"].strip()

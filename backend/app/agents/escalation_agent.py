import json
from datetime import datetime
from app.agents.llm_client import call_llm
from app.util.message_utils import to_llm_messages

ESCALATION_PROMPT = """你是一个电商客服升级处理专员。用户的问题需要转接人工客服处理。
请分析用户的投诉或复杂问题，生成一个结构化的工单信息。

输出格式（JSON）：
{
    "ticket_summary": "问题简述（20字以内）",
    "issue_category": "问题类别",
    "detail": "问题详细描述",
    "urgency": "high/medium/low",
    "suggested_action": "建议处理方法"
}"""


def escalation_node(state):
    user_msg = state["user_message"]

    summary = state.get("summary_message", [])
    full_history = state.get("messages", [])

    llm_messages = [
        {"role": "system", "content": ESCALATION_PROMPT}
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
        temperature=0.2,
        response_format={"type": "json_object"},
    )

    content = msg["content"]
    parsed = json.loads(content)

    ticket = {
        "ticket_id": f"TK-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "timestamp": datetime.now().isoformat(),
        **parsed,
    }

    thought = {
        "messages": [msg],
        "agent": "escalation",
        "status": "completed",
        "input": user_msg,
        "output": f"已生成工单 {ticket['ticket_id']}",
        "detail": f"问题类别: {ticket.get('issue_category', 'N/A')}\n紧急程度: {ticket.get('urgency', 'N/A')}\n已转接人工客服处理",
    }

    existing_thoughts = state.get("thought_chain", [])
    return {
        "escalation_ticket": ticket,
        "thought_chain": existing_thoughts + [thought],
    }

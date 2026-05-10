import json
from datetime import datetime
from app.agents.llm_client import call_llm

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

    msg = call_llm(
        messages=[
            {"role": "system", "content": ESCALATION_PROMPT},
            {"role": "user", "content": user_msg},
        ],
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

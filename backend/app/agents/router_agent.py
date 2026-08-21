import json
from app.agents.llm_client import call_llm
from app.util.message_utils import to_llm_messages

ROUTER_SYSTEM_PROMPT = """你是一个电商智能客服的意图分类器。根据用户的消息，判断其属于以下哪一类：

- order_query: 用户查询订单状态、物流、配送时间等
- product_inquiry: 用户询问产品信息、功能介绍、价格等
- complaint: 用户投诉、表达不满、要求售后等
- general: 其他一般性问题（问候、闲聊等）

只返回 JSON 格式：{"intent": "<分类>", "reason": "<简短理由>"}
"""


def router_node(state):
    user_msg = state["user_message"]

    summary = state.get("summary_message", "")
    full_history = state.get("messages", [])

    llm_messages = [
        {"role": "system", "content": ROUTER_SYSTEM_PROMPT}
    ]

    if summary:
        llm_messages.append({
            "role": "system",
            "content": f"可参考对话历史摘要回答用户问题，【对话历史摘要】{summary}\n"
        })

    recent_messages = full_history[-12:] if len(full_history) > 12 else full_history
    llm_messages += to_llm_messages(recent_messages)

    existing_thoughts = state.get("thought_chain", [])

    msg = call_llm(
        messages=llm_messages,
        temperature=0.1,
        response_format={"type": "json_object"},
    )

    content = msg["content"]
    parsed = json.loads(content)
    intent = parsed.get("intent", "general")

    thought = {
        "agent": "router",
        "status": "completed",
        "input": user_msg,
        "output": intent,
        "detail": parsed.get("reason", ""),
    }

    return {
        "messages": [msg],
        "intent": intent,
        "thought_chain": existing_thoughts + [thought],
    }


def route_decision(state):
    intent = state.get("intent", "general")
    routing = {
        "product_inquiry": "knowledge",
        "order_query": "tool",
        "complaint": "escalation",
        "general": "knowledge",
    }
    return routing.get(intent, "knowledge")

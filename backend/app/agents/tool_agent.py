import json
from app.agents.llm_client import call_llm
from app.data.config import get_data_provider
from dataclasses import asdict
from app.util.message_utils import to_llm_messages

TOOL_SYSTEM_PROMPT = """你是电商客服系统的工具调用助手。根据用户的问题，选择合适的工具来获取信息。"""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "query_order",
            "description": "查询订单状态",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {"type": "string", "description": "订单编号"}
                },
                "required": ["order_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "track_shipment",
            "description": "查询物流信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {"type": "string", "description": "订单编号"}
                },
                "required": ["order_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_return_policy",
            "description": "查询退换货政策",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "商品类别（electronics/clothing/books）",
                    }
                },
                "required": ["category"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_product_info",
            "description": "获取产品详细信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_id": {"type": "string", "description": "产品编号"}
                },
                "required": ["product_id"],
            },
        },
    },
]


def _execute_tool(name: str, args: dict) -> str:
    """通过 Data Provider 执行工具调用"""
    provider = get_data_provider()

    if name == "query_order":
        order = provider.get_order(args.get("order_id", ""))
        if order:
            return json.dumps({"found": True, "order": asdict(order)}, ensure_ascii=False)
        return json.dumps({"found": False, "message": f"未找到订单 {args.get('order_id', '')}"})

    if name == "track_shipment":
        ship = provider.get_shipment(args.get("order_id", ""))
        if ship:
            return json.dumps({"found": True, "shipment": asdict(ship)}, ensure_ascii=False)
        return json.dumps({"found": False, "message": f"未找到订单 {args.get('order_id', '')} 的物流信息"})

    if name == "check_return_policy":
        cat = args.get("category", "electronics")
        policy = provider.get_return_policy(cat)
        if policy:
            return json.dumps({"category": cat, "policy": policy.policy}, ensure_ascii=False)
        return json.dumps({"category": cat, "policy": "暂未找到该类别的退换货政策"})

    if name == "get_product_info":
        pid = args.get("product_id", "")
        product = provider.get_product(pid)
        if product:
            return json.dumps({"found": True, "product": asdict(product)}, ensure_ascii=False)
        return json.dumps({"found": False, "message": f"未找到产品 {pid}"})

    return json.dumps({"error": f"未知工具: {name}"})


def tool_node(state):
    user_msg = state["user_message"]

    summary = state.get("summary_message", "")
    full_history = state.get("messages", [])

    llm_messages = [
        {"role": "system", "content": TOOL_SYSTEM_PROMPT}
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
        tools=TOOLS,
        tool_choice="auto",
        temperature=0.1,
    )

    tool_calls = msg.get("tool_calls")
    results = []
    thought = {
        "agent": "tool",
        "status": "completed",
        "input": user_msg,
        "output": "",
        "detail": "",
    }

    if tool_calls:
        call_details = []
        for tc in tool_calls:
            name = tc["function"]["name"]
            args = json.loads(tc["function"]["arguments"])
            result = _execute_tool(name, args)
            results.append({"name": name, "args": args, "result": result})
            call_details.append(f"调用 {name}({json.dumps(args, ensure_ascii=False)}) -> {result[:80]}...")

        thought["detail"] = "\n".join(call_details)
        thought["output"] = f"执行了 {len(tool_calls)} 个工具调用"
    else:
        thought["detail"] = "未触发工具调用，由 LLM 直接回复"
        thought["output"] = msg.get("content") or "无需调用工具"

    existing_thoughts = state.get("thought_chain", [])
    return {
        "messages": [msg],
        "tool_results": results,
        "thought_chain": existing_thoughts + [thought],
    }

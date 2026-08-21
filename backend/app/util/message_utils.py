from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage

def to_llm_messages(messages: list[BaseMessage]) -> list[dict[str, str]]:
    """
    将 LangChain 消息列表转换为 call_llm 所需的字典列表
    """
    result = []
    for msg in messages:
        if isinstance(msg, HumanMessage):
            role = "user"
        elif isinstance(msg, AIMessage):
            role = "assistant"
        elif isinstance(msg, SystemMessage):
            role = "system"
        else:
            role = "user"  # fallback
        result.append({"role": role, "content": msg.content})
    return result
from langgraph.graph import MessagesState
from pydantic import BaseModel, Field
from typing import Optional


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    conversation_id: Optional[str] = None
    user_id: int = Field(default=1000, description="用户ID，默认为1000")


class SSEEvent(BaseModel):
    event: str = Field(..., pattern=r"^(thought|tool_call|message|error|done)$")
    data: dict


# 定义全局状态,继承MessagesState#messages 字段
class AgentState(MessagesState):
    user_message: str
    # 历史摘要信息
    summary_message: str
    intent: Optional[str]
    retrieved_docs: list
    tool_results: list
    escalation_ticket: Optional[dict]
    final_response: Optional[str]
    thought_chain: list

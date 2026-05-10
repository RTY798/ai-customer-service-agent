from pydantic import BaseModel, Field
from typing import TypedDict, Optional, Any


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    conversation_id: Optional[str] = None


class SSEEvent(BaseModel):
    event: str = Field(..., pattern=r"^(thought|tool_call|message|error|done)$")
    data: dict


class AgentState(TypedDict):
    user_message: str
    messages: list
    intent: Optional[str]
    retrieved_docs: list
    tool_results: list
    escalation_ticket: Optional[dict]
    final_response: Optional[str]
    thought_chain: list

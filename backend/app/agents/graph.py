from langgraph.graph import StateGraph
from app.models.schemas import AgentState
from app.agents.router_agent import router_node, route_decision
from app.agents.knowledge_agent import knowledge_node
from app.agents.tool_agent import tool_node
from app.agents.escalation_agent import escalation_node
from app.agents.summary_agent import summary_node


def build_graph() -> StateGraph:
    workflow = StateGraph(AgentState)

    workflow.add_node("router", router_node)
    workflow.add_node("knowledge", knowledge_node)
    workflow.add_node("tool", tool_node)
    workflow.add_node("escalation", escalation_node)
    workflow.add_node("summary", summary_node)

    workflow.set_entry_point("router")

    workflow.add_conditional_edges(
        "router",
        route_decision,
        {
            "knowledge": "knowledge",
            "tool": "tool",
            "escalation": "escalation",
        },
    )

    workflow.add_edge("knowledge", "summary")
    workflow.add_edge("tool", "summary")
    workflow.add_edge("escalation", "summary")

    workflow.add_edge("summary", "__end__")

    return workflow.compile()


agent_graph = build_graph()

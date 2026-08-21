import json
import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage

from app.config import settings
from app.models.schemas import ChatRequest
from app.agents.graph import agent_graph
from app.util.memory import thread_id_cache

app = FastAPI(title="电商智能客服系统", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health():
    return {"status": "ok"}


@app.post("/api/chat")
async def chat(req: ChatRequest):
    try:
        initial_state = {
            "user_message": req.message,
            "user_id": req.user_id,
            "messages": [HumanMessage(req.message)],
            "thought_chain": [],
            "retrieved_docs": [],
            "tool_results": [],
        }

        # 1. 根据 userId 获取或生成 thread_id
        thread_id = thread_id_cache.get_or_create(initial_state["user_id"])
        config = {"configurable": {"thread_id": thread_id}}

        result = agent_graph.invoke(initial_state, config=config)

        print("messages====>", result["messages"])

        return {
            "reply": result.get("final_response", ""),
            "intent": result.get("intent", "general"),
            "thought_chain": result.get("thought_chain", []),
            "escalation_ticket": result.get("escalation_ticket"),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理请求失败: {str(e)}")


@app.post("/api/chat/stream")
async def chat_stream(req: ChatRequest):
    try:
        initial_state = {
            "user_message": req.message,
            "messages": [],
            "thought_chain": [],
            "retrieved_docs": [],
            "tool_results": [],
        }

        async def event_stream():
            # 分步执行并提供流式更新
            yield f"data: {json.dumps({'event': 'thought', 'data': {'agent': 'router', 'status': 'running', 'detail': '正在分析您的意图...'}})}\n\n"
            await asyncio.sleep(0.3)

            # 使用普通 invoke，模拟流式效果
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, lambda: agent_graph.invoke(initial_state)
            )

            thought_chain = result.get("thought_chain", [])
            for thought in thought_chain:
                yield f"data: {json.dumps({'event': 'thought', 'data': thought})}\n\n"
                await asyncio.sleep(0.2)

            reply = result.get("final_response", "")
            yield f"data: {json.dumps({'event': 'message', 'data': {'content': reply}})}\n\n"

            ticket = result.get("escalation_ticket")
            if ticket:
                yield f"data: {json.dumps({'event': 'ticket', 'data': ticket})}\n\n"

            yield f"data: {json.dumps({'event': 'done', 'data': {}})}\n\n"

        return StreamingResponse(
            event_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            },
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理请求失败: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
    )

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agent.agent import Agent
import uvicorn


app = FastAPI(
    title="AI Agent API",
    description="基于 DeepSeek 的智能 Agent 服务，支持长期记忆和工具调用",
    version="1.0.0"
)

# CORS 配置：允许前端跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    session_id: str = "default_session"
    model_provider: str = "deepseek"


class ChatResponse(BaseModel):
    reply: str
    session_id: str
    model_provider: str = "deepseek"


@app.get("/")
async def root():
    return {
        "message": "AI Agent 服务运行中 🚀",
        "docs": "/docs",
        "status": "active"
    }


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        agent = Agent(session_id=request.session_id)
        reply = agent.run(request.message, model_provider=request.model_provider)
        return ChatResponse(reply=reply, session_id=request.session_id, model_provider=request.model_provider)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent 处理失败: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

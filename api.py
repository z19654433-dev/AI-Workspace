# api.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agent.agent import Agent
import uvicorn

# 创建 FastAPI 应用实例
app = FastAPI(
    title="AI Agent API",
    description="基于 DeepSeek 的智能 Agent 服务，支持长期记忆和工具调用",
    version="1.0.0"
)


# 定义请求体格式
class ChatRequest(BaseModel):
    message: str
    session_id: str = "default_session"  # 默认会话ID，方便多用户扩展


# 定义响应体格式
class ChatResponse(BaseModel):
    reply: str
    session_id: str


# 根路径健康检查
@app.get("/")
async def root():
    return {
        "message": "AI Agent 服务运行中 🚀",
        "docs": "/docs",
        "status": "active"
    }


# 核心聊天接口
@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    与 AI Agent 对话。
    - **message**: 用户输入的问题
    - **session_id**: 会话标识（可选，默认为 default_session）
    """
    try:
        # 为每个请求创建一个新的 Agent 实例
        # 优点：完全无状态，方便水平扩展；每次从 SQLite 拉取最近 20 条记录
        agent = Agent(session_id=request.session_id)

        # 执行 Agent 逻辑（包含工具判断、LLM调用、自动落库）
        reply = agent.run(request.message)

        return ChatResponse(reply=reply, session_id=request.session_id)
    except Exception as e:
        # 捕获异常并返回 500 错误，避免服务崩溃
        raise HTTPException(status_code=500, detail=f"Agent 处理失败: {str(e)}")


# 如果直接运行此文件，启动 Uvicorn 服务器
if __name__ == "__main__":
    uvicorn.run(
        "api:app",  # 指向当前文件的 app 实例
        host="0.0.0.0",  # 监听所有网卡，方便局域网或容器调用
        port=8000,  # 端口号
        reload=True  # 开发模式：代码变更自动重启
    )
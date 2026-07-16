# 🧠 AI Agent · Python + DeepSeek

> 一个基于 **DeepSeek API** 和 **FastAPI** 的智能 Agent 后端服务，具备长期记忆、多会话隔离、自主工具调用（Function Calling）能力，支持开箱即用的 RESTful API 与 Swagger 文档。

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![DeepSeek](https://img.shields.io/badge/DeepSeek-API-orange.svg)](https://deepseek.com/)

---

## ✨ 功能特性

- 🤖 **Agent 架构**：模块化设计（Agent / Chatbot / Tools / Memory 分层解耦），易于扩展新工具。
- 🧠 **自主决策调用工具**：基于 DeepSeek Function Calling，彻底告别硬编码 `if` 判断，由大模型动态决定是否调用工具、调用哪个工具、提取哪些参数。
- 💬 **长期记忆**：通过 SQLite 保存对话历史，支持多会话（`session_id`），重启服务后上下文依然保留。
- 🌐 **RESTful API 服务**：基于 FastAPI 提供 `/chat` 接口，自动生成 Swagger 交互文档（`/docs`），方便前端、移动端或第三方调用。
- 🐳 **容器化就绪**：项目已配备 `Dockerfile`，可在标准服务器环境下快速构建并一键启动（本地构建受网络限制，不影响功能演示）。
- ⚡ **纯 Python 实现**：无需复杂框架，核心代码清晰易读，适合学习与二次开发。

---

## 🗂️ 项目结构
AI-Agent/
├── api.py # FastAPI 服务入口（V5）
├── app.py # 终端交互入口（V1，已退休）
├── config.py # 环境变量加载
├── requirements.txt # 依赖清单
├── Dockerfile # 容器化配置
├── .dockerignore # 忽略文件
├── agent/ # Agent 核心
│ ├── agent.py # 调度器 + 记忆管理 + 工具调用协调
│ └── tool_schemas.py # 工具定义（Function Calling 的 schema）
├── chatbot/ # LLM 调用封装
│ └── chatbot.py # OpenAI SDK 调用 DeepSeek
├── tools/ # 工具实现
│ ├── registry.py # 工具注册表
│ ├── weather.py # 天气查询（示例）
│ └── calculator.py # 计算器（示例）
└── memory/ # 长期记忆
├── memory.py # SQLite 数据库操作
└── chat_history.db # 自动生成的数据库文件

text

---

## 🛠️ 技术栈

- **Python 3.11+**
- **DeepSeek API**（OpenAI 兼容 SDK）
- **FastAPI** + **Uvicorn**（服务化）
- **SQLite**（持久化存储）
- **Pydantic**（数据验证）

---

## 🚀 快速开始

### 1. 克隆项目
```bash
git clone https://github.com/z19654433-dev/AI-Workspace.git
cd AI-Workspace
2. 创建虚拟环境并安装依赖
bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

pip install -r requirements.txt
3. 配置环境变量
在项目根目录创建 .env 文件，填入你的 DeepSeek API Key：

text
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxx
4. 启动服务
bash
uvicorn api:app --host 0.0.0.0 --port 8000
访问 http://127.0.0.1:8000/docs 即可在 Swagger 中测试 API。

5. 使用示例
bash
curl -X POST "http://127.0.0.1:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "今天河南天气怎么样", "session_id": "test"}'
🧪 API 接口说明
方法	路径	描述
GET	/	健康检查，返回服务状态
POST	/chat	与 Agent 对话，请求体需包含 message 和可选的 session_id
请求体示例：

json
{
  "message": "计算 12345 * 678",
  "session_id": "user_001"
}
成功响应：

json
{
  "reply": "12345 乘以 678 等于 8372310",
  "session_id": "user_001"
}
📈 版本迭代路线
版本	功能	状态
V1	终端交互	✅
V2	DeepSeek API 接入	✅
V3	上下文记忆（内存）	✅
V4	SQLite 长期记忆 + 多会话	✅
V5	FastAPI 服务化 + Swagger	✅
V7	Function Calling 自主决策	✅
V6	LangChain 集成（可选）	⏳ 计划中
🐳 Docker 部署（可选）
项目已提供 Dockerfile，在具备 Docker 环境的服务器上可一键构建并启动：

bash
docker build -t ai-agent .
docker run -p 8000:8000 ai-agent
注意：本地构建可能受网络限制，但配置已完成，可在云服务器上正常使用。

🤝 贡献与反馈
本项目是作者为寻找 Python / Agent 开发实习 而构建的实战项目，欢迎提出 Issue 或 PR。

📄 License
MIT License © 2026

🙏 致谢
DeepSeek 提供强大且高性价比的 API

FastAPI 简化 Web 服务开发

所有在开发过程中提供建议的开发者们
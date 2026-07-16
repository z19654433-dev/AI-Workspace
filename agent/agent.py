# agent/agent.py
import json
from chatbot.chatbot import chat
from tools.registry import tools
from memory.memory import Memory
from agent.tool_schemas import tools_schema


class Agent:

    def __init__(self, session_id: str = "default_session"):
        self.name = "MyAgent"
        self.session_id = session_id

        # 初始化记忆模块
        self.memory = Memory()

        # 加载历史记忆（最近20条）
        history = self.memory.load_history(self.session_id, limit=20)

        # 构建 messages：system + 历史记录
        self.messages = [
            {
                "role": "system",
                "content": "你是一个友好的AI助手，可以查询天气和进行数学计算。"
            }
        ]
        self.messages.extend(history)

    def add_user_message(self, content):
        self.messages.append({"role": "user", "content": content})
        self.memory.save_message(self.session_id, "user", content)

    def add_assistant_message(self, content):
        self.messages.append({"role": "assistant", "content": content})
        self.memory.save_message(self.session_id, "assistant", content)

    def add_tool_messages(self, tool_call_id, tool_name, result):
        """记录工具调用过程（方便调试，也存入记忆）"""
        # 保存工具调用结果到 memory（用特殊格式标记）
        self.memory.save_message(
            self.session_id,
            "assistant",
            f"[工具调用] {tool_name} 返回: {result}"
        )

    def run(self, message):
        # 1. 添加用户消息
        self.add_user_message(message)

        # 2. 第一次调用 LLM（带工具定义）
        response = chat(self.messages, tools=tools_schema, tool_choice="auto")
        choice = response.choices[0]
        finish_reason = choice.finish_reason

        # 3. 判断是否需要调用工具
        if finish_reason == "tool_calls":
            # 提取工具调用信息
            tool_call = choice.message.tool_calls[0]
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)

            # 4. 执行工具
            result = None
            result = tools[tool_name](**tool_args)
            # 5. 将模型的工具调用请求加入消息历史
            self.messages.append(choice.message.model_dump())

            # 6. 将工具执行结果加入消息历史
            self.messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(result)
            })

            # 7. 记录工具执行到 memory（便于追踪）
            self.add_tool_messages(tool_call.id, tool_name, str(result))

            # 8. 第二次调用 LLM（不带工具，生成最终回复）
            final_response = chat(self.messages, tools=None)
            final_answer = final_response.choices[0].message.content

            # 9. 保存最终回答到记忆
            self.add_assistant_message(final_answer)

            return final_answer

        # 如果没有工具调用，直接返回普通回答
        else:
            answer = choice.message.content
            self.add_assistant_message(answer)
            return answer

    def clear_memory(self):
        """清空当前会话的记忆"""
        self.memory.clear_session(self.session_id)
        self.messages = [{"role": "system", "content": "你是一个友好的AI助手，可以查询天气和进行数学计算。"}]
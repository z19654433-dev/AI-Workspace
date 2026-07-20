import json
from tools import registry
from memory.memory import Memory
from chatbot.chatbot import chat
from utils.logger import get_logger

logger = get_logger(__name__)

MAX_TOOL_ROUNDS = 5   # 最多 5 轮工具调用，防止死循环


class Agent:

    def __init__(self, session_id: str = "default_session"):
        self.name = "MyAgent"
        self.session_id = session_id
        self.memory = Memory()
        history = self.memory.load_history(self.session_id, limit=20)
        system_prompt = (
            "你是一个友好的AI助手。你可以做以下事情：\n"
            "1. 查询天气：告诉用户输入城市名即可查天气\n"
            "2. 数学计算：进行精确的数学运算\n"
            "3. 今日热榜：查看GitHub趋势项目或百度热搜（默认GitHub）\n"
            "4. 知识库检索：从你的私有知识库中搜索专业内容来回答问题\n"
            "你需要根据用户的问题自主决定调用哪个工具：\n"
            "  - 问天气 → weather\n"
            "  - 算数学 → calculator\n"
            "  - 问热榜 → get_hotlist\n"
            "  - 问知识库里的内容 → knowledge_search\n"
            "  - 普通聊天 → 直接回答\n"
            "回答简洁友好，每次只回答用户的当前问题，不要提前列出一堆功能。"
        )
        self.messages = [
            {
                "role": "system",
                "content": system_prompt,
            }
        ]
        self.messages.extend(history)
        logger.info("Agent 初始化完成, session=%s", session_id)

    # ── 消息管理 ──

    def add_user_message(self, content):
        self.messages.append({"role": "user", "content": content})
        self.memory.save_message(self.session_id, "user", content)

    def add_assistant_message(self, content):
        self.messages.append({"role": "assistant", "content": content})
        self.memory.save_message(self.session_id, "assistant", content)

    def add_tool_messages(self, tool_name, result):
        """持久化工具调用结果（截断过长内容）"""
        truncated = str(result)[:500] + ("..." if len(str(result)) > 500 else "")
        self.memory.save_message(
            self.session_id,
            "tool",
            f"[{tool_name}] {truncated}",
        )

    # ── 核心执行 ──

    def _execute_tool(self, tool_call) -> str:
        """安全执行单个工具，异常时返回错误信息"""
        tool_name = tool_call.function.name
        try:
            tool_args = json.loads(tool_call.function.arguments)
        except json.JSONDecodeError:
            logger.warning("工具参数解析失败: %s", tool_call.function.arguments)
            return f"工具参数解析失败"

        logger.info("执行工具: %s, 参数=%s", tool_name, tool_args)

        tool_func = registry.tools.get(tool_name)
        if tool_func is None:
            logger.warning("未知工具: %s", tool_name)
            return f"工具 {tool_name} 不存在"

        try:
            result = tool_func(**tool_args)
            logger.info("工具 %s 返回成功", tool_name)
            return str(result)
        except Exception as e:
            logger.error("工具 %s 执行失败: %s", tool_name, e)
            return f"工具执行失败: {str(e)}"

    def run(self, message, model_provider: str = "deepseek"):
        self.add_user_message(message)
        logger.info("用户输入: %s", message)

        # ── 多轮 tool calling 循环 ──
        for round_num in range(MAX_TOOL_ROUNDS):
            response = chat(
                self.messages,
                tools=registry.schemas,
                tool_choice="auto",
                provider=model_provider,
            )
            choice = response.choices[0]
            finish_reason = choice.finish_reason

            if finish_reason != "tool_calls":
                # 没有工具调用 → 直接返回
                answer = choice.message.content
                self.add_assistant_message(answer)
                logger.info("回答（第%d轮）: %s", round_num + 1, answer[:100])
                return answer

            # ── 执行工具调用 ──
            tool_calls = choice.message.tool_calls
            logger.info(
                "第%d轮工具调用, 数量=%d, 工具=%s",
                round_num + 1,
                len(tool_calls),
                [tc.function.name for tc in tool_calls],
            )

            # 把 Assistant 消息（含 tool_calls）加入 messages
            self.messages.append(choice.message.model_dump())

            # 逐个执行
            for tool_call in tool_calls:
                result = self._execute_tool(tool_call)
                self.messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result,
                })
                self.add_tool_messages(tool_call.function.name, result)

            # 继续下一轮，让 DeepSeek 决定是否还需要更多工具

        # 超过最大轮数，用当前上下文强制生成答案
        logger.warning("达到最大工具调用轮数 %d，强制生成答案", MAX_TOOL_ROUNDS)
        final_response = chat(
            self.messages,
            tools=registry.schemas,
            tool_choice="none",
            provider=model_provider,
        )
        final_answer = final_response.choices[0].message.content
        self.add_assistant_message(final_answer)
        return final_answer

    def clear_memory(self):
        self.memory.clear_session(self.session_id)
        system_prompt = (
            "你是一个友好的AI助手。你可以做以下事情：\n"
            "1. 查询天气：告诉用户输入城市名即可查天气\n"
            "2. 数学计算：进行精确的数学运算\n"
            "3. 今日热榜：查看GitHub趋势项目或百度热搜（默认GitHub）\n"
            "4. 知识库检索：从你的私有知识库中搜索专业内容来回答问题\n"
            "你需要根据用户的问题自主决定调用哪个工具：\n"
            "  - 问天气 → weather\n"
            "  - 算数学 → calculator\n"
            "  - 问热榜 → get_hotlist\n"
            "  - 问知识库里的内容 → knowledge_search\n"
            "  - 普通聊天 → 直接回答\n"
            "回答简洁友好，每次只回答用户的当前问题，不要提前列出一堆功能。"
        )
        self.messages = [{"role": "system", "content": system_prompt}]
        logger.info("记忆已清除, session=%s", self.session_id)

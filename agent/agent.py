import json
from tools import registry
from memory.memory import Memory
from memory.vector_memory import get_vector_memory
from chatbot.chatbot import chat
from utils.logger import get_logger

logger = get_logger(__name__)

MAX_TOOL_ROUNDS = 5
# 最近对话保留条数（向量检索补丁之外，保留最基本的最近上下文）
RECENT_HISTORY_LIMIT = 5
# 向量检索返回的相关历史条数
VECTOR_MEMORY_K = 3


class Agent:

    def __init__(self, session_id: str = "default_session"):
        self.name = "MyAgent"
        self.session_id = session_id
        self.memory = Memory()
        self.vector_memory = get_vector_memory()

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

        # ── 加载历史：最近 N 条 + 向量检索相关历史 ──
        recent = self.memory.load_history(session_id, limit=RECENT_HISTORY_LIMIT)
        self.messages.extend(recent)
        logger.info("已加载最近 %d 条历史", len(recent))

        logger.info("Agent 初始化完成, session=%s", session_id)

    # ── 消息管理 ──

    def add_user_message(self, content):
        self.messages.append({"role": "user", "content": content})
        self.memory.save_message(self.session_id, "user", content)

    def add_assistant_message(self, content):
        self.messages.append({"role": "assistant", "content": content})
        self.memory.save_message(self.session_id, "assistant", content)

    def add_tool_messages(self, tool_name, result):
        truncated = str(result)[:500] + ("..." if len(str(result)) > 500 else "")
        self.memory.save_message(
            self.session_id,
            "assistant",
            f"[{tool_name}] {truncated}",
        )

    # ── 核心执行 ──

    def _execute_tool(self, tool_call) -> str:
        tool_name = tool_call.function.name
        try:
            tool_args = json.loads(tool_call.function.arguments)
        except json.JSONDecodeError:
            logger.warning("工具参数解析失败: %s", tool_call.function.arguments)
            return "工具参数解析失败"

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
                answer = choice.message.content
                self.add_assistant_message(answer)
                logger.info("回答（第%d轮）: %s", round_num + 1, answer[:100])

                # ── 将本轮回合存入向量记忆 ──
                try:
                    self.vector_memory.add_turn(self.session_id, message, answer)
                except Exception as e:
                    logger.warning("向量记忆写入失败: %s", e)

                return answer

            # ── 执行工具调用 ──
            tool_calls = choice.message.tool_calls
            logger.info(
                "第%d轮工具调用, 数量=%d, 工具=%s",
                round_num + 1,
                len(tool_calls),
                [tc.function.name for tc in tool_calls],
            )
            self.messages.append(choice.message.model_dump())

            for tool_call in tool_calls:
                result = self._execute_tool(tool_call)
                self.messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result,
                })
                self.add_tool_messages(tool_call.function.name, result)

        # 超过最大轮数
        logger.warning("达到最大工具调用轮数 %d", MAX_TOOL_ROUNDS)
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
        self.vector_memory.clear_session(self.session_id)
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

from chatbot.chatbot import chat
from tools.registry import tools


class Agent:

    def __init__(self):
        self.name = "MyAgent"

        self.messages = [
            {
                "role": "system",
                "content": "你是一个友好的AI助手"
            }
        ]

    def add_user_message(self, content):
        self.messages.append(
            {
                "role": "user",
                "content": content
            }
        )

    def add_assistant_message(self, content):
        self.messages.append(
            {
                "role": "assistant",
                "content": content
            }
        )

    def run(self, message):

        # 天气工具
        if "天气" in message:

            self.add_user_message(message)

            if "河南" in message:
                answer = tools["weather"]("河南")
            elif "北京" in message:
                answer = tools["weather"]("北京")
            elif "上海" in message:
                answer = tools["weather"]("上海")
            else:
                answer = "暂不支持查询该城市天气"

            self.add_assistant_message(answer)

            return answer

        # 计算工具
        if "计算" in message:

            self.add_user_message(message)

            expression = message.replace("计算", "").strip()

            answer = tools["calculator"](expression)

            self.add_assistant_message(answer)

            return answer

        # 普通聊天
        self.add_user_message(message)

        answer = chat(self.messages)

        self.add_assistant_message(answer)

        return answer
class ChatBot:
    """一个简单的聊天机器人"""

    def __init__(self):
        self.name = "AI Workspace"

    def reply(self, message: str) -> str:
        """根据用户输入返回回复"""

        if message == "你好":
            return "你好，很高兴认识你！"

        if message == "你是谁":
            return "我是 AI Workspace，一个正在成长的 AI 助手。"

        return "这个问题我还不会回答，以后我会越来越聪明！"
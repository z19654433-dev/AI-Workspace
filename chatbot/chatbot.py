from openai import OpenAI
from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL
client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url=DEEPSEEK_BASE_URL
)


def chat(messages, tools=None, tool_choice="auto"):
    kwargs = {
        "model": "deepseek-chat",
        "messages": messages
    }
    if tools:
        kwargs["tools"] = tools
        kwargs["tool_choice"] = tool_choice

    response = client.chat.completions.create(**kwargs)
    return response
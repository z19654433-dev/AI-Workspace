from openai import OpenAI

from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL


client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url=DEEPSEEK_BASE_URL
)





def chat(messages):


    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages
    )

    answer = response.choices[0].message.content


    return answer
"""全局配置：环境变量加载 + LLM 提供商配置"""

import os
from dotenv import load_dotenv

load_dotenv()


# ========== LLM 提供商配置 ==========
# 可选值: deepseek | openai_compatible
# deepseek: 使用 DeepSeek 官方 API（默认，免费有额度）
# openai_compatible: 兼容 OpenAI SDK 的第三方模型（智谱/千问/零一等）
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "deepseek")

# DeepSeek 配置
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-chat"

# 通用 OpenAI 兼容配置（LLM_PROVIDER=openai_compatible 时生效）
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "")
OPENAI_MODEL_NAME = os.getenv("OPENAI_MODEL_NAME", "")

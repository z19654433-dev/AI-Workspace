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
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

# 通用 OpenAI 兼容配置（保留向后兼容，LLM_PROVIDER=openai_compatible 时可用）
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "")
OPENAI_MODEL_NAME = os.getenv("OPENAI_MODEL_NAME", "")

# ========== 第三方模型独立配置（前端切换器用，各厂商各自的 key）==========
# 智谱 GLM
GLM_API_KEY = os.getenv("GLM_API_KEY", "")
GLM_BASE_URL = os.getenv("GLM_BASE_URL", "https://open.bigmodel.cn/api/paas/v4/")
GLM_MODEL = os.getenv("GLM_MODEL", "glm-4-flash")

# 通义千问
QWEN_API_KEY = os.getenv("QWEN_API_KEY", "")
QWEN_BASE_URL = os.getenv("QWEN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
QWEN_MODEL = os.getenv("QWEN_MODEL", "qwen-turbo")

# 零一万物 Yi
YI_API_KEY = os.getenv("YI_API_KEY", "")
YI_BASE_URL = os.getenv("YI_BASE_URL", "https://api.lingyiwanwu.com/v1")
YI_MODEL = os.getenv("YI_MODEL", "yi-lightning")

"""LLM 适配器：支持多模型切换"""

from openai import OpenAI
from abc import ABC, abstractmethod
from config import (
    LLM_PROVIDER,
    DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL,
    OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL_NAME,
)
from utils.logger import get_logger

logger = get_logger(__name__)


class BaseLLM(ABC):
    """LLM 基类：定义统一的 chat 接口"""

    @abstractmethod
    def chat(self, messages, tools=None, tool_choice="auto"):
        ...


class DeepSeekAdapter(BaseLLM):
    """DeepSeek 官方 API 适配器"""

    def __init__(self):
        self.client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)
        self.model = DEEPSEEK_MODEL
        logger.info("LLM: DeepSeek (%s)", self.model)

    def chat(self, messages, tools=None, tool_choice="auto"):
        kwargs = {"model": self.model, "messages": messages}
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = tool_choice
        return self.client.chat.completions.create(**kwargs)


class OpenAICompatibleAdapter(BaseLLM):
    """通用 OpenAI 兼容适配器（智谱 GLM / 通义千问 / 零一万物 等）"""

    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)
        self.model = OPENAI_MODEL_NAME
        logger.info("LLM: OpenAI Compatible (%s)", self.model)

    def chat(self, messages, tools=None, tool_choice="auto"):
        kwargs = {"model": self.model, "messages": messages}
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = tool_choice
        return self.client.chat.completions.create(**kwargs)


def create_llm() -> BaseLLM:
    """工厂方法：根据配置创建对应的 LLM 适配器"""
    provider = LLM_PROVIDER.lower().strip()

    if provider == "deepseek":
        if not DEEPSEEK_API_KEY:
            logger.error("DEEPSEEK_API_KEY 未配置")
            raise ValueError("请在 .env 中配置 DEEPSEEK_API_KEY")
        return DeepSeekAdapter()

    elif provider == "openai_compatible":
        if not OPENAI_API_KEY or not OPENAI_BASE_URL or not OPENAI_MODEL_NAME:
            logger.error("OPENAI_API_KEY / BASE_URL / MODEL_NAME 未配置完整")
            raise ValueError(
                "使用 openai_compatible 需要在 .env 中配置:\n"
                "  OPENAI_API_KEY=你的API Key\n"
                "  OPENAI_BASE_URL=https://xxx.com/v1\n"
                "  OPENAI_MODEL_NAME=模型名"
            )
        return OpenAICompatibleAdapter()

    else:
        raise ValueError(f"不支持的 LLM_PROVIDER: {provider}，可选: deepseek | openai_compatible")


# 全局 LLM 实例（模块加载时初始化一次）
_llm = None


def chat(messages, tools=None, tool_choice="auto"):
    """对外接口：保持与旧代码兼容的函数签名"""
    global _llm
    if _llm is None:
        _llm = create_llm()
    return _llm.chat(messages, tools, tool_choice)

"""RAG 流程编排 —— LangChain 全链路

index_documents()  加载 → 切片 → 向量化 → 存储
query()            检索 → 格式化 → 返回上下文
"""

from typing import List

from .config import config
from .loader import load_directory
from .chunker import Chunker
from .vector_store import get_vector_store, VectorStore
from .retriever import get_retriever, Retriever
from utils.logger import get_logger

logger = get_logger(__name__)


def index_documents(doc_dir: str | None = None) -> int:
    """索引文档：加载 → 切片 → 向量化 → 存储

    Args:
        doc_dir: 文档目录，默认使用配置中的 DOCS_DIR

    Returns:
        入库的切片数量
    """
    doc_dir = doc_dir or config.DOCS_DIR
    logger.info("开始索引文档: %s", doc_dir)

    # 1. 加载
    docs = load_directory(doc_dir)
    if not docs:
        logger.warning("未找到文档")
        return 0

    # 2. 切片
    chunker = Chunker()
    chunks = chunker.split_documents(docs)

    # 3. 向量化 + 存储
    store = get_vector_store()
    store.add_documents(chunks)

    logger.info("索引完成: %d 个切片入库", len(chunks))
    return len(chunks)


def query(question: str) -> str:
    """RAG 查询：检索 → 格式化

    Args:
        question: 用户问题

    Returns:
        检索到的相关内容文本（供 LLM 生成最终回答）
    """
    # 首次使用自动索引
    store = get_vector_store()
    if store.count() == 0:
        logger.info("知识库为空，自动索引")
        n = index_documents()
        if n == 0:
            return "知识库中暂无内容，请先往 knowledge/docs/ 目录添加文档"

    # 检索
    retriever = get_retriever()
    results = retriever.search(question)

    if not results:
        return "知识库中没有找到相关内容"

    return retriever.format_context(results)

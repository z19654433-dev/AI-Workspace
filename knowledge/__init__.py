"""知识库模块：基于 ChromaDB 的 RAG 检索"""
from .vector_store import KnowledgeBase
from tools import registry
from utils.logger import get_logger

logger = get_logger(__name__)

# 全局知识库实例
kb = KnowledgeBase()


@registry.register(description="从个人知识库中检索信息来回答问题，当用户询问知识库中的内容时调用")
def query_knowledge(question: str) -> str:
    """在知识库中搜索与问题相关的内容。

    Args:
        question: 用户的问题或查询关键词
    """
    logger.info("知识库查询: %s", question)

    # 首次使用时自动导入知识库文档
    stats = kb.get_stats()
    if stats["count"] == 0:
        from pathlib import Path
        docs_dir = str(Path(__file__).parent / "docs")
        n = kb.index_documents(docs_dir)
        if n == 0:
            return "知识库中暂无内容，请先往 knowledge/docs/ 目录添加资料"

    results = kb.search(question, k=3)
    if not results:
        return "知识库中没有找到相关内容"

    lines = ["从知识库中找到以下相关内容：\n"]
    for i, r in enumerate(results, 1):
        lines.append(f"--- 片段 {i}（来自 {r['source']}）---")
        lines.append(r["content"][:300])
        lines.append("")

    return "\n".join(lines)

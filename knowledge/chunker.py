"""文本切片 —— 基于 LangChain Text Splitter"""

from typing import List

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from .config import config
from utils.logger import get_logger

logger = get_logger(__name__)


class Chunker:
    """切片器，封装 LangChain 的 RecursiveCharacterTextSplitter"""

    def __init__(self, chunk_size: int | None = None, chunk_overlap: int | None = None):
        self.chunk_size = chunk_size or config.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or config.CHUNK_OVERLAP

        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n## ", "\n### ", "\n#### ", "\n", ".", "。", "!", "！", "?", "？", " "],
            length_function=len,
        )

    def split_documents(self, documents: List[Document]) -> List[Document]:
        """对 Document 列表执行切片"""
        chunks = self._splitter.split_documents(documents)
        logger.info("切片完成: %d → %d 个片段", len(documents), len(chunks))
        return chunks

    def split_text(self, text: str) -> List[str]:
        """对纯文本执行切片"""
        return self._splitter.split_text(text)


def get_chunker() -> Chunker:
    return Chunker()

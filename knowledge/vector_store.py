"""向量存储：基于 ChromaDB 的知识库检索"""
import os
import chromadb
from pathlib import Path
from .loader import load_documents, chunk_text
from utils.logger import get_logger

logger = get_logger(__name__)

# ChromaDB 持久化目录
_CHROMA_DIR = Path(__file__).parent / "chroma_db"


class KnowledgeBase:
    """知识库：管理文档的向量化存储和检索"""

    def __init__(self, collection_name: str = "my_knowledge"):
        self.collection_name = collection_name
        self._client = None
        self._collection = None
        self._initialized = False

    def _ensure_init(self):
        """延迟初始化 ChromaDB"""
        if self._initialized:
            return

        _CHROMA_DIR.mkdir(parents=True, exist_ok=True)
        self._client = chromadb.PersistentClient(path=str(_CHROMA_DIR))
        # 使用默认的 all-MiniLM-L6-v2 嵌入模型
        try:
            self._collection = self._client.get_or_create_collection(
                name=self.collection_name
            )
            self._initialized = True
            logger.info("知识库初始化完成，当前文档数: %d", self._collection.count())
        except Exception as e:
            logger.error("知识库初始化失败: %s", e)

    def index_documents(self, doc_dir: str | None = None) -> int:
        """将目录下的文档导入向量库"""
        self._ensure_init()
        if not self._initialized:
            return 0

        if doc_dir is None:
            doc_dir = str(Path(__file__).parent / "docs")

        docs = load_documents(doc_dir)
        if not docs:
            logger.info("没有找到可导入的文档: %s", doc_dir)
            return 0

        all_chunks = []
        all_ids = []
        all_metadatas = []
        counter = 0

        for doc in docs:
            chunks = chunk_text(doc["text"])
            for chunk in chunks:
                chunk_id = f"{doc['id']}_{counter}"
                all_chunks.append(chunk)
                all_ids.append(chunk_id)
                all_metadatas.append({"source": doc["source"]})
                counter += 1

        # 分批添加，避免一次太多数据
        batch_size = 100
        for i in range(0, len(all_chunks), batch_size):
            end = i + batch_size
            try:
                self._collection.add(
                    documents=all_chunks[i:end],
                    ids=all_ids[i:end],
                    metadatas=all_metadatas[i:end],
                )
            except Exception as e:
                logger.error("添加向量失败: %s", e)

        logger.info("成功导入 %d 个文档片段到知识库", len(all_chunks))
        return len(all_chunks)

    def search(self, query: str, k: int = 3) -> list[dict]:
        """搜索与 query 最相关的 k 个文档片段"""
        self._ensure_init()
        if not self._initialized:
            return []

        try:
            results = self._collection.query(
                query_texts=[query],
                n_results=k,
            )
        except Exception as e:
            logger.error("搜索知识库失败: %s", e)
            return []

        items = []
        if results["documents"] and results["documents"][0]:
            for i, doc in enumerate(results["documents"][0]):
                metadata = results["metadatas"][0][i] if results["metadatas"] else {}
                items.append({
                    "content": doc,
                    "source": metadata.get("source", "未知"),
                    "distance": results["distances"][0][i] if results.get("distances") else 0,
                })

        return items

    def get_stats(self) -> dict:
        """获取知识库统计信息"""
        self._ensure_init()
        if not self._initialized:
            return {"count": 0, "status": "未初始化"}
        try:
            count = self._collection.count()
            return {"count": count, "status": "就绪"}
        except Exception:
            return {"count": 0, "status": "错误"}

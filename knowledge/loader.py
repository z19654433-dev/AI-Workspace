"""文档加载器：读取 TXT/MD 文件并按段落切片"""
import os
from pathlib import Path

# 支持的文件格式
_SUPPORTED_EXT = {".txt", ".md", ".py", ".json", ".yaml", ".yml", ".toml", ".cfg", ".ini", ".csv"}


def load_documents(doc_dir: str) -> list[dict[str, str]]:
    """加载 doc_dir 下所有支持的文件，返回 [{id, text, source}]"""
    docs = []
    path = Path(doc_dir)
    if not path.exists():
        return docs

    for file_path in path.rglob("*"):
        if file_path.suffix.lower() not in _SUPPORTED_EXT:
            continue
        if file_path.name.startswith("."):
            continue

        try:
            text = file_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        if not text.strip():
            continue

        doc_id = str(file_path.relative_to(doc_dir.parent if doc_dir.endswith("knowledge") else doc_dir))
        docs.append({
            "id": doc_id,
            "text": text,
            "source": str(file_path),
        })

    return docs


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """将长文本切成片段"""
    paragraphs = text.split("\n\n")
    chunks = []
    current = ""

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        if len(current) + len(para) < chunk_size:
            current = (current + "\n\n" + para).strip()
        else:
            if current:
                chunks.append(current)
            # 如果单段就超过 chunk_size，按句号切
            if len(para) > chunk_size:
                sentences = para.replace("。", "。\n").replace("！", "！\n").replace("？", "？\n").split("\n")
                for sent in sentences:
                    sent = sent.strip()
                    if not sent:
                        continue
                    if len(current) + len(sent) < chunk_size:
                        current = (current + sent).strip()
                    else:
                        if current:
                            chunks.append(current)
                        current = sent
            else:
                current = para

    if current:
        chunks.append(current)

    return chunks

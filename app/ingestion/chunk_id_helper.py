"""Chunk ID 辅助。

【职责】
    生成 PG / Neo4j 对齐使用的 chunk_id。
"""

from app.ingestion import ingestion_constants as ic


def build_chunk_id(document_id: str, index: int) -> str:
    """构造 chunk_id。

    参数:
        document_id: 文档 id。
        index: chunk 序号。

    返回:
        str: 形如 document_id:index。
    """
    return f"{document_id}{ic.CHUNK_ID_SEPARATOR}{index}"

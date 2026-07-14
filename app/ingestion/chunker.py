"""Ingestion 文本切分器。

【职责】
    将 IngestionDocument 切为多个 IngestionChunk。

【当前策略】
    固定字符窗口 + overlap。简单可测，后续可替换为按章节/段落/句子切分。
"""

from app.ingestion.chunk_id_helper import build_chunk_id
from app.ingestion.ingestion_models import IngestionChunk, IngestionDocument
from app.ingestion.text_window_helper import iter_text_windows


def chunk_document(
    document: IngestionDocument,
    chunk_size: int,
    chunk_overlap: int,
) -> list[IngestionChunk]:
    """切分文档。

    参数:
        document: 待导入文档。
        chunk_size: 每个 chunk 最大字符数。
        chunk_overlap: 相邻 chunk 重叠字符数。

    返回:
        list[IngestionChunk]: 切分结果。
    """
    windows = iter_text_windows(document.text, chunk_size, chunk_overlap)
    return [_build_chunk(document, index, text) for index, text in enumerate(windows)]


def _build_chunk(
    document: IngestionDocument,
    index: int,
    text: str,
) -> IngestionChunk:
    """构造单个 IngestionChunk。"""
    return IngestionChunk(
        chunk_id=build_chunk_id(document.document_id, index),
        document_id=document.document_id,
        project_id=document.project_id,
        index=index,
        text=text,
        source=document.source,
    )

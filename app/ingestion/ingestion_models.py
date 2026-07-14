"""Ingestion Lite 数据模型。

【职责】
    定义导入文档、切分 chunk、导入结果的结构。
"""

from pydantic import BaseModel, Field


class IngestionDocument(BaseModel):
    """待导入文档。

    参数说明:
        document_id: 文档唯一 id。
        project_id: 项目 id，后续检索过滤用。
        source: 来源说明，如文件路径或章节名。
        text: 文档正文。
    """

    document_id: str = Field(description="文档 id")
    project_id: str = Field(default="default", description="项目 id")
    source: str = Field(default="", description="来源")
    text: str = Field(description="正文")


class IngestionChunk(BaseModel):
    """切分后的文本块。

    参数说明:
        chunk_id: chunk 唯一 id，格式 {document_id}:{index}。
        document_id: 所属文档 id。
        project_id: 所属项目 id。
        index: 文档内 chunk 序号。
        text: chunk 文本。
        source: 来源说明。
    """

    chunk_id: str
    document_id: str
    project_id: str
    index: int
    text: str
    source: str = ""


class IngestionResult(BaseModel):
    """一次导入流水线结果。

    参数说明:
        document_id: 文档 id。
        chunk_count: 生成 chunk 数量。
        dry_run: 是否仅预览不写库。
        chunks: 生成的 chunks。
    """

    document_id: str
    chunk_count: int
    dry_run: bool
    chunks: list[IngestionChunk] = Field(default_factory=list)

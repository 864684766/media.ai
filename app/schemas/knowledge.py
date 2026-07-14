"""知识库 API 数据模型。"""

from pydantic import BaseModel, Field


class KnowledgeDocumentItem(BaseModel):
    """知识库文档条目。"""

    document_id: str = Field(description="文档 id")
    project_id: str = Field(description="项目 id")
    source: str = Field(default="", description="来源")
    preview: str = Field(default="", description="正文预览")
    chunk_count: int = Field(default=0, description="chunk 数量")


class KnowledgeDocumentListResponse(BaseModel):
    """文档列表响应。"""

    items: list[KnowledgeDocumentItem] = Field(default_factory=list)


class KnowledgeIngestJsonRequest(BaseModel):
    """JSON 方式导入文档请求体。"""

    project_id: str = Field(description="项目 id")
    document_id: str = Field(description="文档 id")
    source: str = Field(default="", description="来源说明")
    text: str = Field(min_length=1, description="正文")


class KnowledgeIngestResponse(BaseModel):
    """导入文档响应。"""

    document_id: str = Field(description="文档 id")
    project_id: str = Field(description="项目 id")
    chunk_count: int = Field(description="写入 chunk 数")
    rejected_extensions: list[str] = Field(default_factory=list, description="不支持的扩展名")


class KnowledgeDocumentDetailResponse(BaseModel):
    """单文档详情响应。"""

    document_id: str = Field(description="文档 id")
    project_id: str = Field(description="项目 id")
    source: str = Field(default="", description="来源")
    text_length: int = Field(description="正文字符数")
    chunk_count: int = Field(description="chunk 数量")
    created_at: str = Field(default="", description="创建时间 ISO")


class KnowledgeChunkItem(BaseModel):
    """单条 chunk 预览。"""

    chunk_id: str = Field(description="chunk id")
    chunk_index: int = Field(description="文档内序号")
    text: str = Field(description="chunk 文本")


class KnowledgeChunkListResponse(BaseModel):
    """chunk 分页列表响应。"""

    document_id: str = Field(description="文档 id")
    total: int = Field(description="总 chunk 数")
    offset: int = Field(description="当前偏移")
    limit: int = Field(description="本页条数")
    items: list[KnowledgeChunkItem] = Field(default_factory=list)

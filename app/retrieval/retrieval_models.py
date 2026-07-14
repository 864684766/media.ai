"""检索流水线数据模型。

【职责】
    定义检索链在图内外流转的结构，与 docs/ARCHITECTURE.html sec-15.3 契约一致：
    RetrievedChunk（单条证据）、WebResult（网页结果）、
    RetrievalContext（写入 AgentState.retrieval）、GradeResult（Grader 输出）。
"""

from pydantic import BaseModel, Field


class RetrievedChunk(BaseModel):
    """检索到的单条 chunk 证据。

    参数说明:
        chunk_id: chunk id（PG 与 Neo4j 对齐的同一 id）。
        document_id: 所属文档 id。
        text: chunk 文本。
        score: 融合/重排后的分数（越大越相关）。
        source: 来源说明（citation 展示用）。
    """

    chunk_id: str = Field(description="chunk id")
    document_id: str = Field(default="", description="所属文档 id")
    text: str = Field(description="chunk 文本")
    score: float = Field(default=0.0, description="相关性分数")
    source: str = Field(default="", description="来源说明")


class WebResult(BaseModel):
    """Web 搜索结果条目。

    参数说明:
        title: 网页标题。
        url: 网页链接。
        snippet: 摘要片段。
    """

    title: str = Field(default="", description="网页标题")
    url: str = Field(default="", description="网页链接")
    snippet: str = Field(default="", description="摘要片段")


class RetrievalContext(BaseModel):
    """检索/Web 证据集合（写入 AgentState.retrieval）。

    参数说明:
        chunks: 作品库检索证据。
        web_results: Web 搜索结果。
    """

    chunks: list[RetrievedChunk] = Field(default_factory=list, description="chunk 证据")
    web_results: list[WebResult] = Field(default_factory=list, description="Web 结果")


class GradeResult(BaseModel):
    """Grader 评估结果。

    参数说明:
        verdict: relevant（进 Rerank）/ irrelevant（改写重检）/ no_evidence（Web 兜底）。
        retry_count: 已重试次数（rewrite 回环用）。
    """

    verdict: str = Field(description="判定结果")
    retry_count: int = Field(default=0, description="重试次数")

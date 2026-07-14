"""Provider 流式 chunk 模型。

【职责】
    表达 OpenAI 兼容流式返回中的文本增量与 usage 统计。
"""

from pydantic import BaseModel, Field


class ProviderStreamChunk(BaseModel):
    """单个流式片段。

    参数说明:
        delta: 本次新增文本。
        usage: token 用量统计；通常在最后一个 chunk 才出现。
    """

    delta: str | None = Field(default=None, description="新增文本")
    usage: dict | None = Field(default=None, description="token 用量")

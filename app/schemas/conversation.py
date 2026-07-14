"""会话与消息 API 响应契约。

【职责】
    定义 GET /conversations 与 GET /conversations/{id}/messages 的响应结构。
    与 docs/ARCHITECTURE.html sec-15 对齐，供前端 media-web 消费。
"""

from datetime import datetime

from pydantic import BaseModel, Field


class ConversationSummary(BaseModel):
    """会话列表单项。

    参数说明:
        id: 会话 id（续聊时作为 conversation_id 传给 POST /chat）。
        project_id: 可选项目 id。
        preview: 最近一条消息摘要（列表展示用）。
        updated_at: 最后更新时间。
    """

    id: str = Field(description="会话 id")
    project_id: str | None = Field(default=None, description="项目 id")
    creation_type: str | None = Field(default=None, description="创作类型 novel | video")
    preview: str = Field(default="", description="最近消息摘要")
    updated_at: datetime = Field(description="最后更新时间")


class ConversationListResponse(BaseModel):
    """会话列表响应。"""

    items: list[ConversationSummary] = Field(default_factory=list)


class MessageItem(BaseModel):
    """单条历史消息。"""

    id: int = Field(description="消息 id")
    role: str = Field(description="user / assistant / system")
    content: str = Field(description="消息正文")
    created_at: datetime = Field(description="创建时间")


class MessageListResponse(BaseModel):
    """会话消息列表响应。"""

    conversation_id: str = Field(description="会话 id")
    creation_type: str = Field(description="创作类型 novel | video")
    items: list[MessageItem] = Field(default_factory=list)

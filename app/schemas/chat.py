"""Chat API 数据契约。

【职责】
    定义 HTTP Chat 请求与 SSE 事件的基础结构。

【何时使用】
    app/api/chat.py 接 POST /api/v1/chat 时会用 ChatRequest；
    SSE 输出时会用 ChatStreamEvent。
"""

from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.schemas.clarification import ClarificationResponsePayload


class ChatRequest(BaseModel):
    """Chat 请求体。

    参数说明:
        message: 用户本轮输入（澄清回答轮可与 clarification_response 二选一）。
        clarification_response: 结构化澄清答案（阶段 F）。
        clarification_skip: 跳过澄清引导（须配置 allow_skip）。
        conversation_id: 可选会话 id；空则新会话。
        project_id: 可选项目 id；Phase 2 检索过滤用。
        skill_id: 可选 Skill id；优先于自动匹配。
        creation_type: 创作类型 novel（小说）/ video（视频）；限定 Skill 池与默认人设。
        stream: 是否流式输出。
    """

    message: str = Field(default="", description="用户本轮输入")
    clarification_response: ClarificationResponsePayload | None = Field(
        default=None,
        description="澄清问答结构化回答",
    )
    clarification_skip: bool = Field(default=False, description="跳过澄清引导")
    conversation_id: str | None = Field(default=None, description="续聊会话 id")
    project_id: str | None = Field(default=None, description="项目 id")
    skill_id: str | None = Field(default=None, description="指定 Skill")
    creation_type: Literal["novel", "video"] | None = Field(
        default=None,
        description="创作类型：novel 小说 / video 视频",
    )
    stream: bool = Field(default=True, description="是否流式输出")

    @model_validator(mode="after")
    def check_message_or_clarification(self) -> "ChatRequest":
        """message 与 clarification_response 至少其一有效。"""
        has_message = bool(self.message.strip())
        has_response = self.clarification_response is not None
        if not has_message and not has_response:
            raise ValueError("message 与 clarification_response 至少填一项")
        return self


class ChatStreamEvent(BaseModel):
    """SSE 事件结构。

    参数说明:
        event: 事件名，如 content_delta / message_end。
        data: 事件数据；不同 event 结构不同。
    """

    event: str = Field(description="SSE 事件名")
    data: dict = Field(default_factory=dict, description="事件数据")

"""澄清问答 API 契约（阶段 F）。

【职责】
    定义 SSE clarification_* 事件与 ChatRequest.clarification_response 结构。

【何时调用】
    chat API、clarification_stream_service、media-web types 对齐。
"""

from pydantic import BaseModel, Field, model_validator

from app.core.clarification_constants import SELECTION_MODE_SINGLE


class ClarificationOptionItem(BaseModel):
    """单条可选项。"""

    option_id: str = Field(description="选项 id")
    label: str = Field(description="展示文案")
    hint: str = Field(default="", description="辅助说明")


class ClarificationQuestionItem(BaseModel):
    """单道澄清题。"""

    question_id: str = Field(description="题目 id")
    prompt: str = Field(description="题干")
    selection_mode: str = Field(default=SELECTION_MODE_SINGLE, description="选择模式")
    allow_custom: bool = Field(default=True, description="是否允许自定义输入")
    options: list[ClarificationOptionItem] = Field(default_factory=list)


class ClarificationAnswerItem(BaseModel):
    """用户对单题的回答。"""

    question_id: str = Field(description="题目 id")
    option_id: str | None = Field(default=None, description="选中预设项")
    custom_text: str | None = Field(default=None, description="自定义文本")

    @model_validator(mode="after")
    def check_answer_present(self) -> "ClarificationAnswerItem":
        """option_id 与 custom_text 至少其一非空。"""
        has_option = bool(self.option_id and self.option_id.strip())
        has_custom = bool(self.custom_text and self.custom_text.strip())
        if not has_option and not has_custom:
            raise ValueError("须选择选项或填写自定义说明")
        return self


class ClarificationResponsePayload(BaseModel):
    """ChatRequest 内嵌的澄清回答。"""

    session_id: str = Field(description="会话 id")
    answers: list[ClarificationAnswerItem] = Field(description="本轮答案列表")

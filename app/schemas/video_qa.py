"""连续性 QA API 契约。"""

from pydantic import BaseModel, Field


class ShotQaFailure(BaseModel):
    """单镜 QA 失败说明。"""

    shot_id: str = Field(description="镜头 id")
    shot_no: str = Field(description="镜号")
    status: str = Field(description="qa_failed 或 awaiting_review")
    reasons: list[str] = Field(description="失败原因")


class ContinuityQaResponse(BaseModel):
    """POST qa 响应。"""

    project_id: str = Field(description="项目 id")
    passed_count: int = Field(description="置 qa_passed 的镜头数")
    failed_count: int = Field(description="置 qa_failed 的镜头数")
    awaiting_review_count: int = Field(description="重试超限置 awaiting_review 数")
    failures: list[ShotQaFailure] = Field(default_factory=list)

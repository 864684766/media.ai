"""HITL 镜头审核 API 契约。"""

from pydantic import BaseModel, Field

from app.schemas.video_shot import ShotOutput


class ShotReviewRequest(BaseModel):
    """POST review 请求体。"""

    stage: str = Field(description="qa_overflow / keyframe / storyboard")
    action: str = Field(description="approve / reject")
    comment: str = Field(default="", description="审核备注（可选）")


class ShotReviewResponse(BaseModel):
    """POST review 响应。"""

    shot: ShotOutput = Field(description="更新后的镜头")
    previous_status: str = Field(description="审核前状态")
    comment: str = Field(default="", description="回显备注")

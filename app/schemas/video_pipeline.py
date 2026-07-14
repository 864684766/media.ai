"""视频流水线状态 API 契约。"""

from pydantic import BaseModel, Field

from app.schemas.video_shot import ShotOutput


class PipelineStepOutput(BaseModel):
    """单步进度。"""

    id: str = Field(description="步骤 id")
    label: str = Field(description="展示名")
    done_count: int = Field(description="已完成镜头数")
    total_count: int = Field(description="总镜头数")


class PipelineStatusResponse(BaseModel):
    """GET pipeline 响应。"""

    project_id: str = Field(description="项目 id")
    shots_total: int = Field(description="镜头总数")
    status_counts: dict[str, int] = Field(description="各状态镜头数")
    steps: list[PipelineStepOutput] = Field(description="流水线步骤进度")
    awaiting_review: list[ShotOutput] = Field(description="待人工审核镜头")
    review_config: dict[str, bool] = Field(description="HITL 开关")
    blocking_reason: str = Field(default="", description="阻断原因码；空表示可继续")
    latest_job_id: str = Field(default="", description="最近异步 Job id")

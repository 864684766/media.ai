"""视频管线异步 Job API 契约。"""

from pydantic import BaseModel, Field

from app.schemas.video_pipeline_run import VideoPipelineRunResponse


class VideoPipelineJobStartResponse(BaseModel):
    """POST pipeline/run/async 响应。"""

    job_id: str = Field(description="异步 Job id")
    project_id: str = Field(description="项目 id")
    status: str = Field(description="pending")


class VideoPipelineJobDetailResponse(BaseModel):
    """GET/POST resume Job 响应。"""

    job_id: str = Field(description="Job id")
    project_id: str = Field(description="项目 id")
    status: str = Field(description="Job 状态")
    run: VideoPipelineRunResponse = Field(description="checkpoint 映射的运行结果")

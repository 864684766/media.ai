"""视频子图一键运行 API 契约。"""

from pydantic import BaseModel, Field

from app.schemas.video_compose import ComposeOutputUrls


class VideoPipelineRunResponse(BaseModel):
    """POST pipeline/run 响应。"""

    project_id: str = Field(description="项目 id")
    run_status: str = Field(description="completed / paused / failed")
    current_step: str = Field(description="最后执行的节点")
    steps_completed: list[str] = Field(description="已完成节点列表")
    paused: bool = Field(description="是否暂停待人工")
    pause_reason: str = Field(default="", description="暂停原因")
    validate_validated_count: int = Field(default=0)
    render_job_id: str = Field(default="")
    qa_passed_count: int = Field(default=0)
    qa_awaiting_count: int = Field(default=0)
    compose_output: ComposeOutputUrls | None = Field(default=None, description="合成产物 URL")
    error_message: str = Field(default="", description="失败信息")

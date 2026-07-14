"""LangGraph 视频子图共享状态（阶段 D1）。

【职责】
    编排 validate → review → render → qa → audio → compose 时在各节点间传递进度。

【何时调用】
    video_langgraph_builder 组图；video_pipeline_run_service invoke。
"""

from pydantic import BaseModel, Field

from app.core.video_pipeline_run_constants import PIPELINE_RUN_COMPLETED


class VideoPipelineState(BaseModel):
    """视频子图 state。"""

    project_id: str = Field(description="项目 id")
    run_status: str = Field(default=PIPELINE_RUN_COMPLETED, description="completed/paused/failed")
    current_step: str = Field(default="", description="最近执行的节点名")
    paused: bool = Field(default=False, description="是否因 HITL 暂停")
    pause_reason: str = Field(default="", description="暂停原因码")
    steps_completed: list[str] = Field(default_factory=list, description="已完成节点 id 列表")
    validate_validated_count: int = Field(default=0, description="校验通过镜头数")
    render_job_id: str = Field(default="", description="渲染 Job id")
    qa_passed_count: int = Field(default=0, description="QA 通过数")
    qa_awaiting_count: int = Field(default=0, description="awaiting_review 数")
    compose_output_uri: str = Field(default="", description="成片相对 URI")
    error_message: str = Field(default="", description="失败说明")

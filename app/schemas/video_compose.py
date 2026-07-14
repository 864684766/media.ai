"""视频合成 API 契约（V5）。"""

from pydantic import BaseModel, Field


class ComposeOutputUrls(BaseModel):
    """成片产物访问 URL。"""

    uri: str = Field(description="相对 files 路径")
    open_url: str = Field(description="浏览器打开")
    download_url: str = Field(description="下载")
    subtitles_burned: bool = Field(default=False, description="是否已将 SRT 烧录进 mp4（G3）")


class ComposeJobOutput(BaseModel):
    """合成 Job 状态。"""

    job_id: str = Field(description="任务 id")
    project_id: str = Field(description="项目 id")
    status: str = Field(description="pending/running/completed/failed")
    total_shots: int = Field(description="纳入镜头数")
    output_uri: str = Field(default="", description="产物相对路径")
    output: ComposeOutputUrls | None = Field(default=None, description="访问 URL")


class ComposeStartResponse(BaseModel):
    """POST compose 响应。"""

    job: ComposeJobOutput = Field(description="Job 状态")
    output: ComposeOutputUrls = Field(description="成片 Stub URL")

"""视频渲染 Job 与 Stub 资产 API 契约。"""

from pydantic import BaseModel, Field


class ShotAssetOutput(BaseModel):
    """单条镜头资产。"""

    asset_id: str = Field(description="资产 id")
    shot_id: str = Field(description="镜头 id")
    asset_type: str = Field(description="keyframe / clip")
    uri: str = Field(description="相对 files API 路径")
    provider: str = Field(default="stub", description="生成 Provider id")
    cost: float = Field(default=0.0, description="该资产记账成本（美元占位）")
    open_url: str = Field(description="浏览器打开 URL")
    download_url: str = Field(description="下载 URL")


class RenderJobOutput(BaseModel):
    """渲染 Job 状态。"""

    job_id: str = Field(description="任务 id")
    project_id: str = Field(description="项目 id")
    status: str = Field(description="pending/running/completed/failed")
    total_shots: int = Field(description="总镜头数")
    finished_shots: int = Field(description="已完成镜头数")


class RenderStartResponse(BaseModel):
    """POST render 响应。"""

    job: RenderJobOutput = Field(description="Job 状态")
    assets: list[ShotAssetOutput] = Field(default_factory=list, description="本批产出资产")

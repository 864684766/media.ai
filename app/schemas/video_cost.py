"""视频项目成本 API 契约（V7）。"""

from pydantic import BaseModel, Field


class ActiveProvidersOutput(BaseModel):
    """当前 Provider 选型。"""

    keyframe: str = Field(description="关键帧 Provider id")
    clip: str = Field(description="切片 Provider id")
    compose: str = Field(description="合成模式 stub_json / local_ffmpeg")


class ProjectCostOutput(BaseModel):
    """GET cost 响应。"""

    project_id: str = Field(description="项目 id")
    total_cost_usd: float = Field(description="已累计成本")
    budget_limit_usd: float = Field(description="预算上限，0 表示不限")
    remaining_usd: float = Field(description="剩余预算")
    budget_exceeded: bool = Field(description="是否已超限")
    asset_count: int = Field(description="资产条数")
    active_providers: ActiveProvidersOutput = Field(description="当前 Provider 选型")

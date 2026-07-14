"""视频项目 API 契约。"""

from pydantic import BaseModel, Field

from app.core.video_project_constants import (
    DEFAULT_ASPECT_RATIO,
    DEFAULT_PROJECT_FPS,
    DEFAULT_RESOLUTION,
    DEFAULT_TARGET_DURATION_SEC,
)


class VideoProjectCreateRequest(BaseModel):
    """POST /video/projects 请求体。"""

    title: str = Field(description="展示标题")
    description: str = Field(default="", description="选填项目说明，最长 500 字")
    project_id: str = Field(default="", description="可选 slug，缺省由 title 生成")
    target_duration_sec: float = Field(default=DEFAULT_TARGET_DURATION_SEC)
    aspect_ratio: str = Field(default=DEFAULT_ASPECT_RATIO)
    resolution: str = Field(default=DEFAULT_RESOLUTION)
    fps: int = Field(default=DEFAULT_PROJECT_FPS)
    style_bible: str = Field(default="")
    budget_limit_usd: float = Field(default=0.0, description="0 表示用全局默认")


class VideoProjectOutput(BaseModel):
    """单条项目摘要。"""

    project_id: str = Field(description="项目 slug")
    title: str = Field(description="展示标题")
    description: str = Field(default="", description="项目说明")
    status: str = Field(description="active/archived")
    aspect_ratio: str = Field(description="画幅")
    resolution: str = Field(description="分辨率")
    fps: int = Field(description="帧率")
    budget_limit_usd: float = Field(description="项目预算上限")
    shot_count: int = Field(default=0, description="分镜数量（列表聚合）")
    updated_at: str = Field(default="", description="ISO 更新时间")


class VideoProjectListResponse(BaseModel):
    """GET /video/projects 响应。"""

    items: list[VideoProjectOutput] = Field(default_factory=list)


class VideoProjectDetailResponse(BaseModel):
    """GET /video/projects/{id} 响应。"""

    project: VideoProjectOutput = Field(description="项目元数据")
    style_bible: str = Field(default="")


class ProjectSuggestionItem(BaseModel):
    """命名空间建议项。"""

    project_id: str = Field(description="project_id")
    registered: bool = Field(description="是否已在 video_projects 表")
    title: str = Field(default="", description="已注册时的标题")
    description: str = Field(default="", description="已注册时的描述")
    shot_count: int = Field(default=0)


class ProjectSuggestionListResponse(BaseModel):
    """GET /video/projects/suggestions 响应。"""

    items: list[ProjectSuggestionItem] = Field(default_factory=list)


class VideoProjectUpdateRequest(BaseModel):
    """PATCH /video/projects/{id} 请求体。"""

    style_bible: str | None = Field(default=None, description="全局风格锁段落")

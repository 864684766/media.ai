"""创作大纲 API Schema。"""

from datetime import datetime

from pydantic import BaseModel, Field

from app.core.creative_plan_constants import OUTLINE_CREATION_TYPE_NOVEL
from app.schemas.video_shot import ShotOutput


class NovelChapterItem(BaseModel):
    """小说章节纲要条目。"""

    chapter_no: int = Field(description="章号")
    title: str = Field(description="章节标题")
    beats: list[str] = Field(default_factory=list, description="情节要点")
    foreshadowing: str = Field(default="", description="伏笔/悬念")


class NovelCharacterItem(BaseModel):
    """小说角色条目。"""

    name: str = Field(description="角色名")
    role: str = Field(description="角色定位")


class NovelPlanContent(BaseModel):
    """小说大纲结构化正文。"""

    synopsis: str = Field(description="故事梗概")
    chapters: list[NovelChapterItem] = Field(default_factory=list)
    characters: list[NovelCharacterItem] = Field(default_factory=list)


class VideoSegmentItem(BaseModel):
    """视频分段条目。"""

    start_sec: int = Field(description="起始秒")
    end_sec: int = Field(description="结束秒")
    visual: str = Field(description="画面描述")
    mood: str = Field(description="情绪/节奏")


class VideoPlanContent(BaseModel):
    """视频大纲结构化正文。"""

    hook: str = Field(description="开场钩子")
    segments: list[VideoSegmentItem] = Field(default_factory=list)
    style_notes: str = Field(default="", description="风格说明")
    target_duration_sec: int = Field(default=60, description="目标时长（秒）")


class CreativePlanCreateRequest(BaseModel):
    """创建大纲请求。"""

    conversation_id: str = Field(description="关联会话 id")
    creation_type: str = Field(default=OUTLINE_CREATION_TYPE_NOVEL, description="novel | video")
    project_id: str | None = Field(default=None, description="可选项目命名空间")
    brief: str | None = Field(default=None, description="用户 brief 降级用")
    clarification_session_id: str | None = Field(default=None, description="澄清会话 id")


class CreativePlanPatchRequest(BaseModel):
    """手工编辑大纲 Markdown。"""

    content_md: str = Field(description="用户编辑后的 Markdown")


class CreativePlanReviseRequest(BaseModel):
    """AI 改稿请求。"""

    comment: str = Field(description="用户修改意见")


class CreativePlanItem(BaseModel):
    """大纲详情响应体。"""

    plan_id: str
    conversation_id: str
    project_id: str | None
    creation_type: str
    status: str
    version: int
    title: str
    content_json: dict
    content_md: str
    user_feedback: str
    clarification_session_id: str | None
    revision_count: int
    created_at: datetime
    updated_at: datetime
    approved_at: datetime | None


class CreativePlanDetailResponse(BaseModel):
    """单条大纲响应包装。"""

    plan: CreativePlanItem


class CreativePlanListResponse(BaseModel):
    """会话下大纲列表（通常一条）。"""

    items: list[CreativePlanItem]


class CreativePlanStoryboardRequest(BaseModel):
    """已确认大纲 → 生成分镜请求。"""

    project_id: str | None = Field(default=None, description="可选；缺省时用大纲关联 project_id")


class CreativePlanStoryboardResponse(BaseModel):
    """已确认大纲 → 生成分镜响应。"""

    plan_id: str = Field(description="来源大纲 id")
    project_id: str = Field(description="入库项目 id")
    replaced_count: int = Field(description="替换删除的旧镜头数")
    shots: list[ShotOutput] = Field(description="入库后的镜头列表")

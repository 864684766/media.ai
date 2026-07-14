"""视频分镜 API 数据模型（Pydantic）。

【职责】
    定义 POST storyboard / GET shots 的请求与响应契约，与 VIDEO_PIPELINE §3.3 对齐。
"""

from pydantic import BaseModel, Field


class ShotInput(BaseModel):
    """提交分镜时的单条镜头（无 shot_id，由服务端生成）。"""

    shot_no: str = Field(description="镜号，如 1、2A")
    duration_sec: float = Field(gt=0, description="时长（秒）")
    shot_size: str = Field(default="", description="景别，如中景、特写")
    camera: str = Field(default="", description="机位与运动")
    action: str = Field(default="", description="画面动作描述")
    dialogue: str = Field(default="", description="台词或旁白")
    sfx: str = Field(default="", description="音效")
    character_ids: list[str] = Field(default_factory=list, description="出场角色 ID 列表")
    scene_id: str = Field(default="", description="场景 ID")
    prop_ids: list[str] = Field(default_factory=list, description="道具 ID 列表")
    transition: str = Field(default="", description="与下一镜转场（cut/dissolve 等）")


class ShotOutput(BaseModel):
    """已入库镜头的完整视图。"""

    shot_id: str = Field(description="镜头唯一 id")
    project_id: str = Field(description="项目 id")
    shot_no: str = Field(description="镜号")
    duration_sec: float = Field(description="时长（秒）")
    shot_size: str = Field(default="")
    camera: str = Field(default="")
    action: str = Field(default="")
    dialogue: str = Field(default="")
    sfx: str = Field(default="")
    character_ids: list[str] = Field(default_factory=list)
    scene_id: str = Field(default="")
    prop_ids: list[str] = Field(default_factory=list)
    keyframe_uri: str = Field(default="", description="关键帧 URI，V3 写入")
    transition: str = Field(default="")
    status: str = Field(description="镜头状态，见 VIDEO_PIPELINE 状态机")
    qa_attempts: int = Field(default=0, description="QA 失败重试次数")


class StoryboardSubmitRequest(BaseModel):
    """POST .../storyboard 请求体。"""

    shots: list[ShotInput] = Field(min_length=1, description="结构化分镜数组")


class StoryboardSubmitResponse(BaseModel):
    """POST .../storyboard 响应。"""

    project_id: str = Field(description="项目 id")
    replaced_count: int = Field(description="本次替换删除的旧镜头数")
    shots: list[ShotOutput] = Field(description="入库后的镜头列表")


class StoryboardListResponse(BaseModel):
    """GET .../shots 响应。"""

    project_id: str = Field(description="项目 id")
    shots: list[ShotOutput] = Field(default_factory=list, description="按镜号排序的镜头列表")

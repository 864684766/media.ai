"""视频一致性资产（bible）API 数据模型。"""

from pydantic import BaseModel, Field


class CharacterBibleInput(BaseModel):
    """角色圣经入参。"""

    character_id: str = Field(description="角色 ID")
    name: str = Field(default="", description="角色名")
    appearance: str = Field(default="", description="外观描述")
    costume: str = Field(default="", description="服装")
    age_band: str = Field(default="", description="年龄段")
    ref_image_urls: list[str] = Field(default_factory=list, description="参考图 URL 列表")
    voice_id: str = Field(default="", description="TTS 音色 ID（V8）")


class SceneLockInput(BaseModel):
    """场景锁定入参。"""

    scene_id: str = Field(description="场景 ID")
    name: str = Field(default="", description="场景名")
    setting: str = Field(default="", description="布景描述")
    lighting: str = Field(default="", description="光照")
    ref_image_urls: list[str] = Field(default_factory=list, description="参考图 URL 列表")


class PropInventoryInput(BaseModel):
    """道具清单入参。"""

    prop_id: str = Field(description="道具 ID")
    name: str = Field(default="", description="道具名")
    description: str = Field(default="", description="描述")
    ref_image_urls: list[str] = Field(default_factory=list, description="参考图 URL 列表")


class CharacterBibleUpsertRequest(BaseModel):
    """PUT bible/characters 请求体。"""

    characters: list[CharacterBibleInput] = Field(min_length=1)


class SceneLockUpsertRequest(BaseModel):
    """PUT bible/scenes 请求体。"""

    scenes: list[SceneLockInput] = Field(min_length=1)


class PropInventoryUpsertRequest(BaseModel):
    """PUT bible/props 请求体。"""

    props: list[PropInventoryInput] = Field(min_length=1)


class CharacterBibleOutput(CharacterBibleInput):
    """角色圣经响应条目。"""

    project_id: str = Field(description="项目 id")
    lock_version: int = Field(description="锁定版本号")


class SceneLockOutput(SceneLockInput):
    """场景锁定响应条目。"""

    project_id: str = Field(description="项目 id")


class PropInventoryOutput(PropInventoryInput):
    """道具清单响应条目。"""

    project_id: str = Field(description="项目 id")


class BibleListResponse(BaseModel):
    """GET bible 汇总响应。"""

    project_id: str = Field(description="项目 id")
    characters: list[CharacterBibleOutput] = Field(default_factory=list)
    scenes: list[SceneLockOutput] = Field(default_factory=list)
    props: list[PropInventoryOutput] = Field(default_factory=list)


class ShotValidationFailure(BaseModel):
    """单镜校验失败说明。"""

    shot_id: str = Field(description="镜头 id")
    shot_no: str = Field(description="镜号")
    reasons: list[str] = Field(description="失败原因列表")


class EntityValidateResponse(BaseModel):
    """POST validate 响应。"""

    project_id: str = Field(description="项目 id")
    validated_count: int = Field(description="通过并置 validated 的镜头数")
    rejected_count: int = Field(description="失败并置 rejected 的镜头数")
    failures: list[ShotValidationFailure] = Field(default_factory=list)


class StripShotBibleRefsRequest(BaseModel):
    """从分镜移除 Bible 实体引用请求。"""

    character_ids: list[str] = Field(default_factory=list, description="要从分镜剔除的角色 id")
    scene_ids: list[str] = Field(default_factory=list, description="要从分镜剔除的场景 id")
    prop_ids: list[str] = Field(default_factory=list, description="要从分镜剔除的道具 id")


class StripShotBibleRefsResponse(BaseModel):
    """从分镜移除引用响应。"""

    project_id: str = Field(description="项目 id")
    updated_shot_count: int = Field(description="被修改的镜头数")

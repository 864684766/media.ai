"""bible ORM 与 Pydantic 互转辅助。"""

from app.models.postgres.character_bible_model import CharacterBibleModel
from app.models.postgres.prop_inventory_model import PropInventoryModel
from app.models.postgres.scene_lock_model import SceneLockModel
from app.schemas.video_bible import (
    CharacterBibleInput,
    CharacterBibleOutput,
    PropInventoryInput,
    PropInventoryOutput,
    SceneLockInput,
    SceneLockOutput,
)


def character_input_to_model(
    project_id: str,
    payload: CharacterBibleInput,
    lock_version: int,
) -> CharacterBibleModel:
    """角色入参转 ORM（新建行）。

    参数:
        project_id: 项目 id。
        payload: 角色入参。
        lock_version: 锁定版本。

    返回:
        CharacterBibleModel: 未持久化的 ORM 行。
    """
    return CharacterBibleModel(
        project_id=project_id,
        character_id=payload.character_id,
        name=payload.name,
        appearance=payload.appearance,
        costume=payload.costume,
        age_band=payload.age_band,
        ref_image_urls=list(payload.ref_image_urls),
        voice_id=payload.voice_id,
        lock_version=lock_version,
    )


def character_model_to_output(model: CharacterBibleModel) -> CharacterBibleOutput:
    """角色 ORM 转 API 输出。

    参数:
        model: 已持久化行。

    返回:
        CharacterBibleOutput: 响应条目。
    """
    return CharacterBibleOutput(
        project_id=model.project_id,
        character_id=model.character_id,
        name=model.name,
        appearance=model.appearance,
        costume=model.costume,
        age_band=model.age_band,
        ref_image_urls=list(model.ref_image_urls or []),
        voice_id=model.voice_id or "",
        lock_version=model.lock_version,
    )


def scene_input_to_model(project_id: str, payload: SceneLockInput) -> SceneLockModel:
    """场景入参转 ORM。

    参数:
        project_id: 项目 id。
        payload: 场景入参。

    返回:
        SceneLockModel: 未持久化行。
    """
    return SceneLockModel(
        project_id=project_id,
        scene_id=payload.scene_id,
        name=payload.name,
        setting=payload.setting,
        lighting=payload.lighting,
        ref_image_urls=list(payload.ref_image_urls),
    )


def scene_model_to_output(model: SceneLockModel) -> SceneLockOutput:
    """场景 ORM 转 API 输出。"""
    return SceneLockOutput(
        project_id=model.project_id,
        scene_id=model.scene_id,
        name=model.name,
        setting=model.setting,
        lighting=model.lighting,
        ref_image_urls=list(model.ref_image_urls or []),
    )


def prop_input_to_model(project_id: str, payload: PropInventoryInput) -> PropInventoryModel:
    """道具入参转 ORM。"""
    return PropInventoryModel(
        project_id=project_id,
        prop_id=payload.prop_id,
        name=payload.name,
        description=payload.description,
        ref_image_urls=list(payload.ref_image_urls),
    )


def prop_model_to_output(model: PropInventoryModel) -> PropInventoryOutput:
    """道具 ORM 转 API 输出。"""
    return PropInventoryOutput(
        project_id=model.project_id,
        prop_id=model.prop_id,
        name=model.name,
        description=model.description,
        ref_image_urls=list(model.ref_image_urls or []),
    )

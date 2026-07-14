"""视频 bible 与实体校验 API。

【职责】
    V2：角色/场景/道具 bible upsert、汇总列表、validate_entities。
"""

from fastapi import APIRouter, HTTPException

from app.api.api_constants import VIDEO_ROUTE_PREFIX
from app.schemas.video_bible import (
    BibleListResponse,
    CharacterBibleOutput,
    CharacterBibleUpsertRequest,
    EntityValidateResponse,
    PropInventoryOutput,
    PropInventoryUpsertRequest,
    SceneLockOutput,
    SceneLockUpsertRequest,
    StripShotBibleRefsRequest,
    StripShotBibleRefsResponse,
)
from app.services.bible_delete_service import (
    delete_character,
    delete_prop,
    delete_scene,
)
from app.services.bible_service import (
    list_project_bible,
    upsert_characters,
    upsert_props,
    upsert_scenes,
)
from app.services.bible_shot_ref_strip_service import strip_shot_bible_references
from app.services.entity_validation_service import validate_project_entities
from app.storage.postgres.postgres_session_scope import postgres_session_scope
from app.storage.postgres.postgres_settings_reader import is_postgres_configured

router = APIRouter(prefix=VIDEO_ROUTE_PREFIX, tags=["video"])


def _require_postgres() -> None:
    """未配置 DATABASE_URL 时拒绝。"""
    if not is_postgres_configured():
        raise HTTPException(status_code=503, detail="未配置 DATABASE_URL，无法使用视频 bible API")


@router.put(
    "/projects/{project_id}/bible/characters",
    summary="upsert 角色圣经",
    response_model=list[CharacterBibleOutput],
)
def put_character_bible(
    project_id: str,
    body: CharacterBibleUpsertRequest,
) -> list[CharacterBibleOutput]:
    """按 character_id upsert 角色条目。"""
    _require_postgres()
    with postgres_session_scope() as session:
        return upsert_characters(session, project_id, body)


@router.put(
    "/projects/{project_id}/bible/scenes",
    summary="upsert 场景锁定",
    response_model=list[SceneLockOutput],
)
def put_scene_bible(
    project_id: str,
    body: SceneLockUpsertRequest,
) -> list[SceneLockOutput]:
    """按 scene_id upsert 场景条目。"""
    _require_postgres()
    with postgres_session_scope() as session:
        return upsert_scenes(session, project_id, body)


@router.put(
    "/projects/{project_id}/bible/props",
    summary="upsert 道具清单",
    response_model=list[PropInventoryOutput],
)
def put_prop_bible(
    project_id: str,
    body: PropInventoryUpsertRequest,
) -> list[PropInventoryOutput]:
    """按 prop_id upsert 道具条目。"""
    _require_postgres()
    with postgres_session_scope() as session:
        return upsert_props(session, project_id, body)


@router.get(
    "/projects/{project_id}/bible",
    summary="列出项目 bible",
    response_model=BibleListResponse,
)
def get_project_bible(project_id: str) -> BibleListResponse:
    """返回角色/场景/道具三类条目。"""
    _require_postgres()
    with postgres_session_scope() as session:
        return list_project_bible(session, project_id)


@router.post(
    "/projects/{project_id}/validate",
    summary="校验分镜实体引用",
    response_model=EntityValidateResponse,
)
def post_validate_entities(project_id: str) -> EntityValidateResponse:
    """draft 镜头 → validated / rejected。"""
    _require_postgres()
    with postgres_session_scope() as session:
        return validate_project_entities(session, project_id)


@router.post(
    "/projects/{project_id}/bible/strip-shot-refs",
    summary="从分镜移除 Bible 实体引用",
    response_model=StripShotBibleRefsResponse,
)
def post_strip_shot_bible_refs(
    project_id: str,
    body: StripShotBibleRefsRequest,
) -> StripShotBibleRefsResponse:
    """从全部分镜剔除指定 character/scene/prop ID，不创建 Bible 占位。"""
    _require_postgres()
    with postgres_session_scope() as session:
        return strip_shot_bible_references(session, project_id, body)


@router.delete(
    "/projects/{project_id}/bible/characters/{character_id}",
    summary="删除角色圣经条目",
    status_code=204,
)
def delete_character_bible(project_id: str, character_id: str) -> None:
    """按 character_id 删除角色；不存在时仍返回 204。"""
    _require_postgres()
    with postgres_session_scope() as session:
        delete_character(session, project_id, character_id)


@router.delete(
    "/projects/{project_id}/bible/scenes/{scene_id}",
    summary="删除场景锁定条目",
    status_code=204,
)
def delete_scene_bible(project_id: str, scene_id: str) -> None:
    """按 scene_id 删除场景；不存在时仍返回 204。"""
    _require_postgres()
    with postgres_session_scope() as session:
        delete_scene(session, project_id, scene_id)


@router.delete(
    "/projects/{project_id}/bible/props/{prop_id}",
    summary="删除道具条目",
    status_code=204,
)
def delete_prop_bible(project_id: str, prop_id: str) -> None:
    """按 prop_id 删除道具；不存在时仍返回 204。"""
    _require_postgres()
    with postgres_session_scope() as session:
        delete_prop(session, project_id, prop_id)

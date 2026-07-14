"""bible 资产业务服务。"""

from sqlalchemy.orm import Session

from app.schemas.video_bible import (
    BibleListResponse,
    CharacterBibleOutput,
    CharacterBibleUpsertRequest,
    PropInventoryOutput,
    PropInventoryUpsertRequest,
    SceneLockOutput,
    SceneLockUpsertRequest,
)
from app.storage.postgres.character_bible_repository import CharacterBibleRepository
from app.storage.postgres.prop_inventory_repository import PropInventoryRepository
from app.storage.postgres.scene_lock_repository import SceneLockRepository
from app.video.bible_row_mapper import (
    character_model_to_output,
    prop_model_to_output,
    scene_model_to_output,
)


def upsert_characters(
    session: Session,
    project_id: str,
    request: CharacterBibleUpsertRequest,
) -> list[CharacterBibleOutput]:
    """upsert 角色圣经。"""
    repo = CharacterBibleRepository(session)
    models = repo.upsert_many(project_id, request.characters)
    return [character_model_to_output(row) for row in models]


def upsert_scenes(
    session: Session,
    project_id: str,
    request: SceneLockUpsertRequest,
) -> list[SceneLockOutput]:
    """upsert 场景锁定。"""
    repo = SceneLockRepository(session)
    models = repo.upsert_many(project_id, request.scenes)
    return [scene_model_to_output(row) for row in models]


def upsert_props(
    session: Session,
    project_id: str,
    request: PropInventoryUpsertRequest,
) -> list[PropInventoryOutput]:
    """upsert 道具清单。"""
    repo = PropInventoryRepository(session)
    models = repo.upsert_many(project_id, request.props)
    return [prop_model_to_output(row) for row in models]


def list_project_bible(session: Session, project_id: str) -> BibleListResponse:
    """汇总列出 project 下三类 bible。"""
    char_repo = CharacterBibleRepository(session)
    scene_repo = SceneLockRepository(session)
    prop_repo = PropInventoryRepository(session)
    return BibleListResponse(
        project_id=project_id,
        characters=[character_model_to_output(r) for r in char_repo.list_by_project(project_id)],
        scenes=[scene_model_to_output(r) for r in scene_repo.list_by_project(project_id)],
        props=[prop_model_to_output(r) for r in prop_repo.list_by_project(project_id)],
    )

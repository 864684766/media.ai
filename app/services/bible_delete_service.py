"""Bible 实体删除业务服务。"""

from sqlalchemy.orm import Session

from app.storage.postgres.character_bible_repository import CharacterBibleRepository
from app.storage.postgres.prop_inventory_repository import PropInventoryRepository
from app.storage.postgres.scene_lock_repository import SceneLockRepository


def delete_character(session: Session, project_id: str, character_id: str) -> bool:
    """删除单条角色圣经；不存在时视为已删除。"""
    return CharacterBibleRepository(session).delete_one(project_id, character_id)


def delete_scene(session: Session, project_id: str, scene_id: str) -> bool:
    """删除单条场景锁定；不存在时视为已删除。"""
    return SceneLockRepository(session).delete_one(project_id, scene_id)


def delete_prop(session: Session, project_id: str, prop_id: str) -> bool:
    """删除单条道具；不存在时视为已删除。"""
    return PropInventoryRepository(session).delete_one(project_id, prop_id)

"""跨表 project_id 命名空间聚合（建议列表用）。

【职责】
    从 shots/documents/conversations 提取 DISTINCT project_id。

【何时调用】
    GET /video/projects/suggestions 服务层。
"""

from sqlalchemy import distinct, select
from sqlalchemy.orm import Session

from app.models.postgres.conversation_model import ConversationModel
from app.models.postgres.document_model import DocumentModel
from app.models.postgres.character_bible_model import CharacterBibleModel
from app.models.postgres.prop_inventory_model import PropInventoryModel
from app.models.postgres.scene_lock_model import SceneLockModel
from app.models.postgres.shot_model import ShotModel


def collect_namespace_project_ids(session: Session) -> set[str]:
    """聚合各表出现的 project_id。

    参数:
        session: DB Session。

    返回:
        set[str]: 非空 project_id 集合。
    """
    ids: set[str] = set()
    ids.update(_distinct_shot_ids(session))
    ids.update(_distinct_document_ids(session))
    ids.update(_distinct_conversation_ids(session))
    ids.update(_distinct_bible_project_ids(session))
    ids.discard("")
    return ids


def project_id_in_namespace(session: Session, project_id: str) -> bool:
    """判断 project_id 是否已在任一名.namespace 表出现。"""
    return project_id in collect_namespace_project_ids(session)


def _distinct_shot_ids(session: Session) -> set[str]:
    """shots 表 DISTINCT project_id。"""
    stmt = select(distinct(ShotModel.project_id))
    return {str(v) for v in session.scalars(stmt).all() if v}


def _distinct_document_ids(session: Session) -> set[str]:
    """documents 表 DISTINCT project_id。"""
    stmt = select(distinct(DocumentModel.project_id))
    return {str(v) for v in session.scalars(stmt).all() if v}


def _distinct_conversation_ids(session: Session) -> set[str]:
    """conversations 表非空 project_id。"""
    stmt = select(distinct(ConversationModel.project_id)).where(
        ConversationModel.project_id.isnot(None),
    )
    return {str(v) for v in session.scalars(stmt).all() if v}


def _distinct_bible_project_ids(session: Session) -> set[str]:
    """bible 三表 DISTINCT project_id。"""
    ids: set[str] = set()
    for model in (CharacterBibleModel, SceneLockModel, PropInventoryModel):
        stmt = select(distinct(model.project_id))
        ids.update(str(v) for v in session.scalars(stmt).all() if v)
    return ids

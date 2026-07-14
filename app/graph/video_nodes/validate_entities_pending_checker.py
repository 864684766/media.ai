"""validate_entities 节点：待校验镜头计数。"""

from sqlalchemy.orm import Session

from app.graph.video_pipeline_shot_counter import count_entity_validation_pending


def has_entity_validation_pending(session: Session, project_id: str) -> bool:
    """是否存在 draft/rejected 待校验镜头。"""
    return count_entity_validation_pending(session, project_id) > 0

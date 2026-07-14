"""视频子图：是否跳过某步的检查。"""

from sqlalchemy.orm import Session

from app.storage.postgres.shot_repository import ShotRepository


def count_draft_shots(session: Session, project_id: str) -> int:
    """统计 draft 镜头数。"""
    return len(ShotRepository(session).list_draft_by_project(project_id))


def count_validated_shots(session: Session, project_id: str) -> int:
    """统计 validated 镜头数。"""
    return len(ShotRepository(session).list_validated_by_project(project_id))


def count_rendered_shots(session: Session, project_id: str) -> int:
    """统计 rendered 镜头数。"""
    return len(ShotRepository(session).list_rendered_by_project(project_id))


def count_project_shots(session: Session, project_id: str) -> int:
    """统计项目下全部镜头数。"""
    return len(ShotRepository(session).list_by_project(project_id))


def count_awaiting_review(session: Session, project_id: str) -> int:
    """统计 awaiting_review 镜头数。"""
    return len(ShotRepository(session).list_awaiting_review_by_project(project_id))


def count_rejected_shots(session: Session, project_id: str) -> int:
    """统计 rejected 镜头数。"""
    from app.core.video_constants import SHOT_STATUS_REJECTED

    shots = ShotRepository(session).list_by_project(project_id)
    return sum(1 for item in shots if item.status == SHOT_STATUS_REJECTED)


def count_entity_validation_pending(session: Session, project_id: str) -> int:
    """统计待实体校验镜头数（draft + rejected）。"""
    return len(
        ShotRepository(session).list_entity_validation_pending_by_project(project_id),
    )

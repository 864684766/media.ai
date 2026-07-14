"""从分镜批量移除 Bible 实体引用。"""

from sqlalchemy.orm import Session

from app.models.postgres.time_helper import utc_now
from app.schemas.video_bible import StripShotBibleRefsRequest, StripShotBibleRefsResponse
from app.storage.postgres.shot_repository import ShotRepository
from app.video.shot_bible_ref_stripper import apply_bible_ref_strip


def strip_shot_bible_references(
    session: Session,
    project_id: str,
    body: StripShotBibleRefsRequest,
) -> StripShotBibleRefsResponse:
    """从 project 全部分镜剔除指定 Bible ID 引用。

    参数:
        session: DB Session。
        project_id: 项目 id。
        body: 要移除的三类 ID 列表。

    返回:
        StripShotBibleRefsResponse: 更新镜头数。
    """
    repo = ShotRepository(session)
    char_set = set(body.character_ids)
    scene_set = set(body.scene_ids)
    prop_set = set(body.prop_ids)
    updated = _strip_project_shots(repo, project_id, char_set, scene_set, prop_set)
    return StripShotBibleRefsResponse(project_id=project_id, updated_shot_count=updated)


def _strip_project_shots(
    repo: ShotRepository,
    project_id: str,
    char_set: set[str],
    scene_set: set[str],
    prop_set: set[str],
) -> int:
    """遍历镜头并提交变更。"""
    shots = repo.list_by_project(project_id)
    updated = 0
    for shot in shots:
        if apply_bible_ref_strip(shot, char_set, scene_set, prop_set):
            shot.updated_at = utc_now()
            updated += 1
    if updated > 0:
        repo.commit()
    return updated

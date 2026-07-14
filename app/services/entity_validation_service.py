"""分镜实体校验业务服务（validate_entities）。"""

from sqlalchemy.orm import Session

from app.core.video_constants import SHOT_STATUS_REJECTED, SHOT_STATUS_VALIDATED
from app.schemas.video_bible import EntityValidateResponse, ShotValidationFailure
from app.storage.postgres.character_bible_repository import CharacterBibleRepository
from app.storage.postgres.prop_inventory_repository import PropInventoryRepository
from app.storage.postgres.scene_lock_repository import SceneLockRepository
from app.storage.postgres.shot_repository import ShotRepository
from app.video.entity_validation_checker import BibleIdSets, collect_shot_validation_reasons


def validate_project_entities(
    session: Session,
    project_id: str,
) -> EntityValidateResponse:
    """校验 draft/rejected 镜头引用的 bible ID，并更新状态。

    参数:
        session: PG Session。
        project_id: 项目 id。

    返回:
        EntityValidateResponse: 通过/拒绝计数与失败明细。
    """
    bible_ids = load_bible_id_sets(session, project_id)
    shot_repo = ShotRepository(session)
    pending_shots = shot_repo.list_entity_validation_pending_by_project(project_id)
    return _apply_validation(shot_repo, pending_shots, bible_ids, project_id)


def load_bible_id_sets(session: Session, project_id: str) -> BibleIdSets:
    """加载三类 bible ID 集合。"""
    return BibleIdSets(
        character_ids=CharacterBibleRepository(session).id_set(project_id),
        scene_ids=SceneLockRepository(session).id_set(project_id),
        prop_ids=PropInventoryRepository(session).id_set(project_id),
    )


def _apply_validation(
    shot_repo: ShotRepository,
    draft_shots: list,
    bible_ids: BibleIdSets,
    project_id: str,
) -> EntityValidateResponse:
    """逐镜校验并写回状态。"""
    validated = 0
    rejected = 0
    failures: list[ShotValidationFailure] = []
    for shot in draft_shots:
        reasons = collect_shot_validation_reasons(shot, bible_ids)
        if reasons:
            shot_repo.update_shot_status(shot.shot_id, SHOT_STATUS_REJECTED)
            failures.append(
                ShotValidationFailure(
                    shot_id=shot.shot_id,
                    shot_no=shot.shot_no,
                    reasons=reasons,
                ),
            )
            rejected += 1
            continue
        shot_repo.update_shot_status(shot.shot_id, SHOT_STATUS_VALIDATED)
        validated += 1
    return EntityValidateResponse(
        project_id=project_id,
        validated_count=validated,
        rejected_count=rejected,
        failures=failures,
    )

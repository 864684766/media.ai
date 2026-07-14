"""MCP continuity_check 单镜 QA 服务。"""

from sqlalchemy.orm import Session

from app.services.entity_validation_service import load_bible_id_sets
from app.storage.postgres.shot_repository import ShotRepository
from app.video.continuity_qa_reason_collector import collect_continuity_qa_reasons


def check_shot_continuity_for_mcp(session: Session, shot_id: str) -> dict:
    """对单镜执行规则版连续性检查。

    参数:
        session: PG Session。
        shot_id: 镜头 id。

    返回:
        dict: pass / fail 与 reasons。
    """
    shot = ShotRepository(session).get_shot(shot_id)
    if shot is None:
        raise ValueError(f"镜头不存在: {shot_id}")
    bible_ids = load_bible_id_sets(session, shot.project_id)
    previous = _find_previous_shot(session, shot)
    reasons = collect_continuity_qa_reasons(shot, previous, bible_ids)
    passed = len(reasons) == 0
    return {"shot_id": shot_id, "pass": passed, "reasons": reasons}


def _find_previous_shot(session: Session, shot):
    """按镜号找上一镜（简化：同 project 列表中前一个）。"""
    shots = ShotRepository(session).list_by_project(shot.project_id)
    ordered = sorted(shots, key=lambda row: row.shot_no)
    for index, row in enumerate(ordered):
        if row.shot_id == shot.shot_id and index > 0:
            return ordered[index - 1]
    return None

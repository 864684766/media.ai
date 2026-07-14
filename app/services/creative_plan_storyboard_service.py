"""策划→分镜编排服务（阶段 G2）。

【职责】
    校验已确认视频大纲 → 拆镜 → 调用 submit_storyboard 入库。

【何时调用】
    POST /api/v1/creative/plans/{plan_id}/storyboard
"""

from sqlalchemy.orm import Session

from app.schemas.creative_plan import CreativePlanStoryboardRequest, CreativePlanStoryboardResponse
from app.schemas.video_shot import StoryboardSubmitRequest
from app.services.creative_plan_storyboard_errors import CreativePlanStoryboardNotFoundError
from app.services.creative_plan_storyboard_validator import validate_plan_for_storyboard
from app.services.plan_storyboard_project_resolver import resolve_storyboard_project_id
from app.services.plan_storyboard_shot_source import resolve_shots_for_plan
from app.services.storyboard_service import submit_storyboard
from app.storage.postgres.creative_plan_repository import CreativePlanRepository


def generate_storyboard_from_approved_plan(
    session: Session,
    plan_id: str,
    body: CreativePlanStoryboardRequest,
) -> CreativePlanStoryboardResponse:
    """按已确认大纲生成分镜并入库。

    参数:
        session: PG Session。
        plan_id: 大纲 id。
        body: 可选 project_id 覆盖。

    返回:
        CreativePlanStoryboardResponse: 含 plan_id 与入库结果。
    """
    row = _load_plan_row(session, plan_id)
    validate_plan_for_storyboard(row)
    project_id = resolve_storyboard_project_id(row, body)
    shots = resolve_shots_for_plan(row)
    submit_req = StoryboardSubmitRequest(shots=shots)
    submit_res = submit_storyboard(session, project_id, submit_req)
    return _wrap_response(plan_id, submit_res)


def _load_plan_row(session: Session, plan_id: str):
    """加载大纲或抛 NotFound。"""
    row = CreativePlanRepository(session).get(plan_id)
    if row is None:
        raise CreativePlanStoryboardNotFoundError(plan_id)
    return row


def _wrap_response(plan_id: str, submit_res) -> CreativePlanStoryboardResponse:
    """包装 submit 结果为 G2 响应。"""
    return CreativePlanStoryboardResponse(
        plan_id=plan_id,
        project_id=submit_res.project_id,
        replaced_count=submit_res.replaced_count,
        shots=submit_res.shots,
    )

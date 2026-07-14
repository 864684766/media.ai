"""策划→分镜 project_id 解析。"""

from app.models.postgres.creative_plan_model import CreativePlanModel
from app.schemas.creative_plan import CreativePlanStoryboardRequest
from app.services.creative_plan_storyboard_errors import CreativePlanStoryboardProjectError


def resolve_storyboard_project_id(
    row: CreativePlanModel,
    body: CreativePlanStoryboardRequest,
) -> str:
    """从请求体或大纲记录解析 project_id。

    参数:
        row: 大纲 ORM。
        body: 可选 project_id 覆盖。

    返回:
        str: 非空 project_id。

    异常:
        CreativePlanStoryboardProjectError: 两处均无有效 id。
    """
    candidate = (body.project_id or row.project_id or "").strip()
    if not candidate:
        raise CreativePlanStoryboardProjectError("缺少 project_id")
    return candidate
